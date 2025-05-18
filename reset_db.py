from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE();")
    tables = cursor.fetchall()
    for (table_name,) in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")
            print(f"✅ Tabela `{table_name}` deletada.")
        except Exception as e:
            print(f"❌ Erro ao deletar `{table_name}`: {e}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
