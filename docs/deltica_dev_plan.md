# План коммерческого deployment Deltica

## Текущее состояние
- Dev режим: исходный код Python/Vue.js открыт
- Требует установки Python, Node.js, PostgreSQL на каждом ПК
- Не подходит для коммерческого использования

## Цель
- 10 клиентских ПК + 1 сервер
- Обновления 1 раз в год
- Код защищен от компании (только у разработчика)
- Простая установка без технических знаний

## Архитектура решения

```
Личный ПК (разработка):
├── Исходный код (Python, Vue.js)
├── Git репозиторий
└── Скрипты сборки релизов

Сервер компании:
├── deltica-server.exe (скомпилированный backend)
├── PostgreSQL
└── config.json

Клиентские ПК (10 шт):
└── Deltica.exe (Electron app) → подключение к серверу
```

## Компоненты для создания

### 1. Серверный установщик
**Файл:** `Deltica-Server-v1.0.0.zip`

**Содержимое:**
- `deltica-server.exe` - backend скомпилирован PyInstaller (БЕЗ исходников)
- `config.template.json` - шаблон конфигурации БД
- `first-run.bat` - скрипт первого запуска
- `README.txt` - инструкция по установке

**Установка на сервере:**
1. Установить PostgreSQL
2. Создать БД `deltica_db` и пользователя
3. Распаковать ZIP в `C:\Deltica\`
4. Отредактировать `config.json` (пароль БД)
5. Запустить `first-run.bat`
6. Настроить автозапуск через Task Scheduler

### 2. Клиентский установщик
**Файл:** `Deltica-Client-Setup.exe`

**Содержимое:**
- Electron app с обфусцированным frontend
- ASAR архив (код недоступен)

**Установка на клиентах:**
1. Запустить `.exe`
2. Ввести IP сервера (192.168.1.10)
3. Готово

### 3. Установщик обновлений
**Файл:** `Deltica-Update-v1.1.0.exe`

**Для сервера:**
- Остановка службы
- Backup БД
- Замена `deltica-server.exe`
- Миграции Alembic
- Запуск службы

**Для клиентов:**
- Замена Electron app

## Процесс разработки и деплоя

### Разработка (на личном ПК)
```bash
# 1. Разработка новой функции
git checkout -b feature/new-feature
# ... изменения кода ...
git commit -m "feat: новая функция"
git push

# 2. Тестирование в dev режиме
.\start.ps1

# 3. Слияние в main
git checkout main
git merge feature/new-feature
```

### Создание релиза
```bash
# 1. Сборка серверного установщика
.\build-scripts\build-server.ps1
# Результат: dist\Deltica-Server-v1.0.0.zip

# 2. Сборка клиентского установщика
.\build-scripts\build-client.ps1
# Результат: dist\Deltica-Client-Setup.exe

# 3. Передача компании
# Отправить 2 файла + инструкции
```

### Обновление (1 раз в год)
```bash
# 1. Увеличить версию в package.json и pyproject.toml
# 2. Создать новые миграции (если нужно)
alembic revision --autogenerate -m "update v1.1.0"

# 3. Собрать update.exe
.\build-scripts\build-update.ps1
# Результат: dist\Deltica-Update-v1.1.0.exe

# 4. Передать компании с инструкцией
```

## Защита кода

### Что защищено
✅ Backend логика - скомпилирован в .exe (PyInstaller)
✅ Frontend код - обфусцирован + ASAR архив
✅ База данных - на сервере компании, доступ по паролю
✅ Алгоритмы расчетов - в скомпилированном backend

### Что НЕ защищено (нормально для корпоративного ПО)
⚠️ API endpoints - видны в Network Tab
⚠️ Структура JSON - видна в ответах API
⚠️ UI flow - видно в приложении

### Уровень защиты: B (стандарт для корпоративного ПО)
- Обычные пользователи: 0% доступа к коду
- IT-специалисты компании: теоретически могут декомпилировать, но сложно
- Главная защита: юридический договор на использование

## Скрипты сборки

### build-server.ps1
- Компиляция backend в .exe через PyInstaller
- Упаковка с шаблонами конфигов
- Создание ZIP релиза

### build-client.ps1
- Vite production build
- Обфускация JavaScript
- ASAR упаковка
- NSIS установщик

### build-update.ps1
- Сборка нового backend.exe
- Упаковка миграций
- Создание update script

## Файлы, которые НЕ покидают личный ПК
```
backend/*.py           - исходники Python
frontend/src/*.vue     - исходники Vue.js
frontend/src/*.js      - исходники JavaScript
.git/                  - история разработки
.env                   - секреты и пароли
alembic/versions/*.py  - миграции БД (исходники)
pyproject.toml         - зависимости Python
package.json           - зависимости Node.js
```

## Что получает компания
```
✅ Deltica-Server-v1.0.0.zip      - серверная установка
✅ Deltica-Client-Setup.exe       - клиентская установка
✅ README_install.pdf             - инструкция по установке
✅ README_usage.pdf               - инструкция для пользователей
✅ Deltica-Update-vX.X.X.exe      - обновления (по запросу)
```

## Технические детали

### PyInstaller настройки
```python
# Включаем все зависимости
hiddenimports=[
    'uvicorn.logging', 'uvicorn.loops', 'uvicorn.protocols',
    'passlib.handlers.bcrypt', 'sqlalchemy.sql.default_comparator'
]

# Исключаем ненужное
excludes=['tkinter', 'matplotlib', 'numpy', 'scipy']

# Оптимизация
upx=True  # Сжатие .exe
```

### Обфускация frontend
```javascript
// javascript-obfuscator настройки
{
  identifierNamesGenerator: 'hexadecimal',
  renameGlobals: true,
  stringArray: true,
  rotateStringArray: true,
  compact: true
}
```

### Миграции БД при обновлении
```python
# В update script автоматически:
alembic upgrade head  # Применить все новые миграции
```

## Поддержка и обновления

### Частота обновлений: 1 раз в год

### Процесс:
1. Разработчик создает `Deltica-Update-v1.X.0.exe`
2. Отправляет компании по email/флешке
3. IT-специалист компании:
   - Останавливает сервер
   - Запускает update.exe
   - Проверяет работу
   - Обновляет клиентские ПК

### Техподдержка:
- Логи на сервере: `C:\Deltica\logs\`
- При проблемах - отправить логи разработчику
- Удаленная диагностика через TeamViewer (по согласованию)

## Лицензирование (опционально)

### Если потребуется защита от копирования:
- License key генерация
- Online activation
- Hardware ID binding
- Trial период

**Текущий статус:** Не реализовано (доверие + договор)

---

**Статус плана:** Утверждено
**Версия:** 1.0
**Дата:** 2025-01-09
