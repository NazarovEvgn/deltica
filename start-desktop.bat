@echo off
:: Deltica Desktop Application Launcher (Electron)
:: Запускает backend и Electron desktop приложение

chcp 65001 >nul
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
