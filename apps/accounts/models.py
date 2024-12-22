from django.db import models
from django.contrib.auth.models import User


class Member(models.Model):
    FUNCTION_CHOICES = [
        ('vocal principal', 'Vocal Principal'),
        ('backing vocal', 'Backing Vocal'),
        ('coral', 'Coral'),
        ('guitarra elétrica', 'Guitarra Elétrica'),
        ('baixo elétrico', 'Baixo Elétrico'),
        ('violão', 'Violão'),
        ('teclado', 'Teclado'),
        ('bateria', 'Bateria'),
    ]

    name = models.CharField(max_length=150, null=False, blank=False)
    availability = models.BooleanField()
    cell_phone = models.CharField(max_length=14, blank=True)
    profile_picture = models.ImageField(upload_to="profile_picture/%Y/%m/%d/", blank=True)
    function = models.CharField(max_length=20, blank=True, null=True, choices=FUNCTION_CHOICES)
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='user'
    )

    def __str__(self):
        return f'{self.name} | {self.function}'
