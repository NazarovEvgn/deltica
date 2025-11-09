# Build Scripts - Инструкция по использованию

## Назначение

Скрипты для создания коммерческих релизов Deltica без исходного кода.

## Скрипты

### 1. build-server.ps1
Компиляция backend в .exe для установки на сервере.

**Результат:**
- `dist/Deltica-Server-v1.0.0.zip` (~100 MB)
- Содержит: deltica-server.exe, конфиги, скрипты запуска

**Запуск:**
```powershell
.\build-scripts\build-server.ps1
```

**Требования:**
- PyInstaller (устанавливается автоматически)
- uv (для запуска Python)

---

### 2. build-client.ps1
Сборка Electron установщика для клиентских ПК.

**Результат:**
- `dist/Deltica-Client-v1.0.0.zip` (~50 MB)
- Содержит: Setup.exe, Portable.exe, инструкции

**Запуск:**
```powershell
.\build-scripts\build-client.ps1
```

**Требования:**
- Node.js + npm
- Electron dependencies (устанавливаются через npm install)

---

### 3. build-update.ps1
Создание пакета обновлений (server + client).

**Результат:**
- `dist/Deltica-Server-Update-v1.1.0.zip`
- `dist/Deltica-Client-Update-v1.1.0.zip`
- Скрипты автоматического обновления

**Запуск:**
```powershell
.\build-scripts\build-update.ps1
```

**Внимание:** Вызывает build-server.ps1 и build-client.ps1 автоматически.

---

## Процесс создания релиза

### Первый релиз (v1.0.0)

```powershell
# 1. Собрать сервер
.\build-scripts\build-server.ps1

# 2. Собрать клиент
.\build-scripts\build-client.ps1

# 3. Передать заказчику
# - dist/Deltica-Server-v1.0.0.zip
# - dist/Deltica-Client-v1.0.0.zip
```

### Создание обновления (v1.1.0)

```powershell
# 1. Обновить версию в pyproject.toml и package.json

# 2. Создать новые миграции (если нужно)
uv run alembic revision --autogenerate -m "update v1.1.0"

# 3. Собрать пакет обновлений
.\build-scripts\build-update.ps1

# 4. Передать заказчику
# - dist/Deltica-Server-Update-v1.1.0.zip
# - dist/Deltica-Client-Update-v1.1.0.zip
# - dist/UPDATE_README_v1.1.0.txt
```

---

## Структура результатов

После запуска скриптов:

```
dist/
├── Deltica-Server-v1.0.0/        # Распакованная версия сервера
│   ├── deltica-server.exe
│   ├── start.bat
│   ├── install-service.bat
│   ├── .env.example
│   ├── README.txt
│   └── uploads/, logs/, backups/
│
├── Deltica-Server-v1.0.0.zip     # Релиз сервера (передавать клиенту)
│
├── Deltica-Client-v1.0.0/        # Распакованная версия клиента
│   ├── Deltica-Setup-1.0.0.exe
│   ├── Deltica-Portable-1.0.0.zip
│   └── README.txt
│
├── Deltica-Client-v1.0.0.zip     # Релиз клиента (передавать клиенту)
│
├── Deltica-Server-Update-v1.1.0.zip  # Обновление сервера
├── Deltica-Client-Update-v1.1.0.zip  # Обновление клиента
└── UPDATE_README_v1.1.0.txt          # Инструкция по обновлению
```

---

## Troubleshooting

### Ошибка "PyInstaller не найден"
```powershell
uv pip install pyinstaller
```

### Ошибка "node_modules не найдена"
```powershell
cd frontend
npm install
cd ..
```

### Сборка .exe занимает слишком много времени
Это нормально. PyInstaller анализирует все зависимости (2-5 минут).

### Большой размер .exe файла
deltica-server.exe содержит:
- Python runtime
- Все библиотеки (FastAPI, SQLAlchemy, Alembic, etc.)
- Бизнес-логику приложения

Размер ~80-150 MB - это нормально для PyInstaller.

---

## Что НЕ попадает в релиз

Эти файлы остаются только у разработчика:

```
❌ backend/*.py          - исходники Python
❌ frontend/src/*.vue    - исходники Vue.js
❌ .git/                 - история разработки
❌ .env                  - локальные пароли
❌ node_modules/         - зависимости
❌ .venv/                - виртуальное окружение
```

Компания получает только скомпилированные .exe файлы.

---

## FAQ

**Q: Можно ли декомпилировать .exe обратно в Python?**
A: Теоретически да, но сложно. PyInstaller компилирует в bytecode, который можно попытаться декомпилировать, но результат будет нечитаемым. Для большинства случаев этого достаточно.

**Q: Как защитить код сильнее?**
A: Можно использовать Nuitka вместо PyInstaller (компилирует в C), либо добавить обфускацию Python кода перед компиляцией.

**Q: Почему frontend не компилируется?**
A: JavaScript невозможно скомпилировать полностью. Используется обфускация + ASAR упаковка для затруднения чтения кода.

**Q: Можно ли собрать под Linux/macOS?**
A: Да, но потребуется адаптация скриптов. PyInstaller работает на всех платформах.

---

**Версия:** 1.0
**Дата:** 2025-01-09
