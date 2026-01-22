# Shared user model for testing suite

import pytest
from django.contrib.auth.models import User
from vault.models import Card


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="password123")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="otheruser", password="otherpassword123")


@pytest.fixture
def user_card(db, user):
    return Card.objects.create(
        user=user,
        card_name="Pikachu",
        set_name="151",
        language="EN",
        card_number="58",
        condition="NM",
    )


@pytest.fixture
def other_user_card(db, other_user):
    return Card.objects.create(
        user=other_user,
        card_name="Bulbasaur",
        set_name="151",
        language="EN",
        card_number="1",
        condition="NM",
    )
