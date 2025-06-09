from django.urls import path
from vault.views import (
    CardCreateView,
    CardListView,
    CardUpdateView,
    CardDeleteView,
    test_card_price_view,
    test_charizard_sv03,
    test_get_all_sets,
)


urlpatterns = [
    path("create/", CardCreateView.as_view(), name="card-create"),
    path("", CardListView.as_view(), name="card-list"),
    path("update/<int:pk>/", CardUpdateView.as_view(), name="card-update"),
    path("delete/<int:pk>/", CardDeleteView.as_view(), name="card-delete"),
    path("test-price/", test_card_price_view),
    path("test-zard/", test_charizard_sv03),
    path("test-sets/", test_get_all_sets),
]
