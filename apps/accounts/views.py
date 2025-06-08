from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Count
from django.core import signing
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, UntypedToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.lineup.models import LineupMember, PraiseLineup

from .models import Member, MemberFunctions
from .serializers import (
    ChangePasswordSerializer,
    MemberFunctionsSerializers,
    MemberMeSerializer,
    MemberSerializer,
    MessageSerializer,
    PasswordResetSerializer,
    RegisterUserSerializer,
    RequestPasswordResetSerializer,
    SendEmailResponseSerializer,
    SendEmailSerializer,
    TokenVerificationSerializer,
    UserSerializers,
)
from .utils import generate_email_token, verify_email_token


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

    @swagger_auto_schema(
        method="get",
        operation_description="Retorna o numero de membros",
        responses={
            200: openapi.Response(
                description="Total de membros",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                        )
                    },
                ),
            )
        },
    )
    @action(detail=False, methods=["get"], url_path="total-member")
    def get_total_member(self, request):
        members = Member.objects.all()

        return Response({"total": members.count()}, status=status.HTTP_200_OK)


class MemberMeView(APIView):
    @swagger_auto_schema(
        operation_description="Rota para buscar membro logado.",
        responses={
            200: openapi.Response(
                description="Retorna os dados do membro", schema=MemberMeSerializer
            )
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
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["name"]
    search_fields = ["name", "function__function_name"]


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:

            encrypted_access = signing.dumps(response.data["access"])
            access = encrypted_access

            encrypted_refresh = signing.dumps(response.data["refresh"])
            refresh = encrypted_refresh

            response.data = {"detail": "Login realizado com sucesso"}

            # Define cookie com o token de acesso
            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,  
                secure=True,  
                samesite="None",  
                max_age=60 * 10,  # 10 minutos
                path="/",  
            )

            # Define cookie com o refresh token
            response.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=True,
                samesite="None",  
                max_age=60 * 60 * 24 * 5,  # 5 dias
                path="/",  
            )

            origin = request.headers.get("Origin")
            if origin in settings.CORS_ALLOWED_ORIGINS:
                response["Access-Control-Allow-Origin"] = origin
                response["Access-Control-Allow-Credentials"] = "true"

        return response


class LogoutView(APIView):
    @swagger_auto_schema(
        operation_description="Rota para realizar logout do usuário removendo os cookies de autenticação.",
        responses={
            205: openapi.Response(
                description="Remoção dos cookies concluida", schema=MessageSerializer
            )
        },
    )
    def post(self, request):
        response = Response(
            {"detail": "Logout realizado com sucesso"},
            status=status.HTTP_205_RESET_CONTENT,
        )

        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

        return response


class AuthView(APIView):
    @swagger_auto_schema(
        operation_description="Rota para verificar se o usuário esta logado.",
        responses={
            200: openapi.Response(
                description="Remoção dos cookies concluída", schema=MessageSerializer
            )
        },
    )
    def post(self, request):
        return Response(
            {"detail": "Autenticado"},
            status=status.HTTP_200_OK,
        )


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response({"detail": "Refresh token não encontrado"}, status=401)

        try:
            decrypted_refresh = refresh_token
            refresh = signing.loads(decrypted_refresh)

            try:
                valid_refresh = RefreshToken(refresh)

                encrypted_access = signing.dumps(str(valid_refresh.access_token))
                access_token = encrypted_access

                response = Response({"message": "Token renovado"})
                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    httponly=True,
                    secure=True,
                    samesite="None",
                    max_age=60 * 10,  # 10 min
                    path="/", 
                )
                return response

            except Exception:
                return Response(
                    {"detail": "Refresh token inválido ou expirado"}, status=401
                )
        
        except signing.BadSignature:
            return Response(
                    {"detail": "Refresh token inválido ou expirado"}, status=401
                )


class ChangePasswordView(APIView):
    # documentação da api
    @swagger_auto_schema(
        operation_description="Rota para mudar senha com token.",
        request_body=ChangePasswordSerializer,
        responses={
            201: openapi.Response(
                schema=MessageSerializer, description="Senha alterada"
            )
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Verificar a senha antiga
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"old_password": "Senha antiga incorreta."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Alterar para a nova senha
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            return Response(
                {"detail": "Senha alterada com sucesso"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    # documentação da api
    @swagger_auto_schema(
        operation_description="Rota para gerar um token para redefinir a senha",
        request_body=RequestPasswordResetSerializer,
        responses={
            201: openapi.Response(
                schema=MessageSerializer, description="E-mail enviado"
            )
        },
    )
    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]

            if not username:
                raise Response(
                    {"username": "Usuário não enviado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.filter(username=username).first()
            if not user:
                raise Response(
                    {
                        "username": "Usuário não coresponde com nenhum usuário na base de dados."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            email = user.email

            from_email = getattr(settings, "EMAIL_HOST_USER", None)
            if not from_email:
                raise Response(
                    {"detail": "E-mail host não configurado."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            try:
                refresh = RefreshToken.for_user(user)
                reset_token = refresh.access_token
                reset_token["purpose"] = "password_reset"
                reset_token["user_id"] = user.id
                reset_token.set_exp(lifetime=timedelta(hours=1))

                token = generate_email_token(email)
                link = f"{settings.FRONTEND_URL}/login?token={token}&reset_token={reset_token}"

                context = {
                    "subject": "Redefinir senha",
                    "message": """
                    Olá,

                    Para atualizar sua senha acesse o link a baixo.
                    """,
                    "link": link,
                    "link_expired": "Este convite expira em 1 hora.",
                }

                html_content = render_to_string("emails/invitation_email.html", context)
                send_email = EmailMultiAlternatives(
                    subject=context["subject"],
                    body=f"Seu e-mail não suporta HTML. Clique no link para redefinir sua senha: {link}",
                    from_email=from_email,
                    to=[email],
                )
                send_email.attach_alternative(html_content, "text/html")
                send_email.send()

            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response(
                {"detail": "E-mail enviado"}, status=status.HTTP_201_CREATED
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
            201: openapi.Response(
                schema=MessageSerializer, description="Senha alterada"
            )
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

                return Response(
                    {"detail": "Senha alterada"}, status=status.HTTP_201_CREATED
                )

            except TokenError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterUserView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Rota para registrar o usuário.",
        request_body=RegisterUserSerializer,
        responses={
            201: openapi.Response(
                schema=SendEmailResponseSerializer, description="Usuario criado"
            )
        },
    )
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)

        if serializer.is_valid():
            first_name = serializer.validated_data["first_name"]
            last_name = serializer.validated_data["last_name"]
            name = serializer.validated_data["name"]
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
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if User.objects.filter(username=username).exists():
                return Response(
                    {"username": "Esse usuário já existe."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if decoded_token.get("email") != email:
                return Response(
                    {"email": "Esse e-mail não corresponde."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                username=username,
            )

            Member.objects.create(name=name, cell_phone=cell_phone, user=user)

            return Response(
                {"detail": "Usuario criado"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendRegistrationEmailView(APIView):
    @swagger_auto_schema(
        operation_summary="Enviar convites por e-mail",
        operation_description="Recebe uma lista de e-mails e envia convites personalizados com um link de registro.",
        request_body=SendEmailSerializer,
        responses={
            200: openapi.Response(
                schema=SendEmailResponseSerializer, description="E-mails enviado"
            )
        },
    )
    def post(self, request):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from_email = getattr(settings, "EMAIL_HOST_USER", None)
        if not from_email:
            return Response(
                {"detail": "E-mail host não configurado."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        success = []
        failed = []

        for email in serializer.validated_data["emails"]:
            try:
                # Gerar um token provisório com expiração
                temporary_access_token = AccessToken()
                temporary_access_token.set_exp(
                    lifetime=timedelta(days=1)
                )  # Token válido por 1 dias
                temporary_access_token["email"] = email
                temporary_access_token["purpose"] = "registration"

                token = generate_email_token(email)
                link = f"{settings.FRONTEND_URL}/register?token={token}&temporary_token={temporary_access_token}"

                context = {
                    "subject": "Você foi convidado para participar do nosso site!",
                    "message": """
                    Olá,

                    Você foi convidado para participar do nosso site! Clique no botão abaixo para aceitar o convite.
                    """,
                    "link": link,
                    "link_expired": "Este convite expira em 7 dias.",
                }

                html_content = render_to_string("emails/invitation_email.html", context)
                send_email = EmailMultiAlternatives(
                    subject=context["subject"],
                    body=f"Seu e-mail não suporta HTML. Clique no link: {link}",
                    from_email=from_email,
                    to=[email],
                )
                send_email.attach_alternative(html_content, "text/html")
                send_email.send()
                success.append(email)
            except Exception as e:
                failed.append({"email": email, "detail": str(e)})

        return Response({"sent": success, "failed": failed}, status=status.HTTP_200_OK)


class VerifyRegistrationTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Verificar token de registro",
        operation_description="Verifica se o token recebido por e-mail ainda é válido. Retorna o e-mail original se válido.",
        manual_parameters=[
            openapi.Parameter(
                "token",
                openapi.IN_QUERY,
                description="Token de verificação recebido por e-mail",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="Token válido", schema=TokenVerificationSerializer
            )
        },
    )
    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response(
                {"detail": "Token ausente"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            email = verify_email_token(token)
            return Response({"valid": True, "email": email}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"valid": False, "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class MostEscalatedMembers(APIView):

    @swagger_auto_schema(
        operation_description="Retorna os 10 membros mais escalados no último ano.",
        responses={
            200: openapi.Response(
                description="Lista de membros mais escalados",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "top_members": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                    "total-member": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                },
                            ),
                        )
                    },
                ),
            )
        },
    )
    def get(self, request):
        date_now = timezone.now()
        date_last_year = date_now - relativedelta(years=1)

        lineup = PraiseLineup.objects.filter(
            lineup_date__range=(date_last_year, date_now)
        )

        lineup_ids = lineup.values("id")
        lineup_member = LineupMember.objects.filter(lineup__in=lineup_ids)

        top_members = (
            lineup_member.values("member")
            .annotate(total=Count("member"))
            .order_by("-total")[:10]
        )

        member_ids = [item["member"] for item in top_members]
        members = Member.objects.filter(id__in=member_ids)

        return Response(
            {
                "top_members": [
                    {
                        "name": member.name,
                        "total-member": next(
                            item["total"]
                            for item in top_members
                            if item["member"] == member.id
                        ),
                    }
                    for member in members
                ]
            },
            status=status.HTTP_200_OK,
        )
