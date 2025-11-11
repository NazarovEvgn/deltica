# Скрипт для сборки Windows установщика Deltica
# Запускать: powershell -ExecutionPolicy Bypass -File build-installer.ps1

Write-Host "=== Сборка Windows установщика Deltica ===" -ForegroundColor Cyan
Write-Host ""

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($isAdmin) {
    Write-Host "[OK] Запущено с правами администратора" -ForegroundColor Green
} else {
    Write-Host "[!] Запущено БЕЗ прав администратора" -ForegroundColor Yellow
    Write-Host "    Возможна ошибка с winCodeSign (символические ссылки)" -ForegroundColor Yellow
}
Write-Host ""

# Установка переменных окружения для отключения подписи кода
$env:CSC_IDENTITY_AUTO_DISCOVERY = "false"

# Очистка кэша electron-builder (решает проблему с symbolic links)
$cacheDir = "$env:LOCALAPPDATA\electron-builder\Cache"
if (Test-Path $cacheDir) {
    Write-Host "Очистка кэша electron-builder..." -ForegroundColor Yellow
    Remove-Item -Path $cacheDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Кэш очищен" -ForegroundColor Green
}
Write-Host ""

Write-Host "Запуск electron-builder..." -ForegroundColor Cyan
npm run electron:build:win

Write-Host ""
if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Сборка успешно завершена!" -ForegroundColor Green
    Write-Host "Результаты в: dist-electron\" -ForegroundColor Green
    Write-Host ""
    Get-ChildItem -Path "dist-electron" -Filter "*.exe" | ForEach-Object {
        Write-Host "  - $($_.Name) ($([math]::Round($_.Length/1MB, 2)) MB)" -ForegroundColor White
    }
    Get-ChildItem -Path "dist-electron" -Filter "*.zip" | ForEach-Object {
        Write-Host "  - $($_.Name) ($([math]::Round($_.Length/1MB, 2)) MB)" -ForegroundColor White
    }
} else {
    Write-Host "[ERROR] Сборка завершилась с ошибкой" -ForegroundColor Red
    Write-Host ""
    Write-Host "Решение:" -ForegroundColor Yellow
    Write-Host "1. Запустите PowerShell от имени администратора" -ForegroundColor White
    Write-Host "2. Или включите 'Режим разработчика' в настройках Windows" -ForegroundColor White
    Write-Host "3. Или используйте portable версию: dist-electron\Deltica-Portable-1.0.0.zip" -ForegroundColor White
}
