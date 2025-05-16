from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from apps.accounts.views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    MemberFunctionsViewSet,
    MemberViewSet,
    UserViewSet,
)
from apps.lineup.views import LineupMemberViewSet, PraiseLineupViewSet
from apps.music.views import MusicCategoryViewSet, MusicChordViewSet, MusicViewSet
from apps.playlist.views import PlaylistViewSet

router = routers.DefaultRouter()

# Rotas de accounts
router.register("api/praise/user", UserViewSet, basename="Usuario")
router.register("api/praise/member", MemberViewSet, basename="Membro")
router.register(
    "api/praise/member-functions", MemberFunctionsViewSet, basename="Funções de membros"
)

# Rotas de music
router.register("api/praise/music", MusicViewSet, basename="Música")
router.register(
    "api/praise/music-category", MusicCategoryViewSet, basename="Categoria da música"
)
router.register("api/praise/music-chord", MusicChordViewSet, basename="Acordes")

# Rotas de playlist
router.register("api/praise/playlist", PlaylistViewSet, basename="Playlist")

# Rotas de lineup
router.register(
    "api/praise/praise-lineup", PraiseLineupViewSet, basename="Escalação do louvor"
)
router.register(
    "api/praise/lineup-member", LineupMemberViewSet, basename="Membros escalados"
)


# Documentação
schema_view = get_schema_view(
    openapi.Info(
        title="API de Gerenciamento do louvor",
        default_version="v1",
        description="Organizador das musicas e gerenciamento de escalações do louvor da igreja",
        terms_of_service="http://127.0.0.1:8000/swagger/?format=openapi",
        contact=openapi.Contact(email="wilian.santos.dev@outlook.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],
)


urlpatterns = [
    path("", include(router.urls)),
    path("api/praise/", include("apps.accounts.urls")),
    path("api/praise/", include("apps.music.urls")),
    path("api/praise/", include("apps.lineup.urls")),
    path("api-admin-praise/", admin.site.urls),
    # rotas de autenticação
    path("api/token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    # rota tinymce
    path("tinymce/", include("tinymce.urls")),
    # rotas do django-activity-stream
    path("activity/", include("actstream.urls")),
    # rotas de documentação
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
