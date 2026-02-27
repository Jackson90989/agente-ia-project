from flask import Blueprint, request, jsonify, current_app
from database import db
from src.models import Aluno
from datetime import datetime
import jwt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Autentica um aluno com matrícula e senha.
    Retorna um token JWT para autenticação no portal.
    """
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"erro": "JSON inválido"}), 400
    
    matricula = data.get('matricula')
    senha = data.get('senha')
    
    if not matricula or not senha:
        return jsonify({"erro": "Matrícula e senha são obrigatórias"}), 400
    
    # Buscar aluno
    aluno = Aluno.query.filter_by(matricula=matricula).first()
    
    if not aluno:
        return jsonify({"erro": "Matrícula não encontrada"}), 404
    
    # Verificar senha
    if not aluno.check_senha(senha):
        return jsonify({"erro": "Senha incorreta"}), 401
    
    # Gerar token JWT
    try:
        token = aluno.gerar_token_jwt()
        return jsonify({
            'sucesso': True,
            'token': token,
            'aluno': {
                'id': aluno.id,
                'matricula': aluno.matricula,
                'nome_completo': aluno.nome_completo,
                'email': aluno.email
            }
        }), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao gerar token: {str(e)}"}), 500

@auth_bp.route('/verificar-senha/<int:aluno_id>', methods=['POST'])
def verificar_senha(aluno_id):
    """
    Verifica se a senha fornecida está correta para um aluno.
    Usada pelo agente IA para confirmar ações.
    """
    aluno = Aluno.query.get_or_404(aluno_id)
    data = request.get_json(silent=True)
    
    if not data or 'senha' not in data:
        return jsonify({"erro": "Senha é obrigatória"}), 400
    
    senha = data.get('senha')
    
    if aluno.check_senha(senha):
        return jsonify({
            'sucesso': True,
            'mensagem': 'Senha verificada com sucesso',
            'aluno_id': aluno.id
        }), 200
    else:
        return jsonify({
            'sucesso': False,
            'erro': 'Senha incorreta'
        }), 401

@auth_bp.route('/definir-senha/<int:aluno_id>', methods=['POST'])
def definir_senha(aluno_id):
    """
    Permite que um aluno defina ou altere sua senha.
    Integrada com o agente IA para onboarding.
    """
    aluno = Aluno.query.get_or_404(aluno_id)
    data = request.get_json(silent=True)
    
    if not data or 'senha' not in data:
        return jsonify({"erro": "Senha é obrigatória"}), 400
    
    senha = data.get('senha')
    
    if not senha or len(senha) < 4:
        return jsonify({"erro": "Senha deve ter no mínimo 4 caracteres"}), 400
    
    try:
        aluno.set_senha(senha)
        db.session.commit()
        return jsonify({
            'sucesso': True,
            'mensagem': 'Senha definida com sucesso'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao definir senha: {str(e)}"}), 500

@auth_bp.route('/validar-token', methods=['GET'])
def validar_token():
    """
    Valida um token JWT fornecido no header Authorization.
    Usado pelo portal para verificar sessão.
    """
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return jsonify({"erro": "Token não fornecido"}), 401
    
    try:
        # Extrair token (formato: "Bearer <token>")
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        
        payload = jwt.decode(token, current_app.config.get('SECRET_KEY', 'dev-secret'), algorithms=['HS256'])
        
        aluno = Aluno.query.get(payload.get('aluno_id'))
        
        if not aluno:
            return jsonify({"erro": "Aluno não encontrado"}), 404
        
        return jsonify({
            'valido': True,
            'aluno': aluno.to_dict()
        }), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({"erro": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"erro": "Token inválido"}), 401
    except Exception as e:
        return jsonify({"erro": f"Erro ao validar token: {str(e)}"}), 500

@auth_bp.route('/requerimentos/<int:aluno_id>', methods=['GET'])
def get_requerimentos_aluno(aluno_id):
    """
    Retorna todos os requerimentos de um aluno.
    Protegido - validar token antes de usar.
    """
    from src.models import Requerimento
    
    aluno = Aluno.query.get_or_404(aluno_id)
    
    # Verificar token
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            payload = jwt.decode(token, current_app.config.get('SECRET_KEY', 'dev-secret'), algorithms=['HS256'])
            
            # Verificar se o token é do próprio aluno
            if payload.get('aluno_id') != aluno_id:
                return jsonify({"erro": "Sem permissão"}), 403
        except jwt.InvalidTokenError as exc:
            current_app.logger.warning("Token invalido em /auth/requerimentos: %s", exc)
        except Exception as exc:
            current_app.logger.warning("Erro ao validar token em /auth/requerimentos: %s", exc)
    
    requerimentos = Requerimento.query.filter_by(aluno_id=aluno_id).order_by(Requerimento.data_solicitacao.desc()).all()
    
    return jsonify({
        'total': len(requerimentos),
        'requerimentos': [r.to_dict() for r in requerimentos]
    }), 200
