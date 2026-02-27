"""
Camada de Rotas - API Endpoints
"""

# Import dos blueprints existentes
from routes.alunos import alunos_bp
from routes.auth import auth_bp
from routes.cursos import cursos_bp
from routes.materias import materias_bp
from routes.pagamentos import pagamentos_bp
from routes.portal import portal_bp
from routes.requerimentos import requerimentos_bp

__all__ = [
    'alunos_bp',
    'auth_bp',
    'cursos_bp',
    'materias_bp',
    'pagamentos_bp',
    'portal_bp',
    'requerimentos_bp',
]
