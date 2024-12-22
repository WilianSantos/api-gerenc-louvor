from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework import routers

from apps.accounts.views import UserViewSet, MemberViewSet
from apps.music.views import MusicViewSet, MusicCategoryViewSet, MusicVersionViewSet
from apps.playlist.views import PlaylistViewSet
from apps.lineup.views import PraiseLineupViewSet

router = routers.DefaultRouter()

# Rotas de accounts
router.register('user', UserViewSet, basename='Usuario')
router.register('member', MemberViewSet, basename='Membro')

# Rotas de music
router.register('music', MusicViewSet, basename='Música')
router.register('music', MusicCategoryViewSet, basename='Categoria da música')
router.register('music', MusicVersionViewSet, basename='Versões da música')

# Rotas de playlist
router.register('playlist', PlaylistViewSet, basename='Playlist')

# Rotas de lineup
router.register('praise-lineup', PraiseLineupViewSet, basename='Escalação do louvor')

urlpatterns = [
    path('api/praise/', include(router.urls)),

    path('api-admin-praise/', admin.site.urls),

    # rotas de autenticação
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    #rota tinymce
    path('tinymce/', include('tinymce.urls')),
]
