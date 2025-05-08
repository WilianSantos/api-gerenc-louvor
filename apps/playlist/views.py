from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from django.core.cache import cache
from .models import Playlist
from .serializers import PlaylistSerializers

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializers

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    search_fields = ["playlist_date", "playlist_name"]

    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_QUERY,
                description='ID da playlist',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
        200: openapi.Response(
            description="Links das músicas da playlist",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "links": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING, format="url")
                    )
                }
            )
        ),
        400: openapi.Response(description="ID da playlist é obrigatório."),
        404: openapi.Response(description="Playlist não encontrada."),
    }
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="musics-link"
    )
    def get_musics_link(self, request):
        playlist_id = request.query_params.get("id")

        if not playlist_id:
            return Response(
                {"detail": "ID da playlist é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache_key = f"playlist_links_{playlist_id}"
        cached_links = cache.get(cache_key)

        if cached_links:
            return Response({"links": cached_links}, status=status.HTTP_200_OK)

        try:
            playlist = Playlist.objects.get(id=playlist_id)
        except Playlist.DoesNotExist:
            return Response(
                {"detail": "Playlist não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        music_links = [
            music.music_link for music in playlist.music.all() if music.music_link
        ]

        
        cache.set(cache_key, music_links, timeout=60 * 60 * 1)

        return Response({"links": music_links}, status=status.HTTP_200_OK)

