#!/usr/bin/env python3
"""
Quick Start - Agente IA com Geração de Declarações em PDF

Execute este script para iniciar rapidamente todo o sistema.
"""

import os
import sys
import time
import shutil
from subprocess import call, check_call, Popen, run  # nosec B404
from pathlib import Path

def print_header(texto):
    """Imprime um cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"  {texto}")
    print("="*60)

def verificar_ambiente():
    """Verifica se o ambiente está configurado corretamente"""
    print_header(" Verificando Ambiente")
    
    checks = {
        "Python": sys.version.split()[0],
        "Diretório": os.getcwd().split(os.sep)[-1],
    }
    
    # Verificar dependências
    deps = {
        'jinja2': 'Jinja2',
        'weasyprint': 'WeasyPrint',
    }
    
    for modulo, nome in deps.items():
        try:
            __import__(modulo)
            checks[nome] = " Instalado"
        except ImportError:
            checks[nome] = " NÃO instalado"
    
    for chave, valor in checks.items():
        print(f"  {chave}: {valor}")
    
    # Verificar se template existe
    template_paths = [
        r'C:\Users\JacksonRodrigues\Downloads\AgenteIa\templates\declaracao_template.html',
        os.path.join(os.path.dirname(__file__), '..', 'templates', 'declaracao_template.html'),
    ]
    
    template_existe = any(os.path.exists(p) for p in template_paths)
    print(f"  Template HTML: {' Encontrado' if template_existe else ' NÃO encontrado'}")
    
    # Mostrar avisos se necessário
    if checks.get('WeasyPrint') == " NÃO instalado":
        print("\n  WeasyPrint não instalado!")
        print("   Execute: pip install weasyprint")
        print("   Continuando mesmo assim...")
    
    return True

def opcao_instalar_dependencias():
    """Oferece opção de instalar dependências"""
    print_header(" Instalar Dependências?")

    print("  ⏳ Instalando weasyprint e jinja2...")

    # Encontrar python do ambiente virtual
    python_exe = None
    if os.path.exists(r"..\ambiente\Scripts\python.exe"):
        python_exe = r"..\ambiente\Scripts\python.exe"
    elif os.path.exists("./ambiente/bin/python"):
        python_exe = "./ambiente/bin/python"
    else:
        python_exe = sys.executable

    try:
        check_call([python_exe, "-m", "pip", "install", "weasyprint", "jinja2"])  # nosec B603
        print("   Dependências instaladas!")
        return True
    except Exception as e:
        print(f"   Erro ao instalar: {e}")
        return False

def iniciar_mcp_server():
    """Inicia o MCP Server em um novo terminal"""
    print_header(" Iniciando MCP Server")
    
    print("  ⏳ Abrindo novo terminal...")
    
    if sys.platform == "win32":
        try:
            cmd_exe = os.environ.get("ComSpec", "cmd.exe")
            Popen(
                [
                    cmd_exe,
                    "/k",
                    f"cd /d {os.getcwd()} && ..\\.\\ambiente\\Scripts\\python.exe mcp_escola_server.py",
                ],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )  # nosec B603
            print("   MCP Server iniciado")
            time.sleep(2)
            return True
        except Exception as e:
            print(f"   Erro ao iniciar: {e}")
            return False
    else:
        print("  Instrução para Linux/Mac:")
        print("  1. Abra um terminal")
        print("  2. Execute: python mcp_escola_server.py")
        return True

def iniciar_agente():
    """Inicia o Agente IA"""
    print_header(" Iniciando Agente IA")
    
    print("  ⏳ Iniciando agente...")
    
    try:
        call([sys.executable, "agente_ia_inteligente.py"])  # nosec B603
        return True
    except Exception as e:
        print(f"   Erro ao iniciar agente: {e}")
        return False

def menu_principal():
    """Menu principal de opções"""
    while True:
        print_header(" Menu Principal")
        print("""
  1.  Testar Sistema
  2.  Instalar Dependências
  3.  Iniciar MCP Server
  4.  Iniciar Agente IA
  5.  Ver Documentação
  6. 0⃣  Sair
        """)
        
        opcao = input("  Escolha uma opção (0-6): ").strip()
        
        if opcao == "1":
            print("\n  Executando testes...")
            run([sys.executable, "teste_pdf.py"], check=False)  # nosec B603
        
        elif opcao == "2":
            opcao_instalar_dependencias()
        
        elif opcao == "3":
            iniciar_mcp_server()
        
        elif opcao == "4":
            iniciar_agente()
        
        elif opcao == "5":
            print("\n  Documentação disponível:")
            print("  - README_PDF_REAL.md - Guia de uso do PDF")
            print("  - PDF_TEMPLATE_GUIA.md - Detalhes técnicos")
            print("  - AGENTE_MELHORADO.md - Funcionalidades do agente")
            print("\n  Retornando ao menu...")
        
        elif opcao == "0":
            print("\n   Até logo!")
            break
        
        else:
            print("   Opção inválida")

def main():
    """Função principal"""
    if os.name == "nt":
        run([os.environ.get("ComSpec", "cmd.exe"), "/c", "cls"], check=False)  # nosec B603
    else:
        clear_cmd = shutil.which("clear")
        if clear_cmd:
            run([clear_cmd], check=False)  # nosec B603
    
    print("""

    AGENTE IA - SISTEMA DE DECLARAÇÕES EM PDF REAL     
                                                            
  Bem-vindo! Este é o Quick Start para começar de forma    
  rápida e fácil.                                          

    """)
    
    if not verificar_ambiente():
        print("\n Ambiente não está pronto. Abortando...")
        return 1
    
    print("\n Ambiente verificado com sucesso!")
    
    # Menu principal
    menu_principal()
    
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹  Cancelado pelo usuário")
        exit(0)
    except Exception as e:
        print(f"\n Erro: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
