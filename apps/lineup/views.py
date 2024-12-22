from rest_framework import viewsets, filters

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import PraiseLineupSerializers
from .models import PraiseLineup

class PraiseLineupViewSet(viewsets.ModelViewSet):
    queryset = PraiseLineup
    serializer_class = PraiseLineupSerializers

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['lineup_date', 'lineup_event']
    search_fields = ['lineup_date', 'lineup_event']
