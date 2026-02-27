@echo off
REM ============================================
REM     Sistema Agente IA - Inicialização
REM ============================================

echo.
echo ╔════════════════════════════════════════════╗
echo ║   🚀 Iniciando Sistema Agente IA          ║
echo ╚════════════════════════════════════════════╝
echo.

REM Verificar se ambiente virtual existe
if not exist "ambiente\Scripts\python.exe" (
    echo ❌ Ambiente virtual não encontrado!
    echo.
    echo Execute primeiro:
    echo   python -m venv ambiente
    echo   ambiente\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo ✓ Ambiente virtual encontrado
echo.

REM Aguardar 1 segundo
timeout /t 1 /nobreak >nul

echo 📡 Iniciando Servidor Flask (API)...
start "Flask API Server" cmd /k "cd /d %~dp0 && ambiente\Scripts\activate && python app.py"
timeout /t 3 /nobreak >nul

echo 🔧 Iniciando Servidor MCP (Ferramentas)...
start "MCP Server" cmd /k "cd /d %~dp0agente-ia && ..\ambiente\Scripts\activate && python mcp_escola_server.py"
timeout /t 5 /nobreak >nul

echo 🤖 Iniciando Agente IA...
start "Agente IA" cmd /k "cd /d %~dp0agente-ia && ..\ambiente\Scripts\activate && python agente_ia_inteligente.py"

echo.
echo ✅ Sistema iniciado com sucesso!
echo.
echo 📋 Terminais abertos:
echo    1. Flask API - Backend principal
echo    2. MCP Server - Servidor de ferramentas
echo    3. Agente IA - Interface conversacional
echo.
echo ⚠️  Aguarde alguns segundos para tudo carregar
echo.
echo Para parar: Feche os terminais ou pressione Ctrl+C em cada um
echo.
pause
