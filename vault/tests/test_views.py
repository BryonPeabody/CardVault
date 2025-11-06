# Test list/detail/create view behavior


import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from vault.models import Card

