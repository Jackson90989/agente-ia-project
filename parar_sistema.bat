@echo off
REM ============================================
REM  Sistema Agente IA - Parar Todos os Processos
REM ============================================

echo.
echo ╔════════════════════════════════════════════╗
echo ║   🛑 Parando Sistema Agente IA            ║
echo ╚════════════════════════════════════════════╝
echo.

echo Procurando processos Python relacionados...
echo.

REM Listar processos Python rodando
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq Flask*" 2>nul | find /I "python.exe" >nul
if %errorlevel% equ 0 (
    echo 🔍 Encontrado: Flask API Server
    taskkill /FI "WINDOWTITLE eq Flask*" /F >nul 2>&1
    echo ✅ Flask API Server parado
)

tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq MCP*" 2>nul | find /I "python.exe" >nul
if %errorlevel% equ 0 (
    echo 🔍 Encontrado: MCP Server
    taskkill /FI "WINDOWTITLE eq MCP*" /F >nul 2>&1
    echo ✅ MCP Server parado
)

tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq Agente*" 2>nul | find /I "python.exe" >nul
if %errorlevel% equ 0 (
    echo 🔍 Encontrado: Agente IA
    taskkill /FI "WINDOWTITLE eq Agente*" /F >nul 2>&1
    echo ✅ Agente IA parado
)

REM Tentar parar processos nas portas específicas
echo.
echo Verificando portas...

REM Porta 5000 (Flask)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING"') do (
    echo 🔍 Processo na porta 5000 (PID: %%a^)
    taskkill /PID %%a /F >nul 2>&1
    echo ✅ Processo na porta 5000 parado
)

REM Porta 8000 (MCP)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo 🔍 Processo na porta 8000 (PID: %%a^)
    taskkill /PID %%a /F >nul 2>&1
    echo ✅ Processo na porta 8000 parado
)

echo.
echo ════════════════════════════════════════════
echo ✅ Todos os processos foram parados!
echo ════════════════════════════════════════════
echo.
pause
