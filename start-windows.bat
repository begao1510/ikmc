@echo off
title IKMC Math Practice App
echo.
echo ==========================================
echo    Kangaroo IKMC Math Practice App
echo ==========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

:: Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js from nodejs.org
    pause
    exit /b 1
)

:: Install backend dependencies
echo [1/4] Installing Python dependencies...
cd backend
pip install -r requirements.txt -q
echo       Done!

:: Start Flask backend in new window
echo [2/4] Starting backend server...
start "IKMC Backend" cmd /k "python app.py"
timeout /t 2 /nobreak >nul

:: Install frontend deps if needed
cd ..\frontend
if not exist node_modules (
    echo [3/4] Installing Node.js dependencies (first time only)...
    npm install
) else (
    echo [3/4] Node.js dependencies already installed.
)

:: Start frontend
echo [4/4] Starting frontend...
start "IKMC Frontend" cmd /k "npm run dev"
timeout /t 3 /nobreak >nul

:: Open browser
echo.
echo ==========================================
echo  App is starting! Opening browser...
echo  URL: http://localhost:3000
echo ==========================================
start http://localhost:3000
echo.
echo Press any key to close this window.
echo (The app will keep running in its own windows)
pause >nul
