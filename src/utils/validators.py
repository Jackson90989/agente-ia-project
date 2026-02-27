"""
Validadores de dados
"""
import re
from src.core.errors import ValidationError


def validar_cpf(cpf):
    """Valida um CPF"""
    if not cpf:
        raise ValidationError("CPF é obrigatório")
    
    # Remove caracteres especiais
    cpf_limpo = re.sub(r'\D', '', cpf)
    
    if len(cpf_limpo) != 11:
        raise ValidationError("CPF deve conter 11 dígitos")
    
    # Verificar se todos os dígitos são iguais (CPF inválido)
    if cpf_limpo == cpf_limpo[0] * 11:
        raise ValidationError("CPF inválido")
    
    return cpf_limpo


def validar_email(email):
    """Valida um email"""
    if not email:
        raise ValidationError("Email é obrigatório")
    
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(padrao, email):
        raise ValidationError("Email inválido")
    
    return email.lower()


def validar_telefone(telefone):
    """Valida um telefone"""
    if not telefone:
        raise ValidationError("Telefone é obrigatório")
    
    # Remove caracteres especiais
    telefone_limpo = re.sub(r'\D', '', telefone)
    
    if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
        raise ValidationError("Telefone deve conter 10 ou 11 dígitos")
    
    return telefone_limpo


def validar_senha(senha):
    """Valida uma senha"""
    if not senha:
        raise ValidationError("Senha é obrigatória")
    
    if len(senha) < 4:
        raise ValidationError("Senha deve ter no mínimo 4 caracteres")
    
    if len(senha) > 128:
        raise ValidationError("Senha muito longa")
    
    return senha


def validar_campos_obrigatorios(data, campos):
    """Valida se campos obrigatórios estão presentes"""
    if not isinstance(data, dict):
        raise ValidationError("Dados inválidos ou vazios")
    
    faltando = [campo for campo in campos if campo not in data or data[campo] is None]
    if faltando:
        raise ValidationError(f"Campos obrigatórios ausentes: {', '.join(faltando)}")
    
    return data
