from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.contrib.auth.models import User

from .serializers import \
    UserSerializers, MemberSerializers, MemberFunctionsSerializers, ChangePasswordSerializer, \
        CustomTokenObtainPairSerializer
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

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response("Senha alterada com sucesso!"),
            400: openapi.Response("Erro de validação"),
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
