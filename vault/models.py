from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone


class Card(models.Model):
    CONDITION_CHOICES = [
        ("M", "Mint"),
        ("NM", "Near Mint"),
        ("LP", "Lightly Played"),
        ("MP", "Moderately Played"),
        ("HP", "Heavily Played"),
        ("D", "Damaged"),
    ]

    LANGUAGE_CHOICES = [
        ("EN", "English"),
        ("JP", "Japanese"),
        ("FR", "French"),
        ("DE", "German"),
        # add more as needed
    ]
    SET_CHOICES = [
        ("sv01", "Scarlet & Violet Base"),
        ("sv02", "Paldea Evolved"),
        ("sv03", "Obsidian Flames"),
        ("sv03.5", "151"),
        ("sv04", "Paradox Rift"),
        ("sv04.5", "Paldean Fates"),
        ("sv05", "Temporal Forces"),
        ("sv05.5", "Twilight Masquerade"),
        ("sv06", "Shrouded Fable"),
        ("sv07", "Raging Surf"),
        ("sv08", "Surging Sparks"),
        ("sv09", "Prismatic Evolutions"),
        ("sv10", "Destined Rivals"),
        ("svp", "Scarlet & Violet Promos"),
        ("swsh12", "Silver Tempest"),
        ("swsh12.5", "Crown Zenith"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    set_code = models.CharField(max_length=10, choices=SET_CHOICES)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    card_number = models.CharField(max_length=10)
    condition = models.CharField(max_length=2, choices=CONDITION_CHOICES)

    image_url = models.URLField(blank=True, null=True)
    value_usd = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    price_last_updated = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.set_code = self.set_code.upper()
        super().save(*args, **kwargs)

    def clean(self):
        if (
            Card.objects.filter(
                name__iexact=self.name,
                set_code__iexact=self.set_code,
                card_number=self.card_number,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("This card already exists (case-insensitive match).")

    def __str__(self):
        return f"{self.name} ({self.set_code} #{self.card_number})"
