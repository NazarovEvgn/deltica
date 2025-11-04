@echo off
chcp 65001 >nul
echo ================================================
echo Установка Deltica Backend как Windows Service
echo ================================================
echo.

REM Проверка прав администратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ОШИБКА: Требуются права администратора!
    echo Запустите этот скрипт от имени администратора.
    pause
    exit /b 1
)

REM Определяем путь к проекту
set PROJECT_DIR=%~dp0..
cd /d "%PROJECT_DIR%"

echo Проект расположен в: %CD%
echo.

REM Проверяем наличие NSSM
if not exist "%~dp0nssm.exe" (
    echo ОШИБКА: nssm.exe не найден!
    echo Скачайте NSSM с https://nssm.cc/download
    echo и поместите nssm.exe в папку deployment\
    pause
    exit /b 1
)

REM Проверяем наличие .env файла
if not exist "%PROJECT_DIR%\.env" (
    echo ПРЕДУПРЕЖДЕНИЕ: Файл .env не найден!
    echo Создайте .env файл на основе .env.example
    echo.
    pause
)

REM Проверяем наличие uv
where uv >nul 2>&1
if %errorLevel% neq 0 (
    echo ОШИБКА: uv не установлен!
    echo Установите uv: pip install uv
    pause
    exit /b 1
)

echo Настройка Windows Service...
echo.

REM Удаляем старую службу если существует
"%~dp0nssm.exe" stop DelticaBackend >nul 2>&1
"%~dp0nssm.exe" remove DelticaBackend confirm >nul 2>&1

REM Устанавливаем новую службу
"%~dp0nssm.exe" install DelticaBackend "%ProgramFiles%\Python313\python.exe"
"%~dp0nssm.exe" set DelticaBackend AppDirectory "%PROJECT_DIR%"
"%~dp0nssm.exe" set DelticaBackend AppParameters "-m uvicorn backend.core.main:app --host 0.0.0.0 --port 8000"
"%~dp0nssm.exe" set DelticaBackend DisplayName "Deltica Backend Service"
"%~dp0nssm.exe" set DelticaBackend Description "Backend API для системы управления метрологическим оборудованием Deltica"
"%~dp0nssm.exe" set DelticaBackend Start SERVICE_AUTO_START
"%~dp0nssm.exe" set DelticaBackend AppStdout "%PROJECT_DIR%\backend\logs\service-stdout.log"
"%~dp0nssm.exe" set DelticaBackend AppStderr "%PROJECT_DIR%\backend\logs\service-stderr.log"
"%~dp0nssm.exe" set DelticaBackend AppRotateFiles 1
"%~dp0nssm.exe" set DelticaBackend AppRotateBytes 10485760

echo.
echo Служба успешно установлена!
echo.

REM Запускаем службу
echo Запуск службы...
"%~dp0nssm.exe" start DelticaBackend

if %errorLevel% equ 0 (
    echo.
    echo ================================================
    echo УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!
    echo ================================================
    echo.
    echo Служба DelticaBackend запущена.
    echo API доступен по адресу: http://localhost:8000
    echo.
    echo Управление службой:
    echo   Запуск:   net start DelticaBackend
    echo   Остановка: net stop DelticaBackend
    echo   Перезапуск: net stop DelticaBackend ^&^& net start DelticaBackend
    echo.
    echo Логи службы: %PROJECT_DIR%\backend\logs\
    echo.
) else (
    echo.
    echo ОШИБКА: Не удалось запустить службу!
    echo Проверьте логи: %PROJECT_DIR%\backend\logs\
    echo.
)

pause
