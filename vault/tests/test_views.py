# Test list/detail/create view behavior


import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from vault.models import Card

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
    def fake_fetch_card_data(card_name, set_name, card_number):
        return {"image_url": "https://example.com/fake.jpg"}

    def fake_fetch_card_price(card_name, set_name):
        return {"data": [{"price": 10.50, "date": "2025-11-05"}]}

    def fake_extract_card_price(data, card_number):
        return {"price": 10.50, "price_date": "2025-11-05"}

    monkeypatch.setattr("vault.views.fetch_card_data", fake_fetch_card_data)
    monkeypatch.setattr("vault.views.fetch_card_price", fake_fetch_card_price)
    monkeypatch.setattr("vault.views.extract_card_price", fake_extract_card_price)

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
def test_card_update_view_updates_a_card(user):
    """Ensure a logged in user can update a card in the database"""
    client = Client()
    client.force_login(user)

    # Create original card
    card = Card.objects.create(
        user=user,
        card_name="Bulbasaur",
        set_name="151",
        language="EN",
        card_number="1",
        condition="M",
    )

    # Get to update screen on the created card
    url = reverse("card-update", args=[card.pk])

    # Set data for updated card
    updated_data = {
        "card_name": "Pikachu",
        "set_name": "151",
        "language": "EN",
        "card_number": "10",
        "condition": "NM",
    }

    # Post updated data to the update url
    response = client.post(url, data=updated_data)

    # Ensure expected redirect
    assert response.status_code == 302
    assert response.url == reverse("card-list")

    # Ensure card is updated in database
    card.refresh_from_db()
    assert card.card_name == "Pikachu"
    assert card.card_number == "10"
    assert card.condition == "NM"


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
