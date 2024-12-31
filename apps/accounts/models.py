from django.db import models
from django.contrib.auth.models import User


class MemberFunctions(models.Model):
    functions_name = models.CharField(max_length=50, unique=True, blank=False, null=False)

    def __str__(self):
        return self.functions_name


class Member(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False)
    availability = models.BooleanField(default=True)
    cell_phone = models.CharField(max_length=14, blank=True)
    profile_picture = models.ImageField(upload_to="profile_picture/%Y/%m/%d/", blank=True)
    function = models.ManyToManyField(MemberFunctions)
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        blank=False,
        related_name='user'
    )

    def __str__(self):
        return f'{self.name} | {self.function}'
