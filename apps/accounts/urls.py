from django.urls import path

from .views import (ChangePasswordView, GenerateTemporaryTokenView,
                    LogoutView, PasswordResetView, RegisterUserView, MemberMeView, MemberMeListView,
                    RequestPasswordResetView)

urlpatterns = [
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path(
        "request-password-reset/",
        RequestPasswordResetView.as_view(),
        name="request_password_reset",
    ),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "token-temporary/", GenerateTemporaryTokenView.as_view(), name="temporary_token"
    ),
    path("register-user/", RegisterUserView.as_view(), name="register_user"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MemberMeView.as_view(), name="member_me"),
    path("members-me", MemberMeListView.as_view(), name="member_me_list")
]
