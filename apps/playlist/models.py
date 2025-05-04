from datetime import date

from django.db import models

from apps.accounts.models import TimeStampedModel
from apps.music.models import Music


class Playlist(TimeStampedModel):

    playlist_name = models.CharField(max_length=100, blank=True)
    playlist_date = models.DateField(default=date.today, blank=False)
    music = models.ManyToManyField(Music, blank=True)

    class Meta:
        unique_together = ("playlist_name", "playlist_date")
        ordering = ["-playlist_date"]

    def __str__(self):
        return f"{self.playlist_name} | {self.playlist_date}"
