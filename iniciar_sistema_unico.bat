@echo off
REM ============================================
REM  Sistema Agente IA - Inicialização Única
REM  (Apenas o Agente IA - mais simples)
REM ============================================

echo.
echo ╔════════════════════════════════════════════╗
echo ║   🤖 Iniciando Agente IA                  ║
echo ╚════════════════════════════════════════════╝
echo.

REM Verificar se ambiente virtual existe
if not exist "ambiente\Scripts\python.exe" (
    echo ❌ Ambiente virtual não encontrado!
    pause
    exit /b 1
)

echo ✓ Ambiente virtual encontrado
echo.
echo ⏳ Ativando ambiente e iniciando...
echo.

cd agente-ia
call ..\ambiente\Scripts\activate.bat
python agente_ia_inteligente.py

pause
