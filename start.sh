#!/bin/bash
echo "🚀 Starting Tournament System - Frontend and Backend"
echo "====================================================="

echo ""
echo "📋 Activating virtual environment..."
source .venv/Scripts/activate

echo ""
echo "🖥️ Starting Backend API Server (Port 8000)..."
gnome-terminal --title="Backend API" -- bash -c "python run.py server --port 8000; exec bash" &

echo ""
echo "⏳ Waiting for backend to initialize..."
sleep 3

echo ""
echo "🌐 Starting Frontend Server (Port 3000)..."
gnome-terminal --title="Frontend" -- bash -c "cd frontend && python -m http.server 3000; exec bash" &

echo ""
echo "✅ Both services are starting up!"
echo "====================================================="
echo "🌐 Frontend: http://localhost:3000"
echo "🚀 Backend:  http://localhost:8000"
echo "📊 Health:   http://localhost:8000/health"
echo "====================================================="
