@echo off
REM Script para instalar dependências do Agente IA

echo ============================================
echo Instalando Dependências do Agente IA
echo ============================================
echo.

REM Verificar se ambiente virtual existe
if not exist "..\ambiente\Scripts\python.exe" (
    echo ❌ Ambiente virtual não encontrado!
    echo Execute: python -m venv ambiente
    pause
    exit /b 1
)

echo ✓ Ambiente virtual encontrado

REM Adicionar weasyprint, jinja2 e outras dependências
echo.
echo ⏳ Instalando weasyprint (pode levar alguns minutos)...
..\ambiente\Scripts\python.exe -m pip install --upgrade pip wheel setuptools
..\ambiente\Scripts\python.exe -m pip install weasyprint==60.1 jinja2==3.1.2

echo.
echo ⏳ Instalando outras dependências...
..\ambiente\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo ✅ Dependências instaladas com sucesso!

REM Verificar instalação
echo.
echo Verificando instalação...
..\ambiente\Scripts\python.exe -c "import weasyprint; print('✅ WeasyPrint OK')" 2>nul || echo "⚠️  WeasyPrint não instalado corretamente"
..\ambiente\Scripts\python.exe -c "import jinja2; print('✅ Jinja2 OK')" 2>nul || echo "⚠️  Jinja2 não instalado corretamente"

echo.
echo ============================================
echo Pronto! Agora você pode rodar:
echo - MCP Server: python mcp_escola_server.py
echo - Agente IA: python agente_ia_inteligente.py
echo ============================================
pause
