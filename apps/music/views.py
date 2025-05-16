import fitz  # pymupdf
from dateutil.relativedelta import relativedelta
from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.lineup.models import PraiseLineup
from apps.playlist.models import Playlist

from .models import Music, MusicCategory, MusicChord
from .serializers import (
    MusicCategorySerializers,
    MusicChordSerializers,
    MusicSerializers,
    UploadPdfSerializer,
)
from .utils import is_chord


class MusicViewSet(viewsets.ModelViewSet):
    queryset = Music.objects.all()
    serializer_class = MusicSerializers

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["music_title", "author", "category__category_name"]
    filterset_fields = ["category"]

    @swagger_auto_schema(
        operation_description="Retorna todas as músicas cadastradas.",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "counts": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "musics": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "category": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER
                                            ),
                                            "category_name": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                        },
                                    ),
                                ),
                                "music_chord": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER
                                            ),
                                            "chord_name": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "chord_image": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                format="uri",
                                                nullable=True,
                                            ),
                                        },
                                    ),
                                ),
                                "created_at": openapi.Schema(
                                    type=openapi.TYPE_STRING, format="date-time"
                                ),
                                "updated_at": openapi.Schema(
                                    type=openapi.TYPE_STRING, format="date-time"
                                ),
                                "music_title": openapi.Schema(type=openapi.TYPE_STRING),
                                "author": openapi.Schema(type=openapi.TYPE_STRING),
                                "music_tone": openapi.Schema(type=openapi.TYPE_STRING),
                                "music_text": openapi.Schema(type=openapi.TYPE_STRING),
                                "music_link": openapi.Schema(
                                    type=openapi.TYPE_STRING, format="uri"
                                ),
                            },
                        ),
                    ),
                },
            )
        },
    )
    @action(detail=False, methods=["get"], url_path="musics")
    def musics(self, request):
        queryset = self.filter_queryset(
            self.get_queryset()
        )  # <- aplica filtros, busca, ordenação
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {"counts": queryset.count(), "musics": serializer.data},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_description="Recebe um arquivo PDF contendo cifras de músicas e retorna o conteúdo formatado para ser exibido no TinyMCE.",
        request_body=UploadPdfSerializer,  # Aqui definimos o body que esperamos
        responses={
            200: openapi.Response(
                description="HTML gerado a partir do PDF extraído.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "html": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="HTML formatado com as cifras extraídas do PDF, dentro de uma tag <pre>.",
                        ),
                        "chords": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description="Todas as cifras presentes no texto.",
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                        ),
                    },
                ),
            )
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="upload-pdf",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_pdf(self, request):
        serializer = UploadPdfSerializer(data=request.data)
        if serializer.is_valid():
            file_obj = serializer.validated_data["file"]

            try:
                pdf_file = fitz.open(stream=file_obj.read(), filetype="pdf")
                text_content = ""
                for page in pdf_file:
                    text_content += page.get_text("text")  # preserva quebras de linha
            except Exception as e:
                return Response(
                    {"detail": f"Erro ao processar PDF: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            words = text_content.split()
            chords = []
            for word in words:
                if is_chord(word):
                    chords.append(word)

            chords = list(set(chords))

            # Verificando se existe um acorde e adicionando no banco caso não exista
            model_chords = MusicChord.objects.all()
            for item in chords:
                if not model_chords.filter(chord_name=item).exists():
                    MusicChord.objects.create(chord_name=item)

            html_content = f"<pre>{text_content.strip()}</pre>"

            return Response(
                {"chords": chords, "html": html_content}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method="get",
        operation_description="Retorna o numero de musicas",
        responses={
            200: openapi.Response(
                description="Total de musicas",
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
    @action(detail=False, methods=["get"], url_path="total-music")
    def get_total_music(self, request):
        musics = Music.objects.all()

        return Response({"total": musics.count()}, status=status.HTTP_200_OK)


class MusicCategoryViewSet(viewsets.ModelViewSet):
    queryset = MusicCategory.objects.all()
    serializer_class = MusicCategorySerializers
    pagination_class = None

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["category_name"]
    search_fields = ["category_name"]


class MusicChordViewSet(viewsets.ModelViewSet):
    queryset = MusicChord.objects.all()
    serializer_class = MusicChordSerializers
    pagination_class = None

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["chord_name"]
    search_fields = ["chord_name"]
    filterset_fields = ["chord_name"]


class MostPlayedSongs(APIView):
    @swagger_auto_schema(
        operation_description="Retorna as 5 músicas mais tocadas nas playlists dos últimos 6 meses.",
        responses={
            200: openapi.Response(
                description="Lista das músicas mais tocadas",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "top_musics": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "music": openapi.Schema(type=openapi.TYPE_STRING),
                                    "author": openapi.Schema(type=openapi.TYPE_STRING),
                                    "total": openapi.Schema(type=openapi.TYPE_INTEGER),
                                },
                            ),
                        )
                    },
                ),
            )
        },
    )
    def get(self, request):
        date_now = timezone.now()
        # Ajustando para 6 meses conforme a descrição da API
        date_six_months_ago = date_now - relativedelta(months=6)

        lineups = PraiseLineup.objects.filter(
            lineup_date__range=(date_six_months_ago, date_now)
        )

        playlist_ids = lineups.values_list("playlist_id", flat=True)
        through_model = Playlist.music.through  # acesso à tabela M2M

        top_musics = (
            through_model.objects.filter(playlist_id__in=playlist_ids)
            .values("music")
            .annotate(total=Count("music"))
            .order_by("-total")[:10]
        )

        # Abordagem 1: Preservando a ordem usando Case/When no Django
        music_ids = [item["music"] for item in top_musics]

        print(music_ids)

        # Buscar músicas com a ordem preservada
        musics = Music.objects.filter(id__in=music_ids)

        print([music.id for music in musics])
        # Dicionário para mapear ids de músicas com seus totais
        music_count_map = {item["music"]: item["total"] for item in top_musics}

        # Criar a lista de resultados mantendo a ordem correta
        result = []
        for music in musics:
            result.append(
                {
                    "music": music.music_title,
                    "author": music.author,
                    "total": music_count_map[music.id],
                }
            )

        return Response(
            {"top_musics": result},
            status=status.HTTP_200_OK,
        )
