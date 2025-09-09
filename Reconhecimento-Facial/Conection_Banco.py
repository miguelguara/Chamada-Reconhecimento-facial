import psycopg2

conexao = psycopg2.connect(
    host="localhost",        # Ex: "localhost" ou endereço do servidor
    port=5432,              # Porta padrão do PostgreSQL
    database="alunossesi",  # Nome do banco
    user="postgres",     # Seu usuário PostgreSQL
    password="1234"    # Sua senha
)

cursor = conexao.cursor()
print("✅ Conectado ao PostgreSQL!")

cursor.execute("SELECT version();")
print("Versão do PostgreSQL:", cursor.fetchone())

cursor.close()
conexao.close()

