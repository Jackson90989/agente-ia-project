"""
Agente IA - Processamento de Ferramentas MCP
Parte 2 de 4: Chamadas e integrações com servidor MCP
"""
from agente_ia_inteligente import AgenteIAInteligente

__all__ = ['AgenteIAInteligente']

# Re-export dos métodos de ferramentas para fácil acesso
def chamar_ferramenta(agente, tool_name, arguments):
    return agente.chamar_ferramenta(tool_name, arguments)

def listar_ferramentas(agente):
    return agente.listar_ferramentas()

def verificar_servidor(agente):
    return agente.verificar_servidor()
