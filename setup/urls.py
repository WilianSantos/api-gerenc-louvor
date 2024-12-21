from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework import routers

from apps.accounts.views import UserViewSet, MemberViewSet, MemberFunctionViewSet

router = routers.DefaultRouter()

# Rotas de accounts
router.register('api/user', UserViewSet, basename='Usuario')
router.register('api/member', MemberViewSet, basename='Membro')
router.register('api/member-function', MemberFunctionViewSet, basename='Função')

urlpatterns = [
    path('', include(router.urls)),

    path('api-admin-praise/', admin.site.urls),

    # rotas de autenticação
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
