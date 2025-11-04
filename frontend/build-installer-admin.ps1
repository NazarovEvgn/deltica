# Скрипт для сборки установщика с правами администратора
# Запускать через: PowerShell -ExecutionPolicy Bypass -File build-installer-admin.ps1

Write-Host "Запуск сборки Electron установщика..." -ForegroundColor Cyan
Write-Host "Этот скрипт должен быть запущен с правами администратора" -ForegroundColor Yellow
Write-Host ""

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ВНИМАНИЕ: Скрипт запущен БЕЗ прав администратора" -ForegroundColor Red
    Write-Host "Для решения проблемы с winCodeSign рекомендуется запуск от администратора" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Продолжить без прав администратора? (y/n)"
    if ($continue -ne 'y') {
        exit
    }
}

# Установка переменных окружения
$env:CSC_IDENTITY_AUTO_DISCOVERY = "false"
$env:DEBUG = "electron-builder"

Write-Host "Переменные окружения установлены:" -ForegroundColor Green
Write-Host "  CSC_IDENTITY_AUTO_DISCOVERY=false"
Write-Host ""

# Переход в директорию frontend
Set-Location -Path $PSScriptRoot\..

Write-Host "Запуск npm run electron:build:win..." -ForegroundColor Cyan
npm run electron:build:win

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Сборка успешно завершена!" -ForegroundColor Green
    Write-Host "Установщики находятся в: frontend\dist-electron\" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Сборка завершилась с ошибкой (код: $LASTEXITCODE)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Нажмите любую клавишу для выхода..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
