
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Card(models.Model):
    CONDITION_CHOICES = [
        ('M', 'Mint'),
        ('NM', 'Near Mint'),
        ('LP', 'Lightly Played'),
        ('MP', 'Moderately Played'),
        ('HP', 'Heavily Played'),
        ('D', 'Damaged'),
    ]

    LANGUAGE_CHOICES = [
        ('EN', 'English'),
        ('JP', 'Japanese'),
        ('FR', 'French'),
        ('DE', 'German'),
        # add more as needed
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    set_code = models.CharField(max_length=10)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    card_number = models.CharField(max_length=10)
    condition = models.CharField(max_length=2, choices=CONDITION_CHOICES)

    image_url = models.URLField(blank=True, null=True)
    value_usd = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.set_code = self.set_code.upper()
        super().save(*args, **kwargs)

    def clean(self):
        if Card.objects.filter(
                name__iexact=self.name,
                set_code__iexact=self.set_code,
                card_number=self.card_number
        ).exclude(pk=self.pk).exists():
            raise ValidationError("This card already exists (case-insensitive match).")

    def __str__(self):
        return f"{self.name} ({self.set_code} #{self.card_number})"



