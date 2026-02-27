"""
Funções de formatação
"""
from datetime import datetime


def formatar_data(data, formato='%d/%m/%Y'):
    """Formata uma data"""
    if isinstance(data, str):
        return data
    if isinstance(data, datetime):
        return data.strftime(formato)
    return str(data)


def formatar_moeda(valor, simbolo='R$'):
    """Formata um valor monetário"""
    if valor is None:
        return f"{simbolo} 0,00"
    return f"{simbolo} {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def formatar_cpf(cpf):
    """Formata um CPF"""
    if not cpf:
        return cpf
    cpf_limpo = ''.join(c for c in cpf if c.isdigit())
    if len(cpf_limpo) != 11:
        return cpf
    return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"


def formatar_telefone(telefone):
    """Formata um telefone"""
    if not telefone:
        return telefone
    tel_limpo = ''.join(c for c in telefone if c.isdigit())
    if len(tel_limpo) == 10:
        return f"({tel_limpo[:2]}) {tel_limpo[2:6]}-{tel_limpo[6:]}"
    elif len(tel_limpo) == 11:
        return f"({tel_limpo[:2]}) {tel_limpo[2:7]}-{tel_limpo[7:]}"
    return telefone


def truncar_texto(texto, limite=50):
    """Trunca um texto com reticências"""
    if not texto or len(texto) <= limite:
        return texto
    return texto[:limite-3] + '...'
