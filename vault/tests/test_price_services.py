import pytest
from unittest.mock import patch
from django.conf import settings
from decimal import Decimal
from django.utils import timezone

from vault.models import Card, PriceSnapshot
from vault.services.price_services import refresh_prices_for_user


@pytest.mark.django_db
@patch("vault.services.price_services.get_card_image_url_or_placeholder")
@patch("vault.services.price_services.fetch_card_price")
@patch("vault.services.price_services.extract_card_price")
def test_refresh_heals_placeholder_image(
    mock_extract,
    mock_fetch_price,
    mock_get_image,
    user,
):
    today = timezone.localdate()

    card = Card.objects.create(
        user=user,
        card_name="Bulbasaur",
        set_name="151",
        language="EN",
        card_number="1",
        condition="M",
        image_url=settings.CARD_IMAGE_PLACEHOLDER_URL,
    )

    # Price side
    mock_fetch_price.return_value = {"ok": True}
    mock_extract.return_value = {"price": 10.0}

    # Image side
    mock_get_image.return_value = "https://example.com/real.png"

    refresh_prices_for_user(user)

    card.refresh_from_db()

    assert card.image_url == "https://example.com/real.png"
    assert card.price_last_updated == today
    assert card.value_usd == Decimal("10.0")


@pytest.mark.django_db
@patch("vault.services.price_services.fetch_card_price")
@patch("vault.services.price_services.extract_card_price")
def test_refresh_skips_cards_with_current_price_data(
    mock_extract,
    mock_fetch_price,
    user,
):
    card = Card.objects.create(
        user=user,
        card_name="Pikachu",
        set_name="151",
        language="EN",
        card_number="58",
        condition="NM",
        image_url="valid_image_url",
        value_usd="10.00",
        price_last_updated=timezone.localdate(),
    )

    assert refresh_prices_for_user(user) == 0

    mock_extract.assert_not_called()
    mock_fetch_price.assert_not_called()
    assert PriceSnapshot.objects.count() == 0


@pytest.mark.django_db
@patch("vault.services.price_services.fetch_card_price")
@patch("vault.services.price_services.extract_card_price")
def test_refresh_skips_cards_where_fetch_price_returns_error(
    mock_extract,
    mock_fetch_price,
    user,
):
    card = Card.objects.create(
        user=user,
        card_name="Pikachu",
        set_name="151",
        language="EN",
        card_number="58",
        condition="NM",
        image_url="valid_image_url",
        value_usd="10.00",
    )

    mock_fetch_price.return_value = {
        "error": "rate limited",
        "status": 429,
    }

    assert refresh_prices_for_user(user) == 0

    mock_extract.assert_not_called()
    mock_fetch_price.assert_called()
    assert PriceSnapshot.objects.count() == 0
