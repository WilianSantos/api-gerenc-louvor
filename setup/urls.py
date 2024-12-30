from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenRefreshView

from rest_framework import routers, permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from apps.accounts.views import UserViewSet, MemberViewSet, MemberFunctionsViewSet, ChangePasswordView, \
   CustomTokenObtainPairView
from apps.music.views import MusicViewSet, MusicCategoryViewSet, MusicVersionViewSet
from apps.playlist.views import PlaylistViewSet
from apps.lineup.views import PraiseLineupViewSet


router = routers.DefaultRouter()

# Rotas de accounts
router.register('user', UserViewSet, basename='Usuario')
router.register('member', MemberViewSet, basename='Membro')
router.register('member-functions', MemberFunctionsViewSet, basename='Funções de membros')

# Rotas de music
router.register('music', MusicViewSet, basename='Música')
router.register('music', MusicCategoryViewSet, basename='Categoria da música')
router.register('music', MusicVersionViewSet, basename='Versões da música')

# Rotas de playlist
router.register('playlist', PlaylistViewSet, basename='Playlist')

# Rotas de lineup
router.register('praise-lineup', PraiseLineupViewSet, basename='Escalação do louvor')


# Documentação
schema_view = get_schema_view(
   openapi.Info(
      title="API de Gerenciamento do louvor",
      default_version='v1',
      description="Organizador das musicas e gerenciamento de escalações do louvor da igreja",
      terms_of_service="#",
      contact=openapi.Contact(email="wilian.santos.dev@outlook.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
   path('api/praise/', include(router.urls)),
   path('api/praise/', include('apps.accounts.urls')),

   path('api-admin-praise/', admin.site.urls),

   # rotas de autenticação
   path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
   path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

   #rota tinymce
   path('tinymce/', include('tinymce.urls')),

   # rotas do django-activity-stream
   path('activity/', include('actstream.urls')),

   # rotas de documentação
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
