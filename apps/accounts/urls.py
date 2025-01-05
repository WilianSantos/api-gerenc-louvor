from django.urls import path

from .views import ChangePasswordView, RequestPasswordResetView, ResetPasswordView, \
    GenerateTemporaryTokenView, RegisterUserView

urlpatterns = [
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('request-password-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('token-temporary/', GenerateTemporaryTokenView.as_view(), name='temporary_token'),
    path('register-user/', RegisterUserView.as_view(), name='register_user'),
]