from django.contrib.auth.models import User
from django.db import models
from tinymce.models import HTMLField


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MemberFunctions(models.Model):
    function_name = models.CharField(
        max_length=50, unique=True, blank=False, null=False
    )
    description = HTMLField(blank=True)

    def __str__(self):
        return self.function_name

    class Meta:
        ordering = ["function_name"]


class Member(TimeStampedModel):
    name = models.CharField(max_length=150, null=False, blank=False)
    availability = models.BooleanField(default=True)
    cell_phone = models.CharField(max_length=14, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_picture/%Y/%m/%d/", blank=True, null=True
    )
    function = models.ManyToManyField(MemberFunctions, blank=True)
    user = models.OneToOneField(
        to=User, on_delete=models.CASCADE, blank=False, related_name="user"
    )

    class Meta:
        indexes = [
            models.Index(fields=["availability"]),
            models.Index(fields=["user"]),
        ]
        ordering = ["name"]

    def __str__(self):
        functions = ", ".join(f.function_name for f in self.function.all())
        return f"{self.name} | {functions or 'Sem função'}"
