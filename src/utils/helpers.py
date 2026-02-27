"""
Funções auxiliares
"""
from datetime import datetime, timedelta
from functools import wraps
from flask import jsonify


def criar_resposta_json(sucesso=True, mensagem='', dados=None, status_code=200):
    """Cria uma resposta JSON padrão"""
    resposta = {
        'sucesso': sucesso,
        'mensagem': mensagem,
    }
    
    if dados is not None:
        resposta['dados'] = dados
    
    return jsonify(resposta), status_code


def paginar_lista(items, pagina=1, itens_por_pagina=20):
    """Pagina uma lista de itens"""
    inicio = (pagina - 1) * itens_por_pagina
    fim = inicio + itens_por_pagina
    
    total = len(items)
    total_paginas = (total + itens_por_pagina - 1) // itens_por_pagina
    
    return {
        'items': items[inicio:fim],
        'pagina': pagina,
        'total_items': total,
        'total_paginas': total_paginas,
        'itens_por_pagina': itens_por_pagina
    }


def gerar_matricula(ano, numero_aluno):
    """Gera um número de matrícula"""
    return f"{ano}/{numero_aluno:05d}"


def calcular_idade(data_nascimento):
    """Calcula a idade baseada na data de nascimento"""
    if isinstance(data_nascimento, str):
        data_nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
    
    hoje = datetime.now().date()
    idade = hoje.year - data_nascimento.year
    
    # Ajustar se ainda não fez aniversário este ano
    if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1
    
    return idade


def eh_maior_idade(data_nascimento):
    """Verifica se uma pessoa é maior de idade"""
    return calcular_idade(data_nascimento) >= 18


def is_data_futura(data):
    """Verifica se uma data é futura"""
    if isinstance(data, str):
        data = datetime.strptime(data, '%Y-%m-%d').date()
    return data > datetime.now().date()


def is_data_passada(data):
    """Verifica se uma data é passada"""
    if isinstance(data, str):
        data = datetime.strptime(data, '%Y-%m-%d').date()
    return data < datetime.now().date()
