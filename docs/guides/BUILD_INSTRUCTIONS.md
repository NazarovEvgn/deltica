# Инструкция по сборке установщиков Deltica

## Проблема с winCodeSign

При сборке Windows установщика через `electron-builder` возникает проблема с правами доступа для создания символических ссылок в архиве winCodeSign. Это известная проблема electron-builder в Windows.

### Ошибка
```
ERROR: Cannot create symbolic link : A required privilege is not held by the client.
```

## Решения

### Вариант 1: Запуск от имени администратора (рекомендуется)

1. Откройте PowerShell **от имени администратора**
2. Перейдите в папку проекта:
   ```powershell
   cd C:\Projects\deltica\frontend
   ```
3. Запустите сборку:
   ```powershell
   $env:CSC_IDENTITY_AUTO_DISCOVERY="false"
   npm run electron:build:win
   ```

### Вариант 2: Включить режим разработчика Windows

1. Откройте **Параметры Windows** (Win + I)
2. Перейдите в **Обновление и безопасность** → **Для разработчиков**
3. Включите **Режим разработчика**
4. Перезагрузите компьютер
5. Запустите сборку:
   ```bash
   cd frontend
   npm run electron:build:win
   ```

### Вариант 3: Portable версия (уже готова!)

Portable ZIP версия уже создана автоматически и находится в:
```
frontend/dist-electron/Deltica-Portable-1.0.0.zip
```

Также доступна unpacked версия для прямого запуска:
```
frontend/dist-electron/win-unpacked/Deltica.exe
```

### Вариант 4: Использование готового скрипта

1. Откройте PowerShell **от имени администратора**
2. Перейдите в папку проекта:
   ```powershell
   cd C:\Projects\deltica\frontend\build
   ```
3. Запустите скрипт:
   ```powershell
   .\build-installer-admin.ps1
   ```

## Результаты сборки

После успешной сборки в папке `frontend/dist-electron/` будут созданы:

- **Deltica-Setup-1.0.0.exe** - NSIS установщик с русским интерфейсом
- **Deltica-Portable-1.0.0.exe** - Portable версия (не требует установки)
- **Deltica-Portable-1.0.0.zip** - ZIP архив portable версии
- **win-unpacked/** - Unpacked версия для тестирования

## Конфигурация установщика

Настройки NSIS установщика в `package.json`:

- Русский язык интерфейса (language: 1049)
- Возможность выбора папки установки
- Создание ярлыков на рабочем столе и в меню Пуск
- Автозапуск после установки
- Установка для текущего пользователя (без требования прав администратора)

## Иконка приложения

Иконка автоматически генерируется из `frontend/public/icon.png` (256x256 пикселей).

Исходная иконка: `frontend/public/favicon.png` (30x35 пикселей) - используется для web.

## Дополнительная информация

- Приложение собрано для архитектуры x64
- Electron версия: 38.4.0
- Без цифровой подписи кода (для production рекомендуется добавить)
- Максимальное сжатие (compression: maximum)
- ASAR архивирование включено

## Troubleshooting

### Если установщик не создается

1. Проверьте, что созданаunpacked версия:
   ```
   frontend/dist-electron/win-unpacked/Deltica.exe
   ```
2. Попробуйте создать только portable версию:
   ```powershell
   cd frontend
   npx electron-builder --win --x64 --dir
   ```
3. Используйте готовую portable ZIP версию

### Если нужно пересобрать иконку

```powershell
cd frontend/build
.\create-icon.ps1
```

Это создаст новую иконку 256x256 из favicon.png.
