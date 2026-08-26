@echo off
echo ==============================================
echo  Iniciando Backend Monolitico (FastAPI)
echo ==============================================
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)
python run.py
pause
