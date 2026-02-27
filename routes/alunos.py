from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from database import db
from src.models import Aluno, Matricula, Curso
from datetime import datetime

alunos_bp = Blueprint('alunos', __name__)

def _validar_campos(data, campos_obrigatorios):
    if not isinstance(data, dict):
        return "JSON invalido ou vazio"

    faltando = [campo for campo in campos_obrigatorios if campo not in data]
    if faltando:
        return f"Campos obrigatorios ausentes: {', '.join(faltando)}"

    return None

@alunos_bp.route('/', methods=['GET'])
def get_alunos():
    """Listar todos os alunos"""
    alunos = Aluno.query.all()
    return jsonify([aluno.to_dict() for aluno in alunos])

@alunos_bp.route('/<int:id>', methods=['GET'])
def get_aluno(id):
    """Obter um aluno específico"""
    aluno = Aluno.query.get_or_404(id)
    return jsonify(aluno.to_dict())

@alunos_bp.route('/', methods=['POST'])
def create_aluno():
    """Criar um novo aluno"""
    data = request.get_json(silent=True)

    erro = _validar_campos(data, ["nome_completo", "cpf", "data_nascimento", "email"])
    if erro:
        return jsonify({"erro": erro}), 400
    
    # Gerar matrícula automática
    ultimo_aluno = Aluno.query.order_by(Aluno.id.desc()).first()
    if ultimo_aluno:
        ultima_matricula = int(ultimo_aluno.matricula.split('/')[1])
        nova_matricula = f"{datetime.now().year}/{str(ultima_matricula + 1).zfill(5)}"
    else:
        nova_matricula = f"{datetime.now().year}/00001"
    
    try:
        data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"erro": "data_nascimento deve estar no formato YYYY-MM-DD"}), 400

    aluno = Aluno(
        matricula=nova_matricula,
        nome_completo=data['nome_completo'],
        cpf=data['cpf'],
        rg=data.get('rg'),
        data_nascimento=data_nascimento,
        email=data['email'],
        telefone=data.get('telefone'),
        endereco=data.get('endereco'),
        cidade=data.get('cidade'),
        estado=data.get('estado'),
        cep=data.get('cep')
    )
    
    # Definir senha se fornecida
    if data.get('senha'):
        aluno.set_senha(data['senha'])
    
    db.session.add(aluno)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"erro": "CPF ou email ja cadastrado"}), 409
    
    return jsonify(aluno.to_dict()), 201

@alunos_bp.route('/<int:id>', methods=['PUT'])
def update_aluno(id):
    """Atualizar um aluno"""
    aluno = Aluno.query.get_or_404(id)
    data = request.get_json(silent=True)

    erro = _validar_campos(data, [])
    if erro:
        return jsonify({"erro": erro}), 400

    if not data:
        return jsonify({"erro": "Nenhum campo fornecido para atualizar"}), 400
    
    for key, value in data.items():
        if hasattr(aluno, key) and key not in ['id', 'matricula', 'data_matricula']:
            if key == 'data_nascimento' and value:
                try:
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({"erro": "data_nascimento deve estar no formato YYYY-MM-DD"}), 400
            setattr(aluno, key, value)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"erro": "CPF ou email ja cadastrado"}), 409
    return jsonify(aluno.to_dict())

@alunos_bp.route('/<int:id>', methods=['DELETE'])
def delete_aluno(id):
    """Deletar um aluno (soft delete alterando status)"""
    aluno = Aluno.query.get_or_404(id)
    aluno.status = 'cancelado'
    db.session.commit()
    return jsonify({'message': 'Aluno cancelado com sucesso'})

@alunos_bp.route('/<int:id>/matriculas', methods=['GET'])
def get_aluno_matriculas(id):
    """Listar matrículas de um aluno"""
    aluno = Aluno.query.get_or_404(id)
    matriculas = Matricula.query.filter_by(aluno_id=id).all()
    return jsonify([m.to_dict() for m in matriculas])

@alunos_bp.route('/<int:id>/matriculas', methods=['POST'])
def create_matricula(id):
    """Criar uma nova matrícula para o aluno"""
    aluno = Aluno.query.get_or_404(id)
    data = request.get_json(silent=True)

    erro = _validar_campos(data, ["curso_id"])
    if erro:
        return jsonify({"erro": erro}), 400
    
    # Verificar se o curso existe
    curso = Curso.query.get_or_404(data['curso_id'])
    
    matricula = Matricula(
        aluno_id=id,
        curso_id=data['curso_id'],
        ano=data.get('ano', datetime.now().year),
        semestre=data.get('semestre', 1)
    )

    if matricula.semestre not in [1, 2]:
        return jsonify({"erro": "semestre deve ser 1 ou 2"}), 400

    try:
        matricula.ano = int(matricula.ano)
    except (TypeError, ValueError):
        return jsonify({"erro": "ano deve ser numerico"}), 400
    
    db.session.add(matricula)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"erro": "Matricula ja existente para este aluno/curso"}), 409
    
    return jsonify(matricula.to_dict()), 201