from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from database import db
from src.models import Materia, Curso, MatriculaMateria

materias_bp = Blueprint('materias', __name__)

def _validar_campos(data, campos_obrigatorios):
    if not isinstance(data, dict):
        return "JSON invalido ou vazio"

    faltando = [campo for campo in campos_obrigatorios if campo not in data]
    if faltando:
        return f"Campos obrigatorios ausentes: {', '.join(faltando)}"

    return None

@materias_bp.route('/', methods=['GET'])
def get_materias():
    """Listar todas as matérias"""
    materias = Materia.query.all()
    return jsonify([m.to_dict() for m in materias])

@materias_bp.route('/<int:id>', methods=['GET'])
def get_materia(id):
    """Obter uma matéria específica"""
    materia = Materia.query.get_or_404(id)
    return jsonify(materia.to_dict())

@materias_bp.route('/', methods=['POST'])
def create_materia():
    """Criar uma nova matéria"""
    data = request.get_json(silent=True)

    erro = _validar_campos(data, ["nome", "codigo", "curso_id"])
    if erro:
        return jsonify({"erro": erro}), 400
    
    # Verificar se o curso existe
    curso = Curso.query.get_or_404(data['curso_id'])
    
    materia = Materia(
        nome=data['nome'],
        codigo=data['codigo'],
        carga_horaria=data.get('carga_horaria'),
        creditos=data.get('creditos'),
        semestre=data.get('semestre'),
        curso_id=data['curso_id'],
        professor=data.get('professor'),
        ementa=data.get('ementa')
    )
    
    db.session.add(materia)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"erro": "Codigo de materia ja cadastrado"}), 409
    
    return jsonify(materia.to_dict()), 201

@materias_bp.route('/<int:id>', methods=['PUT'])
def update_materia(id):
    """Atualizar uma matéria"""
    materia = Materia.query.get_or_404(id)
    data = request.get_json(silent=True)

    erro = _validar_campos(data, [])
    if erro:
        return jsonify({"erro": erro}), 400

    if not data:
        return jsonify({"erro": "Nenhum campo fornecido para atualizar"}), 400
    
    for key, value in data.items():
        if hasattr(materia, key) and key not in ['id', 'codigo']:
            setattr(materia, key, value)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"erro": "Codigo de materia ja cadastrado"}), 409
    return jsonify(materia.to_dict())

@materias_bp.route('/<int:id>/alunos', methods=['GET'])
def get_materia_alunos(id):
    """Listar alunos matriculados em uma matéria"""
    materia = Materia.query.get_or_404(id)
    matriculas = MatriculaMateria.query.filter_by(materia_id=id).all()
    
    alunos = []
    for mm in matriculas:
        if mm.matricula and mm.matricula.aluno:
            alunos.append({
                'aluno_id': mm.matricula.aluno.id,
                'aluno_nome': mm.matricula.aluno.nome_completo,
                'matricula_aluno': mm.matricula.aluno.matricula,
                'status': mm.status,
                'nota': mm.nota_final,
                'frequencia': mm.frequencia
            })
    
    return jsonify(alunos)