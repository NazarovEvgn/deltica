@echo off
:: Deltica Desktop Application Launcher
:: Запускает backend и Tauri desktop приложение

title Deltica Desktop

echo ====================================
echo Deltica Desktop Application
echo ====================================
echo.

:: Переход в директорию проекта
cd /d "%~dp0"

:: Запуск PowerShell скрипта
powershell.exe -ExecutionPolicy Bypass -File "%~dp0start-desktop.ps1"

pause
