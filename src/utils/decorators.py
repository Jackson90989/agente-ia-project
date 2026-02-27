"""
Funções e decoradores customizados
"""
from functools import wraps
from flask import request, jsonify, current_app
from src.core.errors import AuthenticationError, AuthorizationError
from src.models.usuario import Usuario
import jwt


def requer_autenticacao(f):
    """Decorador para verificar autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'erro': 'Token ausente'}), 401
        
        try:
            # Remover 'Bearer ' se presente
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])
            request.user_id = payload.get('user_id')
            request.aluno_id = payload.get('aluno_id')
        except jwt.ExpiredSignatureError:
            return jsonify({'erro': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'erro': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def requer_admin(f):
    """Decorador para verificar se usuário é admin"""
    @wraps(f)
    @requer_autenticacao
    def decorated_function(*args, **kwargs):
        user = Usuario.query.get(request.user_id)
        
        if not user or user.tipo != 'admin':
            return jsonify({'erro': 'Acesso negado'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def requer_funcionario(f):
    """Decorador para verificar se usuário é funcionário ou admin"""
    @wraps(f)
    @requer_autenticacao
    def decorated_function(*args, **kwargs):
        user = Usuario.query.get(request.user_id)
        
        if not user or user.tipo not in ['admin', 'funcionario']:
            return jsonify({'erro': 'Acesso negado'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
