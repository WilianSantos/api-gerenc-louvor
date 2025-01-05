from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from itsdangerous import URLSafeTimedSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from datetime import timedelta

from django.contrib.auth.models import User
from django.conf import settings

from .serializers import \
    UserSerializers, MemberSerializers, MemberFunctionsSerializers, \
        ChangePasswordSerializer, EmailVerificationSerializer, ResetPasswordSerializer, \
            CustomTokenObtainPairSerializer, \
                GenerateTemporaryTokenSerializer, RegisterUserSerializer

from .models import Member, MemberFunctions


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializers


class MemberFunctionsViewSet(viewsets.ModelViewSet):
    queryset = MemberFunctions.objects.all()
    serializer_class = MemberFunctionsSerializers


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializers

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['name']
    filterset_fields = ['user']



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordView(APIView):
    #documentação da api
    @swagger_auto_schema(
        operation_description="Rota para mudar senha com token. Nessa rota o usuario consegue alterar sua senha.",
        request_body=ChangePasswordSerializer,
        responses={
            400: openapi.Response("Senha antiga incorreta."),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Verificar a senha antiga
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"detail": "Senha antiga incorreta."}, status=status.HTTP_400_BAD_REQUEST)

            # Alterar para a nova senha
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response(status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RequestPasswordResetView(APIView):
    authentication_classes = []  # Sem autenticação padrão

    #documentação da api
    @swagger_auto_schema(
        operation_description="Rota para redefinição de senha. Envia o e-mail para a rota e recebe um token provisorio",
        request_body=EmailVerificationSerializer,
        responses={
            200: openapi.Response("reset_token"),
            400: openapi.Response("E-mail não coresponde com nenhum usuário."),
        }
    )
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            if not user:
                return Response({"detail": "E-mail não coresponde com nenhum usuário."}, status=status.HTTP_400_BAD_REQUEST)

            # Gera o token de redefinição de senha
            refresh = RefreshToken.for_user(user)
            reset_token = refresh.access_token
            reset_token['purpose'] = 'password_reset' 
            reset_token.set_exp(lifetime=timedelta(minutes=15)) 
            
            return Response({ "reset_token": reset_token}, status=status.HTTP_200_OK)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    authentication_classes = []  # Sem autenticação padrão

    #documentação da api
    @swagger_auto_schema(
        operation_description="Rota para redefinição de senha. Nessa rota é recebida o token de acesso provisório e a nova senha.",
        request_body=ResetPasswordSerializer
    )
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']

            try:
                # Valida o token JWT
                user_data = JWTAuthentication().get_validated_token(token)
                if user_data['purpose'] != 'password_reset':
                    raise AuthenticationFailed(detail='Token inválido ou expirado.')
                
                # Redefine a senha
                user = User.objects.get(id=user_data['user_id'])
                user.set_password(new_password)
                user.save()
                
                return Response(status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            

class GenerateTemporaryTokenView(APIView):
    @swagger_auto_schema(
        operation_description="Rota para gerar um token temporário. Recebe o e-mail e gera um token.\n temporary_token",
        request_body=GenerateTemporaryTokenSerializer
    )
    def post(self, request):
        serializer = GenerateTemporaryTokenSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data.get('email')
        
        # Gerar um token provisório com expiração curta
        temporary_token = AccessToken()
        temporary_token.set_exp(lifetime=timedelta(days=1))  # Token válido por 1 dias
        temporary_token['email'] = email
        temporary_token['purpose'] = 'registration'

        return Response({"temporary_token": str(temporary_token)}, status=status.HTTP_200_OK)

    

class RegisterUserView(APIView):
    authentication_classes = []  # Desabilita autenticação para esta rota
    permission_classes = [AllowAny]  # Permite acesso público

    @swagger_auto_schema(
        operation_description="Rota para registrar o usuário no banco. Recebe os campos necessários para o registro junto com o token e cria o usuário e o membro.",
        request_body=RegisterUserSerializer
    )
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        cell_phone = serializer.validated_data.get('cell_phone', '')
        token = serializer.validated_data['token']

        try:
            # Decodificar o token
            decoded_token = JWTAuthentication().get_validated_token(token)
            
            if decoded_token.get('purpose') != 'registration':
                return Response({"detail": "Token inválido para registro."}, status=status.HTTP_400_BAD_REQUEST)
            
            if decoded_token.get('email') != email:
                return Response({"detail": "Token não corresponde ao e-mail fornecido."}, status=status.HTTP_400_BAD_REQUEST)
            
        except TokenError:
            return Response({"detail": "Token inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar se o usuário já existe
        if User.objects.filter(username=username).exists():
            return Response({"detail": "Esse usuário já existe."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not username:
            return Response({"detail": "É preciso digitar um usuário."}, status=status.HTTP_400_BAD_REQUEST)

        # Criar o usuário e o membro
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        member = Member.objects.create(
            name=f"{first_name} {last_name}",
            cell_phone=cell_phone,
            user=user
        )

        return Response({"user_id": user.id, "member_id": member.id}, status=status.HTTP_201_CREATED)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return response
        except InvalidToken as e:
            return Response({
                "detail": "O token é inválido ou expirado",
                "code": "refresh_token_not_valid"
            }, status=status.HTTP_401_UNAUTHORIZED)
