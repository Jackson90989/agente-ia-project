"""
Modelo de Matéria
"""
from database import db


class Materia(db.Model):
    __tablename__ = 'materias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    carga_horaria = db.Column(db.Integer)
    creditos = db.Column(db.Integer)
    semestre = db.Column(db.Integer)  # Semestre recomendado
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    professor = db.Column(db.String(100))
    ementa = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    matriculas_materias = db.relationship('MatriculaMateria', backref='materia', lazy=True)
    
    def __repr__(self):
        return f'<Materia {self.codigo} - {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'codigo': self.codigo,
            'carga_horaria': self.carga_horaria,
            'creditos': self.creditos,
            'semestre': self.semestre,
            'curso_id': self.curso_id,
            'curso_nome': self.curso.nome if self.curso else None,
            'professor': self.professor,
            'ativo': self.ativo
        }
