import pytest
from unittest.mock import patch
from django.conf import settings
from decimal import Decimal
from django.utils import timezone

from vault.models import Card, PriceSnapshot
from vault.services.price_services import refresh_prices_for_user, create_initial_snapshot


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


@pytest.mark.django_db
@patch("vault.services.price_services.fetch_card_price")
@patch("vault.services.price_services.extract_card_price")
def test_refresh_skips_cards_where_extract_price_returns_error(
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

    mock_fetch_price.return_value = {"ok": True}
    mock_extract.return_value = {
        "error": "rate limited",
        "status": 429,
    }

    assert refresh_prices_for_user(user) == 0

    mock_extract.assert_called_once()
    mock_fetch_price.assert_called_once()
    assert PriceSnapshot.objects.count() == 0

    card.refresh_from_db()
    assert card.price_last_updated is None


@pytest.mark.django_db
@patch("vault.services.price_services.fetch_card_price")
@patch("vault.services.price_services.extract_card_price")
def test_refresh_continues_when_one_card_is_skipped(
    mock_extract,
    mock_fetch_price,
    user,
):

    # This card has a current price and should be skipped
    card_1 = Card.objects.create(
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

    # This card should save, no current day price
    card_2 = Card.objects.create(
        user=user,
        card_name="Bulbasaur",
        set_name="151",
        language="EN",
        card_number="58",
        condition="NM",
        image_url="valid_image_url",
        value_usd="10.00",
    )

    mock_fetch_price.return_value = {"ok": True}
    mock_extract.return_value = {"price": 20.00}

    # Make sure one card only is updated
    assert refresh_prices_for_user(user) == 1

    assert PriceSnapshot.objects.count() == 1
    mock_fetch_price.assert_called_once()
    mock_extract.assert_called_once()

    card_1.refresh_from_db()
    card_2.refresh_from_db()

    # Make sure card_1 is unchanged
    assert card_1.price_last_updated == timezone.localdate()
    assert card_1.value_usd == Decimal("10.00")

    # Make sure card_2 is updated
    assert card_2.value_usd == Decimal("20.0")
    assert card_2.price_last_updated == timezone.localdate()


@pytest.mark.django_db
@patch("vault.services.price_services.fetch_card_price")
@patch("vault.services.price_services.extract_card_price")
def test_running_refresh_will_update_card_but_not_twice_in_one_day(
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

    mock_fetch_price.return_value = {"ok": True}
    mock_extract.return_value = {"price": 20.00}

    # Test first pass succeeds
    assert refresh_prices_for_user(user) == 1
    assert PriceSnapshot.objects.count() == 1

    # Test second pass fails
    assert refresh_prices_for_user(user) == 0
    assert PriceSnapshot.objects.count() == 1

    mock_fetch_price.assert_called_once()
    mock_extract.assert_called_once()

    card.refresh_from_db()
    assert card.price_last_updated == timezone.localdate()
    assert card.value_usd == Decimal("20.0")


@pytest.mark.django_db
def test_create_initial_snapshot_will_not_create_snapshot_for_card_without_price(user):
    card = Card.objects.create(
        user=user,
        card_name="Pikachu",
        set_name="151",
        language="EN",
        card_number="58",
        condition="NM",
    )

    assert not create_initial_snapshot(card)
    assert PriceSnapshot.objects.count() == 0


@pytest.mark.django_db
def test_create_initial_snapshot_saves_expected_snapshot_data(user):
    card = Card.objects.create(
        user=user,
        card_name="Pikachu",
        set_name="151",
        language="EN",
        card_number="58",
        condition="NM",
        value_usd="12.84"
    )

    assert create_initial_snapshot(card)
    assert PriceSnapshot.objects.count() == 1

    snapshot = PriceSnapshot.objects.get()

    assert snapshot.card == card
    assert snapshot.price == Decimal("12.84")
    assert snapshot.source == "pokemonpricetracker"
    assert snapshot.currency == "USD"
    assert snapshot.as_of_date == timezone.localdate()

