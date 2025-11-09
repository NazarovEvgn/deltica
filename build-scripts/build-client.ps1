# ═══════════════════════════════════════════════════════════
# Deltica Client Build Script - Коммерческий релиз
# ═══════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Deltica Client Build Script v1.0" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Проверка, что скрипт запущен из корня проекта
if (-not (Test-Path ".\frontend")) {
    Write-Host "ОШИБКА: Запустите скрипт из корня проекта" -ForegroundColor Red
    Write-Host "Текущая директория: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "Ожидается: C:\Projects\deltica\" -ForegroundColor Yellow
    exit 1
}

# Получение версии из package.json
$version = "1.0.0"
if (Test-Path "frontend\package.json") {
    $packageJson = Get-Content "frontend\package.json" -Raw | ConvertFrom-Json
    $version = $packageJson.version
}

Write-Host "Версия релиза: $version" -ForegroundColor Green
Write-Host ""

# ═══════════════════════════════════════════════════════════
# Шаг 1: Проверка зависимостей
# ═══════════════════════════════════════════════════════════
Write-Host "[1/6] Проверка зависимостей..." -ForegroundColor Yellow

Push-Location frontend

# Проверка node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "  node_modules не найдена, запуск npm install..." -ForegroundColor Gray
    npm install
}

Write-Host "  ✓ Зависимости установлены" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════
# Шаг 2: Очистка старых сборок
# ═══════════════════════════════════════════════════════════
Write-Host "[2/6] Очистка старых сборок..." -ForegroundColor Yellow

if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "dist-electron") { Remove-Item -Recurse -Force "dist-electron" }

Write-Host "  ✓ Старые сборки удалены" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════
# Шаг 3: Production сборка frontend
# ═══════════════════════════════════════════════════════════
Write-Host "[3/6] Production сборка frontend (Vite)..." -ForegroundColor Yellow
Write-Host "  Это может занять 1-2 минуты..." -ForegroundColor Gray

try {
    npm run build

    if (-not (Test-Path "dist\index.html")) {
        throw "Frontend сборка не создала dist/index.html"
    }

    $distSize = (Get-ChildItem -Path "dist" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "  ✓ Frontend собран: dist/ (${distSize:N2} MB)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Ошибка сборки frontend: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

# ═══════════════════════════════════════════════════════════
# Шаг 4: Настройка конфигурации подключения к серверу
# ═══════════════════════════════════════════════════════════
Write-Host "[4/6] Настройка конфигурации..." -ForegroundColor Yellow

# Создаем config.json для Electron
$electronConfig = @"
{
  "serverUrl": "http://192.168.1.10:8000",
  "appName": "Deltica",
  "version": "$version"
}
"@

$electronConfig | Out-File -FilePath "public\config.json" -Encoding UTF8
Write-Host "  ✓ Создан config.json с настройками по умолчанию" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════
# Шаг 5: Сборка Electron установщика
# ═══════════════════════════════════════════════════════════
Write-Host "[5/6] Сборка Electron установщика..." -ForegroundColor Yellow
Write-Host "  Это может занять 3-5 минут..." -ForegroundColor Gray

try {
    npm run electron:build:win

    if (-not (Test-Path "dist-electron")) {
        throw "Electron сборка не создала dist-electron/"
    }

    Write-Host "  ✓ Electron установщик создан" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Ошибка сборки Electron: $_" -ForegroundColor Red
    Write-Host "  Проверьте логи выше для деталей" -ForegroundColor Yellow
    Pop-Location
    exit 1
}

# ═══════════════════════════════════════════════════════════
# Шаг 6: Создание финального релиза
# ═══════════════════════════════════════════════════════════
Write-Host "[6/6] Создание финального релиза..." -ForegroundColor Yellow

Pop-Location

$clientReleaseDir = ".\dist\Deltica-Client-v$version"
if (Test-Path $clientReleaseDir) { Remove-Item -Recurse -Force $clientReleaseDir }
New-Item -ItemType Directory -Path $clientReleaseDir -Force | Out-Null

# Копируем установщики
if (Test-Path "frontend\dist-electron\*.exe") {
    Copy-Item "frontend\dist-electron\*.exe" $clientReleaseDir
    $installers = Get-ChildItem "$clientReleaseDir\*.exe"
    Write-Host "  ✓ Скопированы установщики:" -ForegroundColor Green
    foreach ($installer in $installers) {
        $size = $installer.Length / 1MB
        Write-Host "    - $($installer.Name) (${size:N2} MB)" -ForegroundColor Gray
    }
}

# Копируем portable версию если есть
if (Test-Path "frontend\dist-electron\*.zip") {
    Copy-Item "frontend\dist-electron\*.zip" $clientReleaseDir
    Write-Host "  ✓ Скопирована portable версия" -ForegroundColor Green
}

# Создаем инструкцию по установке для клиентов
$clientReadme = @"
═══════════════════════════════════════════════════════════
  Deltica Client v$version - Инструкция по установке
═══════════════════════════════════════════════════════════

## ЧТО ЭТО

Это клиентское приложение Deltica для рабочих станций.
Приложение подключается к серверу Deltica в локальной сети.

## СИСТЕМНЫЕ ТРЕБОВАНИЯ

- Windows 10/11 (64-bit)
- 500 MB свободного места на диске
- Сетевое подключение к серверу Deltica

## УСТАНОВКА

### Вариант 1: Через установщик (рекомендуется)

1. Запустите Deltica-Setup-$version.exe
2. Следуйте инструкциям мастера установки
3. При первом запуске введите IP адрес сервера
   (например: 192.168.1.10)
4. Готово!

### Вариант 2: Portable версия (без установки)

1. Распакуйте Deltica-Portable-$version.zip в любую папку
2. Запустите Deltica.exe
3. При первом запуске введите IP адрес сервера
4. Готово!

## ПЕРВЫЙ ЗАПУСК

При первом запуске приложение попросит ввести:

  📍 IP адрес сервера Deltica

Узнайте IP адрес у вашего системного администратора.
Обычно это адрес вида: 192.168.X.X

Пример: 192.168.1.10

## ИСПОЛЬЗОВАНИЕ

После успешного подключения к серверу:

1. Войдите в систему используя ваши учетные данные:
   - Логин: (ваш логин)
   - Пароль: (ваш пароль)

2. Приложение готово к работе!

## ОБНОВЛЕНИЕ

Для обновления клиента до новой версии:

1. Закройте приложение Deltica
2. Запустите новый установщик
3. Выберите "Обновить существующую установку"
4. Готово!

## ПРОБЛЕМЫ И РЕШЕНИЯ

### Не могу подключиться к серверу

1. Проверьте, что сервер запущен
2. Проверьте IP адрес (должен быть правильный)
3. Проверьте, что вы в той же сети что и сервер
4. Обратитесь к системному администратору

### Забыли пароль

Обратитесь к администратору системы для сброса пароля.

### Ошибка при запуске

1. Попробуйте перезапустить приложение
2. Если не помогло - переустановите приложение
3. Обратитесь в техподдержку

## ТЕХНИЧЕСКАЯ ПОДДЕРЖКА

При возникновении проблем обращайтесь:
- К вашему системному администратору
- К разработчику (контакты у администратора)

═══════════════════════════════════════════════════════════

Версия: $version
Дата сборки: $(Get-Date -Format "yyyy-MM-dd")
"@

$clientReadme | Out-File -FilePath "$clientReleaseDir\README.txt" -Encoding UTF8
Write-Host "  ✓ Создан README.txt для клиентов" -ForegroundColor Green

# Создаем ZIP архив
$clientZipPath = ".\dist\Deltica-Client-v$version.zip"
if (Test-Path $clientZipPath) { Remove-Item -Force $clientZipPath }

try {
    Compress-Archive -Path "$clientReleaseDir\*" -DestinationPath $clientZipPath -CompressionLevel Optimal -Force
    $zipSize = (Get-Item $clientZipPath).Length / 1MB
    Write-Host "  ✓ ZIP создан: Deltica-Client-v$version.zip (${zipSize:N2} MB)" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Не удалось создать ZIP: $_" -ForegroundColor Yellow
}

# ═══════════════════════════════════════════════════════════
# Итоговая информация
# ═══════════════════════════════════════════════════════════
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ СБОРКА КЛИЕНТА ЗАВЕРШЕНА УСПЕШНО!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Результаты сборки:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📦 ZIP релиз:     .\dist\Deltica-Client-v$version.zip" -ForegroundColor White
Write-Host "  📁 Папка релиза:  .\dist\Deltica-Client-v$version\" -ForegroundColor White
Write-Host ""

# Показываем список созданных файлов
if (Test-Path $clientReleaseDir) {
    Write-Host "Содержимое релиза:" -ForegroundColor Cyan
    Get-ChildItem $clientReleaseDir | ForEach-Object {
        $size = $_.Length / 1MB
        if ($_.Extension -eq ".exe" -or $_.Extension -eq ".zip") {
            Write-Host "  ✓ $($_.Name) (${size:N2} MB)" -ForegroundColor Gray
        } else {
            Write-Host "  ✓ $($_.Name)" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "Следующие шаги:" -ForegroundColor Yellow
Write-Host "  1. Протестируйте установщик на чистой системе" -ForegroundColor White
Write-Host "  2. Передайте ZIP файл или установщики заказчику" -ForegroundColor White
Write-Host "  3. Убедитесь, что сервер доступен в сети" -ForegroundColor White
Write-Host ""
Write-Host "Для создания обновления запустите:" -ForegroundColor Yellow
Write-Host "  .\build-scripts\build-update.ps1" -ForegroundColor White
Write-Host ""
