@echo off
REM Voice Deepfake Detector - Windows Start Script
REM Starts both backend and frontend servers

echo.
echo ================================================
echo    Voice Deepfake Detector - Starting
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [WARNING] Virtual environment not found. Running setup first...
    call setup.bat
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Start backend in new window
echo [INFO] Starting backend server on http://localhost:5000...
start "Backend Server" cmd /k "cd backend && python app.py"
timeout /t 3 /nobreak >nul
echo [SUCCESS] Backend server started

REM Start frontend in new window
echo [INFO] Starting frontend server on http://localhost:3000...
start "Frontend Server" cmd /k "cd frontend && python -m http.server 3000"
timeout /t 2 /nobreak >nul
echo [SUCCESS] Frontend server started

REM Open browser
echo [INFO] Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:3000

REM Success message
echo.
echo ================================================
echo    Application Running Successfully!
echo ================================================
echo.
echo [INFO] Access the application at:
echo   http://localhost:3000
echo.
echo [INFO] Backend API available at:
echo   http://localhost:5000
echo.
echo [WARNING] Close the terminal windows to stop servers
echo.
pause
