from django.db import models

from tinymce.models import HTMLField


class MusicCategory(models.Model):
    category_name = models.CharField(max_length=50, null=False, blank=False, unique=True) #TODO alterar para category_name

    def __str__(self) -> str:
        return self.category_name
    

class Music(models.Model):
    music_title = models.CharField(max_length=100, null=False, blank=False)
    author = models.CharField(max_length=100, null=False, blank=False)
    category = models.ManyToManyField(MusicCategory)                                  
    music_tone = models.CharField(max_length=10, blank=False)  # Campo para o tom da música
    music_chord = models.JSONField(max_length=10, blank=False)
    music_text = HTMLField()
    music_link = models.URLField(max_length=255, blank=True)

    def __str__(self) -> str:
        return self.music_title


class MusicVersion(models.Model):
    music = models.ForeignKey(Music, on_delete=models.CASCADE)
    version_author = models.CharField(max_length=100, null=False, blank=False)
    version_title = models.CharField(max_length=100, blank=False)
    version_link = models.URLField(max_length=255, blank=True)
    

    def __str__(self):
        return f'{self.version_title} | {self.version_author}'
    