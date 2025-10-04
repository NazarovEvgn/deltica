# Скрипт для одновременного запуска backend и frontend

Write-Host "Запуск Deltica..." -ForegroundColor Green

# Запуск backend в отдельном окне PowerShell
Write-Host "Запуск backend (FastAPI)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; uv run uvicorn backend.core.main:app --reload"

# Небольшая задержка для запуска backend
Start-Sleep -Seconds 2

# Запуск frontend в отдельном окне PowerShell
Write-Host "Запуск frontend (Vite)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host ""
Write-Host "Backend запущен на: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend запущен на: http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "Закройте окна PowerShell, чтобы остановить серверы" -ForegroundColor Green
