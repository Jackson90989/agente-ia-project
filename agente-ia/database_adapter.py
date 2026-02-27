from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

import sqlite3  # Adicione no topo do arquivo

class DatabaseAdapter:
    def __init__(self):
        # CAMINHO ABSOLUTO CORRETO - apontando para a raiz do projeto
        db_path = r'C:\Users\JacksonRodrigues\Downloads\AgenteIa\instance\escola.db'
        
        # Verificar se o arquivo existe
        if not os.path.exists(db_path):
            print(f"  Arquivo do banco NÃO encontrado em: {db_path}")
            # Tentar caminho relativo (subir um nível)
            db_path =  r'C:\Users\JacksonRodrigues\Downloads\AgenteIa\instance\escola.db'
            print(f" Tentando caminho relativo: {os.path.abspath(db_path)}")
        
        # Converter para caminho absoluto
        db_path = os.path.abspath(db_path)
        print(f" DatabaseAdapter CONECTANDO EM: {db_path}")
        print(f" Arquivo existe: {os.path.exists(db_path)}")
        
        # Listar TODAS as tabelas deste banco
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f" Tabelas neste banco: {[t[0] for t in tables]}")
                conn.close()
            except Exception as e:
                print(f" Erro ao listar tabelas: {e}")
        
        if not os.path.exists(db_path):
            raise Exception(f"Banco de dados não encontrado em: {db_path}")
        
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)

class DatabaseAdapter:
    def __init__(self):
        # Conectar ao banco de dados da escola
        db_path = r'C:\Users\JacksonRodrigues\Downloads\AgenteIa\instance\escola.db'
        
        # Verificar se o arquivo existe
        if not os.path.exists(db_path):
            print(f"  Arquivo do banco não encontrado em: {db_path}")
            # Tentar caminho alternativo
            db_path = r'C:\Users\JacksonRodrigues\Downloads\AgenteIa\instance\escola.db'
            print(f" Tentando caminho alternativo: {db_path}")
        
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
        
        # Tabela para histórico de consultas
        self._criar_tabela_historico()
    
    def _criar_tabela_historico(self):
        """Cria tabela para histórico de consultas se não existir"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS historico_consultas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        aluno_id INTEGER NOT NULL,
                        pergunta TEXT NOT NULL,
                        resposta TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
        except Exception as e:
            print(f"Erro ao criar tabela de histórico: {e}")
    
    def get_dados_completos_aluno(self, aluno_id):
        """Busca todos os dados de um aluno"""
        try:
            with self.engine.connect() as conn:
                # Dados básicos do aluno
                aluno = conn.execute(
                    text("SELECT * FROM alunos WHERE id = :id"),
                    {"id": aluno_id}
                ).fetchone()
                
                if not aluno:
                    print(f"Aluno ID {aluno_id} não encontrado no banco")
                    return None
                
                # Converter para dicionário
                aluno_dict = dict(aluno._mapping)
                
                # Formatar datas
                if aluno_dict.get('data_nascimento'):
                    aluno_dict['data_nascimento'] = str(aluno_dict['data_nascimento'])
                if aluno_dict.get('data_matricula'):
                    aluno_dict['data_matricula'] = str(aluno_dict['data_matricula'])
                
                # Buscar cursos do aluno (CORRIGIDO)
                cursos = conn.execute(
                    text("""
                        SELECT c.*, m.status, m.ano, m.semestre
                        FROM cursos c
                        JOIN matriculas m ON m.curso_id = c.id
                        WHERE m.aluno_id = :aluno_id
                    """),
                    {"aluno_id": aluno_id}
                ).fetchall()
                
                aluno_dict['cursos'] = []
                for curso in cursos:
                    curso_dict = dict(curso._mapping)
                    aluno_dict['cursos'].append({
                        'id': curso_dict['id'],
                        'nome': curso_dict['nome'],
                        'codigo': curso_dict['codigo'],
                        'status_matricula': curso_dict['status'],  #  CORRIGIDO: agora usa 'status'
                        'ano': curso_dict['ano'],
                        'semestre': curso_dict['semestre']
                    })
                
                # Buscar matérias do aluno
                materias = conn.execute(
                    text("""
                        SELECT 
                            m.id, m.nome, m.codigo, m.carga_horaria, m.creditos,
                            mm.status, mm.nota_final, mm.frequencia,
                            c.nome as curso_nome
                        FROM materias m
                        JOIN matriculas_materias mm ON mm.materia_id = m.id
                        JOIN matriculas mat ON mat.id = mm.matricula_id
                        JOIN cursos c ON c.id = m.curso_id
                        WHERE mat.aluno_id = :aluno_id
                    """),
                    {"aluno_id": aluno_id}
                ).fetchall()
                
                aluno_dict['materias'] = []
                for materia in materias:
                    materia_dict = dict(materia._mapping)
                    aluno_dict['materias'].append(materia_dict)
                
                # Buscar pagamentos
                pagamentos = conn.execute(
                    text("""
                        SELECT * FROM pagamentos 
                        WHERE aluno_id = :aluno_id 
                        ORDER BY data_vencimento DESC
                    """),
                    {"aluno_id": aluno_id}
                ).fetchall()
                
                aluno_dict['pagamentos'] = []
                for pag in pagamentos:
                    pag_dict = dict(pag._mapping)
                    # Formatar datas
                    if pag_dict.get('data_vencimento'):
                        pag_dict['data_vencimento'] = str(pag_dict['data_vencimento'])
                    if pag_dict.get('data_pagamento'):
                        pag_dict['data_pagamento'] = str(pag_dict['data_pagamento'])
                    if pag_dict.get('data_emissao'):
                        pag_dict['data_emissao'] = str(pag_dict['data_emissao'])
                    
                    # Adicionar referência formatada
                    if pag_dict.get('mes_referencia') and pag_dict.get('ano_referencia'):
                        pag_dict['referencia'] = f"{pag_dict['mes_referencia']:02d}/{pag_dict['ano_referencia']}"
                    
                    aluno_dict['pagamentos'].append(pag_dict)
                
                # Buscar requerimentos
                requerimentos = conn.execute(
                    text("""
                        SELECT * FROM requerimentos 
                        WHERE aluno_id = :aluno_id 
                        ORDER BY data_solicitacao DESC
                    """),
                    {"aluno_id": aluno_id}
                ).fetchall()
                
                aluno_dict['requerimentos'] = []
                for req in requerimentos:
                    req_dict = dict(req._mapping)
                    # Formatar datas
                    if req_dict.get('data_solicitacao'):
                        req_dict['data_solicitacao'] = str(req_dict['data_solicitacao'])
                    if req_dict.get('data_processamento'):
                        req_dict['data_processamento'] = str(req_dict['data_processamento'])
                    
                    aluno_dict['requerimentos'].append(req_dict)
                
                return aluno_dict
                
        except Exception as e:
            print(f"Erro ao buscar dados do aluno: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def registrar_consulta(self, aluno_id, pergunta, resposta):
        """Registra consulta no histórico"""
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO historico_consultas (aluno_id, pergunta, resposta)
                        VALUES (:aluno_id, :pergunta, :resposta)
                    """),
                    {
                        "aluno_id": aluno_id,
                        "pergunta": pergunta,
                        "resposta": resposta
                    }
                )
                conn.commit()
        except Exception as e:
            print(f"Erro ao registrar consulta: {e}")
    
    def get_historico_consultas(self, aluno_id, limite=10):
        """Busca histórico de consultas do aluno"""
        try:
            with self.engine.connect() as conn:
                consultas = conn.execute(
                    text("""
                        SELECT * FROM historico_consultas 
                        WHERE aluno_id = :aluno_id 
                        ORDER BY timestamp DESC 
                        LIMIT :limite
                    """),
                    {"aluno_id": aluno_id, "limite": limite}
                ).fetchall()
                
                return [dict(c._mapping) for c in consultas]
        except Exception as e:
            print(f"Erro ao buscar histórico: {e}")
            return []
    
    def validar_aluno(self, aluno_id):
        """Valida se aluno existe"""
        try:
            with self.engine.connect() as conn:
                aluno = conn.execute(
                    text("SELECT id, nome_completo FROM alunos WHERE id = :id"),
                    {"id": aluno_id}
                ).fetchone()
                return aluno is not None
        except Exception as e:
            print(f"Erro ao validar aluno: {e}")
            return False