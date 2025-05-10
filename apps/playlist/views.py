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
                                    "playlist_name": openapi.Schema(type=openapi.TYPE_STRING),
                                    "playlist_date": openapi.Schema(type=openapi.TYPE_STRING, format="date"),
                                    "music": openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(type=openapi.TYPE_INTEGER)  # ou detalhado com TYPE_OBJECT
                                    ),
                                    "playlist_link_display": openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(type=openapi.TYPE_STRING)  # ou detalhado com TYPE_OBJECT
                                    )
                                }
                            )
                        )
                    }
                )
            )
        }
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="playlists"
        
    )
    def get_playlists(self, request):
        queryset = self.filter_queryset(self.get_queryset())  
        serializer = self.get_serializer(queryset, many=True)
        return Response({"playlists": serializer.data}, status=status.HTTP_200_OK)

