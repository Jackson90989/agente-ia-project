from flask import Blueprint, render_template, jsonify, request
from src.models import Aluno, Requerimento
import os

portal_bp = Blueprint('portal', __name__)


@portal_bp.route('/portal', methods=['GET'])
def portal():
    """Serve portal do aluno"""
    return render_template('portal_aluno.html')


@portal_bp.route('/dashboard-data/<int:aluno_id>', methods=['GET'])
def dashboard_data(aluno_id):
    """Retorna dados do dashboard do aluno"""
    try:
        aluno = Aluno.query.get(aluno_id)
        if not aluno:
            return jsonify({'erro': 'Aluno não encontrado'}), 404

        requerimentos = Requerimento.query.filter_by(aluno_id=aluno_id).all()
        
        dados = {
            'aluno': aluno.to_dict(),
            'requerimentos': [req.to_dict() for req in requerimentos],
            'estatisticas': {
                'total': len(requerimentos),
                'concluidos': sum(1 for r in requerimentos if r.status == 'concluido'),
                'pendentes': sum(1 for r in requerimentos if r.status == 'pendente'),
                'rejeitados': sum(1 for r in requerimentos if r.status == 'rejeitado')
            }
        }
        
        return jsonify(dados), 200
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@portal_bp.route('/adicionar-service-link/<int:requerimento_id>', methods=['POST'])
def adicionar_service_link(requerimento_id):
    """Adiciona link de serviço a um requerimento (para PDFs e downloads)"""
    try:
        req = Requerimento.query.get(requerimento_id)
        if not req:
            return jsonify({'erro': 'Requerimento não encontrado'}), 404
        
        data = request.get_json()
        tipo_link = data.get('tipo')  # 'pdf', 'download', etc
        url = data.get('url')
        
        if not tipo_link or not url:
            return jsonify({'erro': 'Tipo e URL são obrigatórios'}), 400
        
        # Armazenar informação de link (opcional, já que URLs são geradas dinamicamente)
        if not hasattr(req, 'service_links'):
            req.service_links = {}
        
        if req.service_links is None:
            req.service_links = {}
        
        req.service_links[tipo_link] = url
        
        from database import db
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Link adicionado com sucesso'
        }), 200
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@portal_bp.route('/servicos-disponiveis', methods=['GET'])
def servicos_disponiveis():
    """Retorna lista de serviços disponíveis no portal"""
    servicos = [
        {
            'id': 'declaracao',
            'nome': 'Gerar Declarações',
            'icone': '',
            'descricao': 'Solicite declarações acadêmicas',
            'tipos': ['matrícula', 'frequência', 'conclusão']
        },
        {
            'id': 'adicao_materia',
            'nome': 'Adicionar Matérias',
            'icone': '',
            'descricao': 'Adicione novas matérias ao seu currículo',
            'tipos': []
        },
        {
            'id': 'boleto',
            'nome': 'Boletos',
            'icone': '',
            'descricao': 'Visualize e gere boletos de pagamento',
            'tipos': []
        },
        {
            'id': 'transferencia',
            'nome': 'Transferência',
            'icone': '',
            'descricao': 'Solicite transferência entre cursos ou instituições',
            'tipos': []
        },
        {
            'id': 'trancamento',
            'nome': 'Trancamento',
            'icone': '⏸',
            'descricao': 'Solicite trancamento temporário',
            'tipos': []
        },
        {
            'id': 'diploma',
            'nome': 'Diploma',
            'icone': '',
            'descricao': 'Solicite emissão de diploma',
            'tipos': []
        }
    ]
    
    return jsonify(servicos), 200
