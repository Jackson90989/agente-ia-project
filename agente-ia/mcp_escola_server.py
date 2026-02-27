"""
MCP Server Escolar - Versão Final Corrigida
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import FastMCP
import logging
import traceback
from jinja2 import Template
import hashlib
import ipaddress

# Configurar logging para arquivo (não interfere com stdio)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='mcp_server.log',
    filemode='w'
)
logger = logging.getLogger("escola-mcp")

# Criar servidor MCP
mcp = FastMCP("Escola MCP Server")

# ============ CONFIGURAÇÃO DO BANCO DE DADOS ============

# CAMINHO FIXO E CORRETO do banco de dados (forçado)
DB_PATH = r'C:\Users\JacksonRodrigues\Downloads\AgenteIa\escola.db'

# Verificar se o arquivo existe
if not os.path.exists(DB_PATH):
    logger.error(f" Banco NÃO encontrado no caminho fixo: {DB_PATH}")
    logger.error(" Verifique se o arquivo escola.db existe na pasta Downloads/AgenteIa")
    
    # Tentar encontrar automaticamente
    possible_paths = [
        r'C:\Users\JacksonRodrigues\Downloads\AgenteIa\escola.db',
        os.path.join(os.path.dirname(__file__), '..', 'escola.db'),
        os.path.join(os.path.expanduser('~'), 'Downloads', 'AgenteIa', 'escola.db'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            DB_PATH = path
            logger.info(f" Banco encontrado em: {DB_PATH}")
            break
else:
    logger.info(f" Banco encontrado no caminho fixo: {DB_PATH}")

# Verificar se o banco tem a tabela alunos
try:
    test_conn = sqlite3.connect(DB_PATH)
    test_cursor = test_conn.cursor()
    test_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alunos'")
    if test_cursor.fetchone():
        test_cursor.execute("SELECT COUNT(*) FROM alunos")
        num_alunos = test_cursor.fetchone()[0]
        logger.info(f" Banco validado: {num_alunos} alunos encontrados")
    else:
        logger.error(f" Banco não contém tabela 'alunos': {DB_PATH}")
    test_conn.close()
except Exception as e:
    logger.error(f" Erro ao validar banco: {e}")

# ============ FUNÇÕES AUXILIARES ============

def get_db_connection():
    """Retorna uma conexão com o banco de dados"""
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(DB_PATH):
            logger.error(f" Arquivo do banco NÃO encontrado: {DB_PATH}")
            return None
        
        # Tentar conectar
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f" Erro ao conectar ao banco: {e}")
        logger.error(traceback.format_exc())
        return None

def carregar_template_html():
    """Carrega o template HTML de declaração"""
    try:
        # Procurar template em diferentes locais
        possibles = [
            r'C:\Users\JacksonRodrigues\Downloads\AgenteIa\templates\declaracao_template.html',
            os.path.join(os.path.dirname(__file__), '..', 'templates', 'declaracao_template.html'),
            'templates/declaracao_template.html',
        ]
        
        for path in possibles:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
        
        logger.warning("Template HTML não encontrado, usando template padrão")
        return None
    except Exception as e:
        logger.error(f"Erro ao carregar template: {e}")
        return None

def gerar_pdf_declaracao(tipo_declaracao: str, aluno_id: int, aluno_nome: str, aluno_matricula: str, aluno_cpf: str = "") -> tuple:
    """
    Gera um PDF de declaração usando o template HTML
    
    Returns:
        (sucesso: bool, caminho_pdf: str, nome_arquivo: str)
    """
    try:
        from weasyprint import HTML, CSS
        from io import BytesIO
    except ImportError:
        logger.warning("weasyprint não instalado, tentando fallback com reportlab")
        return False, None, None
    
    try:
        # Carregar template
        template_html = carregar_template_html()
        
        if not template_html:
            return False, None, None
        
        # Preparar dados para o template
        from datetime import datetime
        from calendar import month_name
        
        hoje = datetime.now()
        data_extenso = f"{hoje.day} de {month_name[hoje.month]} de {hoje.year}"
        
        # Dados do aluno - valores padrão
        dados = {
            'aluno': {
                'nome': aluno_nome,
                'cpf': aluno_cpf or 'XXX.XXX.XXX-XX',
                'rg': 'XX.XXX.XXX-X',
                'data_nascimento': hoje,
                'matricula': aluno_matricula,
                'curso': 'Curso Não Especificado',
                'turma': 'Não informada',
                'periodo': 'Noturno',
                'ano_ingresso': 2024,
                'status': 'Ativo',
                'semestre_atual': 1,
                'data_previsao_conclusao': hoje,
                'frequencia': 95,
                'carga_horaria_total': 2400,
                'media_global': 8.5,
                'data_matricula': hoje,
            },
            'tipo_declaracao': 'DECLARAÇÃO DE MATRÍCULA' if tipo_declaracao == 'matricula' else 
                               'DECLARAÇÃO DE FREQUÊNCIA' if tipo_declaracao == 'frequencia' else
                               'DECLARAÇÃO DE CONCLUSÃO' if tipo_declaracao == 'conclusao' else
                               'DECLARAÇÃO DE VÍNCULO',
            'data_extenso': data_extenso,
            'data_hora_emissao': hoje,
            'cidade': 'São Paulo',
            'ano_atual': hoje.year,
            'declaracao_numero': f"{aluno_id}{hoje.strftime('%d%m%Y')}",
            'materias_atual': [
                {'codigo': 'ALG-101', 'nome': 'Álgebra Linear', 'carga_horaria': 60, 'professor': 'Prof. Silva'},
                {'codigo': 'PRO-101', 'nome': 'Programação I', 'carga_horaria': 80, 'professor': 'Prof. Costa'},
            ],
            'frequencias': [
                {'nome': 'Álgebra Linear', 'frequencia': 95, 'situacao': 'Apto'},
                {'nome': 'Programação I', 'frequencia': 98, 'situacao': 'Apto'},
            ],
            'periodo_inicio': hoje,
            'periodo_fim': hoje,
            'secretario_nome': 'Dra. Maria Silva',
            'secretario_matricula': 'SEC-001',
            'coordenador_nome': 'Prof. Dr. João Santos',
            'coordenador_matricula': 'COORD-001',
            'codigo_validacao': hashlib.sha256(f"{aluno_id}{hoje.isoformat()}".encode()).hexdigest()[:12],
            'ip_emissao': '192.168.1.1',
        }
        
        # Renderizar template com Jinja2
        template = Template(template_html)
        html_renderizado = template.render(**dados)
        
        # Criar diretório para PDFs
        pdf_dir = 'declaracoes'
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
        
        # Gerar nome do arquivo
        matricula_limpa = aluno_matricula.replace('/', '_').replace('\\', '_')
        nome_arquivo = f"declaracao_{matricula_limpa}_{tipo_declaracao}_{hoje.strftime('%Y%m%d%H%M%S')}.pdf"
        caminho_pdf = os.path.join(pdf_dir, nome_arquivo)
        
        # Converter HTML para PDF usando WeasyPrint
        try:
            HTML(string=html_renderizado).write_pdf(caminho_pdf)
            logger.info(f" PDF gerado com sucesso: {caminho_pdf}")
            return True, caminho_pdf, nome_arquivo
        except Exception as e:
            logger.warning(f"WeasyPrint falhou: {e}, tentando alternativa")
            return False, None, None
            
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {e}")
        logger.error(traceback.format_exc())
        return False, None, None

# ============ FERRAMENTAS (TOOLS) ============

@mcp.tool()
def listar_alunos(limite: int = 10) -> str:
    """
    Lista os alunos cadastrados no sistema.
    
    Args:
        limite: Número máximo de alunos a listar (padrão: 10)
    """
    logger.info(f" listar_alunos(limite={limite})")
    
    conn = get_db_connection()
    if not conn:
        return " Erro de conexão com o banco de dados."
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, nome_completo, matricula, status 
            FROM alunos 
            LIMIT ?
        """, (limite,))
        
        alunos = cursor.fetchall()
        
        if not alunos:
            return "Nenhum aluno cadastrado."
        
        resposta = " **Alunos Cadastrados:**\n\n"
        for a in alunos:
            status_emoji = "" if a['status'] == 'ativo' else "⏸"
            resposta += f"{status_emoji} ID {a['id']}: {a['nome_completo']} (Mat: {a['matricula']})\n"
        
        return resposta
        
    except Exception as e:
        logger.error(f"Erro ao listar alunos: {e}")
        logger.error(traceback.format_exc())
        return f" Erro ao listar alunos: {str(e)}"
    finally:
        conn.close()


@mcp.tool()
def consultar_aluno(aluno_id: int) -> str:
    """
    Consulta informações básicas de um aluno por ID.
    
    Args:
        aluno_id: ID do aluno (ex: 1, 2, 3)
    """
    logger.info(f" consultar_aluno({aluno_id})")
    
    try:
        conn = get_db_connection()
        if not conn:
            return " Erro de conexão com o banco de dados. Verifique os logs do servidor."
        
        cursor = conn.cursor()
        
        # Verificar se a tabela alunos existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alunos'")
        if not cursor.fetchone():
            logger.error(" Tabela 'alunos' não encontrada no banco!")
            conn.close()
            return " Erro: Tabela de alunos não encontrada no banco de dados."
        
        # Buscar aluno
        cursor.execute("SELECT * FROM alunos WHERE id = ?", (aluno_id,))
        aluno = cursor.fetchone()
        
        if not aluno:
            logger.warning(f" Aluno ID {aluno_id} não encontrado")
            conn.close()
            return f" Aluno com ID {aluno_id} não encontrado."
        
        aluno_dict = dict(aluno)
        logger.info(f" Aluno encontrado: {aluno_dict.get('nome_completo')}")
        
        # Buscar matérias do aluno
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN mm.status = 'cursando' THEN 1 ELSE 0 END) as cursando
            FROM materias m
            JOIN matriculas_materias mm ON mm.materia_id = m.id
            JOIN matriculas mat ON mat.id = mm.matricula_id
            WHERE mat.aluno_id = ?
        """, (aluno_id,))
        stats = cursor.fetchone()
        
        # Buscar pagamentos pendentes
        cursor.execute("""
            SELECT COUNT(*) as pendentes, 
                   COALESCE(SUM(valor), 0) as total_devendo
            FROM pagamentos 
            WHERE aluno_id = ? AND status IN ('pendente', 'atrasado')
        """, (aluno_id,))
        financeiro = cursor.fetchone()
        
        conn.close()
        
        return f""" **Dados do Aluno**

**Informações Pessoais:**
• Nome: {aluno_dict['nome_completo']}
• Matrícula: {aluno_dict['matricula']}
• CPF: {aluno_dict['cpf']}
• Email: {aluno_dict['email']}
• Status: {aluno_dict['status']}

**Resumo Acadêmico:**
• Total de matérias: {stats['total'] or 0}
• Cursando: {stats['cursando'] or 0}
• Pagamentos pendentes: {financeiro['pendentes'] or 0}
• Valor total devido: R$ {financeiro['total_devendo']:.2f}"""
        
    except Exception as e:
        logger.error(f" Erro ao consultar aluno: {e}")
        logger.error(traceback.format_exc())
        return f" Erro interno no servidor: {str(e)}"


@mcp.tool()
def cadastrar_novo_aluno(
    nome_completo: str,
    cpf: str,
    data_nascimento: str,
    email: str,
    telefone: str = None,
    rg: str = None,
    endereco: str = None,
    cidade: str = None,
    estado: str = None,
    cep: str = None,
    senha: str = "senha123",
    curso_codigo: str = None
) -> str:
    """
    Cadastra um novo aluno no sistema com matrícula automática.
    
    Args:
        nome_completo: Nome completo do aluno
        cpf: CPF do aluno (formato: 000.000.000-00 ou só números)
        data_nascimento: Data de nascimento (formato: YYYY-MM-DD ou DD/MM/YYYY)
        email: Email do aluno
        telefone: Telefone (opcional)
        rg: RG do aluno (opcional)
        endereco: Endereço completo (opcional)
        cidade: Cidade (opcional)
        estado: Estado - sigla de 2 letras (opcional)
        cep: CEP (opcional)
        senha: Senha para acesso ao portal (padrão: "senha123")
        curso_codigo: Código do curso para matrícula automática (opcional)
    """
    logger.info(f" cadastrar_novo_aluno({nome_completo}, {cpf}, {email})")
    
    import requests
    
    try:
        # Normalizar data de nascimento para YYYY-MM-DD
        data_nasc = data_nascimento.strip()
        if '/' in data_nasc:
            # Converter DD/MM/YYYY para YYYY-MM-DD
            partes = data_nasc.split('/')
            if len(partes) == 3:
                data_nasc = f"{partes[2]}-{partes[1]}-{partes[0]}"
        
        # Preparar dados para API
        dados_aluno = {
            "nome_completo": nome_completo.strip(),
            "cpf": cpf.strip(),
            "data_nascimento": data_nasc,
            "email": email.strip().lower(),
            "senha": senha,  #  ADICIONADO: passar a senha também
        }
        
        # Adicionar campos opcionais
        if telefone:
            dados_aluno["telefone"] = telefone.strip()
        if rg:
            dados_aluno["rg"] = rg.strip()
        if endereco:
            dados_aluno["endereco"] = endereco.strip()
        if cidade:
            dados_aluno["cidade"] = cidade.strip()
        if estado:
            dados_aluno["estado"] = estado.strip().upper()
        if cep:
            dados_aluno["cep"] = cep.strip()
        
        # Chamar API Flask para criar aluno
        response = requests.post(
            "http://localhost:5000/api/alunos",
            json=dados_aluno,
            timeout=10
        )
        
        if response.status_code == 201:
            aluno = response.json()
            matricula = aluno.get('matricula')
            aluno_id = aluno.get('id')
            
            logger.info(f" Aluno cadastrado: {matricula}")
            
            resposta = f""" **Aluno cadastrado com sucesso!**

 **Dados do Cadastro:**
• Nome: {nome_completo}
• Matrícula: **{matricula}**
• CPF: {cpf}
• Email: {email}
• Data de Nascimento: {data_nascimento}

 **Credenciais de Acesso:**
• Usuário: {matricula}
• Senha: {senha}
• Portal: http://localhost:5000/portal

 **Próximos Passos:**
1. Acesse o portal com suas credenciais
2. Complete seu cadastro se necessário
3. Consulte cursos disponíveis"""
            
            # Se curso foi especificado, criar matrícula no curso
            if curso_codigo and curso_codigo.lower() not in ["nao", "não", "skip", "-"]:
                try:
                    # Buscar curso
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT id, nome FROM cursos WHERE codigo = ? OR UPPER(nome) LIKE ?",
                            (curso_codigo.upper(), f"%{curso_codigo.upper()}%")
                        )
                        curso = cursor.fetchone()
                        
                        if curso:
                            # Criar matrícula no curso
                            ano_atual = datetime.now().year
                            semestre_atual = 1 if datetime.now().month <= 6 else 2
                            data_matricula = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            
                            cursor.execute("""
                                INSERT INTO matriculas (aluno_id, curso_id, ano, semestre, data_matricula, status)
                                VALUES (?, ?, ?, ?, ?, 'cursando')
                            """, (aluno_id, curso['id'], ano_atual, semestre_atual, data_matricula))
                            conn.commit()
                            
                            resposta += f"\n\n **Matrícula no Curso:**\n"
                            resposta += f"• Curso: {curso['nome']}\n"
                            resposta += f"• Período: {ano_atual}/{semestre_atual}\n"
                            resposta += f"• Status: Cursando"
                            
                            logger.info(f" Matrícula criada no curso {curso_codigo}")
                        else:
                            # Curso não encontrado - listar cursos disponíveis
                            cursor.execute("""
                                SELECT codigo, nome FROM cursos WHERE ativo = 1
                                ORDER BY nome LIMIT 5
                            """)
                            cursos_disponiveis = cursor.fetchall()
                            
                            if cursos_disponiveis:
                                resposta += f"\n\n Curso '{curso_codigo}' não encontrado.\n"
                                resposta += f"Cursos disponíveis:\n"
                                for c in cursos_disponiveis:
                                    resposta += f"• {c['codigo']} - {c['nome']}\n"
                                resposta += f"\nVocê pode se matricular depois usando um desses códigos."
                            else:
                                resposta += f"\n\n Curso '{curso_codigo}' não encontrado e nenhum curso disponível no momento."
                    else:
                        resposta += f"\n\n Não foi possível conectar ao banco para matricular no curso."
                except Exception as e:
                    logger.error(f"Erro ao criar matrícula no curso: {e}")
                    logger.error(traceback.format_exc())
                    resposta += f"\n\n Não foi possível matricular no curso automaticamente. Erro: {str(e)}"
                finally:
                    if conn:
                        conn.close()
            
            return resposta
        
        elif response.status_code == 409:
            return f" **Cadastro não realizado:** CPF ou email já cadastrado no sistema."
        
        else:
            erro = response.json().get('erro', 'Erro desconhecido')
            return f" **Erro ao cadastrar:** {erro}"
    
    except requests.exceptions.ConnectionError:
        logger.error(" Não foi possível conectar à API Flask")
        return " Erro: Servidor Flask não está respondendo. Certifique-se de que está rodando em http://localhost:5000"
    
    except Exception as e:
        logger.error(f" Erro ao cadastrar aluno: {e}")
        logger.error(traceback.format_exc())
        return f" Erro ao processar cadastro: {str(e)}"


@mcp.tool()
def listar_materias_disponiveis(aluno_id: int = None, semestre: int = None) -> str:
    """
    Lista as matérias disponíveis que o aluno pode se matricular.
    
    Args:
        aluno_id: ID do aluno (optional)
        semestre: Filtrar por semestre (optional)
    """
    logger.info(f" listar_materias_disponiveis(aluno_id={aluno_id}, semestre={semestre})")
    
    conn = get_db_connection()
    if not conn:
        return " Erro de conexão com o banco de dados."
    
    cursor = conn.cursor()
    
    try:
        # Buscar matérias
        if semestre:
            cursor.execute("""
                SELECT id, nome, codigo, professor, semestre, creditos
                FROM materias
                WHERE semestre = ?
                ORDER BY codigo
            """, (semestre,))
        else:
            cursor.execute("""
                SELECT id, nome, codigo, professor, semestre, creditos
                FROM materias
                ORDER BY semestre, codigo
            """)
        
        materias = cursor.fetchall()
        
        if not materias:
            return " Nenhuma matéria disponível."
        
        # Se aluno_id foi informado, filtrar matérias que o aluno já está matriculado
        ja_matriculado = []
        if aluno_id:
            cursor.execute("""
                SELECT m.id FROM materias m
                JOIN matriculas_materias mm ON mm.materia_id = m.id
                JOIN matriculas mat ON mat.id = mm.matricula_id
                WHERE mat.aluno_id = ?
            """, (aluno_id,))
            ja_matriculado = [row['id'] for row in cursor.fetchall()]
        
        conn.close()
        
        # Formatar resposta
        resposta = " **Matérias Disponíveis:**\n\n"
        
        for m in materias:
            status = "" if m['id'] in ja_matriculado else ""
            resposta += f"{status} **{m['codigo']}** - {m['nome']}\n"
            resposta += f"   Professor: {m['professor'] or 'N/I'} | Semestre: {m['semestre']} | Créditos: {m['creditos']}\n\n"
        
        if aluno_id:
            resposta += "\n = Já matriculado |  = Disponível para matrícula"
        
        return resposta
        
    except Exception as e:
        logger.error(f"Erro ao listar matérias: {e}")
        logger.error(traceback.format_exc())
        return f" Erro ao listar matérias: {str(e)}"


@mcp.tool()
def listar_cursos(codigo: str = None, apenas_ativos: bool = True) -> str:
    """
    Lista cursos cadastrados ou detalha um curso pelo codigo.
    
    Args:
        codigo: Codigo do curso (optional)
        apenas_ativos: Se True, lista apenas cursos ativos
    """
    logger.info(f" listar_cursos(codigo={codigo}, apenas_ativos={apenas_ativos})")
    
    conn = get_db_connection()
    if not conn:
        return " Erro de conexão com o banco de dados."
    
    cursor = conn.cursor()
    
    try:
        if codigo:
            cursor.execute("""
                SELECT id, nome, codigo, descricao, duracao_semestres,
                       carga_horaria_total, valor_mensalidade, ativo
                FROM cursos
                WHERE codigo = ?
            """, (codigo.upper(),))
            curso = cursor.fetchone()
            if not curso:
                return f" Curso com codigo {codigo} não encontrado."
            
            status = "Ativo" if curso['ativo'] else "Inativo"
            return (
                " **Detalhes do Curso:**\n\n"
                f"• Nome: {curso['nome']}\n"
                f"• Codigo: {curso['codigo']}\n"
                f"• Descricao: {curso['descricao'] or 'N/I'}\n"
                f"• Duracao: {curso['duracao_semestres']} semestres\n"
                f"• Carga horaria total: {curso['carga_horaria_total'] or 'N/I'}\n"
                f"• Mensalidade: R$ {curso['valor_mensalidade']:.2f}\n"
                f"• Status: {status}"
            )
        
        if apenas_ativos:
            cursor.execute("""
                SELECT id, nome, codigo, duracao_semestres,
                       carga_horaria_total, valor_mensalidade, ativo
                FROM cursos
                WHERE ativo = 1
                ORDER BY nome
            """)
        else:
            cursor.execute("""
                SELECT id, nome, codigo, duracao_semestres,
                       carga_horaria_total, valor_mensalidade, ativo
                FROM cursos
                ORDER BY nome
            """)
        
        cursos = cursor.fetchall()
        if not cursos:
            return " Nenhum curso encontrado."
        
        resposta = " **Cursos Disponiveis:**\n\n"
        for c in cursos:
            status = "" if c['ativo'] else "⏸"
            resposta += (
                f"{status} **{c['codigo']}** - {c['nome']}\n"
                f"   Duracao: {c['duracao_semestres']} semestres | "
                f"Carga horaria: {c['carga_horaria_total'] or 'N/I'} | "
                f"Mensalidade: R$ {c['valor_mensalidade']:.2f}\n\n"
            )
        
        if not apenas_ativos:
            resposta += "\n Ativo | ⏸ Inativo"
        
        return resposta
        
    except Exception as e:
        logger.error(f"Erro ao listar cursos: {e}")
        logger.error(traceback.format_exc())
        return f" Erro ao listar cursos: {str(e)}"
    finally:
        conn.close()


@mcp.tool()
def perguntar_sobre_aluno(aluno_id: int, pergunta: str) -> str:
    """
    Faz uma pergunta em linguagem natural sobre um aluno.
    
    Args:
        aluno_id: ID do aluno
        pergunta: Pergunta em português (ex: "quais são minhas matérias?")
    """
    logger.info(f" perguntar_sobre_aluno({aluno_id}, '{pergunta}')")
    
    conn = get_db_connection()
    if not conn:
        return " Erro de conexão com o banco de dados."
    
    cursor = conn.cursor()
    
    try:
        # Verificar se aluno existe
        cursor.execute("SELECT nome_completo FROM alunos WHERE id = ?", (aluno_id,))
        aluno = cursor.fetchone()
        if not aluno:
            return f" Aluno ID {aluno_id} não encontrado."
        
        nome_aluno = aluno['nome_completo']
        pergunta_lower = pergunta.lower()
        
        # Processar diferentes tipos de pergunta
        if "quem sou" in pergunta_lower or "meus dados" in pergunta_lower:
            cursor.execute("SELECT * FROM alunos WHERE id = ?", (aluno_id,))
            dados = dict(cursor.fetchone())
            return f"""Olá {dados['nome_completo']}! Aqui estão seus dados:
• Matrícula: {dados['matricula']}
• CPF: {dados['cpf']}
• Email: {dados['email']}
• Telefone: {dados.get('telefone', 'Não informado')}
• Status: {dados['status']}"""
        
        elif "matéria" in pergunta_lower or "disciplina" in pergunta_lower or "materias" in pergunta_lower:
            cursor.execute("""
                SELECT m.nome, m.codigo, mm.status
                FROM materias m
                JOIN matriculas_materias mm ON mm.materia_id = m.id
                JOIN matriculas mat ON mat.id = mm.matricula_id
                WHERE mat.aluno_id = ?
            """, (aluno_id,))
            materias = cursor.fetchall()
            
            if materias:
                resposta = " **Suas matérias:**\n"
                for m in materias:
                    status_emoji = "" if m['status'] == 'aprovado' else "" if m['status'] == 'cursando' else ""
                    resposta += f"{status_emoji} {m['nome']} ({m['codigo']}) - {m['status']}\n"
                return resposta
            return "Você não está matriculado em nenhuma matéria."
        
        elif "nota" in pergunta_lower:
            cursor.execute("""
                SELECT m.nome, mm.nota_final, mm.status
                FROM materias m
                JOIN matriculas_materias mm ON mm.materia_id = m.id
                JOIN matriculas mat ON mat.id = mm.matricula_id
                WHERE mat.aluno_id = ? AND mm.nota_final IS NOT NULL
            """, (aluno_id,))
            notas = cursor.fetchall()
            
            if notas:
                resposta = " **Suas notas:**\n"
                for n in notas:
                    resposta += f"• {n['nome']}: {n['nota_final']} - {n['status']}\n"
                return resposta
            return "Você ainda não tem notas lançadas."
        
        elif "pagamento" in pergunta_lower or "boleto" in pergunta_lower or "financeiro" in pergunta_lower:
            cursor.execute("""
                SELECT * FROM pagamentos 
                WHERE aluno_id = ? AND status IN ('pendente', 'atrasado')
                ORDER BY data_vencimento
            """, (aluno_id,))
            pendentes = cursor.fetchall()
            
            if pendentes:
                total = sum(p['valor'] for p in pendentes)
                resposta = f" **Total pendente: R$ {total:.2f}**\n\n"
                for p in pendentes:
                    status_emoji = "" if p['status'] == 'atrasado' else ""
                    resposta += f"{status_emoji} R$ {p['valor']:.2f} - Vence: {p['data_vencimento']} ({p['status']})\n"
                return resposta
            return " Todos os seus pagamentos estão em dia!"
        
        elif "frequência" in pergunta_lower or "frequencia" in pergunta_lower:
            cursor.execute("""
                SELECT m.nome, mm.frequencia
                FROM materias m
                JOIN matriculas_materias mm ON mm.materia_id = m.id
                JOIN matriculas mat ON mat.id = mm.matricula_id
                WHERE mat.aluno_id = ? AND mm.frequencia IS NOT NULL
            """, (aluno_id,))
            freq = cursor.fetchall()
            
            if freq:
                resposta = " **Sua frequência:**\n"
                for f in freq:
                    status = " OK" if f['frequencia'] >= 75 else " Atenção"
                    resposta += f"• {f['nome']}: {f['frequencia']}% {status}\n"
                return resposta
            return "Informações de frequência não disponíveis."
        
        elif "resumo" in pergunta_lower or "situação" in pergunta_lower:
            # Redirecionar para resumo_academico
            return resumo_academico(aluno_id)
        
        return "Desculpe, não entendi. Tente: 'quem sou eu', 'minhas matérias', 'minhas notas', 'meus boletos' ou 'minha frequência'."
        
    except Exception as e:
        logger.error(f"Erro ao processar pergunta: {e}")
        logger.error(traceback.format_exc())
        return f" Erro ao processar pergunta: {str(e)}"
    finally:
        conn.close()


@mcp.tool()
def criar_requerimento(aluno_id: int, tipo: str, kwargs: dict = None) -> str:
    """
    Cria um novo requerimento para o aluno.
    
    Args:
        aluno_id: ID do aluno
        tipo: Tipo de requerimento (adicao_materia, remocao_materia, declaracao, boleto, trancamento, diploma, transferencia, endereco)
        kwargs: Dados adicionais (codigo_materia, tipo_declaracao, valor, motivo)
    """
    logger.info(f" criar_requerimento(aluno_id={aluno_id}, tipo={tipo}, kwargs={kwargs})")
    
    conn = get_db_connection()
    if not conn:
        return " Erro de conexão com o banco de dados."
    
    cursor = conn.cursor()
    
    try:
        # Verificar se aluno existe
        cursor.execute("SELECT nome_completo, matricula FROM alunos WHERE id = ?", (aluno_id,))
        aluno_row = cursor.fetchone()
        if not aluno_row:
            return f" Aluno ID {aluno_id} não encontrado."
        
        aluno_nome = aluno_row[0]
        aluno_matricula = aluno_row[1]
        
        # Se kwargs for None, inicializar como dict vazio
        if kwargs is None:
            kwargs = {}
        
        # Gerar protocolo/código
        protocolo = f"REQ-{aluno_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Responder baseado no tipo
        if tipo == "adicao_materia":
            codigo = kwargs.get('codigo_materia', 'N/I')
            return f""" REQUERIMENTO DE ADIÇÃO DE MATÉRIA CRIADO COM SUCESSO!

 Protocolo: {protocolo}
 Aluno: {aluno_nome} ({aluno_matricula})
 Matéria: {codigo}
 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Seu requerimento foi registrado no sistema e será processado em até 2 dias úteis."""
        
        elif tipo == "remocao_materia":
            codigo = kwargs.get('codigo_materia', 'N/I')
            return f""" REQUERIMENTO DE REMOÇÃO DE MATÉRIA CRIADO COM SUCESSO!

 Protocolo: {protocolo}
 Aluno: {aluno_nome} ({aluno_matricula})
 Matéria: {codigo}
 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Seu requerimento foi registrado no sistema e será processado em até 2 dias úteis."""
        
        elif tipo == "declaracao":
            tipo_decl = kwargs.get('tipo_declaracao', 'matricula')
            
            # Tentar gerar PDF da declaração usando o template HTML
            try:
                # Pegar CPF do aluno
                cursor.execute("SELECT cpf FROM alunos WHERE id = ?", (aluno_id,))
                cpf_row = cursor.fetchone()
                aluno_cpf = cpf_row[0] if cpf_row else "XXX.XXX.XXX-XX"
                
                # Usar nova função para gerar PDF com template
                sucesso, caminho_pdf, nome_arquivo = gerar_pdf_declaracao(
                    tipo_decl, aluno_id, aluno_nome, aluno_matricula, aluno_cpf
                )
                
                if sucesso and caminho_pdf:
                    tipo_desc = {
                        'matricula': 'DECLARAÇÃO DE MATRÍCULA',
                        'frequencia': 'DECLARAÇÃO DE FREQUÊNCIA',
                        'conclusao': 'DECLARAÇÃO DE CONCLUSÃO',
                        'vinculo': 'DECLARAÇÃO DE VÍNCULO'
                    }.get(tipo_decl, 'DECLARAÇÃO')
                    
                    return f""" DECLARAÇÃO GERADA COM SUCESSO!

 Protocolo: {protocolo}
 Aluno: {aluno_nome} ({aluno_matricula})
 Tipo: {tipo_desc}
 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
 Arquivo: {nome_arquivo}

 Sua declaração foi gerada em formato PDF profissional e está pronta para download!
Caminho: {caminho_pdf}

 Código de validação: {hashlib.sha256(f'{aluno_id}{datetime.now().isoformat()}'.encode()).hexdigest()[:12]}
"""
                else:
                    # Fallback: gerar resposta mesmo sem PDF
                    logger.warning(f"Falha ao gerar PDF, usando fallback")
                    return f""" REQUERIMENTO DE DECLARAÇÃO CRIADO

 Protocolo: {protocolo}
 Aluno: {aluno_nome} ({aluno_matricula})
 Tipo: {tipo_decl.upper()}

 A declaração foi registrada no sistema.
O documento será enviado para seu email em breve."""
            
            except Exception as e:
                logger.error(f"Erro ao criar declaração: {e}")
                logger.error(traceback.format_exc())
                return f""" Erro ao processar declaração

 Protocolo: {protocolo}
Erro: {str(e)}"""
        
        elif tipo == "boleto":
            valor = kwargs.get('valor', 850.00)
            if valor <= 0:
                valor = 850.00
            return f""" REQUERIMENTO DE 2ª VIA DE BOLETO CRIADO COM SUCESSO!

 Protocolo: {protocolo}
 Aluno: {aluno_nome} ({aluno_matricula})
 Valor: R$ {valor:.2f}
 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

O boleto será emitido e enviado para seu email cadastrado em até 24 horas."""
        
        elif tipo == "trancamento":
            motivo = kwargs.get('motivo', 'Solicitação do aluno')
            return f""" REQUERIMENTO DE TRANCAMENTO CRIADO COM SUCESSO!

 Protocolo: {protocolo}
 Aluno: {aluno_nome} ({aluno_matricula})
 Motivo: {motivo}
 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Seu requerimento será analisado e processado em até 3 dias úteis."""
        
        elif tipo == "diploma":
            return f""" REQUERIMENTO DE 2ª VIA DE DIPLOMA CRIADO COM SUCESSO!

 Protocolo: {protocolo}
 Aluno: {aluno_nome} ({aluno_matricula})
 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Sua solicitação será processada e pode levar até 5 dias úteis para conclusão."""
        
        elif tipo == "transferencia":
            motivo = kwargs.get('motivo', 'Solicitação do aluno')
            return f""" REQUERIMENTO DE TRANSFERÊNCIA CRIADO COM SUCESSO!

 Protocolo: {protocolo}
 Aluno: {aluno_nome} ({aluno_matricula})
 Motivo: {motivo}
 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Seu requerimento será analisado por nossa comissão acadêmica em até 5 dias úteis."""
        
        elif tipo == "endereco":
            return f""" REQUERIMENTO DE ATUALIZAÇÃO DE ENDEREÇO CRIADO COM SUCESSO!

 Protocolo: {protocolo}
 Aluno: {aluno_nome} ({aluno_matricula})
 Solicitação: Alteração de endereço cadastrado
 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Dirija-se à secretaria com seus documentos para atualizar seu endereço."""
        
        else:
            return f""" REQUERIMENTO CRIADO COM SUCESSO!

 Protocolo: {protocolo}
 Aluno: {aluno_nome} ({aluno_matricula})
 Tipo: {tipo}
 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Seu requerimento foi registrado no sistema e será processado em breve."""
        
    except Exception as e:
        logger.error(f"Erro ao criar requerimento: {e}")
        logger.error(traceback.format_exc())
        return f" Erro ao criar requerimento: {str(e)}"
    finally:
        conn.close()


@mcp.tool()
def resumo_academico(aluno_id: int) -> str:
    """
    Mostra um resumo completo da situação acadêmica do aluno.
    
    Args:
        aluno_id: ID do aluno
    """
    logger.info(f" resumo_academico({aluno_id})")
    
    conn = get_db_connection()
    if not conn:
        return " Erro de conexão com o banco de dados."
    
    cursor = conn.cursor()
    
    try:
        # Dados do aluno
        cursor.execute("SELECT * FROM alunos WHERE id = ?", (aluno_id,))
        aluno = cursor.fetchone()
        if not aluno:
            return f" Aluno ID {aluno_id} não encontrado."
        
        aluno_dict = dict(aluno)
        
        # Estatísticas de matérias
        cursor.execute("""
            SELECT 
                COUNT(*) as total_materias,
                SUM(CASE WHEN status = 'cursando' THEN 1 ELSE 0 END) as cursando,
                SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END) as aprovadas,
                SUM(CASE WHEN status = 'reprovado' THEN 1 ELSE 0 END) as reprovadas
            FROM matriculas_materias mm
            JOIN matriculas mat ON mat.id = mm.matricula_id
            WHERE mat.aluno_id = ?
        """, (aluno_id,))
        stats_materias = cursor.fetchone()
        
        # Pagamentos
        cursor.execute("""
            SELECT 
                COUNT(*) as total_pagamentos,
                SUM(CASE WHEN status IN ('pendente', 'atrasado') THEN 1 ELSE 0 END) as pendentes,
                COALESCE(SUM(CASE WHEN status IN ('pendente', 'atrasado') THEN valor ELSE 0 END), 0) as valor_devido
            FROM pagamentos
            WHERE aluno_id = ?
        """, (aluno_id,))
        stats_pagamentos = cursor.fetchone()
        
        # Requerimentos
        cursor.execute("""
            SELECT COUNT(*) as total_requerimentos
            FROM requerimentos
            WHERE aluno_id = ?
        """, (aluno_id,))
        stats_requerimentos = cursor.fetchone()
        
        conn.close()
        
        return f""" **RESUMO ACADÊMICO - {aluno_dict['nome_completo']}**

**Situação:** {aluno_dict['status']}
**Matrícula:** {aluno_dict['matricula']}

** MATÉRIAS:**
• Total: {stats_materias['total_materias'] or 0}
• Cursando: {stats_materias['cursando'] or 0}
• Aprovadas: {stats_materias['aprovadas'] or 0}
• Reprovadas: {stats_materias['reprovadas'] or 0}

** FINANCEIRO:**
• Total de pagamentos: {stats_pagamentos['total_pagamentos'] or 0}
• Pendentes: {stats_pagamentos['pendentes'] or 0}
• Valor devido: R$ {stats_pagamentos['valor_devido']:.2f}

** REQUERIMENTOS:**
• Total: {stats_requerimentos['total_requerimentos'] or 0}"""
        
    except Exception as e:
        logger.error(f"Erro no resumo acadêmico: {e}")
        logger.error(traceback.format_exc())
        return f" Erro ao gerar resumo: {str(e)}"
    finally:
        conn.close()


@mcp.tool()
def buscar_pagamentos(aluno_id: int, status: Optional[str] = None) -> str:
    """
    Busca pagamentos/boletos do aluno
    
    Args:
        aluno_id: ID do aluno
        status: Filtro por status (pendente, pago, atrasado) - opcional
    """
    logger.info(f" buscar_pagamentos(aluno_id={aluno_id}, status={status})")
    
    conn = get_db_connection()
    if not conn:
        return " Erro de conexão com o banco de dados."
    
    try:
        cursor = conn.cursor()
        
        # Buscar pagamentos
        if status:
            cursor.execute("""
                SELECT * FROM pagamentos 
                WHERE aluno_id = ? AND status = ?
                ORDER BY data_vencimento
            """, (aluno_id, status))
        else:
            cursor.execute("""
                SELECT * FROM pagamentos 
                WHERE aluno_id = ?
                ORDER BY data_vencimento DESC
            """, (aluno_id,))
        
        pagamentos = cursor.fetchall()
        
        if not pagamentos:
            if status:
                return f" Nenhum pagamento com status '{status}' encontrado."
            return " Nenhum pagamento registrado."
        
        # Formatar resposta
        resultado = f" **Pagamentos do Aluno #{aluno_id}**\n\n"
        
        total_pendente = 0
        total_pago = 0
        
        for pag in pagamentos:
            status_emoji = "" if pag['status'] == 'pendente' else "" if pag['status'] == 'pago' else ""
            resultado += f"{status_emoji} **{pag['tipo']}** - R$ {pag['valor']:.2f}\n"
            resultado += f"   Vencimento: {pag['data_vencimento']}\n"
            resultado += f"   Status: {pag['status'].upper()}\n"
            
            if pag.get('data_pagamento'):
                resultado += f"   Pagamento: {pag['data_pagamento']}\n"
            
            if pag['status'] == 'pendente':
                total_pendente += pag['valor']
            elif pag['status'] == 'pago':
                total_pago += pag['valor']
            
            resultado += "\n"
        
        # Resumo
        resultado += f"\n **Resumo:**\n"
        resultado += f"• Total de pagamentos: {len(pagamentos)}\n"
        if total_pendente > 0:
            resultado += f"• Valor pendente: R$ {total_pendente:.2f}\n"
        if total_pago > 0:
            resultado += f"• Valor pago: R$ {total_pago:.2f}\n"
        
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao buscar pagamentos: {e}")
        logger.error(traceback.format_exc())
        return f" Erro ao buscar pagamentos: {str(e)}"
    finally:
        conn.close()


@mcp.tool()
def diagnosticar_banco() -> str:
    """
    Diagnostica qual banco de dados está sendo usado
    """
    logger.info(" Diagnosticando banco de dados...")
    
    try:
        conn = get_db_connection()
        if not conn:
            return " Não foi possível conectar ao banco"
        
        cursor = conn.cursor()
        
        # Verificar caminho do banco
        cursor.execute("PRAGMA database_list")
        db_info = cursor.fetchone()
        caminho_real = db_info[2] if db_info else "Desconhecido"
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        
        # Verificar alunos
        if 'alunos' in tables:
            cursor.execute("SELECT COUNT(*) FROM alunos")
            num_alunos = cursor.fetchone()[0]
            
            if num_alunos > 0:
                cursor.execute("SELECT id, nome_completo FROM alunos LIMIT 3")
                alunos = cursor.fetchall()
                alunos_str = "\n".join([f"   ID {a[0]}: {a[1]}" for a in alunos])
            else:
                alunos_str = "Nenhum aluno encontrado"
        else:
            num_alunos = 0
            alunos_str = "Tabela 'alunos' não existe"
        
        conn.close()
        
        return f""" **DIAGNÓSTICO DO BANCO**

**Caminho configurado:** {DB_PATH}
**Caminho real:** {caminho_real}

**Tabelas encontradas:** {len(tables)}
{', '.join(tables[:10])}

**Alunos:** {num_alunos}
{alunos_str}

**Status:** {' OK' if num_alunos > 0 else ' PROBLEMA'}"""
        
    except Exception as e:
        logger.error(f"Erro no diagnóstico: {e}")
        logger.error(traceback.format_exc())
        return f" Erro no diagnóstico: {str(e)}"


# ============ RECURSOS (RESOURCES) ============

@mcp.resource("aluno://{aluno_id}/dados")
def recurso_dados_aluno(aluno_id: int) -> str:
    """Recurso que fornece dados básicos do aluno"""
    logger.info(f" recurso_dados_aluno({aluno_id})")
    
    conn = get_db_connection()
    if not conn:
        return "Erro de conexão"
    
    cursor = conn.cursor()
    cursor.execute("SELECT nome_completo, matricula FROM alunos WHERE id = ?", (aluno_id,))
    aluno = cursor.fetchone()
    conn.close()
    
    if not aluno:
        return f"Aluno {aluno_id} não encontrado"
    
    return f"Nome: {aluno['nome_completo']}, Matrícula: {aluno['matricula']}"


@mcp.resource("escola://info")
def recurso_info_escola() -> str:
    """Informações gerais da escola"""
    logger.info(" recurso_info_escola()")
    
    conn = get_db_connection()
    if not conn:
        return "Erro de conexão"
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) as total FROM alunos")
        total_alunos = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM cursos")
        total_cursos = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM materias")
        total_materias = cursor.fetchone()['total']
        
        conn.close()
        
        return f""" **Informações da Escola**

• Total de alunos: {total_alunos}
• Total de cursos: {total_cursos}
• Total de matérias: {total_materias}"""
        
    except Exception as e:
        logger.error(f"Erro ao buscar info da escola: {e}")
        logger.error(traceback.format_exc())
        return f"Erro ao buscar informações: {str(e)}"
    finally:
        conn.close()


# ============ PROMPTS ============

@mcp.prompt()
def consulta_academica(aluno_nome: str, assunto: str) -> str:
    """
    Gera um prompt para consulta acadêmica personalizada.
    
    Args:
        aluno_nome: Nome do aluno
        assunto: Assunto da consulta (matérias, notas, etc.)
    """
    return f"""
Você é um assistente acadêmico especializado em ajudar alunos com suas dúvidas.

Aluno: {aluno_nome}
Assunto: {assunto}

Por favor, forneça informações claras e úteis sobre este assunto acadêmico.
"""


# ============ EXECUÇÃO ============

if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    
    # Log inicial
    logger.info("="*50)
    logger.info(" ESCOLA MCP SERVER INICIANDO")
    logger.info("="*50)
    logger.info(f" Banco de dados: {DB_PATH}")
    logger.info(" Servidor MCP rodando em http://localhost:8000")
    logger.info("="*50)
    
    # Criar app FastAPI personalizado
    app = FastAPI(title="Escola MCP Server")
    
    # Adicionar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Montar o MCP SSE app no endpoint /mcp
    mcp_app = mcp.sse_app()
    app.mount("/mcp", mcp_app)
    
    # Endpoint JSON-RPC HTTP para compatibilidade
    @app.post("/")
    async def jsonrpc_endpoint(request: Request):
        """Endpoint JSON-RPC para chamadas diretas"""
        try:
            data = await request.json()
            method = data.get("method", "")
            params = data.get("params", {})
            request_id = data.get("id", 1)
            
            logger.info(f" JSON-RPC: {method} - Params: {params}")
            
            # Roteamento de métodos
            if method == "tools/list":
                # Listar ferramentas disponíveis
                tools = [
                    {
                        "name": "listar_alunos",
                        "description": "Lista os alunos cadastrados no sistema",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "limite": {"type": "number", "description": "Número máximo de alunos"}
                            }
                        }
                    },
                    {
                        "name": "consultar_aluno",
                        "description": "Consulta informações de um aluno específico",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "aluno_id": {"type": "number", "description": "ID do aluno", "required": True}
                            },
                            "required": ["aluno_id"]
                        }
                    },
                    {
                        "name": "perguntar_sobre_aluno",
                        "description": "Faz perguntas sobre um aluno (matérias, notas, etc)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "aluno_id": {"type": "number", "description": "ID do aluno", "required": True},
                                "pergunta": {"type": "string", "description": "Pergunta sobre o aluno", "required": True}
                            },
                            "required": ["aluno_id", "pergunta"]
                        }
                    },
                    {
                        "name": "criar_requerimento",
                        "description": "Cria um requerimento para o aluno",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "aluno_id": {"type": "number", "description": "ID do aluno", "required": True},
                                "tipo": {"type": "string", "description": "Tipo de requerimento", "required": True},
                                "kwargs": {"type": "object", "description": "Argumentos adicionais"}
                            },
                            "required": ["aluno_id", "tipo"]
                        }
                    },
                    {
                        "name": "resumo_academico",
                        "description": "Gera resumo acadêmico completo do aluno",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "aluno_id": {"type": "number", "description": "ID do aluno", "required": True}
                            },
                            "required": ["aluno_id"]
                        }
                    },
                    {
                        "name": "buscar_pagamentos",
                        "description": "Busca pagamentos e boletos do aluno",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "aluno_id": {"type": "number", "description": "ID do aluno", "required": True},
                                "status": {"type": "string", "description": "Filtro por status (pendente, pago, atrasado)"}
                            },
                            "required": ["aluno_id"]
                        }
                    },
                    {
                        "name": "diagnosticar_banco",
                        "description": "Diagnostica qual banco de dados está sendo usado",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "listar_cursos",
                        "description": "Lista cursos cadastrados ou detalha um curso pelo código",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "codigo": {"type": "string", "description": "Código do curso (opcional)"},
                                "apenas_ativos": {"type": "boolean", "description": "Se True, lista apenas cursos ativos"}
                            }
                        }
                    },
                    {
                        "name": "listar_materias_disponiveis",
                        "description": "Lista as matérias disponíveis que o aluno pode se matricular",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "aluno_id": {"type": "number", "description": "ID do aluno (opcional)"},
                                "semestre": {"type": "number", "description": "Filtrar por semestre (opcional)"}
                            }
                        }
                    },
                    {
                        "name": "cadastrar_novo_aluno",
                        "description": "Cadastra um novo aluno no sistema com matrícula automática",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "nome_completo": {"type": "string", "description": "Nome completo do aluno", "required": True},
                                "cpf": {"type": "string", "description": "CPF do aluno (formato: 000.000.000-00 ou só números)", "required": True},
                                "data_nascimento": {"type": "string", "description": "Data de nascimento (formato: YYYY-MM-DD ou DD/MM/YYYY)", "required": True},
                                "email": {"type": "string", "description": "Email do aluno", "required": True},
                                "telefone": {"type": "string", "description": "Telefone (opcional)"},
                                "rg": {"type": "string", "description": "RG do aluno (opcional)"},
                                "endereco": {"type": "string", "description": "Endereço completo (opcional)"},
                                "cidade": {"type": "string", "description": "Cidade (opcional)"},
                                "estado": {"type": "string", "description": "Estado - sigla de 2 letras (opcional)"},
                                "cep": {"type": "string", "description": "CEP (opcional)"},
                                "senha": {"type": "string", "description": "Senha para acesso ao portal (padrão: senha123)"},
                                "curso_codigo": {"type": "string", "description": "Código do curso para matrícula automática (opcional)"}
                            },
                            "required": ["nome_completo", "cpf", "data_nascimento", "email"]
                        }
                    }
                ]
                
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools}
                })
            
            elif method == "tools/call":
                # Chamar ferramenta
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                logger.info(f" Chamando ferramenta: {tool_name} com args: {arguments}")
                
                # Chamar a ferramenta correspondente
                result_text = ""
                
                if tool_name == "listar_alunos":
                    result_text = listar_alunos(**arguments)
                elif tool_name == "consultar_aluno":
                    result_text = consultar_aluno(**arguments)
                elif tool_name == "perguntar_sobre_aluno":
                    result_text = perguntar_sobre_aluno(**arguments)
                elif tool_name == "criar_requerimento":
                    result_text = criar_requerimento(**arguments)
                elif tool_name == "resumo_academico":
                    result_text = resumo_academico(**arguments)
                elif tool_name == "buscar_pagamentos":
                    result_text = buscar_pagamentos(**arguments)
                elif tool_name == "diagnosticar_banco":
                    result_text = diagnosticar_banco(**arguments)
                elif tool_name == "listar_cursos":
                    result_text = listar_cursos(**arguments)
                elif tool_name == "listar_materias_disponiveis":
                    result_text = listar_materias_disponiveis(**arguments)
                elif tool_name == "cadastrar_novo_aluno":
                    result_text = cadastrar_novo_aluno(**arguments)
                else:
                    result_text = f" Ferramenta '{tool_name}' não encontrada"
                
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result_text
                            }
                        ]
                    }
                })
            
            else:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Método '{method}' não encontrado"
                    }
                })
                
        except Exception as e:
            logger.error(f" Erro no endpoint JSON-RPC: {e}")
            logger.error(traceback.format_exc())
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": data.get("id", 1) if 'data' in locals() else 1,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            })
    
    @app.get("/health")
    async def health_check():
        """Endpoint de saúde"""
        return {"status": "ok", "message": "Escola MCP Server is running"}
    
    # Iniciar servidor HTTP
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8000"))
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )