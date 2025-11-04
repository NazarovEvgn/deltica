@echo off
chcp 65001 >nul
echo ================================================
echo Удаление Deltica Backend Service
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

REM Проверяем наличие NSSM
if not exist "%~dp0nssm.exe" (
    echo ОШИБКА: nssm.exe не найден!
    pause
    exit /b 1
)

echo Остановка службы...
"%~dp0nssm.exe" stop DelticaBackend

echo Удаление службы...
"%~dp0nssm.exe" remove DelticaBackend confirm

if %errorLevel% equ 0 (
    echo.
    echo ================================================
    echo СЛУЖБА УСПЕШНО УДАЛЕНА!
    echo ================================================
    echo.
) else (
    echo.
    echo Возможно, служба уже была удалена.
    echo.
)

pause
