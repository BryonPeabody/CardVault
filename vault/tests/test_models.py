# Test model logic


import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from vault.models import Card


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

    assert str(card) == "Pikachu (Base Set #25)"


@pytest.mark.django_db
def test_card_save_strips_name_and_uppercases_set(user):
    """Ensure save() strips whitespace and uppercases set_name"""
    card = Card.objects.create(
        user=user,
        # use extra whitespace around card_name
        card_name="   Charizard   ",
        # use all lower case set_name
        set_name="paldea evolved",
        language="EN",
        card_number="4",
        condition="M",
    )
    card.refresh_from_db()

    assert card.card_name == "Charizard"


@pytest.mark.django_db
def test_card_clean_prevents_duplicate_cards(user):
    """Ensure clean() prevents duplicate cards (case insensitive)"""
    Card.objects.create(
        user=user,
        card_name="Pikachu",
        set_name="Base Set",
        language="EN",
        card_number="25",
        condition="NM",
    )

    # attempt to create duplicate
    duplicate = Card(
        user=user,
        card_name="pikachu",  # lowercase variation
        set_name="base set",  # lowercase variation
        language="EN",
        card_number="25",
        condition="LP",
    )

    with pytest.raises(ValidationError) as excinfo:
        duplicate.clean()

    assert "already exists" in str(excinfo.value)
