@echo off
REM Voice Deepfake Detector - Windows Setup Script
REM This script sets up the entire application with one command

echo.
echo ================================================
echo    Voice Deepfake Detector - Setup
echo    AI-Powered Audio Authentication
echo ================================================
echo.

REM Check Python installation
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)
echo [SUCCESS] Python found

REM Check pip
echo [INFO] Checking pip installation...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed. Please install pip.
    pause
    exit /b 1
)
echo [SUCCESS] pip found

REM Create virtual environment
echo [INFO] Setting up Python virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [WARNING] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install backend dependencies
echo [INFO] Installing backend dependencies...
cd backend
pip install --upgrade pip

REM Try to install with TensorFlow first
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [WARNING] TensorFlow installation failed - using lightweight version
    echo [INFO] Installing lightweight dependencies...
    pip install -r requirements-lite.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [SUCCESS] Lightweight dependencies installed (without TensorFlow)
    echo [INFO] The app will use Random Forest instead of CNN
) else (
    echo [SUCCESS] Backend dependencies installed (with TensorFlow)
)

REM Initialize model
echo [INFO] Initializing ML model...
python -c "from model import DeepfakeDetector; detector = DeepfakeDetector(); print('Model initialized successfully')"
if errorlevel 1 (
    echo [ERROR] Failed to initialize model
    pause
    exit /b 1
)
echo [SUCCESS] ML model initialized

cd ..

REM Setup complete
echo.
echo ================================================
echo            Setup Complete!
echo ================================================
echo.
echo [INFO] To start the application, run:
echo   start.bat
echo.
echo [INFO] Or manually start components:
echo   Backend:  cd backend ^&^& python app.py
echo   Frontend: cd frontend ^&^& python -m http.server 3000
echo.
echo [WARNING] The model is initialized with random weights.
echo [WARNING] For production use, train the model on real datasets:
echo   - ASVspoof 2019
echo   - FakeAVCeleb
echo   - WaveFake
echo.
pause
