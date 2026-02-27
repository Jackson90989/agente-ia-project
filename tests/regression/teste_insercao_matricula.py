"""
Script para testar inserção de matrícula no banco
"""
import sqlite3
from datetime import datetime

DB_PATH = r'C:\Users\JacksonRodrigues\Downloads\AgenteIa\escola.db'

def teste_insercao():
    """Testa a inserção de uma matrícula"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar estrutura
        cursor.execute('PRAGMA table_info(matriculas)')
        cols = cursor.fetchall()
        print(' Estrutura da tabela matriculas:')
        for col in cols:
            print(f'  • {col[1]:20} {col[2]:10}')
        
        # Testar formato de data
        data_test = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'\n Data de teste: {data_test}')
        print(f'   Tipo: {type(data_test).__name__}')
        
        # Buscar um aluno e um curso para teste
        cursor.execute("SELECT id FROM alunos LIMIT 1")
        aluno = cursor.fetchone()
        
        cursor.execute("SELECT id FROM cursos LIMIT 1") 
        curso = cursor.fetchone()
        
        if aluno and curso:
            aluno_id = aluno['id']
            curso_id = curso['id']
            
            print(f'\n Teste de INSERT:')
            print(f'  Aluno ID: {aluno_id}')
            print(f'  Curso ID: {curso_id}')
            
            # Tentar insert
            cursor.execute("""
                INSERT INTO matriculas (aluno_id, curso_id, ano, semestre, data_matricula, status)
                VALUES (?, ?, ?, ?, ?, 'cursando')
            """, (aluno_id, curso_id, 2026, 1, data_test))
            
            conn.commit()
            print('   INSERT bem-sucedido!')
            
            # Verificar
            cursor.execute("SELECT COUNT(*) as total FROM matriculas")
            total = cursor.fetchone()['total']
            print(f'   Total de matrículas: {total}')
        else:
            print(' Nenhum aluno ou curso encontrado para teste')
        
        conn.close()
        print('\n Teste concluído com sucesso!')
        return True
        
    except Exception as e:
        print(f' Erro: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print(" TESTE DE INSERÇÃO DE MATRÍCULA")
    print("="*60)
    print()
    teste_insercao()
