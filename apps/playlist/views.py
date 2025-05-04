from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Playlist
from .serializers import PlaylistSerializers


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializers

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["playlist_date"]
    search_fields = ["playlist_date", "playlist_name"]
