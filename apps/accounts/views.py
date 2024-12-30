from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

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
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response("Senha alterada com sucesso!"),
            400: openapi.Response("Senha antiga incorreta."),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Verificar a senha antiga
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": "Senha antiga incorreta."}, status=status.HTTP_400_BAD_REQUEST)

            # Alterar para a nova senha
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({"message": "Senha alterada com sucesso!"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RequestPasswordResetView(APIView):
    #documentação da api
    @swagger_auto_schema(
        request_body=EmailVerificationSerializer,
        responses={
            200: openapi.Response("reset_token")
        }
    )
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Gera o token de redefinição de senha
            reset_token = generate_reset_password_token(user)

            return Response({ "reset_token": reset_token}, status=status.HTTP_200_OK)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]  # Aberto para todos
    authentication_classes = []  # Sem autenticação padrão

    #documentação da api
    @swagger_auto_schema(
        request_body=ResetPasswordSerializer,
        responses={
            200: openapi.Response("Senha redefinida com sucesso!")
        }
    )
    
    def post(self):
        serializer = ResetPasswordSerializer
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']

            try:
                # Valida o token JWT
                user_data = JWTAuthentication().get_validated_token(token)
                if user_data['purpose'] != 'password_reset':
                    raise AuthenticationFailed('Token inválido ou expirado.')
                
                # Redefine a senha
                user = User.objects.get(id=user_data['user_id'])
                user.set_password(new_password)
                user.save()
                
                return Response({"message": "Senha redefinida com sucesso!"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
