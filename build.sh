#!/bin/bash

echo "🔧 Rodando migrações..."
python manage.py migrate --noinput

echo "🎒 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# (opcional) criar superusuário automaticamente
echo "🧙 Criando superusuário..."
python manage.py shell < create_superuser.py
