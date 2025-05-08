from datetime import date

from django.db import models
from django.forms import ValidationError

from apps.accounts.models import Member, MemberFunctions, TimeStampedModel
from apps.playlist.models import Playlist


class PraiseLineup(TimeStampedModel):
    lineup_date = models.DateField(default=date.today)
    lineup_event = models.CharField(max_length=100, blank=True)
    playlist = models.ForeignKey(
        Playlist, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-lineup_date"]

    def __str__(self):
        return f'{self.lineup_event or "Escala"} | {self.lineup_date}'


class LineupMember(TimeStampedModel):
    lineup = models.ForeignKey(
        PraiseLineup, on_delete=models.CASCADE, related_name="members"
    )
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)
    member_name_snapshot = models.CharField(max_length=150, blank=True)

    function = models.ForeignKey(MemberFunctions, on_delete=models.SET_NULL, null=True, blank=True)
    function_name_snapshot = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ("lineup", "member", "function")

    def save(self, *args, **kwargs):
        # Atualiza snapshot sempre que houver alteração
        if self.member:
            self.member_name_snapshot = self.member.name
        if self.function:
            self.function_name_snapshot = self.function.function_name
        super().save(*args, **kwargs)

    def get_member_display(self):
        return self.member.name if self.member else self.member_name_snapshot

    def get_function_display(self):
        return self.function.function_name if self.function else self.function_name_snapshot

    def clean(self):
        if not self.member.function.filter(pk=self.function.pk).exists():
            raise ValidationError(f"{self.member.name} não possui a função '{self.function.function_name}'")


    def __str__(self):
        return (
            f"{self.member} como {self.function} na escala de {self.lineup.lineup_date}"
        )
