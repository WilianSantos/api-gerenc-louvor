from itsdangerous import URLSafeTimedSerializer
from django.conf import settings

def generate_email_token(email: str) -> str:
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt='email-confirm')

def verify_email_token(token: str, max_age: int = 3600) -> str:
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.loads(token, salt='email-confirm', max_age=max_age)
