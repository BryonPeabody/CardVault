# Test list/detail/create view behavior


import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from vault.models import Card


# --------------list view tests


@pytest.mark.django_db
def test_card_list_view_shows_only_user_cards(user):
    """Logged in user only sees their own cards"""
    client = Client()
    client.force_login(user)

    card1 = Card.objects.create(
        user=user,
        card_name="Pikachu",
        set_name="Base_Set",
        language="EN",
        card_number="25",
        condition="NM",
    )

    other_user = user.__class__.objects.create_user(username="other", password="pass")
    Card.objects.create(
        user=other_user,
        card_name="Charizard",
        set_name="Base Set",
        language="EN",
        card_number="4",
        condition="M",
    )

    url = reverse("card-list")
    response = client.get(url)

    assert response.status_code == 200

    cards = response.context["cards"]

    assert card1 in cards
    assert all(card.user == user for card in cards)
    assert not any(c.card_name == "Charizard" for c in cards)


@pytest.mark.django_db
def test_card_list_view_redirects_if_not_logged_in():
    client = Client()
    url = reverse("card-list")
    response = client.get(url)
    assert response.status_code == 302  # redirect to login
    assert "/login" in response.url


# ------------------ create view tests


@pytest.mark.django_db
def test_card_create_view_renders_form_for_logged_in_user(user):
    """ Logged in user can visit card create form """
    client = Client()
    client.force_login(user)

    url = reverse("card-create")
    response = client.get(url)

    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_card_create_view_redirects_if_not_logged_in():
    """ Non-Logged in user is redirected to login page"""
    client = Client()
    url = reverse("card-create")
    response = client.get(url)
    assert response.status_code == 302
    assert "/login" in response.url


@pytest.mark.django_db
def test_card_create_view_creates_card(monkeypatch, user):
    """ Logged in user can create a card """
    client = Client()
    client.force_login(user)

    # Mock helper function so testing does not hit apis
    def fake_fetch_card_data(card_name, set_name, card_number):
        return {"image_url": "https://example.com/fake.jpg"}

    def fake_fetch_card_price(card_name, set_name):
        return {"data": [{"price": 10.50, "date": "2025-11-05"}]}

    def fake_extract_card_price(data, card_name, card_number, set_name):
        return {"price": 10.50, "price_date": "2025-11-05"}

    monkeypatch.setattr("vault.views.fetch_card_data", fake_fetch_card_data)
    monkeypatch.setattr("vault.views.fetch_card_price", fake_fetch_card_price)
    monkeypatch.setattr("vault.views.extract_card_price", fake_extract_card_price)

    # Post valid form data
    form_data = {
        "card_name": "Bulbasaur",
        # Set name must be one of the valid choices in constants.py or form.is_valid will fail and we will not redirect
        "set_name": "151",
        "language": "EN",
        "card_number": "1",
        "condition": "NM",
    }

    url = reverse("card-create")
    response = client.post(url, data=form_data)

    # Make sure view redirects to card list after card creation
    assert response.status_code == 302
    assert response.url == reverse("card-list")

    # Verify the card was saved correctly
    card = Card.objects.get(user=user, card_name="Bulbasaur")
    assert card.image_url == "https://example.com/fake.jpg"
    assert float(card.value_usd) == 10.50



