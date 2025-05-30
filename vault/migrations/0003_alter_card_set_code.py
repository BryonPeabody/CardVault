# Generated by Django 5.2.1 on 2025-05-26 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vault", "0002_alter_card_set_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="card",
            name="set_code",
            field=models.CharField(
                choices=[
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
                ],
                max_length=10,
            ),
        ),
    ]
