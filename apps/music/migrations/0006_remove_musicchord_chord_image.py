# Generated by Django 4.2 on 2025-04-30 13:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("music", "0005_alter_music_options_music_created_at_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="musicchord",
            name="chord_image",
        ),
    ]
