"""
Agente IA - Processamento de LLM e NLP
Parte 3 de 4: Consultas ao LLM e interpretação de texto
"""
from agente_ia_inteligente import AgenteIAInteligente

__all__ = ['AgenteIAInteligente']

# Re-export dos métodos de LLM
def consultar_llm(agente, pergunta):
    return agente.consultar_llm(pergunta)

def processar_interesse_em_materia(agente, pergunta):
    return agente._processar_interesse_em_materia(pergunta)

def processar_necessidade_aluno(agente, pergunta):
    return agente._processar_necessidade_aluno(pergunta)
