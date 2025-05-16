from django.contrib import admin
from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'set_code', 'card_number', 'condition', 'language', 'value_usd')
    list_filter = ('set_code', 'condition', 'language')
    search_fields = ('name', 'set_code', 'card_number')
