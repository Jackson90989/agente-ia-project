"""
Modelo de Pagamento
"""
from datetime import datetime
from database import db


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
    
    def __repr__(self):
        return f'<Pagamento {self.id} - Aluno {self.aluno_id} - R${self.valor}>'
    
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
