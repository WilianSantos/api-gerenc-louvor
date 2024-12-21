from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework import routers

from apps.user.views import UserViewSet

router = routers.DefaultRouter()

# Rotas de User
router.register('user', UserViewSet, basename='Usuario')

urlpatterns = [
    path('', include(router.urls)),

    path('api-admin-praise/', admin.site.urls),

    # rotas de autenticação
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
