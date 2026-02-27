from datetime import datetime
import os
import secrets
import string
from database import db
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

class RequerimentoService:

    @staticmethod
    def _randint(min_value, max_value):
        return secrets.randbelow(max_value - min_value + 1) + min_value

    @staticmethod
    def _random_digits(length):
        return ''.join(secrets.choice(string.digits) for _ in range(length))

    @staticmethod
    def _random_nonzero_digit():
        return secrets.choice("123456789")
    
    @staticmethod
    def processar_adicao_materia(requerimento):
        """Processa adição de matéria via MCP (simulado)"""
        # Simulação de integração com MCP
        resultado = {
            'status': 'processado',
            'mensagem': 'Requisição de adição de matéria enviada para o MCP',
            'data_processamento': datetime.now().isoformat(),
            'mcp_response': {
                'codigo': RequerimentoService._randint(1000, 9999),
                'confirmacao': f"MAT-{RequerimentoService._randint(10000, 99999)}"
            }
        }
        
        # Atualizar requerimento
        requerimento.status = 'concluido'
        requerimento.data_processamento = datetime.now()
        db.session.commit()
        
        return resultado
    
    @staticmethod
    def processar_remocao_materia(requerimento):
        """Processa remoção de matéria via MCP (simulado)"""
        resultado = {
            'status': 'processado',
            'mensagem': 'Requisição de remoção de matéria enviada para o MCP',
            'data_processamento': datetime.now().isoformat(),
            'mcp_response': {
                'codigo': RequerimentoService._randint(1000, 9999),
                'confirmacao': f"REM-{RequerimentoService._randint(10000, 99999)}"
            }
        }
        
        requerimento.status = 'concluido'
        requerimento.data_processamento = datetime.now()
        db.session.commit()
        
        return resultado
    
    @staticmethod
    def gerar_declaracao(aluno, tipo_declaracao):
        """Gera uma declaração em PDF"""
        
        # Criar diretório para declarações se não existir
        declaracoes_dir = 'declaracoes'
        if not os.path.exists(declaracoes_dir):
            os.makedirs(declaracoes_dir)
            print(f"Pasta '{declaracoes_dir}' criada automaticamente")
        
        # Limpar o nome do arquivo (remover caracteres especiais)
        matricula_limpa = aluno.matricula.replace('/', '_').replace('\\', '_')
        
        # Nome do arquivo
        filename = f"declaracao_{matricula_limpa}_{tipo_declaracao}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(declaracoes_dir, filename)
        
        # Pegar curso do aluno se existir
        curso_nome = "Não informado"
        if aluno.matriculas and len(aluno.matriculas) > 0:
            curso_nome = aluno.matriculas[0].curso.nome if aluno.matriculas[0].curso else "Não informado"
        
        # Preparar texto da declaração
        texto = f"""
Declaramos para os devidos fins que {aluno.nome_completo}, 
portador(a) do CPF {aluno.cpf}, matriculado(a) sob o número {aluno.matricula},
está regularmente matriculado(a) neste estabelecimento de ensino.

Curso: {curso_nome}
Data de Matrícula: {aluno.data_matricula.strftime('%d/%m/%Y') if aluno.data_matricula else 'Não informada'}

Por ser expressão da verdade, firmamos a presente declaração.
        """
        
        try:
            # Criar PDF
            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            
            # Cabeçalho
            c.setFont("Helvetica-Bold", 16)
            c.drawString(2*cm, height - 2*cm, "ESCOLA MUNICIPAL PROFESSOR JOSÉ DA SILVA")
            
            c.setFont("Helvetica", 12)
            c.drawString(2*cm, height - 3*cm, "CNPJ: 12.345.678/0001-90")
            c.drawString(2*cm, height - 3.5*cm, "Rua das Flores, 123 - Centro - São Paulo/SP")
            
            # Linha divisória
            c.line(2*cm, height - 4*cm, width - 2*cm, height - 4*cm)
            
            # Título da declaração
            c.setFont("Helvetica-Bold", 14)
            titulos = {
                'matricula': 'DECLARAÇÃO DE MATRÍCULA',
                'frequencia': 'DECLARAÇÃO DE FREQUÊNCIA',
                'conclusao': 'DECLARAÇÃO DE CONCLUSÃO'
            }
            c.drawCentredString(width/2, height - 5*cm, titulos.get(tipo_declaracao, 'DECLARAÇÃO'))
            
            # Texto da declaração
            c.setFont("Helvetica", 11)
            y = height - 7*cm
            
            # Quebrar texto em linhas
            linhas = texto.strip().split('\n')
            for linha in linhas:
                linha_limpa = linha.strip()
                if linha_limpa:
                    # Limitar caracteres por linha
                    if len(linha_limpa) > 80:
                        palavras = linha_limpa.split(' ')
                        linha_atual = ""
                        for palavra in palavras:
                            if len(linha_atual) + len(palavra) + 1 <= 80:
                                linha_atual += palavra + " "
                            else:
                                if linha_atual:
                                    c.drawString(2*cm, y, linha_atual.strip())
                                    y -= 0.5*cm
                                linha_atual = palavra + " "
                        if linha_atual:
                            c.drawString(2*cm, y, linha_atual.strip())
                            y -= 0.5*cm
                    else:
                        c.drawString(2*cm, y, linha_limpa)
                        y -= 0.5*cm
                else:
                    y -= 0.3*cm
            
            # Data e assinatura
            y = height - 15*cm
            data_formatada = datetime.now().strftime('%d de %B de %Y').replace(
                'January', 'janeiro').replace('February', 'fevereiro').replace('March', 'março'
            ).replace('April', 'abril').replace('May', 'maio').replace('June', 'junho'
            ).replace('July', 'julho').replace('August', 'agosto').replace('September', 'setembro'
            ).replace('October', 'outubro').replace('November', 'novembro').replace('December', 'dezembro')
            
            c.drawString(2*cm, y, f"São Paulo, {data_formatada}")
            
            y -= 2*cm
            c.line(2*cm, y, 8*cm, y)
            c.setFont("Helvetica", 10)
            c.drawString(2*cm, y - 0.5*cm, "Secretaria Acadêmica")
            
            c.save()
            
            print(f" PDF gerado com sucesso: {filepath}")
            
            return {
                'texto': texto.strip(),
                'pdf_path': filepath,
                'filename': filename,
                'sucesso': True
            }
        except Exception as e:
            print(f" Erro ao gerar PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            # Retornar com informação de erro
            return {
                'texto': texto.strip(),
                'pdf_path': None,
                'filename': None,
                'sucesso': False,
                'erro': str(e)
            }
        
    @staticmethod
    def gerar_boleto(aluno, valor, vencimento):
        """Gera um boleto (simulado com link de pagamento)"""
        
        # Simular integração com gateway de pagamento
        codigo = f"{aluno.matricula.replace('/', '')}{datetime.now().strftime('%Y%m%d%H%M%S')}"
        link = f"https://pagamento.escola.edu.br/pagar/{codigo}"
        
        return {
            'valor': valor,
            'vencimento': vencimento,
            'codigo': codigo,
            'link': link,
            'linha_digitavel': (
                f"{RequerimentoService._random_digits(5)}.{RequerimentoService._random_digits(5)} "
                f"{RequerimentoService._random_digits(5)}.{RequerimentoService._random_digits(5)} "
                f"{RequerimentoService._random_digits(5)}.{RequerimentoService._random_digits(5)} "
                f"{RequerimentoService._random_nonzero_digit()} {RequerimentoService._random_digits(9)}"
            )
        }