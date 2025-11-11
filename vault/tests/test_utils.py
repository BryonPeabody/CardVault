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
                "number": "1",
                "id": "sv2a-001",
                "cardmarket": {
                    "prices": {"averageSellPrice": 12.34},
                    "updatedAt": "2025/11/05",
                },
            }
        ]
    }

    result = extract_card_price(mock_data, "Bulbasaur", "1", "151")

    assert result["price"] == 12.34
    assert result["price_date"] == date(2025, 11, 5)


def test_extract_card_price_no_data_key():
    """Should return error when data key missing"""

    result = extract_card_price({}, "Bulbasaur", "1", "151")
    assert result["error"] == "No data received from price API"


def test_extract_card_price_unknown_set():
    """Should return error when set name not in map."""

    result = extract_card_price({"data": []}, "Bulbasaur", "1", "NonexistentSet")
    assert "Unknown set" in result["error"]


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

    result = extract_card_price(mock_data, "Bulbasaur", "1", "151")
    assert result["error"] == "Card not found"
