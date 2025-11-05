import pytest
from vault.models import Card


@pytest.mark.django_db
def test_card_str_returns_name():
    """Checks that the __str__ method returns the card name."""
    card = Card(
        card_name="Pikachu",
        set_name="Base Set",
        card_number="25"
    )

    assert str(card) == "Pikachu (Base Set #25)"

