# Test helper functions


import pytest
from vault.utils import _pad_card_number_for_image, extract_card_price
from datetime import date


def test_pad_card_number_for_image():
    assert _pad_card_number_for_image(6) == "006"
    assert _pad_card_number_for_image("25") == "025"
    assert _pad_card_number_for_image("003") == "003"
    assert _pad_card_number_for_image(" 7 ") == "007"


def test_extract_card_price_valid(monkeypatch):
    """Should return price and date for matching card data"""

    # fake map since PRICE_SET_MAP is in another module
    from vault import utils

    utils.PRICE_SET_MAP = {"151": "sv2a"}

    mock_data = {
        "data": [
            {
                "name": "Bulbasaur",
                "cardNumber": "1/165",
                "prices": {
                    "market": 12.34,
                    "lastUpdated": "2025-11-05T10:00:00.000Z",
                    }
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

    utils.PRICE_SET_MAP = {"151": "sv2a"}

    mock_data = {
        "data": [
            {
                "name": "Charmander",
                "number": "5",
                "id": "sv2a-005",
                "cardmarket": {
                    "prices": {"averageSellPrice": 7.77},
                    "updatedAt": "2025/11/05",
                },
            }
        ]
    }

    result = extract_card_price(mock_data, "1")
    assert result["error"] == "Card not found"
