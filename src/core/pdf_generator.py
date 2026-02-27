"""
Funções de geração de PDF
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import os


def gerar_declaracao_pdf(tipo_declaracao, dados_aluno, caminho_saida=None):
    """
    Gera um PDF de declaração acadêmica
    
    Args:
        tipo_declaracao: 'matricula', 'frequencia', ou 'conclusao'
        dados_aluno: dicionário com dados do aluno
        caminho_saida: caminho para salvar o PDF
    
    Returns:
        caminho do arquivo gerado
    """
    
    if not caminho_saida:
        os.makedirs('declaracoes', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        caminho_saida = f"declaracoes/declaracao_{dados_aluno['matricula'].replace('/', '_')}_{tipo_declaracao}_{timestamp}.pdf"
    
    # Criar documento PDF
    doc = SimpleDocTemplate(caminho_saida, pagesize=letter)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=1  # center
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        alignment=4  # justify
    )
    
    # Conteúdo
    story.append(Paragraph("DECLARAÇÃO ACADÊMICA", titulo_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # Dados do aluno
    aluno_info = f"""
    <b>Aluno:</b> {dados_aluno.get('nome_completo', 'N/A')}<br/>
    <b>Matrícula:</b> {dados_aluno.get('matricula', 'N/A')}<br/>
    <b>CPF:</b> {dados_aluno.get('cpf', 'N/A')}<br/>
    <b>Email:</b> {dados_aluno.get('email', 'N/A')}<br/>
    """
    story.append(Paragraph(aluno_info, normal_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # Tipo de declaração
    declaracoes = {
        'matricula': 'Declara-se que o(a) aluno(a) acima identificado(a) encontra-se devidamente matriculado(a) nesta instituição.',
        'frequencia': 'Declara-se que o(a) aluno(a) acima identificado(a) encontra-se com frequência regular às aulas.',
        'conclusao': 'Declara-se que o(a) aluno(a) acima identificado(a) concluiu com sucesso o curso.'
    }
    
    conteudo = declaracoes.get(tipo_declaracao, 'Declaração acadêmica.')
    story.append(Paragraph(f"<b>{conteudo}</b>", normal_style))
    story.append(Spacer(1, 0.5 * inch))
    
    # Assinatura
    data_str = datetime.now().strftime('%d de %B de %Y')
    assinatura = f"""
    <br/><br/><br/>
    ____________________________________________<br/>
    Secretaria Acadêmica<br/>
    {data_str}
    """
    story.append(Paragraph(assinatura, normal_style))
    
    # Gerar PDF
    doc.build(story)
    
    return caminho_saida
