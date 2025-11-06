# Shared user model for testing suite

import pytest
from django.contrib.auth.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="password123")
