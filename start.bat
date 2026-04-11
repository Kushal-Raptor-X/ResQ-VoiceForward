@echo off
REM VoiceForward Startup Script for Windows
REM This script starts all components of the VoiceForward application

echo.
echo 🚀 Starting VoiceForward Application...
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

echo 📦 Installing Backend Dependencies...
cd backend
python -m pip install -r requirements.txt --quiet
cd ..

echo 📦 Installing Real-Time Backend Dependencies...
cd realtime_backend
python -m pip install -r requirements.txt --quiet
cd ..

echo 📦 Installing Frontend Dependencies...
cd frontend
call npm install --silent
cd ..

echo.
echo ✅ All dependencies installed!
echo.
echo 🎯 Starting services...
echo.

REM Start backend
echo 🔧 Starting Main Backend (port 8000)...
cd backend
start "VoiceForward Backend" cmd /k python -m uvicorn main:app --host 0.0.0.0 --port 8000
cd ..

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start real-time backend
echo 🔧 Starting Real-Time Backend (port 8001)...
cd realtime_backend
start "VoiceForward Real-Time Backend" cmd /k python -m uvicorn main:app --host 0.0.0.0 --port 8001
cd ..

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start frontend
echo 🎨 Starting Frontend (port 5173)...
cd frontend
start "VoiceForward Frontend" cmd /k npm run dev
cd ..

echo.
echo ✅ All services started!
echo.
echo 📍 Access points:
echo    Frontend:          http://localhost:5173
echo    Main Backend:      http://localhost:8000
echo    Real-Time Backend: http://localhost:8001
echo.
echo 🔍 Health checks:
echo    Main Backend:      http://localhost:8000/health
echo    Real-Time Backend: http://localhost:8001/health
echo.
echo Press any key to exit...
pause >nul
