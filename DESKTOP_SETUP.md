# Запуск Deltica Desktop Application

## Быстрый старт для разработки

### Способ 1: Двойной клик по BAT-файлу

1. **Запустите `start-desktop.bat`**
   - Находится в корне проекта
   - Автоматически запустит backend и desktop приложение
   - При закрытии Tauri окна backend также остановится

### Способ 2: Создать ярлык на рабочем столе

1. **Правой кнопкой мыши** на `start-desktop.bat`
2. **Отправить → Рабочий стол (создать ярлык)**
3. **Переименуйте ярлык** в "Deltica"
4. **Смените иконку (опционально)**:
   - ПКМ на ярлыке → Свойства
   - Сменить значок
   - Выберите `frontend/public/favicon.ico` (если есть) или любую другую иконку

### Способ 3: Закрепить в панели задач

1. Создайте ярлык как в Способе 2
2. **Перетащите ярлык** на панель задач
3. Теперь можно запускать одним кликом

---

## Запуск только Backend (без desktop UI)

Если нужно запустить только backend сервер:

```bash
# Двойной клик по файлу:
start-backend.bat

# Или через командную строку:
uv run uvicorn backend.core.main:app --reload
```

Backend будет доступен на `http://localhost:8000`

---

## Production режим (установленное приложение)

### Первая сборка приложения

1. **Соберите frontend**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Соберите Tauri приложение**:
   ```bash
   npm run tauri:build
   ```

3. **Установщик будет создан** в:
   ```
   frontend/src-tauri/target/release/bundle/msi/Deltica_0.1.0_x64_en-US.msi
   ```

### Установка

1. **Запустите .msi установщик**
2. Следуйте инструкциям установщика
3. **Приложение появится** в меню "Пуск"

### Использование установленного приложения

**ВАЖНО**: В production режиме приложение не запускает backend автоматически!

**Правильная последовательность**:

1. **Сначала запустите backend**:
   - Двойной клик по `start-backend.bat`
   - Или настройте автозапуск backend как службу Windows

2. **Затем запустите Deltica** из меню "Пуск"

---

## Настройка автозапуска backend

Для production использования рекомендуется настроить backend как службу Windows:

### Вариант 1: Добавить в автозагрузку

1. Создайте ярлык для `start-backend.bat`
2. Нажмите `Win + R`, введите `shell:startup`
3. Скопируйте ярлык в открывшуюся папку
4. Backend будет запускаться при входе в Windows

### Вариант 2: Использовать NSSM (Non-Sucking Service Manager)

1. Скачайте NSSM: https://nssm.cc/download
2. Установите backend как службу:
   ```cmd
   nssm install DelticaBackend "C:\path\to\python.exe" "-m" "uvicorn" "backend.core.main:app" "--host" "127.0.0.1" "--port" "8000"
   ```

3. Запустите службу:
   ```cmd
   nssm start DelticaBackend
   ```

---

## Структура файлов для запуска

```
deltica/
├── start-desktop.bat      # Запуск backend + Tauri (для разработки)
├── start-desktop.ps1      # PowerShell скрипт (вызывается из .bat)
├── start-backend.bat      # Запуск только backend
└── frontend/
    ├── src-tauri/
    │   └── target/release/bundle/
    │       └── msi/
    │           └── Deltica_0.1.0_x64_en-US.msi  # Production установщик
    └── package.json
```

---

## Troubleshooting

### "Backend не отвечает"
- Убедитесь что PostgreSQL запущен
- Проверьте `.env` файл с настройками БД
- Откройте `http://localhost:8000/docs` в браузере

### "Приложение не запускается"
- Проверьте что Rust установлен: `rustc --version`
- Проверьте что Node.js установлен: `node --version`
- Попробуйте запустить через `npm run tauri:dev` вручную

### "Иконки не отображаются"
- Иконки находятся в `frontend/src-tauri/icons/`
- Используйте формат .ico для Windows

---

## Рекомендации для развертывания

Для развертывания на компьютерах пользователей:

1. **Создайте installer** через `npm run tauri:build`
2. **Настройте backend** как службу Windows на сервере
3. **Измените API endpoint** в `.env`:
   ```env
   VITE_API_URL=http://your-server-ip:8000
   ```
4. **Пересоберите приложение** с новым endpoint
5. **Распространите .msi установщик**

Пользователи смогут установить приложение и оно будет подключаться к центральному серверу с backend.
