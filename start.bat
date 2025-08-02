@echo off
echo 🚀 Starting Tournament System - Frontend and Backend
echo =====================================================

echo.
echo 📋 Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo 🖥️ Starting Backend API Server (Port 8000)...
start "Backend API" cmd /k "python run.py server --port 8000"

echo.
echo ⏳ Waiting for backend to initialize...
timeout /t 3 /nobreak > nul

echo.
echo 🌐 Starting Frontend Server (Port 3000)...
start "Frontend" cmd /k "cd frontend && python -m http.server 3000"

echo.
echo ✅ Both services are starting up!
echo =====================================================
echo 🌐 Frontend: http://localhost:3000
echo 🚀 Backend:  http://localhost:8000
echo 📊 Health:   http://localhost:8000/health
echo =====================================================
echo.
echo Press any key to continue...
pause > nul
