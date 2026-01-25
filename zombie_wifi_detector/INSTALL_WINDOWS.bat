@echo off
echo ===================================================================
echo.
echo        ZOMBIE WIFI DETECTOR - WINDOWS INSTALLER
echo.
echo ===================================================================
echo.
echo This will install and set up everything automatically.
echo.
pause

echo.
echo Step 1: Installing dependencies...
python -m pip install --upgrade Flask Flask-CORS Werkzeug scikit-learn xgboost numpy pandas scipy scapy matplotlib seaborn pyyaml joblib

echo.
echo Step 2: Setting up project...
if not exist "backend" mkdir backend
if not exist "frontend" mkdir frontend
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "models" mkdir models
if not exist "data" mkdir data
if not exist "logs" mkdir logs

echo.
echo Step 3: Training model (this may take 2-3 minutes)...
python main.py setup

echo.
echo Step 4: Setting up backend...
if exist "backend\app_integrated.py" (
    copy backend\app_integrated.py backend\app.py
)

echo.
echo ===================================================================
echo.
echo INSTALLATION COMPLETE!
echo.
echo To start the web application:
echo.
echo    START_WEBAPP.bat
echo.
echo Then open your browser to: http://localhost:5000
echo.
echo ===================================================================
echo.
pause
