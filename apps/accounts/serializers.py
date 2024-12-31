from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Member, MemberFunctions

from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'password', 'username', 'first_name', 'last_name', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class MemberFunctionsSerializers(serializers.ModelSerializer):
    class Meta:
        model = MemberFunctions
        fields = '__all__'
    

class MemberSerializers(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Adicionar o user_id ao payload
        user = self.user
        data['user_id'] = user.id  # Adiciona o ID do usuário ao payload

        member = Member.objects.get(user=user.id)
        data['member_id'] = member.id

        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        # Usar o validador de senha embutido do Django
        validate_password(value)
        return value
    

class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Nenhum usuário com este e-mail foi encontrado.")
        return value
    

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        # Usar o validador de senha embutido do Django
        validate_password(value)
        return value
    

class GenerateTemporaryTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class RegisterUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField()
    email = serializers.EmailField(required=True)
    availability = serializers.BooleanField()
    profile_picture = serializers.ImageField()
    function = serializers.ChoiceField()
    cell_phone = serializers.CharField()
    token = serializers.CharField(required=True)