"""
Modelos de Matrícula
"""
from datetime import datetime
from database import db


class Matricula(db.Model):
    __tablename__ = 'matriculas'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    semestre = db.Column(db.Integer, nullable=False)  # 1 ou 2
    data_matricula = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='cursando')  # cursando, concluido, trancado
    
    # Relacionamentos
    materias = db.relationship('MatriculaMateria', backref='matricula', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Matricula Aluno {self.aluno_id} - Curso {self.curso_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'aluno_id': self.aluno_id,
            'aluno_nome': self.aluno.nome_completo if self.aluno else None,
            'curso_id': self.curso_id,
            'curso_nome': self.curso.nome if self.curso else None,
            'ano': self.ano,
            'semestre': self.semestre,
            'data_matricula': self.data_matricula.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status
        }


class MatriculaMateria(db.Model):
    __tablename__ = 'matriculas_materias'
    
    id = db.Column(db.Integer, primary_key=True)
    matricula_id = db.Column(db.Integer, db.ForeignKey('matriculas.id'), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'), nullable=False)
    data_matricula = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='cursando')  # cursando, aprovado, reprovado, dispensado
    nota_final = db.Column(db.Float)
    frequencia = db.Column(db.Float)  # Percentual de frequência
    
    def __repr__(self):
        return f'<MatriculaMateria Matrícula {self.matricula_id} - Matéria {self.materia_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'matricula_id': self.matricula_id,
            'materia_id': self.materia_id,
            'materia_nome': self.materia.nome if self.materia else None,
            'status': self.status,
            'nota_final': self.nota_final,
            'frequencia': self.frequencia
        }
