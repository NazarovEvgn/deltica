# Start Deltica Desktop Application (Electron)
# Запускает backend и Electron desktop приложение

# Установка кодировки UTF-8 для правильного отображения русских символов
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "   Deltica Desktop Application   " -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Проверка Node.js
Write-Host "Проверка Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Node.js не установлен!" -ForegroundColor Red
    Write-Host "Установите Node.js: https://nodejs.org/" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}
Write-Host "[OK] Node.js установлен: $nodeVersion" -ForegroundColor Green

# Проверка Python/uv
Write-Host "Проверка Python/uv..." -ForegroundColor Yellow
$uvVersion = uv --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: uv не установлен!" -ForegroundColor Red
    Write-Host "Установите uv: https://github.com/astral-sh/uv" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}
Write-Host "[OK] uv установлен: $uvVersion" -ForegroundColor Green

Write-Host ""
Write-Host "Запуск приложения..." -ForegroundColor Cyan
Write-Host ""

# Запуск backend в фоне
Write-Host "[1/2] Запуск FastAPI backend..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    uv run uvicorn backend.core.main:app --reload
}

# Ждем 3 секунды чтобы backend успел запуститься
Write-Host "Ожидание запуска backend..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Проверка что backend запустился
$backendReady = $false
for ($i = 1; $i -le 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health/" -UseBasicParsing -TimeoutSec 2 2>$null
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $backendReady) {
    Write-Host "ПРЕДУПРЕЖДЕНИЕ: Backend не отвечает на http://localhost:8000" -ForegroundColor Yellow
    Write-Host "Проверьте логи backend (Job ID: $($backendJob.Id))" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Backend запущен (Job ID: $($backendJob.Id))" -ForegroundColor Green
}

Write-Host ""

# Запуск Electron desktop приложения
Write-Host "[2/2] Запуск Electron desktop приложения..." -ForegroundColor Yellow
Set-Location frontend
npm run electron:dev

# Cleanup при выходе
Write-Host ""
Write-Host "Остановка backend..." -ForegroundColor Yellow
Stop-Job -Job $backendJob
Remove-Job -Job $backendJob
Write-Host "[OK] Backend остановлен" -ForegroundColor Green
Write-Host ""
Write-Host "Приложение закрыто" -ForegroundColor Cyan
