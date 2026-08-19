@echo off
cd /d "%~dp0"
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo Starting Streamlit frontend from virtual environment...
    python -m streamlit run app.py
) else (
    echo Starting Streamlit frontend ...
    python -m streamlit run app.py
)
pause

