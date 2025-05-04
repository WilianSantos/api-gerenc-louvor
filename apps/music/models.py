from django.db import models
from tinymce.models import HTMLField

from apps.accounts.models import TimeStampedModel


class MusicCategory(models.Model):
    category_name = models.CharField(
        max_length=50, null=False, blank=False, unique=True
    )

    def __str__(self) -> str:
        return self.category_name


class MusicChord(models.Model):
    chord_name = models.CharField(max_length=10, blank=False, null=False, unique=True)

    def __str__(self):
        return self.chord_name


class Music(TimeStampedModel):
    music_title = models.CharField(max_length=100, null=False, blank=False)
    author = models.CharField(max_length=100, null=False, blank=False)
    category = models.ManyToManyField(MusicCategory, blank=True)
    music_tone = models.CharField(
        max_length=10, blank=False
    )  # Campo para o tom da música
    music_chord = models.ManyToManyField(MusicChord, blank=True)
    music_text = HTMLField()
    music_link = models.URLField(max_length=255, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["music_title"]),
            models.Index(fields=["author"]),
        ]
        ordering = ["music_title"]

    def __str__(self) -> str:
        return self.music_title
