from django.db import models

from datetime import date

from apps.music.models import Music, MusicVersion

class Playlist(models.Model):
    playlist_name = models.CharField(max_length=100, blank=True)
    playlist_date = models.DateField(default=date.today, blank=False)
    music = models.ManyToManyField(Music, blank=True)
    music_version = models.ManyToManyField(MusicVersion, blank=True)

    def __str__(self):
        return f'{self.playlist_name} | {self.playlist_date}'
