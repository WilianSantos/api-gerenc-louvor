from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Member

from .models import LineupMember, PraiseLineup
from .serializers import LineupMemberSerializers, PraiseLineupSerializers


class PraiseLineupViewSet(viewsets.ModelViewSet):
    queryset = PraiseLineup.objects.all()
    serializer_class = PraiseLineupSerializers
    pagination_class = None

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["lineup_date", "lineup_event"]
    search_fields = ["lineup_date", "lineup_event"]


from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


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
