@echo off
setlocal
cd /d "%~dp0"

REM Detecta Python
set PYTHON_CMD=
where py >nul 2>nul && set PYTHON_CMD=py
if "%PYTHON_CMD%"=="" (
    where python >nul 2>nul && set PYTHON_CMD=python
)
if "%PYTHON_CMD%"=="" (
    echo ❌ Python não encontrado.
    pause
    exit /b
)

echo Iniciando backend...
start "backend" cmd /k "cd backend && %PYTHON_CMD% main.py"

timeout /t 3 /nobreak >nul

echo Iniciando frontend...
start "frontend" cmd /k "cd frontend && npm run dev"

pause
