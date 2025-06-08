from django.core import signing
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuthenticationFromCookie(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")
        
        if raw_token is None:
            # Tenta também buscar no header Authorization como fallback
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header and auth_header.startswith('Bearer '):
                raw_token = auth_header.split(' ')[1]
            else:
                raise NotAuthenticated(detail="Token não encontrado")
        
        try:
            # Descriptografa o token
            decrypted_token = signing.loads(raw_token)
            
            # Valida o token JWT
            validated_token = self.get_validated_token(decrypted_token)
            
            # Retorna usuário e token validado
            return self.get_user(validated_token), validated_token
            
        except signing.BadSignature:
            logger.error("Token com assinatura inválida")
            raise AuthenticationFailed(detail="Token inválido")
        except Exception as e:
            logger.error(f"Erro na validação do token: {str(e)}")
            raise AuthenticationFailed(detail="Token inválido ou expirado")
