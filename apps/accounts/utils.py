from rest_framework_simplejwt.tokens import RefreshToken

from datetime import timedelta


def generate_reset_password_token(user):
    refresh = RefreshToken.for_user(user)
    reset_token = refresh.access_token
    reset_token['purpose'] = 'password_reset'  # Adiciona uma chave personalizada
    reset_token.set_exp(lifetime=timedelta(minutes=15))  # Define o tempo de expiração (opcional)
    return str(reset_token)