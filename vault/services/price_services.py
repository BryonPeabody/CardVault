from django.conf import settings
import logging
from django.utils import timezone
from decimal import Decimal

from vault.utils import fetch_card_price, extract_card_price
from vault.models import Card, PriceSnapshot
from vault.services.image_services import get_card_image_url_or_placeholder

logger = logging.getLogger(__name__)


def create_initial_snapshot(card):
    if card.value_usd is None:
        return False

    today = timezone.localdate()
    PriceSnapshot.objects.update_or_create(
        card=card,
        as_of_date=today,
        defaults={
            "price": card.value_usd,
            "source": "pokemonpricetracker",
            "currency": "USD",
        },
    )
    return True


def refresh_prices_for_user(user) -> int:
    today = timezone.localdate()
    cards = Card.objects.filter(user=user)

    updated = 0

    for card in cards:
        # Attempt to heal any missing images (image api occasionally flaky)
        if not card.image_url or card.image_url == settings.CARD_IMAGE_PLACEHOLDER_URL:
            new_url = get_card_image_url_or_placeholder(
                card_name=card.card_name,
                set_name=card.set_name,
                card_number=card.card_number,
            )
            if (
                new_url != settings.CARD_IMAGE_PLACEHOLDER_URL
                and new_url != card.image_url
            ):
                card.image_url = new_url
                card.save(update_fields=["image_url"])

        # Look for current price on each card
        if card.price_last_updated == today:
            continue  # Skip if price is already current
        data = fetch_card_price(card.card_name, card.set_name)
        if "error" in data:
            logger.warning(
                "Fetch card price failed for %s %s #%s status=%s error=%s",
                card.card_name,
                card.set_name,
                card.card_number,
                data.get("status"),
                data.get("error"),
            )
            continue
        result = extract_card_price(data, card.card_number)

        if "error" in result:
            logger.warning(
                "Price extract failed for %s %s #%s: %s",
                card.card_name,
                card.set_name,
                card.card_number,
                result["error"],
            )
            continue

        price = Decimal(str(result["price"]))

        # Add new price to price history model
        PriceSnapshot.objects.update_or_create(
            card=card,
            as_of_date=today,
            defaults={
                "price": price,
                "source": "pokemonpricetracker",
                "currency": "USD",
            },
        )

        # Save current price onto the card model
        card.value_usd = price
        card.price_last_updated = today
        card.save(update_fields=["value_usd", "price_last_updated"])

        updated += 1

    return updated
