#!/bin/bash

echo "📦 Instalando dependências..."
pip install -r requirements.txt

if [ "$RESET_DB" = "true" ]; then
  echo "🧨 Resetando banco de dados..."
  python manage.py shell < reset_db.py
fi

echo "🔧 Aplicando migrações..."
python manage.py migrate --noinput

echo "🎒 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "🧙 Criando superusuário se necessário..."
python manage.py shell < create_superuser.py
