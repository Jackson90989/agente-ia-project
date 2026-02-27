"""
Exceções customizadas da aplicação
"""


class AgenteIAException(Exception):
    """Exception base para toda a aplicação"""
    pass


class ValidationError(AgenteIAException):
    """Erro de validação"""
    pass


class AuthenticationError(AgenteIAException):
    """Erro de autenticação"""
    pass


class AuthorizationError(AgenteIAException):
    """Erro de autorização"""
    pass


class NotFoundError(AgenteIAException):
    """Recurso não encontrado"""
    pass


class ConflictError(AgenteIAException):
    """Conflito de dados (ex: registro duplicado)"""
    pass


class DatabaseError(AgenteIAException):
    """Erro de banco de dados"""
    pass


class MCPError(AgenteIAException):
    """Erro de integração com MCP"""
    pass


class PDFGenerationError(AgenteIAException):
    """Erro ao gerar PDF"""
    pass
