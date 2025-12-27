from django.urls import path
from vault.views import (
    CardCreateView,
    CardListView,
    CardUpdateView,
    CardDeleteView,
    refresh_prices,
)


urlpatterns = [
    path("create/", CardCreateView.as_view(), name="card-create"),
    path("", CardListView.as_view(), name="card-list"),
    path("update/<int:pk>/", CardUpdateView.as_view(), name="card-update"),
    path("delete/<int:pk>/", CardDeleteView.as_view(), name="card-delete"),
    path("refresh-prices/", refresh_prices, name="refresh-prices"),

]
