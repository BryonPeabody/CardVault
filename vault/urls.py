from django.urls import path
from vault.views import (
    CardCreateView,
    CardListView,
    CardUpdateView,
    CardDeleteView,
    refresh_prices,
    collection_value_series,
    CollectionGraphView,
)


urlpatterns = [
    path("create/", CardCreateView.as_view(), name="card-create"),
    path("", CardListView.as_view(), name="card-list"),
    path("update/<int:pk>/", CardUpdateView.as_view(), name="card-update"),
    path("delete/<int:pk>/", CardDeleteView.as_view(), name="card-delete"),
    path("refresh-prices/", refresh_prices, name="refresh-prices"),
    path(
        "api/collection-value-series/",
        collection_value_series,
        name="collection-value-series",
    ),
    path("collection/graph/", CollectionGraphView.as_view(), name="collection-graph"),
]
