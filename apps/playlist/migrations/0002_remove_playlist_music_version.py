# Generated by Django 4.2 on 2025-04-07 21:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playlist',
            name='music_version',
        ),
    ]
