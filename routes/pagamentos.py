from flask import Blueprint, request, jsonify
from database import db
from src.models import Pagamento, Aluno
from datetime import datetime, timedelta

pagamentos_bp = Blueprint('pagamentos', __name__)

def _validar_campos(data, campos_obrigatorios):
    if not isinstance(data, dict):
        return "JSON invalido ou vazio"

    faltando = [campo for campo in campos_obrigatorios if campo not in data]
    if faltando:
        return f"Campos obrigatorios ausentes: {', '.join(faltando)}"

    return None

@pagamentos_bp.route('/', methods=['GET'])
def get_pagamentos():
    """Listar todos os pagamentos"""
    aluno_id = request.args.get('aluno_id')
    status = request.args.get('status')
    
    query = Pagamento.query
    
    if aluno_id:
        query = query.filter_by(aluno_id=aluno_id)
    if status:
        query = query.filter_by(status=status)
    
    pagamentos = query.order_by(Pagamento.data_emissao.desc()).all()
    return jsonify([p.to_dict() for p in pagamentos])

@pagamentos_bp.route('/<int:id>', methods=['GET'])
def get_pagamento(id):
    """Obter um pagamento específico"""
    pagamento = Pagamento.query.get_or_404(id)
    return jsonify(pagamento.to_dict())

@pagamentos_bp.route('/', methods=['POST'])
def create_pagamento():
    """Criar um novo pagamento/boleto"""
    data = request.get_json(silent=True)

    erro = _validar_campos(data, ["aluno_id", "valor", "data_vencimento"])
    if erro:
        return jsonify({"erro": erro}), 400
    
    aluno = Aluno.query.get_or_404(data['aluno_id'])

    try:
        valor = float(data['valor'])
    except (TypeError, ValueError):
        return jsonify({"erro": "valor deve ser numerico"}), 400

    if valor <= 0:
        return jsonify({"erro": "valor deve ser maior que zero"}), 400
    
    # Gerar link de pagamento (simulado)
    link_boleto = f"https://pagamento.escola.edu.br/boleto/{aluno.matricula}/{datetime.now().strftime('%Y%m%d%H%M%S')}"
    codigo_boleto = f"{aluno.matricula.replace('/', '')}{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    try:
        data_vencimento = datetime.strptime(data['data_vencimento'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"erro": "data_vencimento deve estar no formato YYYY-MM-DD"}), 400

    mes_referencia = data.get('mes_referencia')
    if mes_referencia is not None:
        try:
            mes_referencia = int(mes_referencia)
        except (TypeError, ValueError):
            return jsonify({"erro": "mes_referencia deve ser numerico"}), 400

        if mes_referencia < 1 or mes_referencia > 12:
            return jsonify({"erro": "mes_referencia deve estar entre 1 e 12"}), 400

    ano_referencia = data.get('ano_referencia', datetime.now().year)
    try:
        ano_referencia = int(ano_referencia)
    except (TypeError, ValueError):
        return jsonify({"erro": "ano_referencia deve ser numerico"}), 400

    pagamento = Pagamento(
        aluno_id=data['aluno_id'],
        tipo=data.get('tipo', 'boleto_avulso'),
        valor=valor,
        data_vencimento=data_vencimento,
        link_boleto=link_boleto,
        codigo_boleto=codigo_boleto,
        mes_referencia=mes_referencia,
        ano_referencia=ano_referencia
    )
    
    db.session.add(pagamento)
    db.session.commit()
    
    return jsonify(pagamento.to_dict()), 201

@pagamentos_bp.route('/<int:id>/pagar', methods=['POST'])
def confirmar_pagamento(id):
    """Confirmar pagamento de um boleto"""
    pagamento = Pagamento.query.get_or_404(id)
    
    pagamento.status = 'pago'
    pagamento.data_pagamento = datetime.now()
    
    db.session.commit()
    
    return jsonify(pagamento.to_dict())

@pagamentos_bp.route('/aluno/<int:aluno_id>/mensalidades', methods=['POST'])
def gerar_mensalidades(aluno_id):
    """Gerar mensalidades para um aluno"""
    aluno = Aluno.query.get_or_404(aluno_id)
    data = request.get_json(silent=True) or {}
    
    ano = data.get('ano', datetime.now().year)
    semestre = data.get('semestre', 1)
    valor_mensal = data.get('valor_mensal', 500.0)

    if semestre not in [1, 2]:
        return jsonify({"erro": "semestre deve ser 1 ou 2"}), 400

    try:
        ano = int(ano)
    except (TypeError, ValueError):
        return jsonify({"erro": "ano deve ser numerico"}), 400

    try:
        valor_mensal = float(valor_mensal)
    except (TypeError, ValueError):
        return jsonify({"erro": "valor_mensal deve ser numerico"}), 400

    if valor_mensal <= 0:
        return jsonify({"erro": "valor_mensal deve ser maior que zero"}), 400
    
    meses = range(1, 7) if semestre == 1 else range(7, 13)
    pagamentos = []
    
    for mes in meses:
        vencimento = datetime(ano, mes, 10)  # Vencimento dia 10
        if vencimento < datetime.now():
            continue
            
        link_boleto = f"https://pagamento.escola.edu.br/boleto/{aluno.matricula}/{ano}{mes:02d}"
        codigo_boleto = f"{aluno.matricula.replace('/', '')}{ano}{mes:02d}"
        
        pagamento = Pagamento(
            aluno_id=aluno_id,
            tipo='mensalidade',
            valor=valor_mensal,
            data_vencimento=vencimento.date(),
            link_boleto=link_boleto,
            codigo_boleto=codigo_boleto,
            mes_referencia=mes,
            ano_referencia=ano
        )
        
        db.session.add(pagamento)
        pagamentos.append(pagamento)
    
    db.session.commit()
    
    return jsonify([p.to_dict() for p in pagamentos]), 201