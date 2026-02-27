"""
Modelo de Requerimento
"""
from datetime import datetime
from database import db


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
    
    def __repr__(self):
        return f'<Requerimento {self.id} - Aluno {self.aluno_id} - {self.tipo}>'
    
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
