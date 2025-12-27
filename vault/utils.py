import requests
from django.conf import settings
from datetime import datetime
import logging

from .constants import IMAGE_SET_MAP, PRICE_SET_MAP

# Price history imports
from django.utils import timezone
from decimal import Decimal
from collections import defaultdict

from .models import Card, PriceSnapshot

logger = logging.getLogger(__name__)


def _pad_card_number_for_image(n: str | int) -> str:
    """
    TCGdex image id's use a 3-digit card number: ie, '006'
    V2 of pokepricetracker endpoints also use this format for endpoints,
    now using this helper for fetch_card_data (image) and extract_card_price (price)
    """
    s = str(n).strip()
    return s.zfill(3)


def fetch_card_data(
    card_name: str, set_name: str, card_number: str | int | None = None
):
    # use official set name and filter through map in constants to get api set_code
    set_code = IMAGE_SET_MAP.get(set_name)
    # graceful exit if set_code not found
    if not set_code:
        logger.error("Missing IMAGE_SET_MAP code for set '%s'", set_name)
        return {}
    # hit api to grab a json list of cards with the name from model
    try:
        url = "https://api.tcgdex.net/v2/en/cards"
        # safe timeout after 10 second if no data received
        resp = requests.get(url, params={"name": card_name}, timeout=10)
        # throws exception on bad request so we don't save a 404 page or the like
        resp.raise_for_status()
        # put data in json list if data is good
        data = resp.json() or []  # list
    except Exception as e:
        logger.exception("TCGdex request failed: %s", e)
        return {}
    # use list comprehension to save only cards that have that name and also the correct set_code
    prefix = f"{set_code.lower()}-"
    candidates = [c for c in data if c.get("id", "").lower().startswith(prefix)]
    # more list comprehension to save from those only the cards with also a proper car_number
    if card_number:
        # calling this function ensures the card number matches the json data from this api
        # ie, '006' rather than '6'
        num3 = _pad_card_number_for_image(card_number)
        exact_id = f"{set_code.lower()}-{num3}"
        # attempt to find an exact match
        exact = [c for c in candidates if c.get("id", "").lower() == exact_id]
        # if no exact match fall back to softer 'endswith' search
        candidates = exact or [
            c for c in candidates if c.get("id", "").lower().endswith(f"-{num3}")
        ]
    # and from those only ones with an image
    candidates = [c for c in candidates if c.get("image")]
    # graceful exit if no matches found
    if not candidates:
        return {}
    # this list should only have one match by now but in case not we'll take the first item
    card = candidates[0]
    # return the information
    return {
        "name": card.get("name"),
        "image_url": (card.get("image") or "") + "/high.png",
        "card_id": card.get("id"),
    }


def fetch_card_price(card_name: str, set_name: str, fetch_all: bool = False):
    # the price API requires a key hidden in .env
    api_key = getattr(settings, "CARDVAULT_API_KEY", None)
    # if someone uses this on github and cannot access my key this will fail gracefully unless they add their own
    if not api_key:
        logger.warning("CARDVAULT_API_KEY missing - skipping price fetch.")
        return {"error": "Missing API key"}
    # use the price set map for the set in question
    set_code = PRICE_SET_MAP.get(set_name)
    # if it is not available fail gracefully
    if not set_code:
        logger.error("Missing PRICE_SET_MAP code for set '%s'", set_name)
        return {"error": "Unknown set for price API"}
    # hit the API passing headers and params to access
    url = "https://www.pokemonpricetracker.com/api/v2/cards"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"set": set_code}
    if fetch_all:
        params["fetchAllInSet"] = "true"
    elif card_name:
        params["search"] = card_name

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        # if all goes well, return json dictionary (how the API formats their data)
        if resp.status_code == 200:
            return resp.json()
        # if not, fail gracefully
        return {"error": resp.text, "status": resp.status_code}
    except Exception as e:
        logger.exception("Price API request failed: %s", e)
        return {"error": "Request failed"}


def extract_card_price(data: dict, card_number: str | int):
    # Safety: ensure API returned something usable
    if not data or "data" not in data:
        logger.warning("No valid pricing data provided to extract_card_price.")
        return {"error": "No data received from price API"}

    padded = _pad_card_number_for_image(card_number)

    # Loop through all card variants in the response
    for card in data.get("data", []):
        try:
            # v2 stores this field as "cardNumber" (e.g. "062/197")
            if str(card.get("cardNumber", "")).startswith(padded):
                # Pull price data
                price = card["prices"]["market"]

                # lastUpdated is ISO 8601, not YYYY/MM/DD
                raw_date = card["prices"]["lastUpdated"]
                price_date = raw_date.split("T")[0]  # YYYY-MM-DD

                return {
                    "price": price,
                    "price_date": price_date,
                    # The following may be useful in future feature expansion
                    # "tcgplayer_id": card.get("tcgPlayerId"),
                    # "variant": card.get("rarity"),
                }

        except Exception as e:
            logger.exception("Failed parsing a card variant: %s", e)
            continue

    return {"error": f"Card number {padded} not found"}


def refresh_prices_for_user(user) -> int:
    today = timezone.localdate()
    cards = Card.objects.filter(user=user)

    # group cards by set_name
    cards_by_set = defaultdict(list)
    for card in cards:
        cards_by_set[card.set_name].append(card)

    updated = 0

    for set_name, cards_in_set in cards_by_set.items():
        # fetch once per set
        # pick any card name just to seed the search
        seed_card = cards_in_set[0]
        data = fetch_card_price(seed_card.card_name, set_name, fetch_all=True)

        if "error" in data:
            logger.warning(
                "Fetch card price failed for set=%s seed_name=%s status=%s error=%s",
                set_name,
                seed_card.card_name,
                data.get("status"),
                data.get("error"),
            )
            continue

        for card in cards_in_set:
            result = extract_card_price(data, card.card_number)

            if "error" in result:
                logger.warning("Price extract failed for %s %s #%s: %s",
                               card.card_name, card.set_name, card.card_number, result["error"])
                continue

            price = Decimal(str(result["price"]))

            PriceSnapshot.objects.update_or_create(
                card=card,
                as_of_date=today,
                defaults={"price": price},
            )

            card.value_usd = price
            card.price_last_updated = today
            card.save(update_fields=["value_usd", "price_last_updated"])

            updated += 1

    return updated
