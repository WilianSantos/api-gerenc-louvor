from django.urls import path

from .views import (ChangePasswordView, MostEscalatedMembers,
                    LogoutView, PasswordResetView, RegisterUserView, MemberMeView, MemberMeListView,
                    RequestPasswordResetView, SendRegistrationEmailView, VerifyRegistrationTokenView)

urlpatterns = [
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path(
        "request-password-reset/",
        RequestPasswordResetView.as_view(),
        name="request_password_reset",
    ),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path("register-user/", RegisterUserView.as_view(), name="register_user"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MemberMeView.as_view(), name="member_me"),
    path("members-me", MemberMeListView.as_view(), name="member_me_list"),
    path('send-registration-email/', SendRegistrationEmailView.as_view()),
    path('verify-registration-token/', VerifyRegistrationTokenView.as_view()),
    path("member/most-escalated", MostEscalatedMembers.as_view(), name="most_escalated_members")
]
