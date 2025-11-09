# ═══════════════════════════════════════════════════════════
# Deltica Update Builder - Создание пакета обновлений
# ═══════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Deltica Update Builder v1.0" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Проверка, что скрипт запущен из корня проекта
if (-not (Test-Path ".\backend") -or -not (Test-Path ".\frontend")) {
    Write-Host "ОШИБКА: Запустите скрипт из корня проекта" -ForegroundColor Red
    exit 1
}

# Получение версии
$version = "1.0.0"
if (Test-Path "pyproject.toml") {
    $content = Get-Content "pyproject.toml" -Raw
    if ($content -match 'version\s*=\s*"([^"]+)"') {
        $version = $matches[1]
    }
}

Write-Host "Создание пакета обновления для версии: $version" -ForegroundColor Green
Write-Host ""

# ═══════════════════════════════════════════════════════════
# Шаг 1: Сборка server и client компонентов
# ═══════════════════════════════════════════════════════════
Write-Host "[1/4] Сборка компонентов обновления..." -ForegroundColor Yellow
Write-Host ""

# Собираем server
Write-Host "  Запуск build-server.ps1..." -ForegroundColor Gray
& ".\build-scripts\build-server.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Сборка сервера не удалась" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "  Запуск build-client.ps1..." -ForegroundColor Gray
& ".\build-scripts\build-client.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Сборка клиента не удалась" -ForegroundColor Red
    exit 1
}

Write-Host "  ✓ Компоненты собраны" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════
# Шаг 2: Подготовка обновления сервера
# ═══════════════════════════════════════════════════════════
Write-Host ""
Write-Host "[2/4] Подготовка обновления сервера..." -ForegroundColor Yellow

$updateServerDir = ".\dist\Deltica-Server-Update-v$version"
if (Test-Path $updateServerDir) { Remove-Item -Recurse -Force $updateServerDir }
New-Item -ItemType Directory -Path $updateServerDir -Force | Out-Null

# Копируем новый server.exe
if (Test-Path ".\dist\server\deltica-server.exe") {
    Copy-Item ".\dist\server\deltica-server.exe" "$updateServerDir\deltica-server.exe"
    Write-Host "  ✓ Скопирован deltica-server.exe" -ForegroundColor Green
}

# Копируем новые миграции (если есть)
if (Test-Path ".\backend\alembic\versions") {
    $migrationsDir = "$updateServerDir\migrations"
    New-Item -ItemType Directory -Path $migrationsDir -Force | Out-Null
    Copy-Item ".\backend\alembic\versions\*" $migrationsDir -Recurse
    Write-Host "  ✓ Скопированы миграции БД" -ForegroundColor Green
}

# Создаем скрипт обновления сервера
$updateServerScript = @"
@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════
echo   Deltica Server - Обновление до версии $version
echo ═══════════════════════════════════════════════════════════
echo.

echo ВНИМАНИЕ: Это обновит Deltica Server на сервере!
echo.
echo Убедитесь что:
echo   - Сделан backup базы данных
echo   - Все пользователи вышли из системы
echo.
pause

REM Останавливаем службу/процесс
echo [1/4] Остановка Deltica Server...
taskkill /F /IM deltica-server.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo   ✓ Сервер остановлен

REM Backup текущей версии
echo.
echo [2/4] Создание резервной копии...
if exist C:\Deltica\deltica-server.exe (
    copy /Y C:\Deltica\deltica-server.exe C:\Deltica\deltica-server.exe.backup
    echo   ✓ Backup создан: deltica-server.exe.backup
) else (
    echo   ⚠ Текущая версия не найдена в C:\Deltica\
    echo.
    echo Укажите путь к установке Deltica или нажмите Enter для C:\Deltica\:
    set /p INSTALL_PATH=
    if "%INSTALL_PATH%"=="" set INSTALL_PATH=C:\Deltica
)

if "%INSTALL_PATH%"=="" set INSTALL_PATH=C:\Deltica

REM Копируем новую версию
echo.
echo [3/4] Установка обновления...
copy /Y deltica-server.exe "%INSTALL_PATH%\deltica-server.exe"
echo   ✓ Новая версия установлена

REM Применяем миграции БД
echo.
echo [4/4] Применение миграций базы данных...
if exist migrations (
    echo   Найдены новые миграции, применение...
    cd "%INSTALL_PATH%"
    deltica-server.exe alembic upgrade head
    echo   ✓ Миграции применены
) else (
    echo   ⚠ Новых миграций нет
)

REM Запускаем сервер обратно
echo.
echo Запуск обновленного сервера...
cd "%INSTALL_PATH%"
start "" deltica-server.exe

echo.
echo ═══════════════════════════════════════════════════════════
echo   ✅ ОБНОВЛЕНИЕ ЗАВЕРШЕНО!
echo ═══════════════════════════════════════════════════════════
echo.
echo Deltica Server обновлен до версии $version
echo.
echo Проверьте работу сервера: http://localhost:8000/docs
echo.
pause
"@

$updateServerScript | Out-File -FilePath "$updateServerDir\update-server.bat" -Encoding ASCII
Write-Host "  ✓ Создан update-server.bat" -ForegroundColor Green

# README для обновления сервера
$updateServerReadme = @"
═══════════════════════════════════════════════════════════
  Deltica Server - Обновление до v$version
═══════════════════════════════════════════════════════════

## ПЕРЕД ОБНОВЛЕНИЕМ

1. Создайте резервную копию базы данных:
   - Откройте pgAdmin
   - Правый клик на deltica_db → Backup
   - Сохраните файл в безопасное место

2. Убедитесь, что все пользователи вышли из системы

3. Уведомите пользователей о плановом обновлении

## ПРОЦЕСС ОБНОВЛЕНИЯ

1. Скопируйте эту папку на сервер

2. Запустите update-server.bat от имени администратора
   (правый клик → Запуск от имени администратора)

3. Следуйте инструкциям на экране

4. Скрипт автоматически:
   - Остановит текущий сервер
   - Создаст backup старой версии
   - Установит новую версию
   - Применит миграции БД
   - Запустит сервер

## ПРОВЕРКА

После обновления:

1. Откройте http://localhost:8000/docs
2. Проверьте, что API отвечает
3. Войдите в систему и проверьте основные функции

## ОТКАТ (если что-то пошло не так)

Если обновление вызвало проблемы:

1. Остановите сервер: taskkill /F /IM deltica-server.exe

2. Восстановите старую версию:
   copy /Y C:\Deltica\deltica-server.exe.backup C:\Deltica\deltica-server.exe

3. Восстановите БД из резервной копии через pgAdmin

4. Запустите старую версию

5. Свяжитесь с разработчиком

═══════════════════════════════════════════════════════════

Версия обновления: $version
Дата сборки: $(Get-Date -Format "yyyy-MM-dd")
"@

$updateServerReadme | Out-File -FilePath "$updateServerDir\README.txt" -Encoding UTF8
Write-Host "  ✓ Создан README.txt" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════
# Шаг 3: Подготовка обновления клиента
# ═══════════════════════════════════════════════════════════
Write-Host ""
Write-Host "[3/4] Подготовка обновления клиента..." -ForegroundColor Yellow

$updateClientDir = ".\dist\Deltica-Client-Update-v$version"
if (Test-Path $updateClientDir) { Remove-Item -Recurse -Force $updateClientDir }
New-Item -ItemType Directory -Path $updateClientDir -Force | Out-Null

# Копируем новые установщики
if (Test-Path ".\frontend\dist-electron\*.exe") {
    Copy-Item ".\frontend\dist-electron\*-Setup-*.exe" $updateClientDir -ErrorAction SilentlyContinue
    Copy-Item ".\frontend\dist-electron\*-Portable-*.exe" $updateClientDir -ErrorAction SilentlyContinue
    Write-Host "  ✓ Скопированы установщики клиента" -ForegroundColor Green
}

# README для обновления клиента
$updateClientReadme = @"
═══════════════════════════════════════════════════════════
  Deltica Client - Обновление до v$version
═══════════════════════════════════════════════════════════

## ОБНОВЛЕНИЕ КЛИЕНТОВ

### Вариант 1: Установщик (рекомендуется)

Для каждого клиентского ПК:

1. Закройте приложение Deltica (если запущено)
2. Запустите новый Setup.exe
3. Мастер установки обновит существующую версию
4. Готово!

### Вариант 2: Portable версия

1. Закройте приложение Deltica
2. Удалите старую папку с приложением
3. Распакуйте новую версию
4. При первом запуске введите IP сервера (как раньше)

### Вариант 3: Удаленное развертывание (для IT-отделов)

Используйте GPO (Group Policy) для автоматической установки:

1. Поместите Setup.exe в сетевую папку
2. Создайте GPO для установки при входе пользователя
3. Все клиенты обновятся автоматически при следующем входе

## ПРОВЕРКА

После обновления клиента:

1. Запустите Deltica
2. Войдите в систему
3. Проверьте основные функции

═══════════════════════════════════════════════════════════

Версия обновления: $version
Дата сборки: $(Get-Date -Format "yyyy-MM-dd")
"@

$updateClientReadme | Out-File -FilePath "$updateClientDir\README.txt" -Encoding UTF8
Write-Host "  ✓ Создан README.txt" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════
# Шаг 4: Создание финального пакета обновлений
# ═══════════════════════════════════════════════════════════
Write-Host ""
Write-Host "[4/4] Создание финального пакета..." -ForegroundColor Yellow

# ZIP для сервера
$serverZip = ".\dist\Deltica-Server-Update-v$version.zip"
if (Test-Path $serverZip) { Remove-Item -Force $serverZip }
Compress-Archive -Path "$updateServerDir\*" -DestinationPath $serverZip -CompressionLevel Optimal -Force
$serverZipSize = (Get-Item $serverZip).Length / 1MB
Write-Host "  ✓ Server update: Deltica-Server-Update-v$version.zip (${serverZipSize:N2} MB)" -ForegroundColor Green

# ZIP для клиента
$clientZip = ".\dist\Deltica-Client-Update-v$version.zip"
if (Test-Path $clientZip) { Remove-Item -Force $clientZip }
Compress-Archive -Path "$updateClientDir\*" -DestinationPath $clientZip -CompressionLevel Optimal -Force
$clientZipSize = (Get-Item $clientZip).Length / 1MB
Write-Host "  ✓ Client update: Deltica-Client-Update-v$version.zip (${clientZipSize:N2} MB)" -ForegroundColor Green

# Создаем общую инструкцию по обновлению
$masterReadme = @"
═══════════════════════════════════════════════════════════
  Deltica - Обновление системы до v$version
═══════════════════════════════════════════════════════════

## СОДЕРЖИМОЕ ПАКЕТА ОБНОВЛЕНИЙ

Этот релиз содержит обновления для:

1. Deltica Server (файл: Deltica-Server-Update-v$version.zip)
2. Deltica Client (файл: Deltica-Client-Update-v$version.zip)

## ПОРЯДОК ОБНОВЛЕНИЯ

⚠️ ВАЖНО: Обновляйте в следующем порядке:

### Шаг 1: Обновление сервера (ПЕРВЫМ!)

1. Распакуйте Deltica-Server-Update-v$version.zip
2. Следуйте инструкции из README.txt
3. Проверьте работу сервера
4. Только после этого переходите к клиентам!

### Шаг 2: Обновление клиентов

1. Распакуйте Deltica-Client-Update-v$version.zip
2. Следуйте инструкции из README.txt
3. Обновите все клиентские ПК

## ВРЕМЯ ОБНОВЛЕНИЯ

- Сервер: ~10-15 минут
- Каждый клиент: ~5 минут
- Общее время (сервер + 10 клиентов): ~1 час

## ПОДДЕРЖКА

При возникновении проблем обращайтесь к разработчику.

═══════════════════════════════════════════════════════════

Версия: $version
Дата сборки: $(Get-Date -Format "yyyy-MM-dd")
"@

$masterReadme | Out-File -FilePath ".\dist\UPDATE_README_v$version.txt" -Encoding UTF8
Write-Host "  ✓ Создан общий README" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════
# Итоговая информация
# ═══════════════════════════════════════════════════════════
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ ПАКЕТ ОБНОВЛЕНИЙ СОЗДАН УСПЕШНО!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Результаты сборки обновления:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📦 Server update:  Deltica-Server-Update-v$version.zip (${serverZipSize:N2} MB)" -ForegroundColor White
Write-Host "  📦 Client update:  Deltica-Client-Update-v$version.zip (${clientZipSize:N2} MB)" -ForegroundColor White
Write-Host "  📄 Инструкция:     UPDATE_README_v$version.txt" -ForegroundColor White
Write-Host ""
Write-Host "Передайте заказчику:" -ForegroundColor Yellow
Write-Host "  1. Deltica-Server-Update-v$version.zip" -ForegroundColor White
Write-Host "  2. Deltica-Client-Update-v$version.zip" -ForegroundColor White
Write-Host "  3. UPDATE_README_v$version.txt" -ForegroundColor White
Write-Host ""
Write-Host "Напомните заказчику:" -ForegroundColor Yellow
Write-Host "  - Сделать backup базы данных ПЕРЕД обновлением!" -ForegroundColor Red
Write-Host "  - Обновлять СНАЧАЛА сервер, ПОТОМ клиентов" -ForegroundColor Red
Write-Host "  - Запланировать обновление в нерабочее время" -ForegroundColor Yellow
Write-Host ""
