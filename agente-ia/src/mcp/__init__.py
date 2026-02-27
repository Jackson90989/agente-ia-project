"""
MCP - Model Context Protocol
Integração com servidor FastMCP
"""
from .server import app, server
from .tools_provider import (
    listar_alunos,
    consultar_aluno,
    perguntar_sobre_aluno,
    listar_cursos,
    listar_materias_disponiveis,
    cadastrar_novo_aluno,
    criar_requerimento,
    resumo_academico,
    buscar_pagamentos,
    diagnosticar_banco,
)
from .handlers import (
    gerar_declaracao,
    gerar_boleto,
    adicionar_materia,
    remover_materia,
)
from .validators import (
    validar_cpf,
    validar_aluno_id,
    validar_requerimento,
)

__all__ = [
    'app',
    'server',
    # Tools
    'listar_alunos',
    'consultar_aluno',
    'perguntar_sobre_aluno',
    'listar_cursos',
    'listar_materias_disponiveis',
    'cadastrar_novo_aluno',
    'criar_requerimento',
    'resumo_academico',
    'buscar_pagamentos',
    'diagnosticar_banco',
    # Handlers
    'gerar_declaracao',
    'gerar_boleto',
    'adicionar_materia',
    'remover_materia',
    # Validators
    'validar_cpf',
    'validar_aluno_id',
    'validar_requerimento',
]
