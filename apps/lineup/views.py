from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Count
from django.utils import timezone


from apps.accounts.models import Member

from .models import LineupMember, PraiseLineup
from .serializers import LineupMemberSerializers, PraiseLineupSerializers


class PraiseLineupViewSet(viewsets.ModelViewSet):
    queryset = PraiseLineup.objects.all()
    serializer_class = PraiseLineupSerializers

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["lineup_date", "lineup_event"]
    search_fields = ["lineup_date", "lineup_event"]

    @swagger_auto_schema(
        method='get',
        operation_description="Lista de escalas com links da playlist",
        responses={
            200: openapi.Response(
                description="Lista de escalas",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "scales": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "lineup_event": openapi.Schema(type=openapi.TYPE_STRING),
                                    "lineup_date": openapi.Schema(type=openapi.TYPE_STRING, format="date"),
                                    "playlist": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "playlist_display": openapi.Schema(type=openapi.TYPE_STRING),
                                    "playlist_link_display": openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(type=openapi.TYPE_STRING)
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
        url_path="scales"
        
    )
    def get_scales(self, request):
        queryset = self.filter_queryset(self.get_queryset())  
        serializer = self.get_serializer(queryset, many=True)
        return Response({"scales": serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='get',
        operation_description="Retorna total de escalas",
        responses={
            200: openapi.Response(
                description="Lista de escalas",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                        )
                    }
                )
            )
        }
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="total-scales"
        
    )
    def get_total_scales(self, request):
        scales = PraiseLineup.objects.all()
        
        return Response({"total": scales.count()}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
    method='get',
    operation_description="Retorna as próximas 5 escalas dentro de 6 meses a partir da data atual.",
    responses={
            200: openapi.Response(
                description="Lista das próximas escalas",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "next-scales": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "event": openapi.Schema(type=openapi.TYPE_STRING),
                                    "date": openapi.Schema(type=openapi.TYPE_STRING, format="date")
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
        url_path="next-scales"
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="next-scales"
        
    )
    def get_next_scales(self, request):
        date_now = timezone.now()
        date_next_months = date_now + relativedelta(months=6)
        

        lineups = PraiseLineup.objects.filter(
            lineup_date__range=(date_now, date_next_months)
        )[:5]
        
        return Response({"next-scales": [
           {
            "event": scale.lineup_event,
            "date": scale.lineup_date
           }
            for scale in lineups
        ]}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
    method='get',
    operation_description="Retorna as últimas 5 escalas dos 6 meses anteriores à data atual.",
    responses={
            200: openapi.Response(
                description="Lista das escalas anteriores",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "previous-scales": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "event": openapi.Schema(type=openapi.TYPE_STRING),
                                    "date": openapi.Schema(type=openapi.TYPE_STRING, format="date")
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
        url_path="previous-scales"
        
    )
    def get_previous_scales(self, request):
        date_now = timezone.now()
        date_previous_months = date_now - relativedelta(months=6)
        

        lineups = PraiseLineup.objects.filter(
            lineup_date__range=(date_previous_months, date_now)
        )[:5]
        
        return Response({"previous-scales": [
           {
            "event": scale.lineup_event,
            "date": scale.lineup_date
           }
            for scale in lineups
        ]}, status=status.HTTP_200_OK)


class LineupMemberViewSet(viewsets.ModelViewSet):
    queryset = LineupMember.objects.all()
    serializer_class = LineupMemberSerializers
    pagination_class = None

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["lineup__lineup_date", "lineup__lineup_event"]
    search_fields = ["member__name", "function__function_name"]


class ScaleHistoryViewSet(APIView):
    @swagger_auto_schema(
        operation_description="Rota para retornar o histórico de escalas do membro logado.",
        responses={
            200: openapi.Response(
                description="Lista de escalas",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "scales": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "lineup_date": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        format=openapi.FORMAT_DATE,
                                    ),
                                    "lineup_event": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "function_name": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                },
                            ),
                        )
                    },
                ),
            )
        },
    )
    def get(self, request):
        member_id = Member.objects.get(user=request.user).id
        scales = LineupMember.objects.filter(member_id=member_id)
        scales = scales.values(
            "id",
            "lineup__lineup_date",
            "lineup__lineup_event",
            "function__function_name",
        ).order_by("-lineup__lineup_date")[:10]
        return Response(
            {
                "scales": [
                    {
                        "id": scale["id"],
                        "lineup_date": scale["lineup__lineup_date"],
                        "lineup_event": scale["lineup__lineup_event"],
                        "function_name": scale["function__function_name"],
                    }
                    for scale in scales
                ]
            },
            status=status.HTTP_200_OK,
        )
