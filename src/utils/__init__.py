"""
Utilitários da aplicação
"""
from src.utils.constants import *
from src.utils.validators import (
    validar_cpf,
    validar_email,
    validar_telefone,
    validar_senha,
    validar_campos_obrigatorios,
)
from src.utils.formatters import (
    formatar_data,
    formatar_moeda,
    formatar_cpf,
    formatar_telefone,
    truncar_texto,
)
from src.utils.helpers import (
    criar_resposta_json,
    paginar_lista,
    gerar_matricula,
    calcular_idade,
    eh_maior_idade,
    is_data_futura,
    is_data_passada,
)
from src.utils.decorators import (
    requer_autenticacao,
    requer_admin,
    requer_funcionario,
)

__all__ = [
    # Constants
    'ALUNO_STATUS_ATIVO',
    'REQUERIMENTO_STATUS_PENDENTE',
    'DECLARACAO_TIPO_MATRICULA',
    'PAGAMENTO_STATUS_PENDENTE',
    # Validators
    'validar_cpf',
    'validar_email',
    'validar_telefone',
    'validar_senha',
    'validar_campos_obrigatorios',
    # Formatters
    'formatar_data',
    'formatar_moeda',
    'formatar_cpf',
    'formatar_telefone',
    'truncar_texto',
    # Helpers
    'criar_resposta_json',
    'paginar_lista',
    'gerar_matricula',
    'calcular_idade',
    'eh_maior_idade',
    # Decorators
    'requer_autenticacao',
    'requer_admin',
    'requer_funcionario',
]
