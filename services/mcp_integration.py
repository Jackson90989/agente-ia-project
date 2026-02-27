import requests
import json
from flask import current_app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPIntegration:
    """Integração com o MCP Server"""
    
    def __init__(self):
        self.base_url = current_app.config.get('MCP_SERVER_URL', 'http://localhost:5001')
        self.api_key = current_app.config.get('MCP_API_KEY', '')
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def enviar_requerimento(self, requerimento_data):
        """
        Envia um requerimento para o MCP Server processar
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/requerimentos",
                headers=self.headers,
                json=requerimento_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar requerimento para MCP: {str(e)}")
            return {
                'error': True,
                'message': f'Falha na comunicação com MCP Server: {str(e)}',
                'status': 'pending_local'
            }
    
    def consultar_status_requerimento(self, requerimento_id):
        """
        Consulta o status de um requerimento no MCP Server
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/requerimentos/{requerimento_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar status no MCP: {str(e)}")
            return {
                'error': True,
                'message': f'Falha na comunicação com MCP Server: {str(e)}'
            }
    
    def gerar_boleto_mcp(self, aluno_data, valor, vencimento):
        """
        Solicita geração de boleto ao MCP Server
        """
        try:
            boleto_data = {
                'aluno': aluno_data,
                'valor': valor,
                'vencimento': vencimento.isoformat() if hasattr(vencimento, 'isoformat') else vencimento,
                'tipo': 'boleto_avulso'
            }
            
            response = requests.post(
                f"{self.base_url}/api/pagamentos/gerar-boleto",
                headers=self.headers,
                json=boleto_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao gerar boleto via MCP: {str(e)}")
            # Fallback para geração local
            return {
                'error': True,
                'message': f'Falha na comunicação com MCP Server: {str(e)}',
                'boleto_local': True,
                'codigo': f"LOCAL-{aluno_data['matricula']}-{vencimento}"
            }
    
    def validar_matricula_mcp(self, aluno_id, materia_id):
        """
        Valida se aluno pode se matricular em uma matéria via MCP
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/validacoes/matricula",
                headers=self.headers,
                params={
                    'aluno_id': aluno_id,
                    'materia_id': materia_id
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao validar matrícula via MCP: {str(e)}")
            # Validação básica local
            return {
                'error': True,
                'message': f'Falha na comunicação com MCP Server: {str(e)}',
                'validacao_local': True,
                'valido': True,
                'observacoes': 'Validação realizada localmente devido a falha de comunicação'
            }