"""
Módulos Agente-IA - Organização em camadas
"""
from .agent import AgenteIAInteligente
from .tools import chamar_ferramenta, listar_ferramentas, verificar_servidor
from .llm import consultar_llm, processar_interesse_em_materia, processar_necessidade_aluno
from .processor import (
    normalizar_texto,
    confirmar_acao,
    negar_acao,
    eh_texto_confessional,
)

__all__ = [
    'AgenteIAInteligente',
    'chamar_ferramenta',
    'listar_ferramentas',
    'verificar_servidor',
    'consultar_llm',
    'processar_interesse_em_materia',
    'processar_necessidade_aluno',
    'normalizar_texto',
    'confirmar_acao',
    'negar_acao',
    'eh_texto_confessional',
]
