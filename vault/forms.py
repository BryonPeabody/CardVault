from django import forms
from .models import Card


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ["card_name", "set_name", "language", "card_number", "condition"]
