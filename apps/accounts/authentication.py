from django.core import signing
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuthenticationFromCookie(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")

        if raw_token is None:
            raise NotAuthenticated(detail="Token não encontrado no cookie")
        
        try:
            decrypted_refresh =  signing.loads(raw_token)
            try:
                validated_token = self.get_validated_token(decrypted_refresh)
            except Exception:
                raise AuthenticationFailed(detail="Token inválido ou expirado")
            
        except signing.BadSignature:
            raise AuthenticationFailed(detail="Token inválido ou expirado")

        return self.get_user(validated_token), validated_token
