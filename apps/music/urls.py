from django.urls import path

from .views import MostPlayedSongs

urlpatterns = [
    path("music/most-played", MostPlayedSongs.as_view(), name="most_played_songs")
]
