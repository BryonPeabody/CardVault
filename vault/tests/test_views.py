# Test list/detail/create view behavior


import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from vault.models import Card


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

