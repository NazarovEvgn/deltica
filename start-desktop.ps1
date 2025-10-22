# Start Deltica Desktop Application
# Запускает backend и Tauri desktop приложение

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Deltica Desktop Application" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Проверка Rust
Write-Host "Проверка Rust..." -ForegroundColor Yellow
$rustVersion = rustc --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Rust не установлен!" -ForegroundColor Red
    Write-Host "Установите Rust: https://rustup.rs/" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Rust установлен: $rustVersion" -ForegroundColor Green

# Проверка Node.js
Write-Host "Проверка Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Node.js не установлен!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Node.js установлен: $nodeVersion" -ForegroundColor Green

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
}

Write-Host "[OK] Backend запущен (Job ID: $($backendJob.Id))" -ForegroundColor Green
Write-Host ""

# Запуск Tauri desktop приложения
Write-Host "[2/2] Запуск Tauri desktop приложения..." -ForegroundColor Yellow
Set-Location frontend
npm run tauri:dev

# Cleanup при выходе
Write-Host ""
Write-Host "Остановка backend..." -ForegroundColor Yellow
Stop-Job -Job $backendJob
Remove-Job -Job $backendJob
Write-Host "[OK] Backend остановлен" -ForegroundColor Green
