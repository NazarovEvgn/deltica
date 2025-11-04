@echo off
chcp 65001 >nul
echo ================================================
echo Применение миграций базы данных Deltica
echo ================================================
echo.

REM Определяем путь к проекту
set PROJECT_DIR=%~dp0..
cd /d "%PROJECT_DIR%"

echo Проект расположен в: %CD%
echo.

REM Проверяем наличие .env файла
if not exist "%PROJECT_DIR%\.env" (
    echo ОШИБКА: Файл .env не найден!
    echo Создайте .env файл на основе .env.example
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

echo Проверка текущей версии БД...
uv run alembic current
echo.

echo Применение миграций...
uv run alembic upgrade head

if %errorLevel% equ 0 (
    echo.
    echo ================================================
    echo МИГРАЦИИ ПРИМЕНЕНЫ УСПЕШНО!
    echo ================================================
    echo.
    echo Текущая версия БД:
    uv run alembic current
    echo.
) else (
    echo.
    echo ОШИБКА: Не удалось применить миграции!
    echo Проверьте подключение к PostgreSQL и настройки .env
    echo.
)

pause
