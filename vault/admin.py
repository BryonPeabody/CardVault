from django.contrib import admin
from .models import Card, PriceSnapshot


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        "card_name",
        "set_name",
        "card_number",
        "condition",
        "language",
        "value_usd",
    )
    list_filter = ("set_name", "condition", "language")
    search_fields = ("card_name", "set_name", "card_number")


@admin.register(PriceSnapshot)
class PriceSnapshotAdmin(admin.ModelAdmin):
    list_display = ("card", "price", "as_of_date", "source")
    ordering = ("card__card_name", "-as_of_date")
    list_filter = ("as_of_date",)
