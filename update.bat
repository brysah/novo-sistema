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
    echo ❌ Python não encontrado. Instale o Python e marque "Add to PATH".
    pause
    exit /b
)

echo ===============================
echo  Atualizando sistema...
echo ===============================

git fetch origin main
git reset --hard origin/main

cd backend
%PYTHON_CMD% -m pip install -r requirements.txt
%PYTHON_CMD% -m playwright install chromium

cd ../frontend
npm install --legacy-peer-deps

echo.
echo ===============================
echo  Atualização concluída!
echo ===============================
pause
