import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.getenv("DJANGO_SUPERUSER_USERNAME", "WilianAdmin")
email = os.getenv("DJANGO_SUPERUSER_EMAIL", "wilian.santos.dev@outlook.com")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "wilian")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("✅ Superusuário criado!")
else:
    print("⚠️ Superusuário já existe.")
