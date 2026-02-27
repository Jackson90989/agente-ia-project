from flask import Blueprint, request, jsonify, current_app, send_file
import mimetypes
from database import db
from src.models import Requerimento, Aluno, Materia, Matricula
from services.requerimento_service import RequerimentoService
from datetime import datetime
import os

requerimentos_bp = Blueprint('requerimentos', __name__)

def _validar_campos(data, campos_obrigatorios):
    if not isinstance(data, dict):
        return "JSON invalido ou vazio"

    faltando = [campo for campo in campos_obrigatorios if campo not in data]
    if faltando:
        return f"Campos obrigatorios ausentes: {', '.join(faltando)}"

    return None

@requerimentos_bp.route('/', methods=['GET'])
def get_requerimentos():
    """Listar todos os requerimentos"""
    status = request.args.get('status')
    tipo = request.args.get('tipo')
    aluno_id = request.args.get('aluno_id')
    
    query = Requerimento.query
    
    if status:
        query = query.filter_by(status=status)
    if tipo:
        query = query.filter_by(tipo=tipo)
    if aluno_id:
        query = query.filter_by(aluno_id=aluno_id)
    
    requerimentos = query.order_by(Requerimento.data_solicitacao.desc()).all()
    return jsonify([r.to_dict() for r in requerimentos])

@requerimentos_bp.route('/<int:id>', methods=['GET'])
def get_requerimento(id):
    """Obter um requerimento específico"""
    requerimento = Requerimento.query.get_or_404(id)
    return jsonify(requerimento.to_dict())

@requerimentos_bp.route('/adicao-materia', methods=['POST'])
def criar_requerimento_adicao_materia():
    """Criar requerimento para adicionar matéria"""
    data = request.get_json(silent=True)

    erro = _validar_campos(data, ["aluno_id", "materia_id", "matricula_id"])
    if erro:
        return jsonify({"erro": erro}), 400
    
    # Validar dados
    aluno = Aluno.query.get_or_404(data['aluno_id'])
    materia = Materia.query.get_or_404(data['materia_id'])
    matricula = Matricula.query.get_or_404(data['matricula_id'])
    
    requerimento = Requerimento(
        aluno_id=data['aluno_id'],
        tipo='adicao_materia',
        descricao=f"Solicitação de adição da matéria {materia.nome} ({materia.codigo})",
        materia_id=data['materia_id'],
        matricula_id=data['matricula_id']
    )
    
    db.session.add(requerimento)
    db.session.commit()
    
    # Processar via MCP (simulado)
    resultado = RequerimentoService.processar_adicao_materia(requerimento)
    
    return jsonify({
        'requerimento': requerimento.to_dict(),
        'processamento': resultado
    }), 201

@requerimentos_bp.route('/remocao-materia', methods=['POST'])
def criar_requerimento_remocao_materia():
    """Criar requerimento para remover matéria"""
    data = request.get_json(silent=True)

    erro = _validar_campos(data, ["aluno_id", "materia_id"])
    if erro:
        return jsonify({"erro": erro}), 400
    
    aluno = Aluno.query.get_or_404(data['aluno_id'])
    materia = Materia.query.get_or_404(data['materia_id'])
    
    requerimento = Requerimento(
        aluno_id=data['aluno_id'],
        tipo='remocao_materia',
        descricao=f"Solicitação de remoção da matéria {materia.nome} ({materia.codigo})",
        materia_id=data['materia_id'],
        observacoes=data.get('observacoes', '')
    )
    
    db.session.add(requerimento)
    db.session.commit()
    
    resultado = RequerimentoService.processar_remocao_materia(requerimento)
    
    return jsonify({
        'requerimento': requerimento.to_dict(),
        'processamento': resultado
    }), 201

@requerimentos_bp.route('/declaracao', methods=['POST'])
def criar_requerimento_declaracao():
    """Criar requerimento para emitir declaração"""
    data = request.get_json(silent=True)

    erro = _validar_campos(data, ["aluno_id", "declaracao_tipo"])
    if erro:
        return jsonify({"erro": erro}), 400
    
    aluno = Aluno.query.get_or_404(data['aluno_id'])
    
    declaracao_tipo = data['declaracao_tipo']
    if declaracao_tipo not in ["matricula", "frequencia", "conclusao"]:
        return jsonify({"erro": "declaracao_tipo invalido. Use: matricula, frequencia, conclusao"}), 400

    # Gerar declaração
    declaracao = RequerimentoService.gerar_declaracao(aluno, declaracao_tipo)
    
    requerimento = Requerimento(
        aluno_id=data['aluno_id'],
        tipo='declaracao',
        descricao=f"Solicitação de declaração de {declaracao_tipo}",
        declaracao_tipo=declaracao_tipo,
        declaracao_texto=declaracao['texto'],
        declaracao_assinatura=data.get('assinatura', 'Secretaria Acadêmica'),
        declaracao_data_assinatura=datetime.now(),
        declaracao_pdf_path=declaracao.get('pdf_path')
    )
    
    db.session.add(requerimento)
    db.session.commit()
    
    return jsonify(requerimento.to_dict()), 201

@requerimentos_bp.route('/boleto', methods=['POST'])
def criar_requerimento_boleto():
    """Criar requerimento para emitir boleto"""
    data = request.get_json(silent=True)

    erro = _validar_campos(data, ["aluno_id"])
    if erro:
        return jsonify({"erro": erro}), 400
    
    aluno = Aluno.query.get_or_404(data['aluno_id'])
    
    # Gerar boleto via MCP (simulado)
    valor = data.get('valor', 0)
    if valor is not None:
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            return jsonify({"erro": "valor deve ser numerico"}), 400

        if valor < 0:
            return jsonify({"erro": "valor deve ser positivo"}), 400

    vencimento = data.get('vencimento', datetime.now().date())
    if isinstance(vencimento, str):
        try:
            vencimento = datetime.strptime(vencimento, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"erro": "vencimento deve estar no formato YYYY-MM-DD"}), 400

    boleto = RequerimentoService.gerar_boleto(
        aluno,
        valor,
        vencimento
    )
    
    requerimento = Requerimento(
        aluno_id=data['aluno_id'],
        tipo='boleto',
        descricao=f"Solicitação de emissão de boleto - {data.get('motivo', 'Mensalidade')}",
        boleto_valor=boleto['valor'],
        boleto_vencimento=boleto['vencimento'],
        boleto_link=boleto['link'],
        boleto_codigo=boleto['codigo']
    )
    
    db.session.add(requerimento)
    db.session.commit()
    
    return jsonify(requerimento.to_dict()), 201

@requerimentos_bp.route('/<int:id>/processar', methods=['POST'])
def processar_requerimento(id):
    """Processar um requerimento (aprovar/rejeitar)"""
    requerimento = Requerimento.query.get_or_404(id)
    data = request.get_json(silent=True)

    erro = _validar_campos(data, ["status"])
    if erro:
        return jsonify({"erro": erro}), 400
    
    status = data.get('status', 'processando')
    if status not in ["pendente", "processando", "concluido", "rejeitado"]:
        return jsonify({"erro": "status invalido"}), 400

    requerimento.status = status
    requerimento.observacoes = data.get('observacoes', requerimento.observacoes)
    requerimento.data_processamento = datetime.now()
    
    db.session.commit()
    
    return jsonify(requerimento.to_dict())

@requerimentos_bp.route('/<int:id>/pdf', methods=['GET'])
def download_pdf(id):
    """Baixar PDF de um requerimento (declaração)"""
    requerimento = Requerimento.query.get_or_404(id)
    
    # Verificar se é uma declaração e tem PDF
    if requerimento.tipo != 'declaracao':
        return jsonify({"erro": "Requerimento não é uma declaração"}), 400
    
    if not requerimento.declaracao_pdf_path:
        return jsonify({"erro": "PDF não disponível para este requerimento"}), 404
    
    pdf_path = requerimento.declaracao_pdf_path
    
    # Verificar se o arquivo existe
    if not os.path.exists(pdf_path):
        # Tentar regenerar o PDF
        try:
            resultado = RequerimentoService.gerar_declaracao(
                requerimento.aluno, 
                requerimento.declaracao_tipo
            )
            if resultado['sucesso']:
                pdf_path = resultado['pdf_path']
                requerimento.declaracao_pdf_path = pdf_path
                db.session.commit()
            else:
                return jsonify({"erro": "Não foi possível gerar o PDF"}), 500
        except Exception as e:
            return jsonify({"erro": f"Erro ao regenerar PDF: {str(e)}"}), 500
    
    try:
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=os.path.basename(pdf_path)
        )
    except Exception as e:
        return jsonify({"erro": f"Erro ao servir PDF: {str(e)}"}), 500

@requerimentos_bp.route('/<int:id>/visualizar-pdf', methods=['GET'])
def visualizar_pdf(id):
    """Visualizar PDF inline em um requerimento (declaração)"""
    requerimento = Requerimento.query.get_or_404(id)
    
    # Verificar se é uma declaração e tem PDF
    if requerimento.tipo != 'declaracao':
        return jsonify({"erro": "Requerimento não é uma declaração"}), 400
    
    if not requerimento.declaracao_pdf_path:
        return jsonify({"erro": "PDF não disponível para este requerimento"}), 404
    
    pdf_path = requerimento.declaracao_pdf_path
    
    # Verificar se o arquivo existe
    if not os.path.exists(pdf_path):
        # Tentar regenerar o PDF
        try:
            resultado = RequerimentoService.gerar_declaracao(
                requerimento.aluno, 
                requerimento.declaracao_tipo
            )
            if resultado['sucesso']:
                pdf_path = resultado['pdf_path']
                requerimento.declaracao_pdf_path = pdf_path
                db.session.commit()
            else:
                return jsonify({"erro": "Não foi possível gerar o PDF"}), 500
        except Exception as e:
            return jsonify({"erro": f"Erro ao regenerar PDF: {str(e)}"}), 500
    
    try:
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=False
        )
    except Exception as e:
        return jsonify({"erro": f"Erro ao servir PDF: {str(e)}"}), 500