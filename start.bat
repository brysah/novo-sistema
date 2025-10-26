@echo off
setlocal

REM ===============================
REM Desativa Quick Edit Mode
REM ===============================
if "%1" neq "noquickedit" (
    start "JointMotion System" cmd /k call "%~f0" noquickedit
    exit /b
)

REM ===============================
REM Configuração inicial
REM ===============================
cd /d "%~dp0"

REM ===============================
REM Detecta comando Python disponível
REM ===============================
set PYTHON_CMD=
where py >nul 2>nul && set PYTHON_CMD=py
if "%PYTHON_CMD%"=="" (
    where python >nul 2>nul && set PYTHON_CMD=python
)
if "%PYTHON_CMD%"=="" (
    where python3 >nul 2>nul && set PYTHON_CMD=python3
)
if "%PYTHON_CMD%"=="" (
    echo ❌ Python não encontrado. Instale o Python e marque a opção "Add to PATH".
    pause
    exit /b
)

echo ===============================
echo  Iniciando sistema...
echo ===============================
echo.

REM ===============================
REM Inicia backend
REM ===============================
echo Iniciando backend...
start "Backend" cmd /k "cd /d "%~dp0backend" && %PYTHON_CMD% main.py"

REM Aguarda 3 segundos antes de iniciar frontend
timeout /t 3 /nobreak >nul

REM ===============================
REM Inicia frontend
REM ===============================
echo Iniciando frontend...
start "Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ===============================
echo  Sistema iniciado com sucesso!
echo ===============================
pause
