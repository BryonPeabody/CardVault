# Test helper functions


from vault.utils import _pad_card_number_for_image, extract_card_price


def test_pad_card_number_for_image():
    assert _pad_card_number_for_image(6) == "006"
    assert _pad_card_number_for_image("25") == "025"
    assert _pad_card_number_for_image("003") == "003"
    assert _pad_card_number_for_image(" 7 ") == "007"


def test_extract_card_price_valid(monkeypatch):
    """Should return price and date for matching card data"""

    # fake map since PRICE_SET_MAP is in another module
    from vault import utils

    utils.PRICE_SET_MAP = {"151": "151"}

    mock_data = {
        "data": [
            {
                "name": "Bulbasaur",
                "cardNumber": "001/165",
                "prices": {
                    "market": 12.34,
                    "lastUpdated": "2025-11-05T10:00:00.000Z",
                },
            }
        ]
    }

    result = extract_card_price(mock_data, "1")

    assert result["price"] == 12.34
    assert result["price_date"] == "2025-11-05"


def test_extract_card_price_no_data_key():
    """Should return error when data key missing"""

    result = extract_card_price({}, "1")
    assert result["error"] == "No data received from price API"


def test_extract_card_price_card_not_found(monkeypatch):
    """Should return error when card does not match any in data."""

    from vault import utils

    utils.PRICE_SET_MAP = {"151": "151"}

    mock_data = {
        "data": [
            {
                "name": "Charmander",
                "cardNumber": "005/165",
                "prices": {
                    "market": 15.15,
                    "lastUpdated": "2025-11-05T10:00:00.000Z",
                },
            }
        ]
    }

    result = extract_card_price(mock_data, "1")
    assert result["error"] == "Card number 001 not found"
