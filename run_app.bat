@echo off
cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo Starting IndigoNode on 0.0.0.0:8501 (reachable from other devices on your network)
echo Open on this PC: http://localhost:8501
echo Open on other devices: http://YOUR_IP:8501
echo.
streamlit run Home.py --server.address 0.0.0.0

pause
