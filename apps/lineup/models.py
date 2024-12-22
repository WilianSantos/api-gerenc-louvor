from django.db import models

from datetime import date

from apps.playlist.models import Playlist
from apps.accounts.models import Member

class PraiseLineup(models.Model):
    # Vocal
    lead_vocals = models.ManyToManyField(Member, blank=False, related_name='lineup_lead_vocals')
    backing_vocals = models.ManyToManyField(Member, blank=True, related_name='lineup_backing_vocals')
    choir = models.ManyToManyField(Member, blank=True, related_name='lineup_choir')

    # Instrumentos de Cordas
    electric_guitar = models.ManyToManyField(Member, blank=True, related_name='lineup_electric_guitar')
    electric_bass = models.ManyToManyField(Member, blank=True, related_name='lineup_electric_bass')
    guitar = models.ManyToManyField(Member, blank=True, related_name='lineup_guitar')

    # Instrumentos de Teclado
    musical_keyboard = models.ManyToManyField(Member, blank=True, related_name='lineup_musical_keyboard')

    # Instrumentos de Percussão
    drum_set = models.ManyToManyField(Member, blank=True, related_name='lineup_drum_set')

    lineup_date = models.DateField(default=date.today, blank=False)
    lineup_event = models.CharField(max_length=100, blank=True)
    playlist = models.ForeignKey(
        to=Playlist,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
