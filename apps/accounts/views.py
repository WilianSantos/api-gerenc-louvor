from datetime import timedelta

from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import (AccessToken, RefreshToken,
                                             UntypedToken)
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Member, MemberFunctions
from .serializers import (ChangePasswordSerializer,
                          GenerateTemporaryTokenSerializer,
                          MemberFunctionsSerializers, MemberSerializer, MemberMeSerializer,
                          PasswordResetSerializer, RegisterUserSerializer,
                          RequestPasswordResetSerializer, UserSerializers)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializers

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["first_name"]
    filterset_fields = ["username"]


class MemberFunctionsViewSet(viewsets.ModelViewSet):
    queryset = MemberFunctions.objects.all()
    serializer_class = MemberFunctionsSerializers
    pagination_class = None
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["function_name"]
    search_fields = ["function_name"]


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = None

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["name"]


class MemberMeView(APIView):
    @swagger_auto_schema(
        operation_description="Rota para buscar membro logado.",
        responses={
            200: MemberMeSerializer,
            404: openapi.Response(description="Usuário não é um membro."),
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            member = Member.objects.get(user=request.user)
            serializer = MemberMeSerializer(member, context={"request": request})
            return Response(serializer.data)
        except Member.DoesNotExist:
            return Response(
                {"detail": "Usuário não é um membro."}, status=status.HTTP_404_NOT_FOUND
            )
        

class MemberMeListView(ListAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberMeSerializer
    pagination_class = None
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter
    ]
    ordering_fields = ["name"]
        

class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access = response.data["access"]
            refresh = response.data["refresh"]

            # Define cookie com o token
            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,  # importante: impede acesso via JS
                secure=False,  # true se estiver em HTTPS
                samesite="Lax",  # ou 'Strict' ou 'None' se for cross-domain
                max_age=60 * 10,  # 10 minutos, por exemplo
                # domain='.meusite.com'
            )
            # Define cookie com o refresh token
            response.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,  # importante: impede acesso via JS
                secure=False,  # true se estiver em HTTPS
                samesite="Lax",  # ou 'Strict' ou 'None' se for cross-domain
                max_age=60 * 60 * 24 * 5,  # 5 dias, por exemplo
            )

        return response


class LogoutView(APIView):
    def post(self, request):
        response = Response(
            {"detail": "Logout realizado com sucesso"},
            status=status.HTTP_205_RESET_CONTENT,
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response({"detail": "Refresh token não encontrado"}, status=401)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response({"message": "Token renovado"})
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=60 * 10,  # 10 min
            )
            return response
        except Exception:
            return Response(
                {"detail": "Refresh token inválido ou expirado"}, status=401
            )


class ChangePasswordView(APIView):
    # documentação da api
    @swagger_auto_schema(
        operation_description="Rota para mudar senha com token.",
        request_body=ChangePasswordSerializer,
        responses={
            400: openapi.Response("detail"),
            204: openapi.Response("Sem conteúdo."),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Verificar a senha antiga
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"detail": "Senha antiga incorreta."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Alterar para a nova senha
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    # documentação da api
    @swagger_auto_schema(
        operation_description="Rota para gerar um token para redefinir a senha",
        request_body=RequestPasswordResetSerializer,
        responses={201: openapi.Response("token"), 400: openapi.Response("detail")},
    )
    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]

            if not username:
                raise Response(
                    {"detail": "Usuário não enviado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.filter(username=username).first()
            if not user:
                raise Response(
                    {
                        "detail": "Usuário não coresponde com nenhum usuário na base de dados."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            refresh = RefreshToken.for_user(user)
            reset_token = refresh.access_token
            reset_token["purpose"] = "password_reset"
            reset_token["user_id"] = user.id
            reset_token.set_exp(lifetime=timedelta(hours=1))

            email = user.email

            return Response(
                {"token": str(reset_token), "email": email},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    # documentação da api
    @swagger_auto_schema(
        operation_description="Rota para redefinir a senha",
        request_body=PasswordResetSerializer,
        responses={
            204: openapi.Response("Sem conteudo"),
            400: openapi.Response("detail"),
        },
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data["token"]
            new_password = serializer.validated_data["new_password"]

            if not token or not new_password:
                return Response(
                    {"detail": "Token ou senha não fornecidos."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                # Decodifica e valida o token
                decoded_token = UntypedToken(token)

                if decoded_token.get("purpose") != "password_reset":
                    return Response(
                        {"detail": "Token inválido para redefinição de senha."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user_id = decoded_token.get("user_id")
                if not user_id:
                    return Response(
                        {"detail": "Token inválido."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                user = User.objects.get(id=user_id)
                user.set_password(new_password)
                user.save()

                return Response(status=status.HTTP_204_NO_CONTENT)

            except TokenError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateTemporaryTokenView(APIView):
    @swagger_auto_schema(
        operation_description="Rota para gerar um token temporário.",
        request_body=GenerateTemporaryTokenSerializer,
        responses={201: openapi.Response("Sem conteúdo")},
    )
    def post(self, request):
        serializer = GenerateTemporaryTokenSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get("email")

            # Gerar um token provisório com expiração
            temporary_token = AccessToken()
            temporary_token.set_exp(
                lifetime=timedelta(days=1)
            )  # Token válido por 1 dias
            temporary_token["email"] = email
            temporary_token["purpose"] = "registration"

            return Response(
                {"temporary_token": str(temporary_token)},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterUserView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Rota para registrar o usuário no banco.",
        request_body=RegisterUserSerializer,
        responses={201: openapi.Response("user_id"), 400: openapi.Response("detail")},
    )
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)

        if serializer.is_valid():
            first_name = serializer.validated_data["first_name"]
            last_name = serializer.validated_data["last_name"]
            username = serializer.validated_data["username"]
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            cell_phone = serializer.validated_data.get("cell_phone", "")
            token = serializer.validated_data["token"]

            try:
                decoded_token = JWTAuthentication().get_validated_token(token)

                if decoded_token.get("purpose") != "registration":
                    return Response(
                        {"detail": "Token inválido para registro."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if not decoded_token.get("email"):
                    return Response(
                        {"detail": "Sem e-mail para registro."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            except TokenError:
                return Response(
                    {"detail": "Token inválido ou expirado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if User.objects.filter(username=username).exists():
                return Response(
                    {"detail": "Esse usuário já existe."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if decoded_token.get("email") != email:
                return Response(
                    {"detail": "Esse e-mail não corresponde."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                username=username,
            )

            Member.objects.create(
                name=f"{first_name} {last_name}", cell_phone=cell_phone, user=user
            )

            return Response({"user_id": user.id}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
