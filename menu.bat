@echo off
chcp 65001 >nul
REM ============================================
REM    Sistema Agente IA - Menu Principal
REM ============================================

:menu
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║        🤖 Sistema Agente IA               ║
echo ║           Menu Principal                  ║
echo ╚════════════════════════════════════════════╝
echo.
echo  [1] 📦 Instalar/Configurar Sistema
echo  [2] 🚀 Iniciar Sistema Completo (3 terminais)
echo  [3] 🤖 Iniciar Apenas Agente IA
echo  [4] 🛑 Parar Todos os Processos
echo  [5] 📖 Abrir Guia Rápido
echo  [6] 🔍 Verificar Status
echo  [0] ❌ Sair
echo.
echo ════════════════════════════════════════════
set /p opcao="Escolha uma opção: "

if "%opcao%"=="1" goto instalar
if "%opcao%"=="2" goto iniciar_completo
if "%opcao%"=="3" goto iniciar_unico
if "%opcao%"=="4" goto parar
if "%opcao%"=="5" goto guia
if "%opcao%"=="6" goto status
if "%opcao%"=="0" goto sair
goto menu

:instalar
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║   📦 Instalando Sistema...                ║
echo ╚════════════════════════════════════════════╝
echo.
call instalar_completo.bat
goto menu

:iniciar_completo
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║   🚀 Iniciando Sistema Completo...        ║
echo ╚════════════════════════════════════════════╝
echo.
call iniciar_sistema.bat
goto menu

:iniciar_unico
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║   🤖 Iniciando Agente IA...               ║
echo ╚════════════════════════════════════════════╝
echo.
call iniciar_sistema_unico.bat
goto menu

:parar
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║   🛑 Parando Sistema...                   ║
echo ╚════════════════════════════════════════════╝
echo.
call parar_sistema.bat
goto menu

:guia
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║   📖 Abrindo Guia Rápido...               ║
echo ╚════════════════════════════════════════════╝
echo.
if exist "GUIA_RAPIDO.md" (
    start notepad GUIA_RAPIDO.md
    echo ✅ Guia aberto no Notepad
) else (
    echo ❌ Arquivo GUIA_RAPIDO.md não encontrado
)
echo.
pause
goto menu

:status
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║   🔍 Verificando Status do Sistema        ║
echo ╚════════════════════════════════════════════╝
echo.

REM Verificar ambiente virtual
if exist "ambiente\Scripts\python.exe" (
    echo ✅ Ambiente virtual instalado
) else (
    echo ❌ Ambiente virtual NÃO encontrado
    echo    Execute a opção 1 (Instalar/Configurar)
)

REM Verificar processos rodando
echo.
echo Processos Python ativos:
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq Flask*" 2>nul | find /I "python.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ Flask API Server rodando
) else (
    echo ⚪ Flask API Server não está rodando
)

tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq MCP*" 2>nul | find /I "python.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ MCP Server rodando
) else (
    echo ⚪ MCP Server não está rodando
)

tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq Agente*" 2>nul | find /I "python.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ Agente IA rodando
) else (
    echo ⚪ Agente IA não está rodando
)

REM Verificar portas
echo.
echo Portas em uso:
netstat -ano | findstr ":5000.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Porta 5000 (Flask) em uso
) else (
    echo ⚪ Porta 5000 livre
)

netstat -ano | findstr ":8000.*LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Porta 8000 (MCP) em uso
) else (
    echo ⚪ Porta 8000 livre
)

echo.
echo ════════════════════════════════════════════
pause
goto menu

:sair
cls
echo.
echo 👋 Até logo!
echo.
timeout /t 1 /nobreak >nul
exit

