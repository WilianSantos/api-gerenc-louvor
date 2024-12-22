from rest_framework import viewsets, filters

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import MusicSerializers, MusicCategorySerializers, MusicVersionSerializers
from .models import Music, MusicCategory, MusicVersion


class MusicViewSet(viewsets.ModelViewSet):
    queryset = Music.objects.all()
    serializer_class = MusicSerializers

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['music_title']
    search_fields = ['music_title', 'author', 'category']


class MusicCategoryViewSet(viewsets.ModelViewSet):
    queryset = MusicCategory.objects.all()
    serializer_class = MusicCategorySerializers

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['category_name']
    search_fields = ['category_name']


class MusicVersionViewSet(viewsets.ModelViewSet):
    queryset = MusicVersion.objects.all()
    serializer_class = MusicVersionSerializers

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['version_title']
    search_fields = ['version_title', 'music', 'version_author']
