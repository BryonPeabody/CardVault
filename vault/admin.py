from django.contrib import admin
from .models import Card


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
