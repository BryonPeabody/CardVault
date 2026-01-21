# Test form validation and errors


import pytest
from vault.forms import CardForm


@pytest.mark.django_db
def test_valid_card_is_validated_by_form(monkeypatch):

    def fake_fetch_card_price(card_name, set_name):
        return {"data": [{"price": 10.50, "date": "2025-11-05"}]}

    def fake_extract_card_price(data, card_number):
        return {"price": 10.50, "price_date": "2025-11-05"}

    monkeypatch.setattr("vault.forms.fetch_card_price", fake_fetch_card_price)
    monkeypatch.setattr("vault.forms.extract_card_price", fake_extract_card_price)

    form = CardForm(
        data={
            "card_name": "Pikachu",
            "set_name": "151",
            "language": "EN",
            "card_number": "58",
            "condition": "NM",
        }
    )

    assert form.is_valid()
    assert "price" in form.cleaned_price
    assert "price_date" in form.cleaned_price


@pytest.mark.django_db
def test_fetch_card_price_errors_out_validation_errors_out(monkeypatch):

    def fake_fetch_card_price(card_name, set_name):
        return {"error": "whichever error"}

    monkeypatch.setattr("vault.forms.fetch_card_price", fake_fetch_card_price)

    form = CardForm(
        data={
            "card_name": "Pikachu",
            "set_name": "151",
            "language": "EN",
            "card_number": "58",
            "condition": "NM",
        }
    )

    assert not form.is_valid()
    assert form.non_field_errors()
    assert "Price lookup failed" in form.non_field_errors()[0]


@pytest.mark.django_db
def test_extract_card_price_errors_out_validation_errors_out(monkeypatch):

    def fake_fetch_card_price(card_name, set_name):
        return {"data": [{"price": 10.50, "date": "2025-11-05"}]}

    def fake_extract_card_price(data, card_number):
        return {"error": "whichever error"}

    monkeypatch.setattr("vault.forms.fetch_card_price", fake_fetch_card_price)
    monkeypatch.setattr("vault.forms.extract_card_price", fake_extract_card_price)

    form = CardForm(
        data={
            "card_name": "Pikachu",
            "set_name": "151",
            "language": "EN",
            "card_number": "58",
            "condition": "NM",
        }
    )

    assert not form.is_valid()
    assert "card_name" in form.errors
