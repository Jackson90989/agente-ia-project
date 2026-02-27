"""
Script para criar cursos de teste no banco de dados
"""
import sqlite3
from datetime import datetime

DB_PATH = r'C:\Users\JacksonRodrigues\Downloads\AgenteIa\escola.db'

# Cursos a serem criados
CURSOS = [
    {
        "nome": "Bacharelado em Ciência da Computação",
        "codigo": "BCC",
        "descricao": "Curso de graduação em Ciência da Computação",
        "duracao_semestres": 8,
        "carga_horaria_total": 2800,
        "valor_mensalidade": 1200.00,
        "ativo": True
    },
    {
        "nome": "Engenharia de Software",
        "codigo": "ENGSOFT",
        "descricao": "Curso de graduação em Engenharia de Software",
        "duracao_semestres": 8,
        "carga_horaria_total": 2400,
        "valor_mensalidade": 1100.00,
        "ativo": True
    },
    {
        "nome": "Administração",
        "codigo": "ADM",
        "descricao": "Curso de graduação em Administração",
        "duracao_semestres": 8,
        "carga_horaria_total": 2160,
        "valor_mensalidade": 900.00,
        "ativo": True
    },
    {
        "nome": "Sistemas de Informação",
        "codigo": "SI",
        "descricao": "Curso de graduação em Sistemas de Informação",
        "duracao_semestres": 8,
        "carga_horaria_total": 2400,
        "valor_mensalidade": 1050.00,
        "ativo": True
    },
    {
        "nome": "Engenharia de Controle e Automação",
        "codigo": "ENGC",
        "descricao": "Curso de graduação em Engenharia de Controle e Automação",
        "duracao_semestres": 8,
        "carga_horaria_total": 2800,
        "valor_mensalidade": 1250.00,
        "ativo": True
    },
]

def criar_cursos():
    """Cria os cursos de teste no banco"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cursos'")
        if not cursor.fetchone():
            print(" Tabela 'cursos' não encontrada!")
            return False
        
        # Verificar quantos cursos já existem
        cursor.execute("SELECT COUNT(*) FROM cursos")
        total_existente = cursor.fetchone()[0]
        print(f" Cursos existentes: {total_existente}")
        
        # Inserir cursos novos
        inseridos = 0
        for curso in CURSOS:
            # Verificar se o curso já existe
            cursor.execute("SELECT id FROM cursos WHERE codigo = ?", (curso['codigo'],))
            if cursor.fetchone():
                print(f"⏭  Curso '{curso['codigo']}' já existe, pulando...")
                continue
            
            # Inserir novo curso
            cursor.execute("""
                INSERT INTO cursos (nome, codigo, descricao, duracao_semestres, 
                                   carga_horaria_total, valor_mensalidade, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                curso['nome'],
                curso['codigo'],
                curso['descricao'],
                curso['duracao_semestres'],
                curso['carga_horaria_total'],
                curso['valor_mensalidade'],
                curso['ativo']
            ))
            inseridos += 1
            print(f" Curso '{curso['codigo']}' criado com sucesso")
        
        conn.commit()
        
        # Listar todos os cursos
        cursor.execute("SELECT id, codigo, nome FROM cursos ORDER BY codigo")
        cursos = cursor.fetchall()
        
        print(f"\n Total de cursos no banco: {len(cursos)}")
        print("Cursos cadastrados:")
        for c in cursos:
            print(f"  • {c[1]} - {c[2]} (ID: {c[0]})")
        
        conn.close()
        
        print(f"\n {inseridos} novo(s) curso(s) criado(s) com sucesso!")
        return True
        
    except Exception as e:
        print(f" Erro ao criar cursos: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print(" SCRIPT PARA CRIAR CURSOS DE TESTE")
    print("="*60)
    print()
    
    if criar_cursos():
        print("\n Operação concluída com sucesso!")
    else:
        print("\n Operação falhou!")
