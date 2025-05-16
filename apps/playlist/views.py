from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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
    search_fields = ["playlist_date", "playlist_name"]

    @swagger_auto_schema(
        method="get",
        responses={
            200: openapi.Response(
                description="Lista das playlists",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "playlists": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "playlist_name": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "playlist_date": openapi.Schema(
                                        type=openapi.TYPE_STRING, format="date"
                                    ),
                                    "music": openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(
                                            type=openapi.TYPE_INTEGER
                                        ),  # ou detalhado com TYPE_OBJECT
                                    ),
                                    "playlist_link_display": openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),  # ou detalhado com TYPE_OBJECT
                                    ),
                                },
                            ),
                        )
                    },
                ),
            )
        },
    )
    @action(detail=False, methods=["get"], url_path="playlists")
    def get_playlists(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"playlists": serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        method="get",
        operation_description="Retorna o numero de playlist",
        responses={
            200: openapi.Response(
                description="Total de playlist",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                        )
                    },
                ),
            )
        },
    )
    @action(detail=False, methods=["get"], url_path="total-playlist")
    def get_total_playlist(self, request):
        playlists = Playlist.objects.all()

        return Response({"total": playlists.count()}, status=status.HTTP_200_OK)
