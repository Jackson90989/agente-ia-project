"""
Agente IA Inteligente - Versão final corrigida (FastMCP 1.26.0)
"""
import ast
import logging
import requests
import json
import re
import time
import unicodedata
import secrets

# Configurações
USE_OLLAMA = True
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

logger = logging.getLogger(__name__)


def _safe_eval_math(expression):
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        return None

    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.USub,
        ast.UAdd,
        ast.Constant,
    )

    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            return None

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.UnaryOp):
            value = _eval(node.operand)
            if value is None:
                return None
            if isinstance(node.op, ast.UAdd):
                return value
            if isinstance(node.op, ast.USub):
                return -value
            return None
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            if left is None or right is None:
                return None
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Pow):
                return left ** right
            if isinstance(node.op, ast.Mod):
                return left % right
            return None
        return None

    return _eval(tree)

class AgenteIAInteligente:
    def __init__(self, mcp_url="http://localhost:8000"):
        self.mcp_url = mcp_url  # URL base sem /mcp
        self.aluno_id = None
        self.aluno_nome = None
        self.contexto = []
        self.request_id = 1
        self.ferramentas = []
        self.acao_pendente = None
        self.dados_cadastro = None  # Para coletar dados de novos alunos
        
    def _get_next_id(self):
        """Retorna o próximo ID de requisição"""
        self.request_id += 1
        return self.request_id
    
    def _resposta_ferramenta_indisponivel(self, tool_name):
        """Retorna uma resposta útil quando uma ferramenta não está disponível"""
        respostas_alternativas = {
            "listar_cursos": (
                " **Cursos Disponíveis**\n\n"
                "Atualmente temos diversos cursos nas áreas de:\n"
                "• Ciência da Computação\n"
                "• Engenharias\n"
                "• Administração\n"
                "• Direito\n"
                "• Saúde\n\n"
                " **Para mais informações:**\n"
                "• Entre em contato com a secretaria\n"
                "• Visite nosso site institucional\n"
                "• Ou faça seu cadastro para ter acesso completo ao sistema\n\n"
                " Nota: A ferramenta de listagem de cursos está temporariamente indisponível. "
                "Tente novamente mais tarde ou reinicie o servidor MCP."
            )
        }
        
        return respostas_alternativas.get(
            tool_name,
            f" A ferramenta '{tool_name}' está temporariamente indisponível.\n\n"
            f" Dica: Tente reiniciar o servidor MCP ou entre em contato com o suporte."
        )
    
    def _chamar_fastmcp(self, metodo, params=None):
        """
        Chama o servidor FastMCP via HTTP (endpoint raiz)
        """
        if params is None:
            params = {}
        
        # Preparar payload JSON-RPC
        payload = {
            "jsonrpc": "2.0",
            "method": metodo,
            "params": params,
            "id": self._get_next_id()
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # print(f" [FastMCP] {metodo} (ID: {payload['id']})")  # Debug desabilitado
        
        try:
            # IMPORTANTE: usar a URL base sem /mcp
            response = requests.post(
                self.mcp_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            # print(f" Status: {response.status_code}")  # Debug desabilitado
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    return result
                except json.JSONDecodeError:
                    return {"error": "Resposta não é JSON válido"}
            else:
                try:
                    erro = response.json()
                    return {"error": erro}
                except:
                    return {"error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.ConnectionError:
            return {"error": "ConnectionError - servidor não está respondendo"}
        except Exception as e:
            return {"error": str(e)}
    
    def verificar_servidor(self, max_tentativas=10, intervalo=1):
        """Verifica se o servidor está respondendo com retry"""
        for tentativa in range(1, max_tentativas + 1):
            try:
                print(f"   Tentativa {tentativa}/{max_tentativas}...", end="\r")
                response = requests.get(f"{self.mcp_url}/health", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    print(f"\n[OK] Servidor conectado com sucesso!                  ")
                    return True
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                if tentativa < max_tentativas:
                    time.sleep(intervalo)
                else:
                    print(f"\n[ERRO] Nao consegui conectar ao servidor apos {max_tentativas} tentativas")
                    print(f"   URL: {self.mcp_url}")
                    print("\n   Certifique-se de que:")
                    print("   1. O MCP Server esta rodando: mcp_escola_server.py")
                    print("   2. A porta 8000 esta disponivel")
                    print("   3. Nao ha firewall bloqueando a conexao")
                    return False
            except Exception as e:
                if tentativa >= max_tentativas:
                    print(f"\n[ERRO] Erro ao verificar servidor: {e}")
                    return False
        
        return False
    
    def listar_ferramentas(self):
        """
        Lista as ferramentas disponíveis
        """
        print("\n Listando ferramentas...")
        
        resposta = self._chamar_fastmcp("tools/list", {})
        
        if "result" in resposta:
            result = resposta["result"]
            if isinstance(result, dict) and "tools" in result:
                tools = result["tools"]
                print(f" {len(tools)} ferramentas encontradas:")
                for tool in tools:
                    print(f"  • {tool.get('name')}: {tool.get('description', 'Sem descrição')}")
                return tools
        elif "error" in resposta:
            print(f" Erro ao listar ferramentas: {resposta['error']}")
        
        print(" Usando lista padrão de ferramentas")
        return [
            {"name": "listar_alunos", "description": "Lista os alunos cadastrados"},
            {"name": "consultar_aluno", "description": "Consulta informações de um aluno"},
            {"name": "perguntar_sobre_aluno", "description": "Faz perguntas sobre um aluno"},
            {"name": "listar_cursos", "description": "Lista cursos cadastrados"},
            {"name": "listar_materias_disponiveis", "description": "Lista matérias disponíveis para matrícula"},
            {"name": "cadastrar_novo_aluno", "description": "Cadastra um novo aluno no sistema"},
            {"name": "criar_requerimento", "description": "Cria um requerimento (adicao_materia, remocao_materia, declaracao, boleto, trancamento, diploma, transferencia, endereco)"},
            {"name": "resumo_academico", "description": "Mostra resumo acadêmico completo"},
            {"name": "buscar_pagamentos", "description": "Busca pagamentos e boletos do aluno"},
            {"name": "diagnosticar_banco", "description": "Diagnostica qual banco de dados está sendo usado"}
        ]
    
    def chamar_ferramenta(self, tool_name, arguments):
        """
        Chama uma ferramenta específica
        """
        # print(f"\n Chamando ferramenta: {tool_name}")  # Debug desabilitado
        
        # Ferramentas que NÃO requerem aluno_id
        ferramentas_publicas = ["listar_alunos", "diagnosticar_banco", "listar_cursos", "listar_materias_disponiveis", "cadastrar_novo_aluno"]
        
        # Ferramentas que REQUEREM aluno_id
        ferramentas_privadas = ["consultar_aluno", "perguntar_sobre_aluno", "criar_requerimento", 
                               "resumo_academico", "buscar_pagamentos"]
        
        # Verificar se é uma ferramenta privada sem aluno_id
        if tool_name in ferramentas_privadas and not self.aluno_id:
            return " Para usar este recurso, você precisa fazer login primeiro.\n\n" + \
                   " Use o menu inicial e escolha a opção [1] Fazer login.\n\n" + \
                   "Se você é um novo aluno, você pode:\n" + \
                   "• Consultar cursos disponíveis\n" + \
                   "• Ver informações sobre matérias\n" + \
                   "• Obter informações gerais sobre a instituição"
        
        # Adicionar aluno_id se necessário
        if "aluno_id" not in arguments and tool_name not in ferramentas_publicas:
            if self.aluno_id:
                arguments["aluno_id"] = self.aluno_id
                # print(f" Adicionando aluno_id={self.aluno_id}")  # Debug desabilitado
        
        # print(f" Argumentos: {json.dumps(arguments, ensure_ascii=False)}")  # Debug desabilitado
        
        params = {
            "name": tool_name,
            "arguments": arguments
        }
        
        resposta = self._chamar_fastmcp("tools/call", params)
        
        # Processar resposta
        if "result" in resposta:
            result = resposta["result"]
            
            # Formato FastMCP: result.content[0].text
            if isinstance(result, dict):
                if "content" in result:
                    content = result["content"]
                    if content and isinstance(content, list) and len(content) > 0:
                        if "text" in content[0]:
                            return content[0]["text"]
                return result
            return result
        elif "error" in resposta:
            erro = resposta["error"]
            if isinstance(erro, dict):
                mensagem_erro = erro.get('message', str(erro))
                # Tratar ferramentas não encontradas de forma mais amigável
                if "not found" in mensagem_erro.lower() or "não encontrada" in mensagem_erro.lower():
                    return self._resposta_ferramenta_indisponivel(tool_name)
                return f" Erro: {mensagem_erro}"
            return f" Erro: {erro}"
        else:
            return str(resposta)
    
    def consultar_llm(self, pergunta):
        """Consulta o LLM para interpretar a pergunta"""
        
        # Lista de ferramentas para o prompt
        tools_list = "\n".join([f"- {f['name']}: {f.get('description', '')}" for f in self.ferramentas])
        
        # Verificar se usuário está autenticado para personalizar o prompt
        usuario_autenticado = self.aluno_id is not None
        
        system_prompt = f"""Você é um agente de uma faculdade e um assistente inteligente para ajudar alunos. Sua missão é:
1. Responder perguntas sobre assuntos acadêmicos e ajudar com requerimentos
2. Se a pergunta for fora do contexto acadêmico, responder de forma inteligente, amigável e útil

Ferramentas acadêmicas disponíveis:
{tools_list}

IMPORTANTE - FERRAMENTAS QUE REQUEREM LOGIN:
 Ferramentas que SÓ funcionam para usuários logados:
   - consultar_aluno (dados pessoais)
   - perguntar_sobre_aluno (matérias, notas, etc)
   - criar_requerimento (requerimentos acadêmicos)
   - resumo_academico (histórico acadêmico)
   - buscar_pagamentos (boletos e pagamentos)

 Ferramentas públicas (funcionam SEM login):
   - listar_cursos (lista todos os cursos)
   - listar_materias_disponiveis (lista disciplinas disponíveis)
   - cadastrar_novo_aluno (cadastra novo aluno no sistema)
   - diagnosticar_banco (informações do sistema)

USUÁRIO ATUAL: {"LOGADO (tem acesso a todas as ferramentas)" if usuario_autenticado else "NÃO LOGADO (só pode usar ferramentas públicas)"}

Responda SEMPRE com JSON no formato:
{{"acao": "ferramenta", "ferramenta": "nome", "argumentos": {{}}}}
ou {{"acao": "conversa", "resposta": "texto"}}

INSTRUÇÕES IMPORTANTES:
1. Primeiro, tente identificar se é uma pergunta acadêmica ou geral
2. Se for acadêmica:
   - {"Use ferramentas disponíveis conforme necessário" if usuario_autenticado else "Use APENAS listar_cursos ou listar_materias_disponiveis (ferramentas públicas)"}
   - {"Use criar_requerimento para requerimentos" if usuario_autenticado else "Oriente o usuário a fazer login para criar requerimentos"}
3. Se FOR UMA PERGUNTA GERAL (não acadêmica):
   - Sempre responda com {{"acao": "conversa", "resposta": "..."}} com uma resposta inteligente, contextualizada e amigável
   - Seja conversível, prestativo e sempre mantenha um tom útil
   - Responda completamente a pergunta de forma natural
4. Seja educado, amigável e prestativo com os alunos
5. Entenda perguntas implícitas e contexto
6. Se o usuário NÃO está logado e pede dados pessoais, oriente-o a fazer login primeiro

TIPOS DE REQUERIMENTOS ACADÊMICOS DISPONÍVEIS:
- adicao_materia: Para adicionar uma disciplina
- remocao_materia: Para remover uma disciplina
- declaracao: Para gerar declarações (matricula, frequencia, conclusao)
- boleto: Para solicitar 2ª via de boleto
- trancamento: Para trancar semestre/matéria
- certificado: Para solicitar certificado
- transferencia: Para solicitar transferência interna/externa
- endereco: Para solicitar atualização de endereço
- diploma: Para solicitar 2ª via de diploma

EXEMPLOS ACADÊMICOS:
- "quem sou eu?" -> {{"acao": "ferramenta", "ferramenta": "consultar_aluno", "argumentos": {{}}}}
- "minhas matérias" -> {{"acao": "ferramenta", "ferramenta": "perguntar_sobre_aluno", "argumentos": {{"pergunta": "minhas matérias"}}}}
- "quais são os cursos?" -> {{"acao": "ferramenta", "ferramenta": "listar_cursos", "argumentos": {{}}}}
- "me fale sobre os cursos" -> {{"acao": "ferramenta", "ferramenta": "listar_cursos", "argumentos": {{}}}}
- "cursos disponíveis" -> {{"acao": "ferramenta", "ferramenta": "listar_cursos", "argumentos": {{}}}}
- "quero adicionar matéria ALG-101" -> {{"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {{"tipo": "adicao_materia", "kwargs": {{"codigo_materia": "ALG-101"}}}}}}
- "remover MAT-102" -> {{"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {{"tipo": "remocao_materia", "kwargs": {{"codigo_materia": "MAT-102"}}}}}}
- "preciso de declaração de matrícula" -> {{"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {{"tipo": "declaracao", "kwargs": {{"tipo_declaracao": "matricula"}}}}}}
- "segunda via de boleto" -> {{"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {{"tipo": "boleto", "kwargs": {{"valor": 850.00}}}}}}
- "resumo acadêmico" -> {{"acao": "ferramenta", "ferramenta": "resumo_academico", "argumentos": {{}}}}

EXEMPLOS NÃO ACADÊMICOS (Respostas conversacionais):
- "obrigado" -> {{"acao": "conversa", "resposta": "Por nada! Estou aqui para ajudar com qualquer coisa. "}}
- "como você está?" -> {{"acao": "conversa", "resposta": "Estou bem! Pronto para ajudar você em tudo que precisar. Como posso ajudá-lo?"}}
- "qual é a capital da França?" -> {{"acao": "conversa", "resposta": "A capital da França é Paris, uma das cidades mais bonitas e históricas do mundo."}}
- "me conte um piada" -> {{"acao": "conversa", "resposta": "Claro! Por que o livro de matemática se suicidou? Porque tinha muitos problemas! "}}
- "está chovendo?" -> {{"acao": "conversa", "resposta": "Não tenho informações meteorológicas em tempo real, mas você pode verificar em um aplicativo de previsão do tempo."}}"""
        
        if USE_OLLAMA:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": f"{system_prompt}\n\nPergunta: {pergunta}\n\nResposta JSON:",
                "stream": False,
                "temperature": 0.3,  # Um pouco maior para mais criatividade em respostas gerais
                "format": "json"
            }
            
            try:
                # print(" Consultando Ollama...")  # Debug desabilitado
                response = requests.post(OLLAMA_URL, json=payload, timeout=30)
                
                if response.status_code == 200:
                    texto = response.json().get("response", "{}")
                    # print(f" Resposta LLM: {texto[:200]}...")  # Debug desabilitado
                    
                    # Extrair JSON
                    try:
                        return json.loads(texto)
                    except json.JSONDecodeError as exc:
                        logger.debug("Falha ao decodificar JSON do LLM: %s", exc)
                        match = re.search(r'\{.*\}', texto, re.DOTALL)
                        if match:
                            try:
                                return json.loads(match.group())
                            except json.JSONDecodeError as exc:
                                logger.debug("Falha ao extrair JSON do LLM: %s", exc)
                    
                    # Se não conseguiu fazer JSON, pero temos texto, retornar como conversação
                    if texto and texto.strip():
                        return {"acao": "conversa", "resposta": texto}
                    return {"acao": "conversa", "resposta": "Desculpe, não consegui processar sua pergunta."}
                else:
                    # Fallback: análise simples baseada em palavras-chave
                    return self._analise_inteligente(pergunta)
                    
            except requests.exceptions.ConnectionError:
                # Fallback: análise inteligente quando Ollama não está disponível
                return self._analise_inteligente(pergunta)
            except Exception as e:
                # Fallback: análise inteligente em caso de erro
                return self._analise_inteligente(pergunta)
        
        # Se USE_OLLAMA for False
        return self._analise_inteligente(pergunta)
    
    def _analise_inteligente(self, pergunta):
        """
        Análise inteligente da pergunta - tenta identificar ação acadêmica
        Se não conseguir, tenta responder como um chatbot inteligente
        """
        pergunta_lower = pergunta.lower()
        pergunta_sem_acento = self._normalizar_texto(pergunta)

        # Detectar se é apenas um código de matéria (ex: "ALG-101")
        if re.match(r'^[A-Z]{3}-\d{3}$', pergunta.strip(), re.IGNORECASE):
            codigo = pergunta.strip().upper()
            # Assumir que é para adicionar uma matéria
            return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "adicao_materia", "kwargs": {"codigo_materia": codigo}}}
        
        # Padrões de reconhecimento
        if any(palavra in pergunta_lower for palavra in ["quem sou", "meus dados", "minhas informações"]):
            # Só pode consultar dados se tiver aluno_id
            if self.aluno_id:
                return {"acao": "ferramenta", "ferramenta": "consultar_aluno", "argumentos": {}}
            else:
                return {"acao": "conversa", "resposta": "Para consultar seus dados, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}
        
        elif any(palavra in pergunta_sem_acento for palavra in ["materia", "disciplina", "cadeira"]) and \
             not any(palavra in pergunta_sem_acento for palavra in ["adicionar", "mudar", "trocar", "remover", "deletar", "excluir"]):
            # Só pode consultar matérias se tiver aluno_id
            if self.aluno_id:
                return {"acao": "ferramenta", "ferramenta": "perguntar_sobre_aluno", "argumentos": {"pergunta": "minhas matérias"}}
            else:
                return {"acao": "conversa", "resposta": "Para consultar suas matérias, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}
        
        elif any(palavra in pergunta_lower for palavra in ["notas", "média", "nota"]):
            # Só pode consultar notas se tiver aluno_id
            if self.aluno_id:
                return {"acao": "ferramenta", "ferramenta": "perguntar_sobre_aluno", "argumentos": {"pergunta": "minhas notas"}}
            else:
                return {"acao": "conversa", "resposta": "Para consultar suas notas, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}
        
        elif any(palavra in pergunta_sem_acento for palavra in ["curso", "cursos"]):
            # Esta ferramenta NÃO requer aluno_id - qualquer um pode usar
            # Verificar se a ferramenta listar_cursos está disponível
            ferramentas_disponiveis = [f.get('name') for f in self.ferramentas] if self.ferramentas else []
            
            if "listar_cursos" in ferramentas_disponiveis:
                match = re.search(
                    r'\bcurso(?:s)?\s+(?:do|da|de)?\s*([A-Z]{2,6}(?:-\d{1,3})?)\b',
                    pergunta,
                    re.IGNORECASE
                )
                if match:
                    return {"acao": "ferramenta", "ferramenta": "listar_cursos", "argumentos": {"codigo": match.group(1).upper()}}
                return {"acao": "ferramenta", "ferramenta": "listar_cursos", "argumentos": {}}
            else:
                # Fornecer resposta direta se a ferramenta não estiver disponível
                return {"acao": "conversa", "resposta": self._resposta_ferramenta_indisponivel("listar_cursos")}
        
        elif any(palavra in pergunta_lower for palavra in ["boleto", "pagamento", "financeiro", "mensalidade"]):
            # Só pode consultar boletos se tiver aluno_id
            if self.aluno_id:
                return {"acao": "ferramenta", "ferramenta": "perguntar_sobre_aluno", "argumentos": {"pergunta": "meus boletos"}}
            else:
                return {"acao": "conversa", "resposta": "Para consultar boletos e pagamentos, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}
        
        elif any(palavra in pergunta_lower for palavra in ["resumo", "situação academica", "histórico"]):
            # Só pode consultar resumo acadêmico se tiver aluno_id
            if self.aluno_id:
                return {"acao": "ferramenta", "ferramenta": "resumo_academico", "argumentos": {}}
            else:
                return {"acao": "conversa", "resposta": "Para consultar seu resumo acadêmico, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}

        # DESISTÊNCIA / CANCELAMENTO DE MATRÍCULA
        elif any(palavra in pergunta_sem_acento for palavra in ["desistir", "desistencia", "desistência", "cancelar matricula", "cancelamento", "sair da faculdade", "abandonar curso"]):
            # Só pode criar requerimento se tiver aluno_id
            if self.aluno_id:
                return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "trancamento", "kwargs": {"motivo": "Desistência do aluno"}}}
            else:
                return {"acao": "conversa", "resposta": "Para criar requerimentos, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}
        
        # DECLARAÇÃO - detectar requerimento de declaração
        elif any(palavra in pergunta_sem_acento for palavra in ["declaracao", "declaração", "comprovante"]):
            # Só pode criar declaração se tiver aluno_id
            if not self.aluno_id:
                return {"acao": "conversa", "resposta": "Para solicitar declarações, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}
            
            if any(palavra in pergunta_sem_acento for palavra in ["matricula", "matrícula"]):
                return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "declaracao", "kwargs": {"tipo_declaracao": "matricula"}}}
            elif any(palavra in pergunta_sem_acento for palavra in ["frequencia", "presenca", "presença"]):
                return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "declaracao", "kwargs": {"tipo_declaracao": "frequencia"}}}
            elif any(palavra in pergunta_sem_acento for palavra in ["conclusao", "conclusão", "formatura", "tcc"]):
                return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "declaracao", "kwargs": {"tipo_declaracao": "conclusao"}}}
            else:
                # Padrão geral de declaração
                return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "declaracao", "kwargs": {"tipo_declaracao": "matricula"}}}
        
        # SEGUNDA VIA DE BOLETO
        elif any(palavra in pergunta_sem_acento for palavra in ["segunda via", "2 via", "segunda_via"]) or \
             any(palavra in pergunta_lower for palavra in ["reemitir boleto", "emitirboletonov"]):
            # Só pode solicitar boleto se tiver aluno_id
            if not self.aluno_id:
                return {"acao": "conversa", "resposta": "Para solicitar segunda via de boleto, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}
            
            # Extrair valor se fornecido
            match = re.search(r'r?\$?\s*(\d+[.,]\d{2})', pergunta, re.IGNORECASE)
            valor = float(match.group(1).replace(',', '.')) if match else 850.00
            return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "boleto", "kwargs": {"valor": valor}}}
        
        # TRANCAMENTO DE SEMESTRE
        elif any(palavra in pergunta_sem_acento for palavra in ["trancar", "trancamento", "pausar"]):
            # Só pode trancar se tiver aluno_id
            if not self.aluno_id:
                return {"acao": "conversa", "resposta": "Para solicitar trancamento, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}
            
            if any(palavra in pergunta_sem_acento for palavra in ["materia", "disciplina"]):
                match = re.search(r'\b([A-Z]{3}-\d{3})\b', pergunta, re.IGNORECASE)
                if match:
                    return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "remocao_materia", "kwargs": {"codigo_materia": match.group(1).upper()}}}
            else:
                return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "trancamento", "kwargs": {"motivo": "Solicitação do aluno"}}}
        
        # DIPLOMA/CERTIFICADO
        elif any(palavra in pergunta_sem_acento for palavra in ["diploma", "certificado", "segunda via diploma"]):
            # Só pode solicitar diploma se tiver aluno_id
            if not self.aluno_id:
                return {"acao": "conversa", "resposta": "Para solicitar diploma ou certificado, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}
            
            return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "diploma", "kwargs": {}}}
        
        # TRANSFERÊNCIA
        elif any(palavra in pergunta_sem_acento for palavra in ["transferencia", "transferência", "mudar de curso"]):
            # Só pode solicitar transferência se tiver aluno_id
            if not self.aluno_id:
                return {"acao": "conversa", "resposta": "Para solicitar transferência, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}
            
            return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "transferencia", "kwargs": {"motivo": "Solicitação do aluno"}}}
        
        # ATUALIZAR ENDEREÇO
        elif any(palavra in pergunta_sem_acento for palavra in ["endereco", "endereço", "mudar endereco", "mudar endereço"]):
            # Só pode atualizar endereço se tiver aluno_id
            if not self.aluno_id:
                return {"acao": "conversa", "resposta": "Para atualizar endereço, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}
            
            return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "endereco", "kwargs": {}}}
        
        # ADICIONAR MATÉRIA - com várias palavras-chave
        elif any(palavra in pergunta_sem_acento for palavra in ["adicionar", "matricular", "inscrever", "quero uma materia", "preciso de uma materia", "registrar materia"]):
            # Só pode adicionar matéria se tiver aluno_id
            if not self.aluno_id:
                return {"acao": "conversa", "resposta": "Para adicionar matérias, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}
            
            # Tentar extrair código da matéria (ex: ALG-101)
            match = re.search(r'\b([A-Z]{3}-\d{3})\b', pergunta, re.IGNORECASE)
            if match:
                codigo = match.group(1).upper()
                return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "adicao_materia", "kwargs": {"codigo_materia": codigo}}}
            # Se não forneceu código, listar matérias disponíveis
            return {"acao": "ferramenta", "ferramenta": "listar_materias_disponiveis", "argumentos": {"aluno_id": self.aluno_id}}
        
        # MUDAR/TROCAR MATÉRIA
        elif any(palavra in pergunta_sem_acento for palavra in ["mudar", "trocar", "cambiar"]) and \
             any(palavra in pergunta_sem_acento for palavra in ["materia", "disciplina"]):
            # Só pode trocar matéria se tiver aluno_id
            if not self.aluno_id:
                return {"acao": "conversa", "resposta": "Para trocar de matéria, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}
            
            # Tentar extrair código
            matches = re.findall(r'\b([A-Z]{3}-\d{3})\b', pergunta, re.IGNORECASE)
            if len(matches) >= 2:
                # Usuário forneceu 2 códigos (remover e adicionar)
                return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "remocao_materia", "kwargs": {"codigo_materia": matches[0].upper()}}}
            elif len(matches) == 1:
                return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "adicao_materia", "kwargs": {"codigo_materia": matches[0].upper()}}}
            return {"acao": "conversa", "resposta": "Para trocar de matéria, qual é o código da matéria que deseja adicionar? (ex: ALG-101)"}
        
        # REMOVER/DELETAR MATÉRIA
        elif any(palavra in pergunta_sem_acento for palavra in ["remover", "deletar", "excluir"]) and \
             any(palavra in pergunta_sem_acento for palavra in ["materia", "disciplina"]):
            # Só pode remover matéria se tiver aluno_id
            if not self.aluno_id:
                return {"acao": "conversa", "resposta": "Para remover matérias, você precisa fazer login primeiro. Use o menu inicial e escolha a opção [1] Fazer login."}
            
            match = re.search(r'\b([A-Z]{3}-\d{3})\b', pergunta, re.IGNORECASE)
            if match:
                codigo = match.group(1).upper()
                return {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "remocao_materia", "kwargs": {"codigo_materia": codigo}}}
            return {"acao": "conversa", "resposta": "Para remover uma matéria, qual é o código dela? (ex: ALG-101)"}
        
        # AGRADECIMENTOS
        elif any(palavra in pergunta_lower for palavra in ["obrigado", "valeu", "agradeço", "brigadão", "obrigada"]):
            return {"acao": "conversa", "resposta": "Por nada! Estou aqui para ajudar com qualquer coisa relacionada à sua vida acadêmica. "}
        
        # SAUDAÇÕES
        elif any(palavra in pergunta_lower for palavra in ["oi", "olá", "bom dia", "boa tarde", "boa noite", "e ai"]):
            return {"acao": "conversa", "resposta": "Olá! Como posso ajudá-lo com sua vida acadêmica hoje?"}
        
        # FREQUÊNCIA
        elif any(palavra in pergunta_sem_acento for palavra in ["frequencia", "frequência"]):
            return {"acao": "ferramenta", "ferramenta": "perguntar_sobre_aluno", "argumentos": {"pergunta": "minha frequência"}}
        
        else:
            # Se chegou aqui, não é uma pergunta acadêmica reconhecida
            # Tentar responder como um assistente inteligente geral
            return self._resposta_contextualizada_geral(pergunta)
    
    def _mapear_necessidade_para_requerimento(self, pergunta):
        """
        Mapeia necessidades/interesses do aluno para requerimentos disponíveis.
        Detecta interesse em serviços como declarações, boletos, transferência, etc.
        Retorna (tipo_servico, confirmado, mensagem_sugestao)
        """
        pergunta_lower = pergunta.lower()
        pergunta_sem_acento = self._normalizar_texto(pergunta)
        
        # MAPEAMENTO GENÉRICO DE NECESSIDADES
        mapa_necessidades = {
            # DECLARAÇÕES
            "declaracao": {
                "triggers": ["preciso de declaracao", "quero declaracao", "gostaria de declaracao", "necessito declaracao",
                           "declaracao de", "comprovante de", "preciso comprovante"],
                "subtypes": {
                    "matricula": ["matricula", "matrícula", "inscrito"],
                    "frequencia": ["frequencia", "presença", "presenca"],
                    "conclusao": ["conclusao", "conclusão", "formatura", "tcc", "formado"]
                },
                "mensagem_padrao": "Posso gerar uma declaração para você. Qual tipo você precisa?",
                "requerimento": "declaracao"
            },
            # BOLETO
            "boleto": {
                "triggers": ["boleto", "segunda via", "reemitir", "2 via", "boleto novo", "nova emissao"],
                "subtypes": {},
                "mensagem_padrao": "Você gostaria de solicitar segunda via do boleto?",
                "requerimento": "boleto"
            },
            # TRANSFERÊNCIA
            "transferencia": {
                "triggers": ["transferencia", "transferência", "mudar de curso", "trocar curso", "sair deste curso"],
                "subtypes": {
                    "interna": ["interna", "interno"],
                    "externa": ["externa", "externo", "outra instituicao"]
                },
                "mensagem_padrao": "Você gostaria de fazer uma transferência? Pode ser interna ou externa.",
                "requerimento": "transferencia"
            },
            # TRANCAMENTO
            "trancamento": {
                "triggers": ["trancar", "trancamento", "pausar", "parar", "dar um tempo"],
                "subtypes": {},
                "mensagem_padrao": "Você gostaria de trancar o semestre?",
                "requerimento": "trancamento"
            },
            # DIPLOMA
            "diploma": {
                "triggers": ["diploma", "segunda via diploma", "2 via diploma", "solicitar diploma"],
                "subtypes": {},
                "mensagem_padrao": "Você gostaria de solicitar segunda via do diploma?",
                "requerimento": "diploma"
            },
            # ENDEREÇO
            "endereco": {
                "triggers": ["endereco", "endereço", "mudar endereco", "mudar endereço", "atualizar dados"],
                "subtypes": {},
                "mensagem_padrao": "Você gostaria de atualizar seu endereço?",
                "requerimento": "endereco"
            },
            # CERTIFICADO
            "certificado": {
                "triggers": ["certificado", "certificacao", "certificação"],
                "subtypes": {},
                "mensagem_padrao": "Você gostaria de solicitar um certificado?",
                "requerimento": "certificado"
            },
            # CADASTRO / MATRÍCULA (NOVO ALUNO)
            "cadastro": {
                "triggers": ["quero me cadastrar", "fazer matricula", "fazer matrícula", "me inscrever", 
                           "quero estudar", "iniciar curso", "ser aluno", "entrar na faculdade",
                           "ingressar", "fazer inscricao", "nova matricula", "primeiro acesso",
                           "sou novo", "quero me matricular"],
                "subtypes": {},
                "mensagem_padrao": "Você gostaria de fazer matrícula como novo aluno?",
                "requerimento": "cadastro"
            }
        }
        
        # Verificar cada necessidade
        for tipo_servico, config in mapa_necessidades.items():
            # Verificar triggers
            tem_trigger = any(trigger in pergunta_sem_acento for trigger in config["triggers"])
            
            if tem_trigger:
                return {
                    "tipo": tipo_servico,
                    "config": config,
                    "subtipo": self._detectar_subtipo(pergunta_sem_acento, config.get("subtypes", {}))
                }
        
        return None
    
    def _detectar_subtipo(self, pergunta_sem_acento, subtypes):
        """Detecta subtipo da necessidade (ex: matrícula, frequência para declaração)"""
        for subtipo, triggers in subtypes.items():
            if any(trigger in pergunta_sem_acento for trigger in triggers):
                return subtipo
        return None
    
    def _processar_necessidade_aluno(self, pergunta):
        """
        Processa quando o aluno demonstra necessidade em um serviço.
        Oferece executar o serviço e pede confirmação.
        """
        resultado = self._mapear_necessidade_para_requerimento(pergunta)
        
        if not resultado:
            return None
        
        tipo_servico = resultado["tipo"]
        config = resultado["config"]
        subtipo = resultado["subtipo"]
        
        # Se for cadastro, iniciar fluxo de coleta de dados especial
        if tipo_servico == "cadastro":
            return self._iniciar_coleta_dados_cadastro()
        
        mensagem_resposta = config["mensagem_padrao"]
        
        # Construir requerimento
        requerimento_args = {"tipo": config["requerimento"]}
        
        # Adicionar kwargs se houver subtipo
        if subtipo:
            if tipo_servico == "declaracao":
                requerimento_args["kwargs"] = {"tipo_declaracao": subtipo}
                mensagem_resposta = f"Vou gerar uma declaração de {subtipo} para você. Confirme: Sim ou Não?"
            elif tipo_servico == "transferencia":
                requerimento_args["kwargs"] = {"tipo_transferencia": subtipo, "motivo": "Solicitação do aluno"}
                mensagem_resposta = f"Você gostaria de fazer uma transferência {subtipo}? Confirme: Sim ou Não?"
            else:
                requerimento_args["kwargs"] = {}
        else:
            requerimento_args["kwargs"] = {}
        
        # Criar ação pendente para confirmar
        self.acao_pendente = {
            "tipo": "servico_interesse",
            "servico": tipo_servico,
            "subtipo": subtipo,
            "pergunta_original": pergunta,
            "decisao": {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": requerimento_args}
        }
        
        return {"acao": "conversa", "resposta": f"{mensagem_resposta}\n\nResponda: Sim ou Não"}
    
    def _iniciar_coleta_dados_cadastro(self):
        """
        Inicia o processo de coleta de dados para cadastro de novo aluno.
        Retorna uma estrutura com os campos necessários e ordem de coleta.
        """
        self.dados_cadastro = {
            "etapa_atual": "confirmacao",
            "campos_coletados": {},
            "campos_necessarios": [
                {"nome": "nome_completo", "pergunta": "Qual é o seu nome completo?", "validacao": "texto"},
                {"nome": "cpf", "pergunta": "Qual é o seu CPF? (somente números ou com formatação)", "validacao": "cpf"},
                {"nome": "data_nascimento", "pergunta": "Qual é a sua data de nascimento? (DD/MM/AAAA)", "validacao": "data"},
                {"nome": "email", "pergunta": "Qual é o seu email?", "validacao": "email"},
                {"nome": "telefone", "pergunta": "Qual é o seu telefone? (opcional, pode responder 'pular')", "validacao": "telefone", "opcional": True},
                {"nome": "cidade", "pergunta": "Em qual cidade você mora? (opcional)", "validacao": "texto", "opcional": True},
                {"nome": "estado", "pergunta": "Qual é o seu estado? (sigla com 2 letras, opcional)", "validacao": "estado", "opcional": True},
                {"nome": "senha", "pergunta": "Defina uma senha para acessar o portal (mínimo 4 caracteres):", "validacao": "senha"},
                {"nome": "curso", "pergunta": " **Deseja se matricular em algum curso agora?**\n(Digite o código do curso como 'BCC', 'ENGC', etc. ou 'não' para pular)", "validacao": "texto", "opcional": True}
            ],
            "indice_atual": 0
        }
        
        mensagem = """ **Cadastro de Novo Aluno**

Ótimo! Vou te ajudar a fazer seu cadastro.
Vou te fazer algumas perguntas para coletar suas informações.

Você confirma que deseja iniciar o cadastro?
Responda: Sim ou Não"""
        
        return {"acao": "conversa", "resposta": mensagem}
    
    def _processar_resposta_cadastro(self, resposta):
        """
        Processa a resposta do usuário durante a coleta de dados de cadastro.
        Valida e armazena os dados coletados.
        """
        if not self.dados_cadastro:
            return None
        
        etapa = self.dados_cadastro["etapa_atual"]
        
        # Etapa de confirmação inicial
        if etapa == "confirmacao":
            if self._confirmar_acao_pendente(resposta):
                self.dados_cadastro["etapa_atual"] = "coletando"
                return self._proxima_pergunta_cadastro()
            elif self._negar_acao_pendente(resposta):
                self.dados_cadastro = None
                return {"acao": "conversa", "resposta": "Tudo bem! Se mudar de ideia, é só me avisar. "}
            else:
                return {"acao": "conversa", "resposta": "Não entendi. Você deseja fazer o cadastro? Responda Sim ou Não."}
        
        # Etapa de coleta de dados
        elif etapa == "coletando":
            indice = self.dados_cadastro["indice_atual"]
            campos = self.dados_cadastro["campos_necessarios"]
            
            if indice >= len(campos):
                # Todos os dados coletados - executar cadastro
                return self._finalizar_cadastro()
            
            campo_atual = campos[indice]
            nome_campo = campo_atual["nome"]
            validacao = campo_atual["validacao"]
            opcional = campo_atual.get("opcional", False)
            
            # Permitir pular campos opcionais
            if opcional and resposta.lower().strip() in ["pular", "nao", "não", "skip", "-", "sem curso", "sem"]:
                self.dados_cadastro["indice_atual"] += 1
                return self._proxima_pergunta_cadastro()
            
            # Validar resposta
            valor_validado, mensagem_erro = self._validar_campo_cadastro(nome_campo, resposta, validacao)
            
            if valor_validado is not None:
                # Valor válido - armazenar e ir para próximo campo
                self.dados_cadastro["campos_coletados"][nome_campo] = valor_validado
                self.dados_cadastro["indice_atual"] += 1
                return self._proxima_pergunta_cadastro()
            else:
                # Valor inválido - pedir novamente
                return {"acao": "conversa", "resposta": f" {mensagem_erro}\n\n{campo_atual['pergunta']}"}
        
        return None
    
    def _proxima_pergunta_cadastro(self):
        """Retorna a próxima pergunta para coletar dados de cadastro"""
        indice = self.dados_cadastro["indice_atual"]
        campos = self.dados_cadastro["campos_necessarios"]
        
        if indice >= len(campos):
            return self._finalizar_cadastro()
        
        campo = campos[indice]
        opcional_texto = " (opcional)" if campo.get("opcional") else ""
        
        mensagem = f" **Campo {indice + 1}/{len(campos)}**{opcional_texto}\n\n{campo['pergunta']}"
        
        return {"acao": "conversa", "resposta": mensagem}
    
    def _validar_campo_cadastro(self, nome_campo, valor, tipo_validacao):
        """
        Valida um campo do cadastro.
        Retorna (valor_validado, mensagem_erro)
        """
        valor = valor.strip()
        
        if tipo_validacao == "texto":
            if len(valor) < 2:
                return None, "Por favor, forneça um valor válido."
            return valor, None
        
        elif tipo_validacao == "cpf":
            # Remover formatação
            cpf_limpo = re.sub(r'[^0-9]', '', valor)
            if len(cpf_limpo) != 11:
                return None, "CPF deve ter 11 dígitos. Ex: 123.456.789-01 ou 12345678901"
            # Formatar CPF
            cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
            return cpf_formatado, None
        
        elif tipo_validacao == "data":
            # Aceitar DD/MM/AAAA ou DD/MM/AA
            match = re.match(r'(\d{2})/(\d{2})/(\d{2,4})', valor)
            if not match:
                return None, "Data deve estar no formato DD/MM/AAAA. Ex: 15/03/2000"
            dia, mes, ano = match.groups()
            # Converter ano de 2 dígitos
            if len(ano) == 2:
                ano = "19" + ano if int(ano) > 50 else "20" + ano
            # Validar data
            try:
                from datetime import datetime
                data = datetime.strptime(f"{dia}/{mes}/{ano}", "%d/%m/%Y")
                # Retornar no formato aceito pela API
                return data.strftime("%Y-%m-%d"), None
            except:
                return None, "Data inválida. Use o formato DD/MM/AAAA."
        
        elif tipo_validacao == "email":
            if "@" not in valor or "." not in valor.split("@")[1]:
                return None, "Email inválido. Ex: seu.nome@email.com"
            return valor.lower(), None
        
        elif tipo_validacao == "telefone":
            # Aceitar vários formatos
            telefone_limpo = re.sub(r'[^0-9]', '', valor)
            if len(telefone_limpo) < 10:
                return None, "Telefone deve ter pelo menos 10 dígitos. Ex: (11) 98765-4321"
            return valor, None
        
        elif tipo_validacao == "estado":
            estado_upper = valor.upper()
            if len(estado_upper) != 2:
                return None, "Estado deve ser a sigla com 2 letras. Ex: SP, RJ, MG"
            return estado_upper, None
        
        elif tipo_validacao == "senha":
            if len(valor) < 4:
                return None, "Senha deve ter no mínimo 4 caracteres."
            return valor, None
        
        return valor, None
    
    def _finalizar_cadastro(self):
        """Executa o cadastro do aluno com os dados coletados"""
        dados = self.dados_cadastro["campos_coletados"]
        
        # Preparar argumentos para a ferramenta
        args = {
            "nome_completo": dados.get("nome_completo"),
            "cpf": dados.get("cpf"),
            "data_nascimento": dados.get("data_nascimento"),
            "email": dados.get("email"),
            "senha": dados.get("senha", "senha123")
        }
        
        # Adicionar campos opcionais se fornecidos
        if "telefone" in dados:
            args["telefone"] = dados["telefone"]
        if "cidade" in dados:
            args["cidade"] = dados["cidade"]
        if "estado" in dados:
            args["estado"] = dados["estado"]
        if "curso" in dados and dados["curso"].lower() not in ["nao", "não", "skip", "-"]:
            args["curso_codigo"] = dados["curso"]
        
        # Chamar ferramenta MCP para cadastrar
        resposta = self.chamar_ferramenta("cadastrar_novo_aluno", args)
        
        # Limpar dados de cadastro
        self.dados_cadastro = None
        
        return {"acao": "conversa", "resposta": resposta}
    
    def _detectar_interesse_em_materia(self, pergunta):
        """
        Detecta quando o aluno demonstra interesse em uma matéria.
        Retorna (tem_interesse, nome_materia, codigo_materia)
        """
        pergunta_lower = pergunta.lower()
        pergunta_sem_acento = self._normalizar_texto(pergunta)
        
        # Palavras que indicam interesse/gosto
        palavras_interesse = ["gosto", "adorei", "amei", "legal", "legal demais", "interessante", 
                             "fascinante", "incrivel", "incrível", "excelente", "adoravel", "amor"]
        
        tem_interesse = any(palavra in pergunta_sem_acento for palavra in palavras_interesse)
        
        if not tem_interesse:
            return None, None, None
        
        # Palavras que indicam que estamos falando de disciplina
        tem_materia = any(palavra in pergunta_sem_acento for palavra in ["materia", "disciplina", "cadeira", "curso", "de"])
        
        if not tem_materia:
            return None, None, None
        
        # Tentar extrair código da matéria (ex: ALG-101)
        match_codigo = re.search(r'\b([A-Z]{3}-\d{3})\b', pergunta, re.IGNORECASE)
        if match_codigo:
            codigo = match_codigo.group(1).upper()
            return True, codigo, codigo
        
        # Tentar extrair nome da matéria
        # Procurar padrão: "gosto de [materia]", "adorei [materia]", etc
        padrao_interesse = r'(?:gosto|adorei|amei|legal|interessante|fascinante|incrivel|excelente|adoravel)(?:\s+(?:de|da|do))?\s+(.+?)(?:$|[,.])'
        match_nome = re.search(padrao_interesse, pergunta_lower)
        
        if match_nome:
            nome_completo = match_nome.group(1).strip()
            # Limpar a string
            nome_completo = re.sub(r'\s+', ' ', nome_completo)
            return True, nome_completo, None
        
        return None, None, None
    
    def _verificar_aluno_cursando_materia(self, codigo_materia):
        """
        Verifica no backend se o aluno está cursando a matéria.
        Retorna (esta_cursando, informacoes)
        """
        if not self.aluno_id or not codigo_materia:
            return None, None
        
        try:
            # Tentar consultar matérias do aluno
            resposta = self.chamar_ferramenta("perguntar_sobre_aluno", {
                "aluno_id": self.aluno_id,
                "pergunta": f"estou cursando {codigo_materia}"
            })
            
            resposta_str = str(resposta).lower()
            
            # Verificar se está cursando
            se_cursando = "sim" in resposta_str and "cursando" in resposta_str
            se_nao_cursando = ("nao" in resposta_str or "não" in resposta_str) and "cursando" in resposta_str
            
            if se_cursando:
                return True, resposta
            elif se_nao_cursando:
                return False, resposta
            else:
                # Resposta não conclusiva
                return None, resposta
        except Exception as e:
            return None, str(e)
    
    def _processar_interesse_em_materia(self, pergunta):
        """
        Processa quando aluno demonstra interesse em uma matéria.
        Se tiver código, verifica se está cursando e oferece adicionar.
        Se não tiver código, pede especificação.
        """
        tem_interesse, nome_materia, codigo_materia = self._detectar_interesse_em_materia(pergunta)
        
        if not tem_interesse:
            return None
        
        # Se não tem código, pedir especificação
        if not codigo_materia:
            resposta = f"Que legal você se interessar por {nome_materia}! \n\n"
            resposta += "Para adicionar à sua grade, preciso do código da disciplina (ex: ALG-101, MAT-102).\n\n"
            resposta += "Qual é o código exato da matéria?"
            return {"acao": "conversa", "resposta": resposta}
        
        # Tem código - verificar se aluno está cursando
        esta_cursando, info = self._verificar_aluno_cursando_materia(codigo_materia)
        
        if esta_cursando is True:
            # Aluno já está cursando
            resposta = f"Que legal!  Você já está cursando {codigo_materia}.\n\n"
            resposta += "Espero que esteja aproveitando bem a disciplina!"
            return {"acao": "conversa", "resposta": resposta}
        
        elif esta_cursando is False:
            # Aluno NÃO está cursando - oferecer adicionar
            resposta = f"Que legal você se interessar por {codigo_materia}! \n\n"
            resposta += f"Você não está cursando essa disciplina no momento. Gostaria de adicionar {codigo_materia} à sua grade de disciplinas?\n\n"
            resposta += "Confirme: Sim ou Não?"
            
            # Guardar ação pendente para adicionar matéria
            self.acao_pendente = {
                "tipo": "adicionar_materia_interesse",
                "materia": codigo_materia,
                "pergunta_original": pergunta,
                "decisao": {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "adicao_materia", "kwargs": {"codigo_materia": codigo_materia}}}
            }
            
            return {"acao": "conversa", "resposta": resposta}
        
        else:
            # Não conseguiu verificar
            resposta = f"Que legal você se interessar por {codigo_materia}! \n\n"
            resposta += "Gostaria de adicionar essa disciplina à sua grade?\n"
            resposta += "Responda: Sim ou Não"
            
            # Guardar ação pendente
            self.acao_pendente = {
                "tipo": "adicionar_materia_interesse",
                "materia": codigo_materia,
                "pergunta_original": pergunta,
                "decisao": {"acao": "ferramenta", "ferramenta": "criar_requerimento", "argumentos": {"tipo": "adicao_materia", "kwargs": {"codigo_materia": codigo_materia}}}
            }
            
            return {"acao": "conversa", "resposta": resposta}
    
    def _resposta_contextualizada_geral(self, pergunta):
        """
        Responde a perguntas gerais (não acadêmicas) de forma inteligente.
        Ao invés de dizer que não entendeu, tenta responder como um assistente conversacional.
        """
        pergunta_lower = pergunta.lower()
        pergunta_sem_acento = self._normalizar_texto(pergunta)
        
        # Mapeamento de palavras-chave para respostas inteligentes
        # SAUDAÇÕES E PERGUNTAS DE BEM-ESTAR
        if any(palavra in pergunta_lower for palavra in ["como vai", "como você está", "tudo bem", "e aí"]):
            if "como vai" in pergunta_lower or "como está" in pergunta_lower:
                return {"acao": "conversa", "resposta": "Estou ótimo, obrigado por perguntar!  E você, como está? Posso ajudá-lo em algo?"}
            elif "tudo bem" in pergunta_lower:
                return {"acao": "conversa", "resposta": "Tudo certo! E com você? Como posso ajudá-lo?"}
            else:
                return {"acao": "conversa", "resposta": "Tudo bem sim! Pronto para ajudar você. O que você precisa?"}
        
        # AGRADECIMENTOS
        elif any(palavra in pergunta_lower for palavra in ["obrigado", "vlw", "valeu", "brigadão", "brigado", "muito obrigado"]):
            respostas = [
                "De nada! Estou sempre aqui para ajudar. ",
                "Por nada! Se precisar novamente, é só chamar!",
                "Fico feliz em ajudar! Há mais algo que eu possa fazer?"
            ]
            return {"acao": "conversa", "resposta": secrets.choice(respostas)}
        
        # DESPEDIDAS
        elif any(palavra in pergunta_lower for palavra in ["tchau", "até logo", "adeus", "até mais", "falou"]):
            return {"acao": "conversa", "resposta": "Até logo! Volte sempre que precisar de ajuda! "}
        
        # ELOGIOS
        elif any(palavra in pergunta_lower for palavra in ["obrigado", "você é legal", "você é bom", "gosto", "adorei", "perfeito", "excelente"]):
            if any(palavra in pergunta_lower for palavra in ["você", "agente", "assistente"]):
                return {"acao": "conversa", "resposta": "Obrigado! Fico feliz em ajudar. Meu objetivo é tornar sua vida acadêmica mais fácil e confortável! "}
        
        # PERGUNTAS SOBRE O AGENTE
        if any(palavra in pergunta_sem_acento for palavra in ["quem", "o que"] + ["voce", "você"]) and \
           any(palavra in pergunta_lower for palavra in ["quem é", "o que é", "quem é você"]):
            return {"acao": "conversa", "resposta": "Sou um assistente de IA inteligente da faculdade! Estou aqui para ajudar você com tudo relacionado à sua vida acadêmica: requerimentos, matérias, notas, boletos, declarações, e muito mais. Além disso, posso conversar sobre outros assuntos também! "}
        
        # PERGUNTAS SOBRE HORÁRIOS E DATAS
        if any(palavra in pergunta_sem_acento for palavra in ["horas", "hora", "que horas", "qual hora", "que dia"]):
            import datetime
            agora = datetime.datetime.now()
            hora_formatada = agora.strftime("%H:%M")
            data_formatada = agora.strftime("%d/%m/%Y")
            return {"acao": "conversa", "resposta": f"Agora são {hora_formatada} em {data_formatada}. "}
        
        # PERGUNTAS SOBRE ASSUNTOS VÁRIOS
        if "piada" in pergunta_lower or "piadas" in pergunta_lower:
            piadas = [
                "Por que o livro de matemática se suicidou? Porque tinha muitos problemas! ",
                "O que o 0 (zero) falou para o 8 (oito)? Que cinto legal! ",
                "Qual é a comida favorita do programador? Array (aletria)! ",
            ]
            return {"acao": "conversa", "resposta": secrets.choice(piadas)}
        
        # CÁLCULOS SIMPLES
        if "quanto é" in pergunta_lower or "calcular" in pergunta_lower or "calcula" in pergunta_lower:
            import re
            # Tenta encontrar uma operação matemática simples
            match = re.search(r'(\d+)\s*[\+\-\*\/]\s*(\d+)', pergunta)
            if match:
                operacao = pergunta[match.start():match.end()]
                resultado = _safe_eval_math(operacao)
                if resultado is not None:
                    return {"acao": "conversa", "resposta": f"Deixe-me calcular: {operacao} = {resultado}"}
        
        # TÓPICOS INTERESSANTES QUE AGENTE PODE COMENTAR
        topicos_interessantes = {
            "python": "Python é uma linguagem de programação muito popular! É usada em ciência de dados, web, automação e muito mais. Você está estudando programação?",
            "inteligencia artificial": "Inteligência Artificial é fascinante! Estou usando um modelo de IA para conversar com você agora. É incrível como a tecnologia evolui!",
            "tecnologia": "A tecnologia é o futuro! Estamos vivendo em uma era de inovação constante. Que área da tecnologia você mais se interessa?",
            "estudos": "Dedicação aos estudos é fundamental! Se você tiver alguma dúvida sobre a faculdade, estou aqui para ajudar.",
            "trabalho": "Trabalhar e estudar ao mesmo tempo é desafiador, mas possível! Se precisar de ajuda para gerenciar seus prazos, posso tentar ajudar.",
        }
        
        for topico, resposta in topicos_interessantes.items():
            if topico in pergunta_sem_acento:
                return {"acao": "conversa", "resposta": resposta}
        
        # RESPOSTA GENÉRICA INTELIGENTE PARA PERGUNTAS DESCONHECIDAS
        # Usar uma estratégia de resposta contextualizada
        resposta_generica = self._gerar_resposta_generica(pergunta)
        return {"acao": "conversa", "resposta": resposta_generica}
    
    def _gerar_resposta_generica(self, pergunta):
        """
        Gera uma resposta genérica mas contextualizada para perguntas desconhecidas.
        Tenta usar o LLM se disponível, senão usa heurísticas.
        """
        # Tenta consultar o LLM para responder perguntas gerais
        if USE_OLLAMA:
            resposta_llm = self._consultar_llm_para_pergunta_geral(pergunta)
            if resposta_llm:
                return resposta_llm
        
        # Fallback: estratégias de resposta baseada no tipo de pergunta
        if "?" in pergunta:
            # É uma pergunta
            palavras_chave = pergunta.lower().split()
            
            # Detectar categoria de pergunta
            if any(p in palavras_chave for p in ["como", "qual", "onde", "quando", "por que"]):
                respostas = [
                    f"Que pergunta interessante!  Infelizmente não tenho a resposta específica para isso, mas posso te ajudar. Você quer saber mais sobre algo acadêmico?",
                    f"Ótima pergunta!  Essa é uma área que requer mais pesquisa. Se for relacionado a seus estudos, posso ajudar!",
                    f"Muito bom você estar curioso!  Se for sobre assuntos acadêmicos, posso definitivamente ajudar!",
                ]
            else:
                respostas = [
                    f"Entendi sua pergunta!  Posso não ter a resposta exata agora, mas estou aprendendo constantemente.",
                    f"Hmm, interessante!  Se for sobre seus estudos ou a faculdade, tenho mais recursos para ajudar!",
                ]
        else:
            # É uma afirmação
            respostas = [
                f"Entendi!  Obrigado por compartilhar isso comigo. Há algo em que eu possa ajudá-lo?",
                f"Que legal!  É bom saber disso. Como posso te ajudar hoje?",
                f"Certo! Estou aqui para ajudá-lo no que precisar.",
            ]
        
        return secrets.choice(respostas)
    
    def _consultar_llm_para_pergunta_geral(self, pergunta):
        """
        Consulta o LLM especificamente para responder perguntas gerais (não acadêmicas)
        """
        system_prompt = """Você é um assistente de IA inteligente e amigável. Responda perguntas com clareza, bom humor quando apropriado, e sempre sendo útil.
        
Regras:
1. Responda de forma natural e conversacional
2. Use emojis quando apropriado para tornar a resposta mais amigável
3. Seja conciso mas completo
4. Se não souber a resposta exata, admita e tente ser helpful mesmo assim
5. Sempre mantenha um tom amigável e prestativo"""
        
        if USE_OLLAMA:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": f"{system_prompt}\n\nPergunta: {pergunta}\n\nResposta:",
                "stream": False,
                "temperature": 0.5  # Mais criatividade para perguntas gerais
            }
            
            try:
                response = requests.post(OLLAMA_URL, json=payload, timeout=20)
                
                if response.status_code == 200:
                    texto = response.json().get("response", "").strip()
                    if texto:
                        return texto
            except requests.exceptions.RequestException as exc:
                logger.debug("Falha ao consultar LLM: %s", exc)
        
        return None
    def _detectar_oportunidades(self, pergunta):
        """
        Detecta oportunidades de ações/sugestões baseado na pergunta do aluno.
        Oferece próximos passos relevantes para melhorar a experiência do aluno.
        """
        pergunta_lower = pergunta.lower()
        pergunta_sem_acento = self._normalizar_texto(pergunta)
        oportunidades = []
        
        # OPORTUNIDADES COM MATÉRIAS
        if any(palavra in pergunta_sem_acento for palavra in ["materia", "disciplina", "cadeira", "aula", "professor"]):
            if any(palavra in pergunta_sem_acento for palavra in ["dificil", "difícil", "complicado", "nao entendo", "não entendi", "perdido"]):
                oportunidades.append({
                    "tipo": "suporte",
                    "titulo": "Dificuldade nas Aulas",
                    "sugestoes": [
                        " Quer mudar para outra matéria com menos dificuldade?",
                        " Posso ajudar a consultar suas matérias atuais",
                        " Considere conversar com o monitor da disciplina"
                    ]
                })
            
            if any(palavra in pergunta_sem_acento for palavra in ["gosto", "legal", "adorei", "perfeito", "bom"]):
                oportunidades.append({
                    "tipo": "aprendizado",
                    "titulo": "Excelente Progresso!",
                    "sugestoes": [
                        " Quer adicionar matérias optativas relacionadas?",
                        " Posso listar cursos complementares",
                        " Veja seu resumo acadêmico para planejamento"
                    ]
                })
        
        # OPORTUNIDADES COM BOLETO/PAGAMENTO
        if any(palavra in pergunta_sem_acento for palavra in ["boleto", "pagamento", "mensalidade", "financeiro", "dinheiro", "valor"]):
            if "problema" in pergunta_sem_acento or "atraso" in pergunta_sem_acento or "nao posso" in pergunta_sem_acento:
                oportunidades.append({
                    "tipo": "financeiro_critico",
                    "titulo": "Situação Financeira",
                    "sugestoes": [
                        " Consulte sua situação de boletos",
                        " Você pode solicitar segunda via do boleto",
                        " Converse com o setor financeiro sobre opções de pagamento"
                    ]
                })
            else:
                oportunidades.append({
                    "tipo": "financeiro",
                    "titulo": "Informações Financeiras",
                    "sugestoes": [
                        " Quer solicitar segunda via do boleto?",
                        " Consulte seus boletos pendentes",
                        " Verifique sua situação financeira"
                    ]
                })
        
        # OPORTUNIDADES COM NOTAS/DESEMPENHO
        if any(palavra in pergunta_sem_acento for palavra in ["nota", "nota", "desempenho", "resultado", "prova"]):
            if any(palavra in pergunta_sem_acento for palavra in ["baixa", "ruim", "problema", "nao passou", "reprovei", "falha"]):
                oportunidades.append({
                    "tipo": "academico_alerta",
                    "titulo": "Atenção ao Desempenho",
                    "sugestoes": [
                        " Verifique o seu histórico acadêmico completo",
                        " Considere reforço em matérias críticas",
                        " Converse com um orientador"
                    ]
                })
            elif any(palavra in pergunta_sem_acento for palavra in ["boa", "bom", "legal", "excelente", "ótimo"]):
                oportunidades.append({
                    "tipo": "academico_positivo",
                    "titulo": "Excelente Desempenho!",
                    "sugestoes": [
                        " Parabéns pelo bom desempenho!",
                        " Considere desafios acadêmicos adicionais",
                        " Mantenha o ritmo e vise o melhor"
                    ]
                })
        
        # OPORTUNIDADES COM FREQUÊNCIA
        if any(palavra in pergunta_sem_acento for palavra in ["frequencia", "presença", "presenca", "falta", "ausencia", "ausência"]):
            if any(palavra in pergunta_sem_acento for palavra in ["baixa", "problema", "ruim", "muita"]):
                oportunidades.append({
                    "tipo": "frequencia_alerta",
                    "titulo": "Frequência Baixa",
                    "sugestoes": [
                        " Verifique sua frequência atual",
                        " Solicite declaração de frequência se necessário",
                        " Converse com a coordenação sobre ausências justificadas"
                    ]
                })
        
        # OPORTUNIDADES COM CURSOS
        if any(palavra in pergunta_sem_acento for palavra in ["curso", "cursos", "programas", "especialização"]):
            oportunidades.append({
                "tipo": "explorar",
                "titulo": "Explorar Oportunidades",
                "sugestoes": [
                    " Consulte todos os cursos disponíveis",
                    " Veja pré-requisitos de cada disciplina",
                    " Considere mudar de curso se interessado"
                ]
            })
        
        # OPORTUNIDADES COM DIPLOMA/CERTIFICADO
        if any(palavra in pergunta_sem_acento for palavra in ["diploma", "certificado", "formatura", "conclusao"]):
            oportunidades.append({
                "tipo": "conclusao",
                "titulo": "Finalização de Estudos",
                "sugestoes": [
                    " Solicite segunda via de diploma se necessário",
                    " Verifique status da sua conclusão",
                    " Consulte o resumo acadêmico completo"
                ]
            })
        
        # OPORTUNIDADES COM TRANSFERÊNCIA
        if any(palavra in pergunta_sem_acento for palavra in ["transferencia", "transferência", "mudar", "sair"]):
            oportunidades.append({
                "tipo": "transferencia",
                "titulo": "Mudança de Curso",
                "sugestoes": [
                    " Solicite transferência interna ou externa",
                    " Converse sobre seus objetivos acadêmicos",
                    " Veja opções de outros cursos"
                ]
            })
        
        # OPORTUNIDADES COM TRANCAMENTO
        if any(palavra in pergunta_sem_acento for palavra in ["trancar", "trancamento", "pausar", "parar", "sair"]):
            if "temporario" in pergunta_sem_acento or "temporária" in pergunta_sem_acento:
                oportunidades.append({
                    "tipo": "trancamento_temp",
                    "titulo": "Pausa nos Estudos",
                    "sugestoes": [
                        "⏸ Solicite trancamento de semestre",
                        " Você pode voltar após resolver seus problemas",
                        " Converse com a coordenação sobre opções"
                    ]
                })
        
        # OPORTUNIDADES COM ENDEREÇO/DADOS
        if any(palavra in pergunta_sem_acento for palavra in ["endereco", "endereço", "dados", "informacao", "informação", "mudar", "atualizar"]):
            oportunidades.append({
                "tipo": "dados",
                "titulo": "Manter Dados Atualizados",
                "sugestoes": [
                    " Atualize seu endereço se mudou",
                    " Mantenha seus dados pessoais em dia",
                    " Solicite atualização de cadastro se necessário"
                ]
            })
        
        # OPORTUNIDADES COM REQUERIMENTOS GERAIS
        if any(palavra in pergunta_sem_acento for palavra in ["requerimento", "solicitacao", "solicitar", "pedir"]):
            oportunidades.append({
                "tipo": "administrativo",
                "titulo": "Requerimentos Disponíveis",
                "sugestoes": [
                    " Posso ajudar com diversos tipos de requerimentos",
                    " Especifique o que você precisa",
                    " Requerimentos processados rapidamente"
                ]
            })
        
        # OPORTUNIDADES COM DIFICULDADES GERAIS NA FACULDADE
        if any(palavra in pergunta_sem_acento for palavra in ["problema", "dificuldade", "duvida", "dúvida", "ajuda", "help", "nao sei"]):
            if "estudar" in pergunta_sem_acento or "aprender" in pergunta_sem_acento or "entender" in pergunta_sem_acento:
                oportunidades.append({
                    "tipo": "suporte_academico",
                    "titulo": "Apoio Acadêmico",
                    "sugestoes": [
                        " Consulte suas matérias atuais",
                        " Considere reforço ou monitoria",
                        " Converse com um orientador"
                    ]
                })
        
        # OPORTUNIDADES COM STRESS/CANSAÇO/BEM-ESTAR
        if any(palavra in pergunta_sem_acento for palavra in ["cansado", "estressado", "estressada", "cansaco", "cansaço", "pressao", "pressão", "sobrecarregado"]):
            oportunidades.append({
                "tipo": "bem_estar",
                "titulo": "Seu Bem-Estar Acadêmico",
                "sugestoes": [
                    " Seu bem-estar é importante!",
                    "⏸ Considere trancar semestre se necessário",
                    " Fale com a coordenação de alunos"
                ]
            })
        
        # OPORTUNIDADES COM PLANEJAMENTO/FUTURO
        if any(palavra in pergunta_sem_acento for palavra in ["plano", "planejamento", "futuro", "carreira", "depois", "proximos passos", "próximos"]):
            oportunidades.append({
                "tipo": "planejamento",
                "titulo": "Planejamento Acadêmico",
                "sugestoes": [
                    " Veja cursos disponíveis para aprimoramento",
                    " Consulte matérias optativas e eletivas",
                    " Considere especialização ou extensão"
                ]
            })
        
        # OPORTUNIDADES COM BOLSA/AUXÍLIO
        if any(palavra in pergunta_sem_acento for palavra in ["bolsa", "auxilio", "auxílio", "financiamento", "financeiro"]):
            oportunidades.append({
                "tipo": "financeiro_bolsa",
                "titulo": "Oportunidades Financeiras",
                "sugestoes": [
                    " Consulte bolsas e auxílios disponíveis",
                    " Veja sua situação de pagamentos",
                    " Converse com o financeiro sobre opções"
                ]
            })
        
        # OPORTUNIDADES COM COMPARECIMENTO/PARTICIPAÇÃO
        if any(palavra in pergunta_sem_acento for palavra in ["evento", "palestra", "workshop", "semana academica", "congresso", "atividade"]):
            oportunidades.append({
                "tipo": "participacao",
                "titulo": "Eventos e Atividades",
                "sugestoes": [
                    " Participe de eventos da instituição",
                    " Amplie seu conhecimento com palestras",
                    " Conheça outros alunos e profissionais"
                ]
            })
        
        # OPORTUNIDADES COM RENOVAÇÃO/CONTINUIDADE
        if any(palavra in pergunta_sem_acento for palavra in ["continuar", "renovar", "próximo semestre", "proximo", "semestre que vem"]):
            oportunidades.append({
                "tipo": "continuidade",
                "titulo": "Continuação dos Estudos",
                "sugestoes": [
                    " Planeje disciplinas para o próximo período",
                    " Revise matérias e prepare-se antecipadamente",
                    " Defina seus objetivos para o próximo semestre"
                ]
            })
        
        # OPORTUNIDADES COM DÚVIDAS ADMINISTRATIVAS
        if any(palavra in pergunta_sem_acento for palavra in ["administrativo", "burocracia", "documento", "papelada", "registro"]):
            oportunidades.append({
                "tipo": "administrativo_geral",
                "titulo": "Documentação e Registros",
                "sugestoes": [
                    " Solicite declarações e comprovantes",
                    " Regularize sua documentação",
                    " Mantenha seus registros atualizados"
                ]
            })
        
        return oportunidades
    
    def _formatar_oportunidades(self, oportunidades):
        """
        Formata as oportunidades detectadas em um texto amigável para o aluno
        """
        if not oportunidades:
            return ""
        
        texto = "\n\n **Oportunidades e Próximas Ações:**"
        
        for oport in oportunidades[:2]:  # Mostrar no máximo 2 oportunidades
            texto += f"\n\n {oport['titulo']}"
            for sugestao in oport['sugestoes'][:2]:  # Mostrar no máximo 2 sugestões por oportunidade
                texto += f"\n   {sugestao}"
        
        return texto
    
    def _integrar_oportunidades_na_resposta(self, resposta_base, pergunta):
        """
        Integra oportunidades detectadas na resposta do agente de forma natural
        """
        # Detectar oportunidades
        oportunidades = self._detectar_oportunidades(pergunta)
        
        # Se houver oportunidades e a pergunta é acadêmica, adicionar sugestões
        pergunta_sem_acento = self._normalizar_texto(pergunta)
        eh_academica = any(palavra in pergunta_sem_acento for palavra in [
            "materia", "disciplina", "curso", "boleto", "nota", "frequencia",
            "requerimento", "diploma", "transferencia", "endereco", "dados"
        ])
        
        if oportunidades and eh_academica:
            # Adicionar oportunidades à resposta
            resposta_com_oport = resposta_base + self._formatar_oportunidades(oportunidades)
            return resposta_com_oport
        
        return resposta_base
    
    def _enriquecer_resposta_requerimento(self, resposta, ferramenta, args):
        """
        Enriquece a resposta de um requerimento com informações adicionais úteis.
        Ex: Link para download de PDF, número de protocolo, próximas etapas, etc.
        """
        if ferramenta != "criar_requerimento":
            return resposta
        
        tipo_req = args.get("tipo") if isinstance(args, dict) else None
        resposta_str = str(resposta).lower()
        
        # Tentar obter o ID do requerimento mais recente do aluno
        requerimento_id = None
        if self.aluno_id:
            try:
                # Fazer requisição para obter requerimentos do aluno
                response = requests.get(
                    f"http://localhost:5000/api/requerimentos",
                    params={"aluno_id": self.aluno_id},
                    timeout=5
                )
                if response.status_code == 200:
                    dados = response.json()
                    if isinstance(dados, dict) and "requerimentos" in dados:
                        requerimentos = dados["requerimentos"]
                    elif isinstance(dados, list):
                        requerimentos = dados
                    else:
                        requerimentos = []
                    
                    # Pegar o mais recente
                    if requerimentos:
                        # Ordenar por data de criação (descendente) e pegar o primeiro
                        requerimentos_ordenados = sorted(
                            requerimentos, 
                            key=lambda x: x.get('id', 0), 
                            reverse=True
                        )
                        requerimento_id = requerimentos_ordenados[0].get('id')
            except Exception as e:
                logger.warning("Erro ao obter ID do requerimento: %s", e)
        
        # Se é uma declaração e foi processada com sucesso
        if tipo_req == "declaracao":
            if "sucesso" in resposta_str or "processado" in resposta_str or "concluido" in resposta_str or "criado" in resposta_str:
                resposta += "\n\n **Seu documento está pronto!**"
                resposta += "\n Você pode acessar e baixar sua declaração através do portal acadêmico"
                
                # Adicionar link com ID correto se conseguiu obter
                if requerimento_id:
                    resposta += f"\n\n **Links diretos:**"
                    resposta += f"\n Baixar PDF: http://localhost:5000/api/requerimentos/{requerimento_id}/pdf"
                    resposta += f"\n Visualizar: http://localhost:5000/api/requerimentos/{requerimento_id}/visualizar-pdf"
                    resposta += f"\n Portal: http://localhost:5000/portal"
                else:
                    resposta += "\n\n Acesse o portal em http://localhost:5000/portal para ver seu documento"
        
        # Se é um boleto
        elif tipo_req == "boleto":
            if "sucesso" in resposta_str or "processado" in resposta_str:
                resposta += "\n\n **Boleto gerado com sucesso!**"
                resposta += "\n Você receberá o boleto por email em breve"
                resposta += "\n Número do boleto: Verifique na sua conta"
                resposta += "\n⏰ Vencimento: Confira a data no boleto enviado"
                resposta += "\n Acesse o portal: http://localhost:5000/portal"
        
        # Se é uma transferência
        elif tipo_req == "transferencia":
            if "sucesso" in resposta_str or "processado" in resposta_str:
                resposta += "\n\n **Transferência solicitada!**"
                resposta += "\n Sua solicitação foi registrada no sistema"
                resposta += "\n Protocolo: Acompanhe via portal acadêmico"
                resposta += "\n⏳ Tempo estimado: 5 a 10 dias úteis"
                resposta += "\n Portal: http://localhost:5000/portal"
        
        # Se é trancamento
        elif tipo_req == "trancamento":
            if "sucesso" in resposta_str or "processado" in resposta_str:
                resposta += "\n\n⏸ **Trancamento registrado!**"
                resposta += "\n Seu semestre foi trancado com sucesso"
                resposta += "\n Você poderá retomar seus estudos quando desejar"
                resposta += "\n Em caso de dúvidas, fale com a coordenação"
                resposta += "\n Portal: http://localhost:5000/portal"
        
        # Se é diploma
        elif tipo_req == "diploma":
            if "sucesso" in resposta_str or "processado" in resposta_str:
                resposta += "\n\n **Diploma solicitado!**"
                resposta += "\n Sua solicitação de 2ª via foi registrada"
                resposta += "\n⏳ Tempo de impressão: Até 15 dias úteis"
                resposta += "\n Retire no setor de registros"
                resposta += "\n Portal: http://localhost:5000/portal"
        
        # Adicionar mensagem genérica para acompanhamento
        if "protocolo" in resposta_str:
            resposta += "\n\n **Acompanhe seu requerimento:**"
            resposta += "\n Portal do Aluno: http://localhost:5000/portal"
            resposta += "\n(Faça login com sua matrícula e senha)"
        
        return resposta
    
    def _criar_requerimento_banco(self, tipo_req, subtipo=None):
        """
        Cria um requerimento directamente no banco via API Flask.
        Retorna o ID do requerimento criado ou None se falhar.
        """
        if not self.aluno_id:
            return None
        
        try:
            if tipo_req == "declaracao":
                # Chamar endpoint Flask para criar declaração
                response = requests.post(
                    "http://localhost:5000/api/requerimentos/declaracao",
                    json={
                        "aluno_id": self.aluno_id,
                        "declaracao_tipo": subtipo or "matricula"
                    },
                    timeout=10
                )
                if response.status_code == 201:
                    dados = response.json()
                    return dados.get('id')
            
            elif tipo_req == "boleto":
                response = requests.post(
                    "http://localhost:5000/api/requerimentos/boleto",
                    json={"aluno_id": self.aluno_id},
                    timeout=10
                )
                if response.status_code == 201:
                    dados = response.json()
                    return dados.get('id')
            
            elif tipo_req == "adicao_materia":
                response = requests.post(
                    "http://localhost:5000/api/requerimentos/adicao-materia",
                    json={
                        "aluno_id": self.aluno_id,
                        "codigo_materia": subtipo or ""
                    },
                    timeout=10
                )
                if response.status_code == 201:
                    dados = response.json()
                    return dados.get('id')
            
            elif tipo_req == "remocao_materia":
                response = requests.post(
                    "http://localhost:5000/api/requerimentos/remocao-materia",
                    json={
                        "aluno_id": self.aluno_id,
                        "codigo_materia": subtipo or ""
                    },
                    timeout=10
                )
                if response.status_code == 201:
                    dados = response.json()
                    return dados.get('id')
        
        except Exception as e:
            logger.warning("Erro ao criar requerimento no banco: %s", e)
        
        return None
    
    def _fazer_login(self):
        """Realiza o login de um aluno existente"""
        print("\n" + "-"*70)
        print(" LOGIN DE ALUNO")
        print("-"*70)
        
        tentativas = 0
        max_tentativas = 3
        
        while tentativas < max_tentativas:
            try:
                entrada = input("\n Digite seu ID de aluno (ou 'voltar' para o menu): ").strip()
                
                if entrada.lower() in ['voltar', 'v', 'menu', 'sair']:
                    return False
                
                if not entrada:
                    continue
                
                self.aluno_id = int(entrada)
                
                print(" Verificando aluno...")
                resposta = self.chamar_ferramenta("consultar_aluno", {"aluno_id": self.aluno_id})
                
                if "" not in str(resposta) and "não encontrado" not in str(resposta).lower():
                    # Tentar extrair nome
                    if isinstance(resposta, str):
                        match = re.search(r'Nome:?\s*([^\n]+)', resposta)
                        self.aluno_nome = match.group(1) if match else f"Aluno {self.aluno_id}"
                    else:
                        self.aluno_nome = f"Aluno {self.aluno_id}"
                    
                    print(f"\n Login realizado com sucesso!")
                    print(f" Bem-vindo(a), {self.aluno_nome}!")
                    return True
                else:
                    tentativas += 1
                    restantes = max_tentativas - tentativas
                    print(f" Aluno não encontrado")
                    if restantes > 0:
                        print(f"  Você tem {restantes} tentativa(s) restante(s)")
                    self.aluno_id = None
                    
            except ValueError:
                tentativas += 1
                restantes = max_tentativas - tentativas
                print(" ID inválido! Digite apenas números.")
                if restantes > 0:
                    print(f"  Você tem {restantes} tentativa(s) restante(s)")
            except Exception as e:
                print(f" Erro: {e}")
                tentativas += 1
                self.aluno_id = None
        
        print("\n  Número máximo de tentativas excedido.")
        print(" Dica: Se você é novo, escolha a opção 'Quero me matricular'")
        return False
    
    def iniciar(self):
        """Inicia o assistente com menu de opções melhorado"""
        print("\n" + "="*70)
        print(" SISTEMA AGENTE IA - GERENCIAMENTO ESCOLAR")
        print("="*70)
        
        # Verificar conectividade
        if not self.verificar_servidor():
            print("\n Certifique-se de que o servidor MCP está rodando:")
            print("   cd agente-ia")
            print("   ..\\ambiente\\Scripts\\python.exe mcp_escola_server.py")
            return False
        
        # Listar ferramentas
        self.ferramentas = self.listar_ferramentas()
        
        print(f"\n Total: {len(self.ferramentas)} ferramentas disponíveis")
        print("="*70)
        
        # Menu principal
        print("\n")
        print("            BEM-VINDO AO PORTAL ACADÊMICO             ")
        print("")
        print("\nSelecione uma opção:")
        print("  [1]  Já sou aluno (fazer login)")
        print("  [2]  Quero me matricular (novo aluno)")
        print("  [3]   Modo visitante (consultas gerais)")
        print("  [0]  Sair")
        
        while True:
            try:
                opcao = input("\n Escolha uma opção (0-3): ").strip()
                
                if opcao == "0":
                    print("\n Até logo!")
                    return False
                
                elif opcao == "1":
                    # Login de aluno existente
                    if self._fazer_login():
                        return True
                    # Se login falhar, volta ao menu
                    print("\n" + "="*70)
                    print("Selecione uma opção:")
                    print("  [1]  Já sou aluno (fazer login)")
                    print("  [2]  Quero me matricular (novo aluno)")
                    print("  [3]   Modo visitante (consultas gerais)")
                    print("  [0]  Sair")
                
                elif opcao == "2":
                    # Iniciar cadastro de novo aluno
                    print("\n Ótimo! Vou te ajudar a fazer sua matrícula.")
                    print(" Você pode começar digitando 'quero me cadastrar' ou simplesmente conversar comigo.\n")
                    self.aluno_nome = "Visitante"
                    return True
                
                elif opcao == "3":
                    # Modo visitante
                    print("\n Bem-vindo ao modo visitante!")
                    print(" Você pode fazer consultas gerais e conversar comigo.\n")
                    self.aluno_nome = "Visitante"
                    return True
                
                else:
                    print(" Opção inválida! Por favor, escolha entre 0 e 3.")
                    
            except KeyboardInterrupt:
                print("\n\n Até logo!")
                return False
            except Exception as e:
                print(f" Erro: {e}")
        
        return False

    def executar(self):
        """Loop principal"""
        if not self.iniciar():
            return
        
        print("\n" + "="*70)
        print(" COMO POSSO AJUDAR?")
        print("="*70)
        
        # Mensagem personalizada baseada no tipo de usuário
        if self.aluno_id:
            print(f"\n Logado como: {self.aluno_nome} (ID: {self.aluno_id})")
            print("\n O que você pode fazer:")
            print("\n    Consultas")
            print("      • 'meus dados' ou 'quem sou eu?'")
            print("      • 'minhas matérias' ou 'minha grade'")
            print("      • 'minhas notas' ou 'meu histórico'")
            print("      • 'meus boletos' ou 'quanto devo?'")
            print("      • 'resumo acadêmico'")
            print("\n    Documentos")
            print("      • 'declaração de matrícula'")
            print("      • 'segunda via de boleto'")
            print("      • 'histórico escolar'")
            print("\n    Solicitações")
            print("      • 'adicionar matéria ALG-101'")
            print("      • 'remover matéria MAT-102'")
            print("      • 'trancar o semestre'")
            print("      • 'solicitar transferência'")
        else:
            print(f"\n  Modo: {self.aluno_nome}")
            print("\n O que você pode fazer:")
            print("      • 'quero me cadastrar' ou 'fazer matrícula'")
            print("      • 'quais cursos tem?' ou 'me fale sobre os cursos'")
            print("      • Fazer perguntas gerais sobre a faculdade")
            print("      • Conversar comigo sobre diversos assuntos")
        
        print("\n Dica: Apenas pergunte naturalmente! Estou aqui para ajudar.")
        print("\n" + "="*70)
        
        while True:
            try:
                pergunta = input(f"\n Você: ").strip()
                
                if pergunta.lower() in ['sair', 'exit', 'quit']:
                    break
                
                if not pergunta:
                    continue

                pergunta_sem_acento = self._normalizar_texto(pergunta)

                # Processar fluxo de cadastro se estiver em andamento
                if self.dados_cadastro:
                    resultado = self._processar_resposta_cadastro(pergunta)
                    if resultado:
                        print(f" Assistente: {resultado['resposta']}")
                        time.sleep(0.5)
                        continue

                # Confirmar ou cancelar acao pendente
                if self.acao_pendente:
                    if self.acao_pendente.get("tipo") == "adicionar_materia_interesse":
                        # Ação pendente especial para interesse em matéria
                        if self._confirmar_acao_pendente(pergunta_sem_acento):
                            # Confirmar adição de matéria
                            resposta = f"Perfeito!  Vou abrir um requerimento para adicionar {self.acao_pendente.get('materia')} à sua grade.\n\n"
                            resposta += "Seu requerimento foi processado com sucesso!"
                            self.acao_pendente = None
                            print(f" Assistente: {resposta}")
                            time.sleep(0.5)
                            continue
                        elif self._negar_acao_pendente(pergunta_sem_acento):
                            self.acao_pendente = None
                            print(f" Assistente: Tudo bem! Se mudar de ideia, é só me chamar. ")
                            time.sleep(0.5)
                            continue
                        else:
                            self.acao_pendente = None
                            decisao = self.consultar_llm(pergunta)
                    
                    elif self.acao_pendente.get("tipo") == "servico_interesse":
                        # Ação pendente para serviço de interesse (declaração, boleto, etc)
                        if self._confirmar_acao_pendente(pergunta_sem_acento):
                            # Confirmar serviço - EXECUTAR A FERRAMENTA
                            servico = self.acao_pendente.get('servico')
                            subtipo = self.acao_pendente.get('subtipo')
                            
                            # Extrair argumentos da ação pendente
                            ferramenta = self.acao_pendente.get('decisao', {}).get('ferramenta')
                            args = self.acao_pendente.get('decisao', {}).get('argumentos', {})
                            
                            if ferramenta == "criar_requerimento":
                                # CRIAR REQUERIMENTO NO BANCO PRIMEIRO
                                requerimento_id = self._criar_requerimento_banco(servico, subtipo)
                                
                                # EXECUTAR A FERRAMENTA MCP PARA RESPOSTA INTELIGENTE
                                resposta = self.chamar_ferramenta(ferramenta, args)
                                # Enriquecer com link do PDF (agora temos o ID correto)
                                resposta = self._enriquecer_resposta_requerimento(resposta, ferramenta, args)
                                
                                # Se conseguiu ID e é declaração, adicionar links diretos na resposta
                                if requerimento_id and servico == "declaracao":
                                    resposta += f"\n\n **Links diretos:**"
                                    resposta += f"\n Baixar PDF: http://localhost:5000/api/requerimentos/{requerimento_id}/pdf"
                                    resposta += f"\n Visualizar: http://localhost:5000/api/requerimentos/{requerimento_id}/visualizar-pdf"
                                    resposta += f"\n Portal: http://localhost:5000/portal"
                            else:
                                mensagens_sucesso = {
                                    "declaracao": f"Perfeito!  Vou gerar sua declaração {f'de {subtipo}' if subtipo else ''}.\n\nSeu documento foi processado!",
                                    "boleto": "Perfeito!  Vou solicitar segunda via do boleto.\n\nSua solicitação foi processada!",
                                    "transferencia": "Perfeito!  Vou processar sua transferência.\n\nSua solicitação foi recebida!",
                                    "trancamento": "Perfeito!  Vou processar seu trancamento.\n\nSua solicitação foi processada!",
                                    "diploma": "Perfeito!  Vou solicitar segunda via do diploma.\n\nSua solicitação foi processada!",
                                    "endereco": "Perfeito!  Vou atualizar seu endereço.\n\nSeus dados foram atualizados!",
                                    "certificado": "Perfeito!  Vou solicitar o certificado.\n\nSua solicitação foi processada!"
                                }
                                resposta = mensagens_sucesso.get(servico, "Perfeito!  Sua solicitação foi processada com sucesso!")
                            
                            self.acao_pendente = None
                            print(f" Assistente: {resposta}")
                            time.sleep(0.5)
                            continue
                        elif self._negar_acao_pendente(pergunta_sem_acento):
                            self.acao_pendente = None
                            print(f" Assistente: Tudo bem! Se precisar depois, é só me chamar. ")
                            time.sleep(0.5)
                            continue
                        else:
                            self.acao_pendente = None
                            decisao = self.consultar_llm(pergunta)
                    
                    else:
                        # Ação pendente padrão
                        if self._confirmar_acao_pendente(pergunta_sem_acento):
                            decisao = self.acao_pendente
                            self.acao_pendente = None
                        elif self._negar_acao_pendente(pergunta_sem_acento):
                            self.acao_pendente = None
                            decisao = {"acao": "conversa", "resposta": "Tudo bem. Se precisar de algo, estou aqui."}
                        else:
                            self.acao_pendente = None
                            decisao = self.consultar_llm(pergunta)

                            # Para confissoes, pedir confirmacao antes de executar requerimento
                            if self._texto_confessional(pergunta_sem_acento) and decisao.get("acao") == "ferramenta" and decisao.get("ferramenta") == "criar_requerimento":
                                self.acao_pendente = decisao
                                decisao = self._montar_confirmacao_acao(decisao)
                else:
                    # Verificar se há interesse em matéria ANTES de consultar LLM
                    resultado_interesse = self._processar_interesse_em_materia(pergunta)
                    
                    if resultado_interesse:
                        # Há interesse em matéria - usar a resposta processada
                        decisao = resultado_interesse
                    else:
                        # Verificar se há necessidade de serviço (declaração, boleto, etc)
                        resultado_necessidade = self._processar_necessidade_aluno(pergunta)
                        
                        if resultado_necessidade:
                            # Há necessidade de serviço - usar a resposta processada
                            decisao = resultado_necessidade
                        else:
                            # Não há interesse ou necessidade específica - consultar LLM normalmente
                            decisao = self.consultar_llm(pergunta)

                            # Para confissoes, pedir confirmacao antes de executar requerimento
                            if self._texto_confessional(pergunta_sem_acento) and decisao.get("acao") == "ferramenta" and decisao.get("ferramenta") == "criar_requerimento":
                                self.acao_pendente = decisao
                                decisao = self._montar_confirmacao_acao(decisao)
                
                if decisao.get("acao") == "ferramenta":
                    ferramenta = decisao.get("ferramenta")
                    args = decisao.get("argumentos", {})
                    
                    if ferramenta:
                        resposta = self.chamar_ferramenta(ferramenta, args)
                        # Enriquecer resposta com informações de requerimento
                        resposta = self._enriquecer_resposta_requerimento(resposta, ferramenta, args)
                    else:
                        resposta = "Não identifiquei a ferramenta"
                else:
                    resposta = decisao.get("resposta", "OK")
                
                # Integrar oportunidades na resposta
                resposta = self._integrar_oportunidades_na_resposta(resposta, pergunta)
                
                print(f" Assistente: {resposta}")
                
                # Pequena pausa para não sobrecarregar
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f" Erro: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n Até logo!")

    def _confirmar_acao_pendente(self, pergunta_sem_acento):
        """Detecta confirmacao explicita para executar acao pendente"""
        confirmacoes_frases = ["pode abrir", "pode fazer"]
        confirmacoes_palavras = ["sim", "pode", "ok", "confirmo", "quero", "faca", "prosseguir"]

        if any(frase in pergunta_sem_acento for frase in confirmacoes_frases):
            return True

        return any(re.search(rf"\b{re.escape(palavra)}\b", pergunta_sem_acento) for palavra in confirmacoes_palavras)

    def _negar_acao_pendente(self, pergunta_sem_acento):
        """Detecta negativa para cancelar acao pendente"""
        negativas_frases = ["nao quero", "nao precisa", "nao precisa nao"]
        negativas_palavras = ["nao", "cancela", "cancelar", "deixa", "deixe", "pare", "parar"]

        if any(frase in pergunta_sem_acento for frase in negativas_frases):
            return True

        return any(re.search(rf"\b{re.escape(palavra)}\b", pergunta_sem_acento) for palavra in negativas_palavras)

    def _texto_confessional(self, pergunta_sem_acento):
        """Detecta confissao/intencao que deve pedir confirmacao"""
        gatilhos_frases = [
            "nao gostei"
        ]
        gatilhos_palavras = [
            "quero",
            "gostaria",
            "preciso",
            "vou",
            "pretendo",
            "decidi"
        ]

        if any(frase in pergunta_sem_acento for frase in gatilhos_frases):
            return True

        return any(re.search(rf"\b{re.escape(palavra)}\b", pergunta_sem_acento) for palavra in gatilhos_palavras)

    def _normalizar_texto(self, texto):
        """Normaliza texto removendo acentos e convertendo para minusculas"""
        texto_normalizado = unicodedata.normalize("NFD", texto)
        texto_sem_acento = "".join(ch for ch in texto_normalizado if unicodedata.category(ch) != "Mn")
        return texto_sem_acento.lower()

    def _descricao_requerimento(self, decisao):
        """Gera descricao curta do requerimento para confirmacao"""
        if decisao.get("ferramenta") != "criar_requerimento":
            return None

        argumentos = decisao.get("argumentos", {})
        tipo = argumentos.get("tipo") if isinstance(argumentos, dict) else None
        kwargs = argumentos.get("kwargs", {}) if isinstance(argumentos, dict) else {}

        if tipo == "declaracao":
            tipo_declaracao = kwargs.get("tipo_declaracao")
            if tipo_declaracao:
                return f"um requerimento de declaracao de {tipo_declaracao}"
            return "um requerimento de declaracao"

        if tipo == "adicao_materia":
            codigo = kwargs.get("codigo_materia")
            return f"um requerimento de adicao de materia {codigo}" if codigo else "um requerimento de adicao de materia"

        if tipo == "remocao_materia":
            codigo = kwargs.get("codigo_materia")
            return f"um requerimento de remocao de materia {codigo}" if codigo else "um requerimento de remocao de materia"

        if tipo == "boleto":
            valor = kwargs.get("valor")
            if valor is None:
                return "um requerimento de segunda via de boleto"
            try:
                valor_formatado = f"{float(valor):.2f}"
            except (TypeError, ValueError):
                valor_formatado = str(valor)
            return f"um requerimento de segunda via de boleto (R$ {valor_formatado})"

        if tipo:
            return f"um requerimento de {tipo}"

        return "um requerimento"

    def _montar_confirmacao_acao(self, decisao):
        """Monta a resposta de confirmacao para uma acao pendente"""
        descricao = self._descricao_requerimento(decisao)
        texto = f"Posso abrir {descricao}. Quer que eu abra?" if descricao else "Posso abrir esse requerimento para voce. Quer que eu abra?"
        return {"acao": "conversa", "resposta": texto}

def main():
    """Funcao principal"""
    print("\n" + "="*70)
    print("AGENTE IA - SISTEMA DE GERENCIAMENTO ESCOLAR")
    print("="*70)
    print("\n[INFO] Iniciando agente...")
    print("[INFO] Conectando ao servidor em http://localhost:8000")
    print()
    
    # Iniciar agente
    agente = AgenteIAInteligente()
    
    try:
        agente.executar()
    except KeyboardInterrupt:
        print("\n\n[INFO] Ate logo!")
        input("\nPressione ENTER para sair...")
    except Exception as e:
        print(f"\n[ERRO] Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        input("\nPressione ENTER para sair...")

if __name__ == "__main__":
    main()