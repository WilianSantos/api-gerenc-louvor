from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.contrib.auth.models import User

from .serializers import \
    UserSerializers, MemberSerializers, MemberFunctionsSerializers, \
        ChangePasswordSerializer, EmailVerificationSerializer, ResetPasswordSerializer, \
            CustomTokenObtainPairSerializer

from .models import Member, MemberFunctions
from .utils import generate_reset_password_token


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
            reset_token = generate_reset_password_token(user)

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
            


