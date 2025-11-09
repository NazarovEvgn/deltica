# ═══════════════════════════════════════════════════════════
# Deltica Server Build Script - Коммерческий релиз
# ═══════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Deltica Server Build Script v1.0" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Проверка, что скрипт запущен из корня проекта
if (-not (Test-Path ".\backend")) {
    Write-Host "ОШИБКА: Запустите скрипт из корня проекта" -ForegroundColor Red
    Write-Host "Текущая директория: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "Ожидается: C:\Projects\deltica\" -ForegroundColor Yellow
    exit 1
}

# Получение версии из pyproject.toml
$version = "1.0.0"
if (Test-Path "pyproject.toml") {
    $content = Get-Content "pyproject.toml" -Raw
    if ($content -match 'version\s*=\s*"([^"]+)"') {
        $version = $matches[1]
    }
}

Write-Host "Версия релиза: $version" -ForegroundColor Green
Write-Host ""

# ═══════════════════════════════════════════════════════════
# Шаг 1: Установка PyInstaller
# ═══════════════════════════════════════════════════════════
Write-Host "[1/7] Установка PyInstaller..." -ForegroundColor Yellow
try {
    uv pip install pyinstaller
    Write-Host "  ✓ PyInstaller установлен" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Ошибка установки PyInstaller: $_" -ForegroundColor Red
    exit 1
}

# ═══════════════════════════════════════════════════════════
# Шаг 2: Очистка старых сборок
# ═══════════════════════════════════════════════════════════
Write-Host "[2/7] Очистка старых сборок..." -ForegroundColor Yellow
if (Test-Path ".\dist\server") { Remove-Item -Recurse -Force ".\dist\server" }
if (Test-Path ".\build\server") { Remove-Item -Recurse -Force ".\build\server" }
if (Test-Path ".\deltica-server.spec") { Remove-Item -Force ".\deltica-server.spec" }
Write-Host "  ✓ Старые сборки удалены" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════
# Шаг 3: Создание PyInstaller spec файла
# ═══════════════════════════════════════════════════════════
Write-Host "[3/7] Создание PyInstaller spec файла..." -ForegroundColor Yellow

$specContent = @'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['backend/core/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('backend/alembic', 'alembic'),
        ('backend/alembic.ini', '.'),
        ('backend/app', 'app'),
        ('backend/core', 'core'),
        ('backend/routes', 'routes'),
        ('backend/services', 'services'),
        ('backend/middleware', 'middleware'),
        ('backend/utils', 'utils'),
        ('backend/scripts', 'scripts'),
        ('config', 'config'),
        ('docs/docx-templates', 'docs/docx-templates'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'passlib.handlers.bcrypt',
        'sqlalchemy.sql.default_comparator',
        'psycopg',
        'psycopg2',
        'alembic.operations',
        'docxtpl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy.tests',
        'scipy',
        'pytest',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='deltica-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'@

$specContent | Out-File -FilePath "deltica-server.spec" -Encoding UTF8
Write-Host "  ✓ Spec файл создан: deltica-server.spec" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════
# Шаг 4: Компиляция backend в .exe
# ═══════════════════════════════════════════════════════════
Write-Host "[4/7] Компиляция backend в .exe (2-5 минут)..." -ForegroundColor Yellow
Write-Host "  Это может занять несколько минут, подождите..." -ForegroundColor Gray

try {
    uv run pyinstaller deltica-server.spec --clean --distpath .\dist\server --workpath .\build\server

    if (-not (Test-Path ".\dist\server\deltica-server.exe")) {
        throw "Файл deltica-server.exe не найден после сборки"
    }

    $exeSize = (Get-Item ".\dist\server\deltica-server.exe").Length / 1MB
    Write-Host "  ✓ Backend скомпилирован: deltica-server.exe (${exeSize:N2} MB)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Ошибка компиляции: $_" -ForegroundColor Red
    exit 1
}

# ═══════════════════════════════════════════════════════════
# Шаг 5: Создание структуры релиза
# ═══════════════════════════════════════════════════════════
Write-Host "[5/7] Создание структуры релиза..." -ForegroundColor Yellow

$releaseDir = ".\dist\Deltica-Server-v$version"
if (Test-Path $releaseDir) { Remove-Item -Recurse -Force $releaseDir }
New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null

# Копируем скомпилированный сервер
Copy-Item ".\dist\server\deltica-server.exe" "$releaseDir\deltica-server.exe"
Write-Host "  ✓ Скопирован deltica-server.exe" -ForegroundColor Green

# Создаем папки для данных
New-Item -ItemType Directory -Path "$releaseDir\uploads" -Force | Out-Null
New-Item -ItemType Directory -Path "$releaseDir\logs" -Force | Out-Null
New-Item -ItemType Directory -Path "$releaseDir\backups" -Force | Out-Null
Write-Host "  ✓ Созданы папки: uploads, logs, backups" -ForegroundColor Green

# Создаем шаблон конфига
$configTemplate = @"
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "user": "deltica_user",
    "password": "CHANGE_ME_TO_SECURE_PASSWORD",
    "database": "deltica_db"
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "security": {
    "secret_key": "GENERATE_RANDOM_SECRET_KEY_HERE_MIN_32_CHARS",
    "algorithm": "HS256",
    "access_token_expire_minutes": 1440
  }
}
"@
$configTemplate | Out-File -FilePath "$releaseDir\config.template.json" -Encoding UTF8
Write-Host "  ✓ Создан config.template.json" -ForegroundColor Green

# Создаем .env.example для сервера
$envExample = @"
# База данных PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=deltica_user
DB_PASSWORD=your_secure_password_here
DB_NAME=deltica_db

# API сервер
API_HOST=0.0.0.0
API_PORT=8000

# Безопасность (JWT)
SECRET_KEY=generate_random_secret_key_min_32_characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
"@
$envExample | Out-File -FilePath "$releaseDir\.env.example" -Encoding UTF8
Write-Host "  ✓ Создан .env.example" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════
# Шаг 6: Создание скриптов запуска
# ═══════════════════════════════════════════════════════════
Write-Host "[6/7] Создание скриптов запуска..." -ForegroundColor Yellow

# Скрипт первого запуска
$firstRunScript = @"
@echo off
chcp 65001 >nul
echo ========================================
echo   Deltica Server - Первый запуск
echo ========================================
echo.

REM Проверка наличия .env
if not exist .env (
    echo [ОШИБКА] Файл .env не найден!
    echo.
    echo Скопируйте .env.example в .env и отредактируйте:
    echo   copy .env.example .env
    echo   notepad .env
    echo.
    pause
    exit /b 1
)

REM Проверка PostgreSQL
echo [1/3] Проверка PostgreSQL...
pg_isready -h localhost -p 5432 >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] PostgreSQL не запущен!
    echo.
    echo Установите PostgreSQL и запустите службу:
    echo   https://www.postgresql.org/download/windows/
    echo.
    pause
    exit /b 1
)
echo   ✓ PostgreSQL запущен

REM Информация о запуске
echo.
echo [2/3] Настройка окружения...
echo   ✓ Переменные окружения загружены из .env

REM Запуск сервера
echo.
echo [3/3] Запуск Deltica Server...
echo   API: http://localhost:8000
echo   Swagger UI: http://localhost:8000/docs
echo.
echo Нажмите Ctrl+C для остановки сервера
echo.
deltica-server.exe

pause
"@
$firstRunScript | Out-File -FilePath "$releaseDir\start.bat" -Encoding ASCII
Write-Host "  ✓ Создан start.bat" -ForegroundColor Green

# Скрипт создания Windows Service
$serviceScript = @"
@echo off
chcp 65001 >nul
echo ========================================
echo   Установка Deltica как службы Windows
echo ========================================
echo.
echo ВНИМАНИЕ: Требуются права администратора!
echo.
pause

REM Проверка прав администратора
net session >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Запустите скрипт от имени администратора!
    pause
    exit /b 1
)

REM Установка службы через Task Scheduler
echo Создание задачи в планировщике Windows...

schtasks /create /tn "Deltica Server" /tr "%CD%\deltica-server.exe" /sc onstart /ru SYSTEM /f

if errorlevel 0 (
    echo.
    echo ✓ Служба Deltica Server установлена!
    echo.
    echo Для управления службой:
    echo   - Запуск: schtasks /run /tn "Deltica Server"
    echo   - Остановка: taskkill /F /IM deltica-server.exe
    echo   - Удаление: schtasks /delete /tn "Deltica Server" /f
    echo.
) else (
    echo.
    echo [ОШИБКА] Не удалось создать службу
)

pause
"@
$serviceScript | Out-File -FilePath "$releaseDir\install-service.bat" -Encoding ASCII
Write-Host "  ✓ Создан install-service.bat" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════
# Шаг 7: Создание README
# ═══════════════════════════════════════════════════════════
Write-Host "[7/7] Создание документации..." -ForegroundColor Yellow

$readme = @"
═══════════════════════════════════════════════════════════
  Deltica Server v$version - Инструкция по установке
═══════════════════════════════════════════════════════════

## СИСТЕМНЫЕ ТРЕБОВАНИЯ

- Windows Server 2016+ или Windows 10/11
- PostgreSQL 13+ (установлен и запущен)
- 2 GB RAM
- 1 GB свободного места на диске
- Сетевое подключение (для клиентов)

═══════════════════════════════════════════════════════════
  УСТАНОВКА НА СЕРВЕРЕ
═══════════════════════════════════════════════════════════

### Шаг 1: Установите PostgreSQL

Скачайте и установите PostgreSQL:
https://www.postgresql.org/download/windows/

При установке:
- Запомните пароль для пользователя postgres
- Порт по умолчанию: 5432

### Шаг 2: Создайте базу данных

Откройте pgAdmin или psql и выполните:

    CREATE DATABASE deltica_db;
    CREATE USER deltica_user WITH PASSWORD 'ваш_надежный_пароль';
    GRANT ALL PRIVILEGES ON DATABASE deltica_db TO deltica_user;

### Шаг 3: Настройте Deltica Server

1. Распакуйте эту папку в C:\Deltica\
2. Скопируйте .env.example в .env:

   copy .env.example .env

3. Отредактируйте .env (откройте в Блокноте):

   - DB_PASSWORD - укажите пароль из Шага 2
   - SECRET_KEY - сгенерируйте случайную строку (минимум 32 символа)

### Шаг 4: Первый запуск

Дважды кликните на start.bat

Если все настроено правильно, вы увидите:
  ✓ PostgreSQL запущен
  ✓ API: http://localhost:8000
  ✓ Swagger UI: http://localhost:8000/docs

Откройте браузер: http://localhost:8000/docs
Вы должны увидеть API документацию.

### Шаг 5: Автозапуск (опционально)

Чтобы сервер запускался автоматически при загрузке Windows:

1. Запустите install-service.bat от имени администратора
   (правый клик → Запуск от имени администратора)

2. Служба будет создана и настроена на автозапуск

═══════════════════════════════════════════════════════════
  ПРОВЕРКА РАБОТЫ
═══════════════════════════════════════════════════════════

1. Откройте браузер: http://localhost:8000/docs
2. Вы должны увидеть Swagger UI с документацией API
3. Попробуйте войти:
   - Логин: admin
   - Пароль: admin123

═══════════════════════════════════════════════════════════
  НАСТРОЙКА ДОСТУПА ПО СЕТИ
═══════════════════════════════════════════════════════════

Чтобы клиенты могли подключаться к серверу:

### 1. Настройка Windows Firewall

Откройте порт 8000:
1. Windows Defender Firewall → Дополнительные параметры
2. Правила для входящих подключений → Создать правило
3. Тип: Для порта → TCP → 8000
4. Действие: Разрешить подключение
5. Название: "Deltica Server API"

### 2. Узнайте IP адрес сервера

Откройте cmd и выполните:
    ipconfig

Найдите IPv4-адрес (например: 192.168.1.10)
Этот адрес нужно будет ввести при установке клиентов.

═══════════════════════════════════════════════════════════
  СТРУКТУРА ПАПОК
═══════════════════════════════════════════════════════════

C:\Deltica\
├── deltica-server.exe       - Основное приложение
├── .env                      - Конфигурация (создайте из .env.example)
├── start.bat                 - Скрипт запуска
├── install-service.bat       - Установка как службы Windows
├── uploads\                  - Загруженные файлы
├── logs\                     - Логи работы сервера
└── backups\                  - Резервные копии БД

═══════════════════════════════════════════════════════════
  ЛОГИ И ДИАГНОСТИКА
═══════════════════════════════════════════════════════════

Логи сохраняются в: C:\Deltica\logs\deltica.log

При возникновении проблем:
1. Проверьте логи
2. Убедитесь, что PostgreSQL запущен
3. Проверьте настройки в .env

═══════════════════════════════════════════════════════════
  ТЕХНИЧЕСКАЯ ПОДДЕРЖКА
═══════════════════════════════════════════════════════════

При возникновении проблем свяжитесь с разработчиком.

Приложите:
- Файл logs\deltica.log
- Скриншот ошибки
- Описание действий, которые привели к ошибке

═══════════════════════════════════════════════════════════

Версия: $version
Дата сборки: $(Get-Date -Format "yyyy-MM-dd")
"@
$readme | Out-File -FilePath "$releaseDir\README.txt" -Encoding UTF8
Write-Host "  ✓ Создан README.txt" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════
# Создание ZIP архива
# ═══════════════════════════════════════════════════════════
Write-Host ""
Write-Host "Создание ZIP архива..." -ForegroundColor Yellow

$zipPath = ".\dist\Deltica-Server-v$version.zip"
if (Test-Path $zipPath) { Remove-Item -Force $zipPath }

try {
    Compress-Archive -Path "$releaseDir\*" -DestinationPath $zipPath -CompressionLevel Optimal -Force
    $zipSize = (Get-Item $zipPath).Length / 1MB
    Write-Host "  ✓ ZIP создан: Deltica-Server-v$version.zip (${zipSize:N2} MB)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Ошибка создания ZIP: $_" -ForegroundColor Red
    exit 1
}

# ═══════════════════════════════════════════════════════════
# Итоговая информация
# ═══════════════════════════════════════════════════════════
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ СБОРКА СЕРВЕРА ЗАВЕРШЕНА УСПЕШНО!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Результаты сборки:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📦 ZIP релиз:     .\dist\Deltica-Server-v$version.zip" -ForegroundColor White
Write-Host "  📁 Папка релиза:  .\dist\Deltica-Server-v$version\" -ForegroundColor White
Write-Host "  💾 Размер .exe:   ${exeSize:N2} MB" -ForegroundColor White
Write-Host "  💾 Размер ZIP:    ${zipSize:N2} MB" -ForegroundColor White
Write-Host ""
Write-Host "Содержимое релиза:" -ForegroundColor Cyan
Write-Host "  ✓ deltica-server.exe       - Скомпилированный backend" -ForegroundColor Gray
Write-Host "  ✓ .env.example             - Шаблон конфигурации" -ForegroundColor Gray
Write-Host "  ✓ start.bat                - Скрипт запуска" -ForegroundColor Gray
Write-Host "  ✓ install-service.bat      - Установка как службы" -ForegroundColor Gray
Write-Host "  ✓ README.txt               - Инструкция по установке" -ForegroundColor Gray
Write-Host ""
Write-Host "Следующие шаги:" -ForegroundColor Yellow
Write-Host "  1. Протестируйте релиз на тестовом сервере" -ForegroundColor White
Write-Host "  2. Передайте ZIP файл заказчику" -ForegroundColor White
Write-Host "  3. Заказчик следует инструкции из README.txt" -ForegroundColor White
Write-Host ""
Write-Host "Для сборки клиентской части запустите:" -ForegroundColor Yellow
Write-Host "  .\build-scripts\build-client.ps1" -ForegroundColor White
Write-Host ""
