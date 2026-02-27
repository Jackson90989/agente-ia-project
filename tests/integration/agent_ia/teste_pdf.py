"""
Script de Teste - Geração de Declarações em PDF
Testa se o sistema de geração de PDFs está funcionando corretamente
"""

import sys
import os
from datetime import datetime

# Adicionar o diretório ao path
sys.path.insert(0, os.path.dirname(__file__))

def testar_dependencias():
    """Testa se todas as dependências estão instaladas"""
    print("\n" + "="*60)
    print(" TESTE DE DEPENDÊNCIAS")
    print("="*60)
    
    dependencias = {
        'jinja2': 'Jinja2 (Template Engine)',
        'weasyprint': 'WeasyPrint (HTML to PDF)',
        'reportlab': 'ReportLab (PDF alternativo)',
    }
    
    faltando = []
    for modulo, nome in dependencias.items():
        try:
            __import__(modulo)
            print(f" {nome}: Instalado")
        except ImportError:
            print(f" {nome}: NÃO instalado")
            faltando.append(modulo)
    
    if faltando:
        print(f"\n  Pacotes faltando: {', '.join(faltando)}")
        print("\nPara instalar, execute:")
        print(f"  pip install {' '.join(faltando)}")
        return False
    
    print("\n Todas as dependências estão instaladas!")
    return True

def testar_template():
    """Testa se o template HTML existe e pode ser carregado"""
    print("\n" + "="*60)
    print(" TESTE DE TEMPLATE")
    print("="*60)
    
    possibles = [
        r'C:\Users\JacksonRodrigues\Downloads\AgenteIa\templates\declaracao_template.html',
        os.path.join(os.path.dirname(__file__), '..', 'templates', 'declaracao_template.html'),
        'templates/declaracao_template.html',
    ]
    
    for path in possibles:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f" Template encontrado: {path}")
                    print(f"   Tamanho: {len(content)} bytes")
                    print(f"   Variáveis detectadas: ", end="")
                    
                    # Detectar variáveis do template
                    import re
                    variaveis = set(re.findall(r'\{\{[\s]?(\w+)[\s]?\}\}', content))
                    if variaveis:
                        print(", ".join(list(variaveis)[:5]) + "...")
                    else:
                        print("(nenhuma encontrada)")
                    
                    return True
            except Exception as e:
                print(f" Erro ao ler template: {e}")
                return False
    
    print(f" Template não encontrado em nenhum dos locais:")
    for path in possibles:
        print(f"   - {path}")
    return False

def testar_geracao_pdf():
    """Testa a geração de um PDF de exemplo"""
    print("\n" + "="*60)
    print(" TESTE DE GERAÇÃO DE PDF")
    print("="*60)
    
    try:
        from jinja2 import Template
        print(" Jinja2 importado com sucesso")
    except ImportError:
        print(" Falha ao importar Jinja2")
        return False
    
    try:
        from weasyprint import HTML
        print(" WeasyPrint importado com sucesso")
    except ImportError:
        print("  WeasyPrint não disponível, tentando alternativa...")
        try:
            from reportlab.pdfgen import canvas
            print(" ReportLab disponível como alternativa")
        except ImportError:
            print(" Nenhuma biblioteca de PDF disponível!")
            return False
    
    # Criar um HTML simples de teste
    html_teste = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Teste PDF</title>
        <style>
            body { font-family: Arial; margin: 2cm; }
            .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }
            .content { margin: 30px 0; text-align: justify; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Declaração de Teste</h1>
        </div>
        <div class="content">
            <p>Este é um PDF gerado automaticamente para teste.</p>
            <p><strong>Data:</strong> {{ data }}</p>
            <p><strong>Aluno:</strong> {{ aluno_nome }}</p>
            <p><strong>Matrícula:</strong> {{ aluno_matricula }}</p>
        </div>
    </body>
    </html>
    """
    
    # Renderizar com dados de teste
    template = Template(html_teste)
    html_renderizado = template.render(
        data=datetime.now().strftime('%d/%m/%Y %H:%M'),
        aluno_nome='João Silva (Teste)',
        aluno_matricula='TEST-001'
    )
    
    # Tentar gerar PDF
    try:
        from weasyprint import HTML
        
        # Criar diretório de teste
        test_dir = 'teste_pdf'
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
        
        arquivo_teste = os.path.join(test_dir, 'teste_geracao.pdf')
        HTML(string=html_renderizado).write_pdf(arquivo_teste)
        
        if os.path.exists(arquivo_teste):
            tamanho = os.path.getsize(arquivo_teste)
            print(f" PDF gerado com sucesso!")
            print(f"   Arquivo: {arquivo_teste}")
            print(f"   Tamanho: {tamanho} bytes")
            return True
        else:
            print(" PDF não foi criado")
            return False
            
    except Exception as e:
        print(f" Erro ao gerar PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("\n")
    print("" + "="*58 + "")
    print("  TESTE COMPLETO - SISTEMA DE GERAÇÃO DE DECLARAÇÕES  ")
    print("" + "="*58 + "")
    
    resultados = {
        "Dependências": testar_dependencias(),
        "Template HTML": testar_template(),
        "Geração de PDF": testar_geracao_pdf(),
    }
    
    print("\n" + "="*60)
    print(" RESUMO DOS TESTES")
    print("="*60)
    
    for teste, resultado in resultados.items():
        status = " PASSOU" if resultado else " FALHOU"
        print(f"{teste}: {status}")
    
    total = sum(1 for r in resultados.values() if r)
    print(f"\nTotal: {total}/{len(resultados)} testes passaram")
    
    if all(resultados.values()):
        print("\n Todos os testes passaram! Sistema pronto para uso!")
        print("\nPróximo passo:")
        print("  1. Execute: python mcp_escola_server.py")
        print("  2. Em outro terminal: python agente_ia_inteligente.py")
        print("  3. Digite seu ID de aluno e solicite uma declaração!")
        return 0
    else:
        print("\n  Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    exit(main())
