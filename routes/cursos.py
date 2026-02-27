from flask import Blueprint, request, jsonify
from database import db
from src.models import Curso

cursos_bp = Blueprint('cursos', __name__)

@cursos_bp.route('/', methods=['GET'])
def get_cursos():
    """Listar todos os cursos"""
    cursos = Curso.query.all()
    return jsonify([c.to_dict() for c in cursos])

@cursos_bp.route('/<int:id>', methods=['GET'])
def get_curso(id):
    """Obter um curso específico"""
    curso = Curso.query.get_or_404(id)
    return jsonify(curso.to_dict())

@cursos_bp.route('/<string:codigo>', methods=['GET'])
def get_curso_by_codigo(codigo):
    """Obter um curso pelo código"""
    curso = Curso.query.filter_by(codigo=codigo).first_or_404()
    return jsonify(curso.to_dict())
