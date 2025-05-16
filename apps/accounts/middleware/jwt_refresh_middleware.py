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

                # Criar nova resposta
                new_response = JsonResponse({"detail": "Token renovado"})

                # Transferir cabeçalhos CORS da resposta original para a nova resposta
                cors_headers = [
                    "Access-Control-Allow-Origin",
                    "Access-Control-Allow-Methods",
                    "Access-Control-Allow-Headers",
                    "Access-Control-Allow-Credentials",
                    "Access-Control-Expose-Headers",
                    "Access-Control-Max-Age",
                ]

                for header in cors_headers:
                    if header in response:
                        new_response[header] = response[header]

                # Definir cabeçalho CORS explicitamente caso a origem seja de Vercel
                if (
                    "Origin" in request.headers
                    and "vercel" in request.headers["Origin"]
                ):
                    new_response["Access-Control-Allow-Origin"] = request.headers[
                        "Origin"
                    ]
                    new_response["Access-Control-Allow-Credentials"] = "true"

                # Configurar cookie
                new_response.set_cookie(
                    key="access_token",
                    value=new_access,
                    httponly=True,
                    secure=True,  # True em produção
                    samesite="None",
                    max_age=60 * 10,  # 10 minutos
                )

                return new_response

            except (TokenError, InvalidToken):
                # Refresh inválido -> logout
                new_response = JsonResponse(
                    {"detail": "Sessão expirada. Faça login novamente."}, status=401
                )

                # Transferir cabeçalhos CORS da resposta original para a nova resposta
                cors_headers = [
                    "Access-Control-Allow-Origin",
                    "Access-Control-Allow-Methods",
                    "Access-Control-Allow-Headers",
                    "Access-Control-Allow-Credentials",
                    "Access-Control-Expose-Headers",
                    "Access-Control-Max-Age",
                ]

                for header in cors_headers:
                    if header in response:
                        new_response[header] = response[header]

                # Definir cabeçalho CORS explicitamente caso a origem seja de Vercel
                if (
                    "Origin" in request.headers
                    and "vercel" in request.headers["Origin"]
                ):
                    new_response["Access-Control-Allow-Origin"] = request.headers[
                        "Origin"
                    ]
                    new_response["Access-Control-Allow-Credentials"] = "true"

                new_response.delete_cookie("access_token")
                new_response.delete_cookie("refresh_token")
                return new_response

        return response
