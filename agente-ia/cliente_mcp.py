import requests
import json
from datetime import datetime
import os
import re

class AgenteAssistente:
    def __init__(self, mcp_url="http://localhost:8000"):  #  Porta alterada para 8000
        self.mcp_url = mcp_url
        self.aluno_id = None
        self.aluno_nome = None
    
    def iniciar(self):
        """Inicia o assistente"""
        print("="*60)
        print(" ASSISTENTE ACADÊMICO INTELIGENTE (MCP REAL)")
        print("="*60)
        print()
        
        # Solicitar ID do aluno
        while not self.aluno_id:
            try:
                self.aluno_id = int(input(" Digite seu ID de aluno: "))
                
                # Verificar se aluno existe usando a tool consultar_aluno
                resposta = self.chamar_ferramenta("consultar_aluno", {"aluno_id": self.aluno_id})
                
                if "não encontrado" not in resposta.lower():
                    # Extrair nome do aluno da resposta
                    match = re.search(r'Nome: ([^\n]+)', resposta)
                    self.aluno_nome = match.group(1) if match else f'Aluno {self.aluno_id}'
                    print(f"\n Bem-vindo(a), {self.aluno_nome}!")
                    print("="*60)
                    self.mostrar_ajuda()
                    break
                else:
                    print(" Aluno não encontrado. Tente novamente.")
                    self.aluno_id = None
            except ValueError:
                print(" Por favor, digite um número válido.")
            except requests.exceptions.ConnectionError:
                print(" Erro de conexão com o MCP Server. Verifique se o servidor está rodando.")
                return
    
    def chamar_ferramenta(self, tool_name, arguments):
        """Chama uma ferramenta do MCP Server via JSON-RPC"""
        try:
            # Montar requisição JSON-RPC
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 1
            }
            
            response = requests.post(
                f"{self.mcp_url}/",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    # Extrair conteúdo da resposta
                    content = result["result"].get("content", [])
                    if content and len(content) > 0:
                        return content[0].get("text", "Resposta vazia")
                    return "Resposta processada"
                elif "error" in result:
                    return f" Erro: {result['error'].get('message', 'Erro desconhecido')}"
            else:
                return f" Erro HTTP: {response.status_code}"
        except Exception as e:
            return f" Erro de conexão: {str(e)}"
    
    def perguntar_sobre_aluno(self, pergunta):
        """Usa a tool perguntar_sobre_aluno"""
        return self.chamar_ferramenta(
            "perguntar_sobre_aluno",
            {"aluno_id": self.aluno_id, "pergunta": pergunta}
        )
    
    def criar_requerimento(self, tipo, dados=None):
        """Usa a tool criar_requerimento"""
        kwargs = dados or {}
        return self.chamar_ferramenta(
            "criar_requerimento",
            {"aluno_id": self.aluno_id, "tipo": tipo, "kwargs": kwargs}
        )
    
    def listar_alunos(self, limite=10):
        """Usa a tool listar_alunos"""
        return self.chamar_ferramenta("listar_alunos", {"limite": limite})
    
    def resumo_academico(self):
        """Usa a tool resumo_academico"""
        return self.chamar_ferramenta("resumo_academico", {"aluno_id": self.aluno_id})
    
    def consultar_aluno(self):
        """Usa a tool consultar_aluno"""
        return self.chamar_ferramenta("consultar_aluno", {"aluno_id": self.aluno_id})
    
    def mostrar_ajuda(self):
        """Mostra menu de ajuda"""
        print("\n **Comandos disponíveis:**")
        print("   • Perguntas em linguagem natural")
        print("   • 'resumo' - Ver resumo acadêmico")
        print("   • 'dados' - Ver dados pessoais")
        print("   • 'listar' - Listar todos os alunos")
        print("   • 'requerimento ajuda' - Instruções para requerimentos")
        print("   • 'sair' - Encerrar")
        print("="*60)
    
    def processar_comando_requerimento(self, pergunta):
        """Processa comandos de requerimento"""
        pergunta_lower = pergunta.lower()
        
        if 'adicionar materia' in pergunta_lower:
            match = re.search(r'adicionar materia\s+(\S+)', pergunta_lower)
            if match:
                codigo = match.group(1)
                return self.criar_requerimento('adicao_materia', {'codigo_materia': codigo})
            else:
                return "Por favor, informe o código da matéria. Exemplo: `adicionar materia ALG-101`"
        
        elif 'remover materia' in pergunta_lower:
            match = re.search(r'remover materia\s+(\S+)', pergunta_lower)
            if match:
                codigo = match.group(1)
                return self.criar_requerimento('remocao_materia', {'codigo_materia': codigo})
            else:
                return "Por favor, informe o código da matéria. Exemplo: `remover materia ALG-101`"
        
        elif 'declaracao' in pergunta_lower and 'ajuda' not in pergunta_lower:
            tipos = ['matricula', 'frequencia', 'conclusao']
            for tipo in tipos:
                if tipo in pergunta_lower:
                    return self.criar_requerimento('declaracao', {'tipo_declaracao': tipo})
            return "Tipos de declaração disponíveis: matricula, frequencia, conclusao. Exemplo: `declaracao matricula`"
        
        elif 'boleto' in pergunta_lower:
            match = re.search(r'boleto\s+(\d+\.?\d*)', pergunta_lower)
            if match:
                valor = float(match.group(1))
                return self.criar_requerimento('boleto', {'valor': valor})
            else:
                return "Por favor, informe o valor do boleto. Exemplo: `boleto 350.00`"
        
        elif 'requerimento ajuda' in pergunta_lower:
            return self.mostrar_ajuda_requerimentos()
        
        return None
    
    def mostrar_ajuda_requerimentos(self):
        """Mostra ajuda específica para requerimentos"""
        return """ **INSTRUÇÕES PARA REQUERIMENTOS**

**Adicionar Matéria:**
`adicionar materia CODIGO`
Exemplo: `adicionar materia ALG-101`

**Remover Matéria:**
`remover materia CODIGO`
Exemplo: `remover materia BD-201`

**Declarações:**
`declaracao TIPO`
Tipos: matricula, frequencia, conclusao
Exemplo: `declaracao matricula`

**Boletos:**
`boleto VALOR`
Exemplo: `boleto 350.00`

Após criar, seu requerimento será processado pela secretaria acadêmica."""
    
    def executar(self):
        """Loop principal do assistente"""
        if not self.aluno_id:
            self.iniciar()
        
        print("\n Como posso ajudar você hoje?")
        print("   Digite 'ajuda' para ver os comandos disponíveis")
        
        while True:
            try:
                pergunta = input("\n Você: ").strip()
                
                if pergunta.lower() in ['sair', 'exit', 'quit']:
                    print("\n Até logo! Foi um prazer ajudar!")
                    break
                
                elif pergunta.lower() in ['ajuda', 'help', '?']:
                    self.mostrar_ajuda()
                
                elif pergunta.lower() == 'resumo':
                    print(" Assistente:", self.resumo_academico())
                
                elif pergunta.lower() == 'dados':
                    print(" Assistente:", self.consultar_aluno())
                
                elif pergunta.lower() == 'listar':
                    print(" Assistente:", self.listar_alunos())
                
                elif not pergunta:
                    continue
                
                else:
                    # Verificar se é um comando de requerimento
                    resultado_req = self.processar_comando_requerimento(pergunta)
                    
                    if resultado_req:
                        print(f" Assistente: {resultado_req}")
                    else:
                        # É uma pergunta normal
                        print(" Assistente: ", end="")
                        resposta = self.perguntar_sobre_aluno(pergunta)
                        print(resposta)
            
            except KeyboardInterrupt:
                print("\n\n Até logo!")
                break
            except Exception as e:
                print(f" Erro inesperado: {str(e)}")

def main():
    """Função principal"""
    print("="*60)
    print(" VERIFICANDO CONEXÃO COM MCP SERVER")
    print("="*60)
    
    # Verificar se MCP Server está rodando na porta 8000
    try:
        response = requests.get("http://localhost:8000/docs", timeout=3)
        if response.status_code == 200:
            print(f" MCP Server respondendo em http://localhost:8000")
        else:
            print("  Resposta inesperada do servidor")
    except requests.exceptions.ConnectionError:
        print(" MCP Server não está respondendo em http://localhost:8000")
        print("\n Para iniciar o MCP Server:")
        print("   1. Abra outro terminal")
        print("   2. Navegue até: cd C:\\Users\\JacksonRodrigues\\Downloads\\AgenteIa\\agente-ia")
        print("   3. Execute: python mcp_escola_server.py")
        print("\nDepois execute este assistente novamente.")
        return
    except Exception as e:
        print(f" Erro inesperado: {e}")
        return
    
    print("\n" + "="*60)
    
    # Iniciar assistente
    agente = AgenteAssistente()
    agente.executar()

if __name__ == "__main__":
    main()