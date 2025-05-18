# reset_db.py
from django.core.management import call_command
from django.db import connection

def reset_db():
    # Desativa verificação de chaves estrangeiras
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    # Obtém lista de tabelas
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
    
    # Remove cada tabela
    with connection.cursor() as cursor:
        for table in tables:
            print(f"Dropping table {table}")
            cursor.execute(f"DROP TABLE IF EXISTS `{table}`;")
    
    # Reativa verificação de chaves estrangeiras
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    
    print("Database reset complete")

if __name__ == "__main__":
    reset_db()