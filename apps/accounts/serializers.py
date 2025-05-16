from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from .models import Member, MemberFunctions


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "password", "username", "first_name", "last_name", "email"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    # def validate_username(self, value):
    #     user = self.context['request'].user
    #     # Verifica se o nome de usuário já existe, excluindo o usuário atual
    #     if User.objects.exclude(pk=user.pk).filter(username=value).exists():
    #         raise serializers.ValidationError("Este nome de usuário já está em uso.")
    #     return value


class MemberFunctionsSerializers(serializers.ModelSerializer):
    class Meta:
        model = MemberFunctions
        fields = "__all__"


class MemberSerializer(WritableNestedModelSerializer):

    class Meta:
        model = Member
        fields = "__all__"


class MemberMeSerializer(serializers.ModelSerializer):
    user = UserSerializers(read_only=True)
    function = MemberFunctionsSerializers(many=True, read_only=True)
    profile_picture = serializers.ImageField(read_only=True)

    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = "__all__"

    def get_profile_picture(self, obj):
        request = self.context.get("request")
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        # Usar o validador de senha embutido do Django
        validate_password(value)
        return value


class RequestPasswordResetSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Nenhum usuário encontrado com esse nome."
            )
        return value


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, max_length=500)
    new_password = serializers.CharField(required=True)


class RegisterUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    cell_phone = serializers.CharField()
    token = serializers.CharField(required=True, max_length=500)


class SendEmailSerializer(serializers.Serializer):
    emails = serializers.ListField(
        child=serializers.EmailField(),
        allow_empty=False,
        help_text="Lista de e-mails para os quais o convite será enviado.",
    )


class TokenVerificationSerializer(serializers.Serializer):
    valid = serializers.BooleanField(help_text="Indica se o token é válido.")
    email = serializers.EmailField(
        help_text="Email associado ao token válido.", required=False
    )
    detail = serializers.CharField(
        help_text="Mensagem de erro, caso o token seja inválido.", required=False
    )


class SendEmailResponseSerializer(serializers.Serializer):
    sent = serializers.ListField(
        child=serializers.EmailField(), help_text="E-mails enviados com sucesso."
    )
    failed = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        help_text="Lista de e-mails que falharam com detalhes do erro.",
    )


class MessageSerializer(serializers.Serializer):
    detail = serializers.CharField(help_text="Mensagem de informação")
