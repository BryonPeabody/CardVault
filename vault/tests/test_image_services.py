from unittest.mock import patch
from django.conf import settings

from vault.services.image_services import get_card_image_url_or_placeholder


@patch("vault.utils.fetch_card_data", return_value=None)
def test_image_wrapper_returns_placeholder_when_api_fails(mock_fetch):
    url = get_card_image_url_or_placeholder(
        card_name="Bulbasaur",
        set_name="151",
        card_number="1",
    )

    assert url == settings.CARD_IMAGE_PLACEHOLDER_URL
