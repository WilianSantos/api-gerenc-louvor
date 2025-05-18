echo "📦 Instalando dependências..."
pip install -r requirements.txt

echo "🧨 Resetando banco de dados MySQL..."
python manage.py shell < reset_db.py

echo "🔧 Aplicando migrações..."
python manage.py migrate --noinput

echo "🎒 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "🧙 Criando superusuário se necessário..."
python manage.py shell < create_superuser.py

