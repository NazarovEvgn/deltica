@echo off
REM Скрипт для одновременного запуска backend и frontend

echo Запуск Deltica...

REM Запуск backend
echo Запуск backend (FastAPI)...
start "Deltica Backend" cmd /k "uv run uvicorn backend.core.main:app --reload"

REM Небольшая задержка
timeout /t 2 /nobreak >nul

REM Запуск frontend
echo Запуск frontend (Vite)...
start "Deltica Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Закройте окна для остановки серверов
