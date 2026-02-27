"""
Modelo de Aluno
"""
from datetime import datetime, timedelta
from database import db
import bcrypt
import jwt
from flask import current_app


class Aluno(db.Model):
    __tablename__ = 'alunos'
    
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(20), unique=True, nullable=False)
    nome_completo = db.Column(db.String(200), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    rg = db.Column(db.String(20))
    data_nascimento = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    cep = db.Column(db.String(10))
    data_matricula = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='ativo')  # ativo, trancado, formado, cancelado
    
    # Segurança
    senha_hash = db.Column(db.String(255), nullable=True)  # Hash bcrypt da senha
    
    # Relacionamentos
    matriculas = db.relationship('Matricula', backref='aluno', lazy=True, cascade='all, delete-orphan')
    requerimentos = db.relationship('Requerimento', backref='aluno', lazy=True, cascade='all, delete-orphan')
    pagamentos = db.relationship('Pagamento', backref='aluno', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Aluno {self.matricula} - {self.nome_completo}>'
    
    def set_senha(self, senha):
        """Define a senha do aluno (armazena hash bcrypt)"""
        if not senha or len(senha) < 4:
            raise ValueError("Senha deve ter no mínimo 4 caracteres")
        self.senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_senha(self, senha):
        """Verifica se a senha fornecida está correta"""
        if not self.senha_hash or not senha:
            return False
        return bcrypt.checkpw(senha.encode('utf-8'), self.senha_hash.encode('utf-8'))
    
    def gerar_token_jwt(self, expiracao_horas=24):
        """Gera um token JWT para autenticação"""
        payload = {
            'aluno_id': self.id,
            'matricula': self.matricula,
            'exp': datetime.utcnow() + timedelta(hours=expiracao_horas)
        }
        return jwt.encode(payload, current_app.config.get('SECRET_KEY', 'dev-secret'), algorithm='HS256')
    
    def to_dict(self):
        return {
            'id': self.id,
            'matricula': self.matricula,
            'nome_completo': self.nome_completo,
            'cpf': self.cpf,
            'rg': self.rg,
            'data_nascimento': self.data_nascimento.strftime('%Y-%m-%d') if self.data_nascimento else None,
            'email': self.email,
            'telefone': self.telefone,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'cep': self.cep,
            'data_matricula': self.data_matricula.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'tem_senha': self.senha_hash is not None
        }
