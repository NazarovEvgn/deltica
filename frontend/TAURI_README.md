# Tauri Desktop Application

## Требования

### Windows
- Rust 1.70+ (установлен ✅)
- Node.js 20.19+ или 22.12+ (установлен ✅)
- Microsoft Visual C++ Build Tools или Visual Studio с C++ workload

### Проверка установки
```bash
rustc --version
node --version
npm --version
```

## Запуск приложения в режиме разработки

### 1. Запустить backend сервер
В корне проекта:
```bash
uv run uvicorn backend.core.main:app --reload
```

Backend будет доступен на `http://localhost:8000`

### 2. Запустить Tauri desktop приложение
В директории `frontend`:
```bash
npm run tauri:dev
```

Эта команда автоматически:
- Запустит Vite dev server на порту 5173
- Скомпилирует Rust код
- Откроет desktop приложение

## Сборка production версии

### 1. Собрать frontend
```bash
cd frontend
npm run build
```

### 2. Собрать Tauri приложение
```bash
npm run tauri:build
```

Собранные файлы будут в `frontend/src-tauri/target/release/`

## Структура проекта

```
frontend/
├── src/                    # Vue.js исходники
├── src-tauri/              # Tauri/Rust код
│   ├── src/                # Rust исходники
│   ├── icons/              # Иконки приложения
│   ├── Cargo.toml          # Rust зависимости
│   └── tauri.conf.json     # Конфигурация Tauri
├── package.json
└── vite.config.js
```

## Конфигурация

### API Endpoint
По умолчанию используется `http://localhost:8000`

Для изменения создайте `.env` файл:
```env
VITE_API_URL=http://your-api-server:8000
```

### Настройки окна
Редактируйте `frontend/src-tauri/tauri.conf.json`:
- Размер окна: `width`, `height`
- Минимальный размер: `minWidth`, `minHeight`
- Заголовок: `title`

## Особенности desktop версии

### Отличия от web версии
- Работает как нативное приложение Windows
- Не требует браузера
- Более быстрый запуск
- Доступ к системным API через Tauri

### Архитектура
- **Frontend**: Vue 3 + Vite + Naive UI
- **Backend Bridge**: Tauri (Rust)
- **API**: FastAPI backend (должен быть запущен отдельно)

## Troubleshooting

### Ошибка компиляции Rust
Убедитесь что установлены Visual C++ Build Tools:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Ошибка подключения к API
Проверьте что backend запущен:
```bash
curl http://localhost:8000/health/
```

### Порт Vite занят
Измените порт в `vite.config.js` и `tauri.conf.json`

## Полезные команды

```bash
# Проверить конфигурацию Tauri
npm run tauri info

# Собрать только для текущей платформы
npm run tauri:build

# Очистить кэш сборки
cd src-tauri
cargo clean
```

## Дополнительная информация

- [Tauri Documentation](https://tauri.app/)
- [Tauri GitHub](https://github.com/tauri-apps/tauri)
