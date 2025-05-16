from django.urls import path
from vault.views import CardCreateView, CardListView

urlpatterns = [
    path('create/', CardCreateView.as_view(), name='card-create'),
    path('', CardListView.as_view(), name='card-list')
]