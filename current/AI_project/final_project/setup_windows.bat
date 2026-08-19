@echo off
cd /d "%~dp0"
echo Creating Python virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

cd backend
set PYTHONPATH=.
python -m app.ml.train
python scripts/seed.py
cd ..
echo.
echo Setup complete. Start backend with start_backend.bat and frontend with start_streamlit.bat
pause
