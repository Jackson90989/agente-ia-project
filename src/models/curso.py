"""
Modelo de Curso
"""
from database import db


class Curso(db.Model):
    __tablename__ = 'cursos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    duracao_semestres = db.Column(db.Integer, nullable=False)
    carga_horaria_total = db.Column(db.Integer)
    valor_mensalidade = db.Column(db.Float, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    materias = db.relationship('Materia', backref='curso', lazy=True)
    matriculas = db.relationship('Matricula', backref='curso', lazy=True)
    
    def __repr__(self):
        return f'<Curso {self.codigo} - {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'codigo': self.codigo,
            'descricao': self.descricao,
            'duracao_semestres': self.duracao_semestres,
            'carga_horaria_total': self.carga_horaria_total,
            'valor_mensalidade': self.valor_mensalidade,
            'ativo': self.ativo
        }
