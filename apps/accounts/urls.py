from django.urls import path

from .views import ChangePasswordView, RequestPasswordResetView, ResetPasswordView

urlpatterns = [
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('request-password-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]