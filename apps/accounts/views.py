from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from datetime import timedelta

from django.contrib.auth.models import User

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
        operation_description="Rota para gerar um token temporario. Recebe o e-mail e gera um token.",
        request_body=GenerateTemporaryTokenSerializer
    )

    def post(self, request):
        serializer = GenerateTemporaryTokenSerializer(data=request.data)
        email = request.data.get('email')
        
        if serializer:
            if not email:
                return Response({"detail": "O campo 'email' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Gerar um token provisório com expiração curta
            temporary_token = AccessToken()
            temporary_token.set_exp(lifetime=timedelta(minutes=5))  # Token válido por 30 minutos
            temporary_token['email'] = email
            temporary_token['purpose'] = 'registration'

            return Response({"temporary_token": str(temporary_token)}, status=status.HTTP_200_OK)
    

class RegisterUserView(APIView):
    @swagger_auto_schema(
        operation_description="Rota para registrar o usuário no banco. Recebe os campos necessarios para o registro junto com o token e criar o usuário e o membro.",
        request_body=RegisterUserSerializer
    )

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)

        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        availability = request.data.get('availability') 
        profile_picture = request.data.get('profile_picture')
        function = request.data.get('function')
        cell_phone = request.data.get('cell_phone')
        token = request.data.get('token')
        
        if serializer.is_valid():
            if not all([token, email, password, first_name, last_name, username]):
                return Response({"detail": "Existem campos obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Decodificar o token
                decoded_token = AccessToken(token)
                
                if decoded_token['purpose'] != 'registration':
                    return Response({"detail": "Token inválido para registro."}, status=status.HTTP_400_BAD_REQUEST)
                
                if decoded_token['email'] != email:
                    return Response({"detail": "Token não corresponde ao e-mail fornecido."}, status=status.HTTP_400_BAD_REQUEST)
                
            except TokenError:
                return Response({"detail": "Token inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.get(username=username):
                return Response({"detail": "Esse usuário ja existe."}, status=status.HTTP_400_BAD_REQUEST)
            # Criar o usuário
            User.objects.create_user(
                email=email, 
                password=password, 
                first_name=first_name,
                last_name=last_name,
                username=username
            )

            user = User.objects.get(username=username)
            Member.objects.create(
                name=first_name + ' ' + last_name,
                availability=availability,
                cell_phone=cell_phone,
                profile_picture=profile_picture,
                function=function,
                user=user.id
            )
        return Response(status=status.HTTP_201_CREATED)
