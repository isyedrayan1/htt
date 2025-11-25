@echo off
echo ========================================
echo   GR-X BLINDSPOT COMMAND - HACKATHON
echo   AI Driver Coaching Platform
echo ========================================
echo.

echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [2/4] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 16+
    pause
    exit /b 1
)

echo [3/4] Starting Backend Server...
start "Backend - FastAPI" cmd /k "cd backend && python -m pip install -r requirements.txt >nul 2>&1 && echo Backend dependencies installed! && uvicorn main:app --reload --port 8000"

timeout /t 5 /nobreak >nul

echo [4/4] Starting Frontend Server...
start "Frontend - React" cmd /k "cd frontend && npm install >nul 2>&1 && echo Frontend dependencies installed! && set PORT=3001 && npm start"

echo.
echo ========================================
echo   SERVERS STARTING...
echo ========================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3001
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to stop all servers...
pause >nul

echo Stopping servers...
taskkill /FI "WINDOWTITLE eq Backend - FastAPI" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend - React" /T /F >nul 2>&1
echo Servers stopped!
