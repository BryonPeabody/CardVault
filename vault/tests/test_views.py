# Test list/detail/create view behavior


import pytest
from django.urls import reverse
from django.test import Client
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from unittest.mock import patch
from vault.models import Card, PriceSnapshot


""" 
    When creating a card for tests, the set_name must be one of the sets listed in the constants.py file
    or else card creation will fail.
"""


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
    """Logged in user can visit card create form"""

    # Create and login a user
    client = Client()
    client.force_login(user)

    # Attempt to see card creation form
    url = reverse("card-create")
    response = client.get(url)

    # Ensure success
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_card_create_view_redirects_if_not_logged_in():
    """Non-Logged in user is redirected to login page"""
    client = Client()

    # Attempt to see card creation form without logging in a user
    url = reverse("card-create")
    response = client.get(url)

    # Ensure it fails and redirects to login page
    assert response.status_code == 302
    assert "/login" in response.url


@pytest.mark.django_db
def test_card_create_view_creates_card(monkeypatch, user):
    """Logged in user can create a card"""

    # Create and login a user
    client = Client()
    client.force_login(user)

    # Mock helper function so testing does not hit apis
    def get_card_image_url_or_placeholder(*, card_name, set_name, card_number):
        return "https://example.com/fake.jpg"

    monkeypatch.setattr(
        "vault.views.get_card_image_url_or_placeholder",
        get_card_image_url_or_placeholder,
    )

    def fake_fetch_card_price(card_name, set_name):
        return {"data": [{"price": 10.50, "date": "2025-11-05"}]}

    def fake_extract_card_price(data, card_number):
        return {"price": 10.50, "price_date": "2025-11-05"}

    monkeypatch.setattr("vault.forms.fetch_card_price", fake_fetch_card_price)
    monkeypatch.setattr("vault.forms.extract_card_price", fake_extract_card_price)

    # Post valid form data
    form_data = {
        "card_name": "Bulbasaur",
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


# --------------- update view tests


@pytest.mark.django_db
def test_card_update_view_redirects_non_logged_in_user(user):
    client = Client()

    card = Card.objects.create(
        user=user,
        card_name="Bulbasaur",
        set_name="151",
        language="EN",
        card_number="1",
        condition="M",
    )
    url = reverse("card-update", args=[card.pk])
    response = client.get(url)

    assert response.status_code == 302
    assert "/login" in response.url


@pytest.mark.django_db
def test_card_update_view_updates_only_condition(user):
    client = Client()
    client.force_login(user)

    card = Card.objects.create(
        user=user,
        card_name="Bulbasaur",
        set_name="151",
        language="EN",
        card_number="1",
        condition="M",
    )

    url = reverse("card-update", args=[card.pk])

    response = client.post(
        url,
        data={
            "condition": "LP",
            # Only condition should be able to update
            "card_name": "Pikachu",
            "set_name": "Base",
            "card_number": "10",
            "language": "JP",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("card-list")

    card.refresh_from_db()
    assert card.condition == "LP"
    assert card.card_name == "Bulbasaur"
    assert card.set_name == "151"
    assert card.card_number == "1"
    assert card.language == "EN"


@pytest.mark.django_db
def test_logged_in_user_cannot_update_another_users_card(user):
    """Ensure logged in user can not update a different user's card"""
    # Log in user
    client = Client()
    client.force_login(user)

    # Create second user
    other_user = user.__class__.objects.create_user(
        username="otherUser", password="pass123"
    )

    # Create card owned by second user
    card = Card.objects.create(
        user=other_user,
        card_name="Bulbasaur",
        card_number="1",
        language="EN",
        set_name="151",
        condition="NM",
    )

    # Attempt to pull update form for second user's card for logged in user
    url = reverse("card-update", args=[card.pk])
    response = client.get(url)

    # Ensure the card is filtered out of logged in user data and page does not render
    assert response.status_code == 404


# ----------------- delete view tests


@pytest.mark.django_db
def test_card_delete_view_reroutes_non_logged_in_user(user):
    """Ensure a user must be logged in to delete a card or will be redirected to login"""
    client = Client()

    # Create a card in database
    card = Card.objects.create(
        user=user,
        card_name="Bulbasaur",
        card_number="1",
        language="EN",
        set_name="151",
        condition="NM",
    )

    # Attempt a delete without login
    url = reverse("card-delete", args=[card.pk])
    response = client.post(url)

    # Ensure proper redirect and that the card remains in db
    assert response.status_code == 302
    assert "/login" in response.url
    assert Card.objects.filter(pk=card.pk).exists()


@pytest.mark.django_db
def test_logged_in_user_can_delete_a_card(user):
    """Ensure a logged in user can delete their card"""

    # Create and login a user
    client = Client()
    client.force_login(user)

    # Create a card in database for user
    card = Card.objects.create(
        user=user,
        card_name="Bulbasaur",
        card_number="1",
        language="EN",
        set_name="151",
        condition="NM",
    )

    # Attempt a delete of the card
    url = reverse("card-delete", args=[card.pk])
    response = client.post(url)

    # Ensure proper redirect and the card is deleted
    assert response.status_code == 302
    expected_url = reverse("card-list")
    assert response.url == expected_url
    assert not Card.objects.filter(pk=card.pk).exists()


@pytest.mark.django_db
def test_user_cant_delete_different_users_card(user):
    """Ensure a user can not delete another user's card"""
    # Create and login user
    client = Client()
    client.force_login(user)

    # Create second user
    other_user = user.__class__.objects.create_user(
        username="other_user", password="pass123"
    )

    # Create card in second user's db
    foreign_card = Card.objects.create(
        user=other_user,
        card_name="Bulbasaur",
        card_number="1",
        language="EN",
        set_name="151",
        condition="NM",
    )

    # Attempt to delete from unauthorized first user
    url = reverse("card-delete", args=[foreign_card.pk])
    response = client.post(url)

    # Ensure delete post fails
    assert response.status_code == 404
    assert Card.objects.filter(pk=foreign_card.pk).exists()


# ------------------ collection value series tests


@pytest.mark.django_db
def test_collection_value_series_requires_login():
    client = Client()

    url = reverse("collection-value-series")
    response = client.get(url)

    assert response.status_code == 302
    assert "/login" in response.url


@pytest.mark.django_db
def test_user_with_no_price_snapshots_returns_empty(user):
    client = Client()
    client.force_login(user)

    url = reverse("collection-value-series")
    response = client.get(url)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_value_series_returns_aggregated_data_for_user_and_ignores_other_user_data(
    user, other_user
):
    client = Client()
    client.force_login(user)

    today = timezone.localdate()

    # ----- User's cards -----
    card1 = Card.objects.create(
        user=user,
        card_name="Pikachu",
        set_name="151",
        language="EN",
        card_number="25",
        condition="NM",
    )

    card2 = Card.objects.create(
        user=user,
        card_name="Bulbasaur",
        set_name="151",
        language="EN",
        card_number="1",
        condition="NM",
    )

    PriceSnapshot.objects.create(
        card=card1,
        as_of_date=today,
        price=Decimal("10.00"),
        source="test",
        currency="USD",
    )

    PriceSnapshot.objects.create(
        card=card2,
        as_of_date=today,
        price=Decimal("5.00"),
        source="test",
        currency="USD",
    )

    # ----- Other user's data (should be ignored) -----
    other_card = Card.objects.create(
        user=other_user,
        card_name="Charmander",
        set_name="151",
        language="EN",
        card_number="4",
        condition="NM",
    )

    PriceSnapshot.objects.create(
        card=other_card,
        as_of_date=today,
        price=Decimal("100.00"),
        source="test",
        currency="USD",
    )

    url = reverse("collection-value-series")
    response = client.get(url)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["date"] == today.isoformat()
    assert Decimal(data[0]["value"]) == Decimal("15.00")


@pytest.mark.django_db
def test_value_series_respects_range_override(user):
    client = Client()
    client.force_login(user)

    today = timezone.localdate()
    old_date = today - timedelta(days=60)

    card = Card.objects.create(
        user=user,
        card_name="Pikachu",
        set_name="151",
        language="EN",
        card_number="25",
        condition="NM",
    )

    PriceSnapshot.objects.create(
        card=card,
        as_of_date=old_date,
        price=Decimal("20.00"),
        source="test",
        currency="USD",
    )

    url = reverse("collection-value-series")

    # ---- Default range (30d) should exclude snapshot ----
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == []

    # ---- Expanded range (90d) should include snapshot ----
    response = client.get(f"{url}?range=90d")
    data = response.json()

    assert len(data) == 1
    assert data[0]["date"] == old_date.isoformat()
    assert Decimal(data[0]["value"]) == Decimal("20.00")


# -------------------- Collection graph view tests --------


def test_collection_graph_requires_login(client):
    response = client.get(reverse("collection-graph"))
    assert response.status_code == 302


def test_collection_graph_default_range(user):
    client = Client()
    client.force_login(user)
    response = client.get(reverse("collection-graph"))
    assert response.context["range"] == "30d"


def test_collection_graph_custom_range(user):
    client = Client()
    client.force_login(user)
    response = client.get(reverse("collection-graph") + "?range=90d")
    assert response.context["range"] == "90d"


# ----------------- Refresh prices view tests -----


@patch("vault.views.refresh_prices_for_user")
def test_refresh_prices_post_calls_service(mock_refresh, client, user):
    client.force_login(user)

    response = client.post(reverse("refresh-prices"))

    mock_refresh.assert_called_once_with(user)
    assert response.status_code == 302


@patch("vault.views.refresh_prices_for_user")
def test_refresh_prices_get_does_not_call_service(mock_refresh, client, user):
    client.force_login(user)

    response = client.get(reverse("refresh-prices"))

    mock_refresh.assert_not_called()
    assert response.status_code == 302
