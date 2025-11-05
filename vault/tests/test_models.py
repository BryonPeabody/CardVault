# Test model logic


import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from vault.models import Card


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="password123")


@pytest.mark.django_db
def test_card_str_returns_name(user):
    """Checks that the __str__ method returns the card name."""
    card = Card.objects.create(
        user=user,
        card_name="Pikachu",
        set_name="Base Set",
        language="EN",
        card_number="25",
        condition="NM",
    )

    assert str(card) == "Pikachu (BASE SET #25)"

