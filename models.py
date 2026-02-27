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


class Requerimento(db.Model):
    __tablename__ = 'requerimentos'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # adicao_materia, remocao_materia, declaracao, etc
    status = db.Column(db.String(20), default='pendente')  # pendente, processando, concluido, rejeitado
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_processamento = db.Column(db.DateTime)
    descricao = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    
    # Campos específicos para adição/remoção de matérias
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'), nullable=True)
    matricula_id = db.Column(db.Integer, db.ForeignKey('matriculas.id'), nullable=True)
    
    # Campos para declaração
    declaracao_tipo = db.Column(db.String(50))  # matricula, frequencia, conclusao
    declaracao_texto = db.Column(db.Text)
    declaracao_assinatura = db.Column(db.String(200))  # Nome do assinante
    declaracao_data_assinatura = db.Column(db.DateTime)
    declaracao_pdf_path = db.Column(db.String(500))
    
    # Campos para boletos
    boleto_valor = db.Column(db.Float)
    boleto_vencimento = db.Column(db.Date)
    boleto_link = db.Column(db.String(500))
    boleto_codigo = db.Column(db.String(100))
    
    # Relacionamentos
    materia = db.relationship('Materia', foreign_keys=[materia_id])
    matricula_rel = db.relationship('Matricula', foreign_keys=[matricula_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'aluno_id': self.aluno_id,
            'aluno_nome': self.aluno.nome_completo if self.aluno else None,
            'tipo': self.tipo,
            'status': self.status,
            'data_solicitacao': self.data_solicitacao.strftime('%Y-%m-%d %H:%M:%S'),
            'data_processamento': self.data_processamento.strftime('%Y-%m-%d %H:%M:%S') if self.data_processamento else None,
            'descricao': self.descricao,
            'observacoes': self.observacoes,
            'materia_id': self.materia_id,
            'materia_nome': self.materia.nome if self.materia else None,
            'declaracao_info': {
                'tipo': self.declaracao_tipo,
                'assinatura': self.declaracao_assinatura,
                'data_assinatura': self.declaracao_data_assinatura.strftime('%Y-%m-%d') if self.declaracao_data_assinatura else None,
                'pdf_path': self.declaracao_pdf_path
            } if self.declaracao_tipo else None,
            'boleto_info': {
                'valor': self.boleto_valor,
                'vencimento': self.boleto_vencimento.strftime('%Y-%m-%d') if self.boleto_vencimento else None,
                'link': self.boleto_link,
                'codigo': self.boleto_codigo
            } if self.boleto_valor is not None else None
        }


class Pagamento(db.Model):
    __tablename__ = 'pagamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    requerimento_id = db.Column(db.Integer, db.ForeignKey('requerimentos.id'), nullable=True)
    tipo = db.Column(db.String(50), nullable=False)  # mensalidade, boleto_avulso, taxa
    valor = db.Column(db.Float, nullable=False)
    data_emissao = db.Column(db.DateTime, default=datetime.utcnow)
    data_vencimento = db.Column(db.Date, nullable=False)
    data_pagamento = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pendente')  # pendente, pago, atrasado, cancelado
    link_boleto = db.Column(db.String(500))
    codigo_boleto = db.Column(db.String(100))
    mes_referencia = db.Column(db.Integer)  # Mês de referência (1-12)
    ano_referencia = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'aluno_id': self.aluno_id,
            'aluno_nome': self.aluno.nome_completo if self.aluno else None,
            'tipo': self.tipo,
            'valor': self.valor,
            'data_emissao': self.data_emissao.strftime('%Y-%m-%d %H:%M:%S'),
            'data_vencimento': self.data_vencimento.strftime('%Y-%m-%d'),
            'data_pagamento': self.data_pagamento.strftime('%Y-%m-%d %H:%M:%S') if self.data_pagamento else None,
            'status': self.status,
            'link_boleto': self.link_boleto,
            'codigo_boleto': self.codigo_boleto,
            'referencia': f"{self.mes_referencia:02d}/{self.ano_referencia}" if self.mes_referencia and self.ano_referencia else None
        }


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    nome_completo = db.Column(db.String(200))
    tipo = db.Column(db.String(20), default='funcionario')  # admin, funcionario, professor
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def generate_token(self):
        payload = {
            'user_id': self.id,
            'username': self.username,
            'tipo': self.tipo,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None