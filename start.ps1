# Tournament System Startup Script
Write-Host "🚀 Starting Tournament System - Frontend and Backend" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green

Write-Host ""
Write-Host "📋 Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "🖥️ Starting Backend API Server (Port 8000)..." -ForegroundColor Cyan
Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "python run.py server --port 8000" -WindowStyle Normal

Write-Host ""
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "🌐 Starting Frontend Server (Port 3000)..." -ForegroundColor Cyan
Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "cd frontend; python -m http.server 3000" -WindowStyle Normal

Write-Host ""
Write-Host "✅ Both services are starting up!" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "🚀 Backend:  http://localhost:8000" -ForegroundColor White  
Write-Host "📊 Health:   http://localhost:8000/health" -ForegroundColor White
Write-Host "=====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
