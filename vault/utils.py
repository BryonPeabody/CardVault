import requests
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def fetch_card_data(name, set_code=None, card_number=None):
    url = f"https://api.tcgdex.net/v2/en/cards?name={name}"
    response = requests.get(url)

    if response.status_code != 200:
        return {}

    data = response.json()  # This is a list

    if not data:
        return {}

    # filter to cards that match the set_code based on ID prefix
    if set_code:
        data = [
            card
            for card in data
            if card.get("id", "").lower().startswith(set_code.lower() + "-")
        ]

    if not data:
        return {}

    if card_number:
        card_number = str(card_number).strip()
        data = [
            card
            for card in data
            if card.get("id", "").lower().endswith(f"-{card_number}")
        ]

    data = [
        card for card in data if card.get("id", "").lower().endswith(f"-{card_number}")
    ]

    # Prefer cards with an image
    data = [card for card in data if card.get("image")]

    if not data:
        return {}

    card = data[0]  # Use the first match

    return {
        "name": card.get("name"),
        "image_url": card.get("image")
        + "/high.png",  # requires the added string for image
        "card_id": card.get("id"),
    }


# needed for pricing api as it accepts sv3 instead of sv03 for filtering
def normalize_set_code_for_api(set_code):
    print(f"Original set_code: {set_code}")
    for i, char in enumerate(set_code):
        if char.isdigit():
            prefix = set_code[:i]
            suffix = set_code[i:]
            break
    else:
        return set_code

    print(f"Prefix: {prefix}, Suffix before normalization: {suffix}")

    if "." in suffix:
        whole, decimal = suffix.split(".")
        print(f"Whole before int: {whole}, Decimal: {decimal}")
        whole = str(int(whole))
        suffix = whole + "pt" + decimal
    else:
        suffix = str(int(suffix))

    normalized = prefix + suffix
    print(f"Normalized set_code: {normalized}")
    return normalized


def fetch_card_price(card_name, set_code):
    api_key = getattr(settings, "CARDVAULT_API_KEY", None)
    if not api_key:
        logger.warning("CARDVAULT_API_KEY missing - skipping price fetch.")
        return {"error": "Missing API key"}

    url = "https://www.pokemonpricetracker.com/api/prices"
    headers = {"Authorization": f"Bearer {api_key}"}

    set_code = normalize_set_code_for_api(set_code)
    params = {"setId": set_code, "name": card_name}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text, "status": response.status_code}


def extract_card_price(data, name, number, set_code):
    if not data or "data" not in data:
        logger.warning("no valid pricing data provided to extract_card_price.")
        return {"error": "No data received from price API"}

    set_code = normalize_set_code_for_api(set_code)
    for card in data.get("data", []):

        if (
            card.get("name", "").lower() == name.lower()
            and card.get("number") == number
            and card.get("id", "").startswith(set_code)
        ):
            print("MATCH FOUND:", card.get("id"))

            try:
                price = card["cardmarket"]["prices"]["averageSellPrice"]
                raw_date = card["cardmarket"]["updatedAt"]
                formatted_date = datetime.strptime(raw_date, "%Y/%m/%d").date()
                print("PRICE FOUND:", price, "DATE:", formatted_date)

                return {"price": price, "price_date": formatted_date}
            except (KeyError, TypeError) as e:
                print("ERROR GETTING PRICE:", e)
                return {"error": "Price data missing"}
    return {"error": "Card not found"}


def fetch_sets():
    api_key = getattr(settings, "CARDVAULT_API_KEY", None)
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(
        "https://www.pokemonpricetracker.com/api/v1/sets", headers=headers
    )
    sets = response.json()
    print(sets)
