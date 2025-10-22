@echo off
:: Deltica Backend Server
:: Запускает только FastAPI backend

title Deltica Backend Server

echo ====================================
echo Deltica Backend Server
echo ====================================
echo.
echo Запуск на http://localhost:8000
echo Для остановки нажмите Ctrl+C
echo.

cd /d "%~dp0"

:: Запуск backend
uv run uvicorn backend.core.main:app --reload

pause
