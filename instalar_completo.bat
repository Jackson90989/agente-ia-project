@echo off
REM ============================================
REM  Sistema Agente IA - Instalação Completa
REM ============================================

echo.
echo ╔════════════════════════════════════════════╗
echo ║   📦 Instalação Completa do Sistema       ║
echo ╚════════════════════════════════════════════╝
echo.

REM 1. Criar ambiente virtual
echo [1/4] Criando ambiente virtual...
if exist "ambiente" (
    echo ⚠️  Ambiente virtual já existe, pulando...
) else (
    python -m venv ambiente
    if errorlevel 1 (
        echo ❌ Erro ao criar ambiente virtual!
        pause
        exit /b 1
    )
    echo ✅ Ambiente virtual criado
)
echo.

REM 2. Atualizar pip
echo [2/4] Atualizando pip...
ambiente\Scripts\python.exe -m pip install --upgrade pip wheel setuptools
echo.

REM 3. Instalar dependências da raiz
echo [3/4] Instalando dependências principais...
if exist "requirements.txt" (
    ambiente\Scripts\python.exe -m pip install -r requirements.txt
    echo ✅ Dependências principais instaladas
) else (
    echo ⚠️  requirements.txt não encontrado
)
echo.

REM 4. Instalar dependências do agente-ia
echo [4/4] Instalando dependências do agente-ia...
if exist "agente-ia\requirements.txt" (
    ambiente\Scripts\python.exe -m pip install -r agente-ia\requirements.txt
    echo ✅ Dependências do agente-ia instaladas
) else (
    echo ⚠️  agente-ia\requirements.txt não encontrado
)
echo.

REM Verificar instalações críticas
echo.
echo ════════════════════════════════════════════
echo Verificando instalações...
echo ════════════════════════════════════════════
ambiente\Scripts\python.exe -c "import flask; print('✅ Flask OK')" 2>nul || echo "⚠️  Flask não instalado"
ambiente\Scripts\python.exe -c "import fastmcp; print('✅ FastMCP OK')" 2>nul || echo "⚠️  FastMCP não instalado"
ambiente\Scripts\python.exe -c "import sqlalchemy; print('✅ SQLAlchemy OK')" 2>nul || echo "⚠️  SQLAlchemy não instalado"
ambiente\Scripts\python.exe -c "import requests; print('✅ Requests OK')" 2>nul || echo "⚠️  Requests não instalado"
echo.

echo ════════════════════════════════════════════
echo ✅ Instalação Concluída!
echo ════════════════════════════════════════════
echo.
echo Próximos passos:
echo   1. Execute: iniciar_sistema.bat
echo   2. Ou execute: iniciar_sistema_unico.bat (versão simplificada)
echo.
pause
