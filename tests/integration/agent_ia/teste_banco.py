from database_adapter import DatabaseAdapter
import sqlite3
import os

print("="*50)
print(" TESTE DE CONEXÃO COM BANCO DE DADOS")
print("="*50)

# Vamos primeiro descobrir qual banco o DatabaseAdapter está usando
print("\n Descobrindo qual banco o DatabaseAdapter usa...")

try:
    # Criar instância para ver os prints de debug
    print("\n Inicializando DatabaseAdapter...")
    adapter = DatabaseAdapter()
    print(" DatabaseAdapter inicializado")
    
    print("\n" + "="*50)
    print(" Teste Direto com SQLite3")
    print("="*50)
    
    # Procurar o banco na raiz do projeto
    db_path_raiz = r'C:\Users\JacksonRodrigues\Downloads\AgenteIa\escola.db'
    db_path_local = os.path.join(os.path.dirname(__file__), 'escola.db')
    db_path_pai = os.path.join(os.path.dirname(__file__), '..', 'escola.db')
    
    # Testar todos os caminhos possíveis
    caminhos = [
        ("Raiz do projeto", db_path_raiz),
        ("Pasta agente-ia", db_path_local),
        ("Pasta pai", db_path_pai)
    ]
    
    for nome, caminho in caminhos:
        caminho_abs = os.path.abspath(caminho)
        print(f"\n Testando {nome}: {caminho_abs}")
        print(f"   Arquivo existe: {os.path.exists(caminho_abs)}")
        
        if os.path.exists(caminho_abs):
            try:
                conn = sqlite3.connect(caminho_abs)
                cursor = conn.cursor()
                
                # Listar tabelas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                tabelas = [t[0] for t in tables]
                print(f"    Tabelas: {tabelas}")
                
                if 'alunos' in tabelas:
                    cursor.execute("SELECT COUNT(*) FROM alunos")
                    count = cursor.fetchone()[0]
                    print(f"    Total de alunos: {count}")
                    
                    if count > 0:
                        cursor.execute("SELECT id, nome_completo, matricula FROM alunos LIMIT 3")
                        alunos = cursor.fetchall()
                        print(f"    Primeiros alunos:")
                        for aluno in alunos:
                            print(f"      ID: {aluno[0]} - {aluno[1]} (Mat: {aluno[2]})")
                else:
                    print(f"    Tabela 'alunos' não encontrada")
                
                conn.close()
            except Exception as e:
                print(f"    Erro: {e}")
    
    print("\n" + "="*50)
    print(" Testando DatabaseAdapter com aluno 1")
    print("="*50)
    
    aluno = adapter.get_dados_completos_aluno(1)
    if aluno:
        print(f" Aluno 1 encontrado: {aluno['nome_completo']}")
        print(f"   Matrícula: {aluno['matricula']}")
        print(f"   Email: {aluno['email']}")
        print(f"   Cursos: {len(aluno.get('cursos', []))}")
        print(f"   Matérias: {len(aluno.get('materias', []))}")
        print(f"   Pagamentos: {len(aluno.get('pagamentos', []))}")
        print(f"   Requerimentos: {len(aluno.get('requerimentos', []))}")
    else:
        print(" Aluno 1 não encontrado")
        
except Exception as e:
    print(f" Erro: {e}")
    import traceback
    traceback.print_exc()