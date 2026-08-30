@echo off
echo Starting AI Project Intelligence and Risk Advisor...

:: Go to the directory where this script is located
cd /d "%~dp0"

:: Start Backend in a new window
echo Starting FastAPI Backend...
start "FastAPI Backend" cmd /c "if exist .venv\Scripts\activate.bat (call .venv\Scripts\activate.bat) & cd backend & set PYTHONPATH=. & python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

:: Wait a few seconds to let backend start up before starting frontend
timeout /t 3 /nobreak > nul

:: Start Frontend in this window
echo Starting Streamlit Frontend...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo Starting Streamlit frontend from virtual environment...
    python -m streamlit run app.py
) else (
    echo Starting Streamlit frontend ...
    python -m streamlit run app.py
)

pause
