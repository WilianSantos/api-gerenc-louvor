from django.db import models
from django.contrib.auth.models import User


# BD - Funçao do membro da igreja
class MemberFunction(models.Model):
    name = models.CharField(max_length=100, blank=False) #TODO adicionar propriedade unique=True e alterar o nome do campo para function_name


    def __str__(self):
        return self.name


class Member(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False)
    availability = models.BooleanField()
    cell_phone = models.CharField(max_length=14, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_picture/%Y/%m/%d/", 
        blank=True
        )
    function = models.ManyToManyField(to=MemberFunction, blank=True)
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='user'
    )

    def __str__(self):
        return f'{self.name} | {self.function}'
