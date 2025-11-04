@echo off
chcp 65001 >nul
echo ================================================
echo Синхронизация пользователей Deltica
echo ================================================
echo.

REM Определяем путь к проекту
set PROJECT_DIR=%~dp0..
cd /d "%PROJECT_DIR%"

echo Проект расположен в: %CD%
echo.

REM Проверяем наличие конфига пользователей
if not exist "%PROJECT_DIR%\config\users_config.yaml" (
    echo ОШИБКА: Файл config\users_config.yaml не найден!
    pause
    exit /b 1
)

REM Проверяем наличие uv
where uv >nul 2>&1
if %errorLevel% neq 0 (
    echo ОШИБКА: uv не установлен!
    echo Установите uv: pip install uv
    pause
    exit /b 1
)

echo Синхронизация пользователей из config\users_config.yaml...
echo.

uv run python backend/scripts/sync_users.py

if %errorLevel% equ 0 (
    echo.
    echo ================================================
    echo СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА!
    echo ================================================
    echo.
) else (
    echo.
    echo ОШИБКА: Не удалось синхронизировать пользователей!
    echo.
)

pause
