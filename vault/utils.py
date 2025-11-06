import requests
from django.conf import settings
from datetime import datetime
import logging

from .constants import IMAGE_SET_MAP, PRICE_SET_MAP

logger = logging.getLogger(__name__)


def _pad_card_number_for_image(n: str | int) -> str:
    """
    TCGdex image id's use a 3-digit card number: ie, '006'
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


def fetch_card_price(card_name: str, set_name: str):
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
    url = "https://www.pokemonpricetracker.com/api/prices"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"setId": set_code, "name": card_name}
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


def extract_card_price(
    data: dict, card_name: str, card_number: str | int, set_name: str
):
    # make sure data from fetch_card_price is available to work on
    if not data or "data" not in data:
        logger.warning("No valid pricing data provided to extract_card_price.")
        return {"error": "No data received from price API"}
    # and make sure we have a set code
    set_code = PRICE_SET_MAP.get(set_name)
    if not set_code:
        return {"error": f"Unknown set for price api: {set_name}"}
    number_str = str(card_number).strip()
    # dig through the dictionary
    for card in data.get("data", []):
        try:
            if (
                # find the matching card
                card.get("name", "").lower() == card_name.lower()
                and str(card.get("number", "")).strip() == number_str
                and str(card.get("id", "")).startswith(set_code)
            ):
                # pull average sale price and the date updated for display
                price = card["cardmarket"]["prices"]["averageSellPrice"]
                raw_date = card["cardmarket"]["updatedAt"]  # YYYY/MM/DD
                price_date = datetime.strptime(raw_date, "%Y/%m/%d").date()
                return {"price": price, "price_date": price_date}
        # or fail gracefully
        except (KeyError, TypeError, ValueError):
            continue
    return {"error": "Card not found"}
