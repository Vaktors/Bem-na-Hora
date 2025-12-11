import mysql.connector

print("Testando conexao...")
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="senac",
        database="BemNaHora",
        port=3307
    )
    cursor = conn.cursor(dictionary=True, buffered=True)

    # Verificar se ha profissionais
    cursor.execute("SELECT COUNT(*) as count FROM profissional")
    prof_count = cursor.fetchone()['count']
    print(f"Profissionais: {prof_count}")

    # Verificar clinicas
    cursor.execute("SELECT COUNT(*) as count FROM clinica")
    clin_count = cursor.fetchone()['count']
    print(f"Clinicas: {clin_count}")

    # Verificar servicos
    cursor.execute("SELECT COUNT(*) as count FROM servicos_profissional")
    serv_count = cursor.fetchone()['count']
    print(f"Servicos profissionais: {serv_count}")

    # Verificar procedimentos
    cursor.execute("SELECT COUNT(*) as count FROM procedimentos")
    proc_count = cursor.fetchone()['count']
    print(f"Procedimentos: {proc_count}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Erro: {e}")