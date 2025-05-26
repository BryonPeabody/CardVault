import requests


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
        data = [card for card in data if card.get("id", "").lower().endswith(f"-{card_number}")]

    data = [
        card for card in data
        if card.get("id", "").lower().endswith(f"-{card_number}")
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
