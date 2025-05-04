from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class RefreshTokenMiddleware(MiddlewareMixin):
    def process_response(self, request, response):

        if response.status_code == 401 and request.COOKIES.get("refresh_token"):
            refresh_token = request.COOKIES.get("refresh_token")

            try:
                refresh = RefreshToken(refresh_token)
                new_access = str(refresh.access_token)

                response = JsonResponse({"detail": "Token renovado"})
                response.set_cookie(
                    key="access_token",
                    value=new_access,
                    httponly=True,
                    secure=False,  # True em produção
                    samesite="Lax",
                    max_age=60 * 10,  # 10 minutos
                )

                return response

            except (TokenError, InvalidToken):
                # Refresh inválido -> logout
                response = JsonResponse(
                    {"detail": "Sessão expirada. Faça login novamente."}, status=401
                )
                response.delete_cookie("access_token")
                response.delete_cookie("refresh_token")
                return response

        return response
