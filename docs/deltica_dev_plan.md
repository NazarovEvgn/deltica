# План разработки

### Предыстория
- Изначально был выбран Tauri v2 в качестве desktop обертки
- Обнаружены критические проблемы: конфликт с RevoGrid (отсутствие отображения), проблемы с кэшем
- Принято решение о миграции на Electron для гарантированной совместимости

### Причины выбора Electron
- **Совместимость с RevoGrid**: Electron использует Chromium - тот же движок, что и в веб-версии
- **Зрелость экосистемы**: проверен годами (VS Code, Slack, Discord)
- **Единая среда разработки**: только JavaScript/TypeScript (не требуется Rust)
- **Предсказуемое поведение**: встроенный Chromium обеспечивает одинаковое поведение на всех машинах
- **Корпоративный контекст**: размер установщика не критичен для внутреннего развертывания

### План миграции (пошаговый чеклист)

#### Этап 1: Подготовка и очистка
- [x] Удалить директорию `frontend/src-tauri/` со всем содержимым
- [x] Удалить файл `frontend/TAURI_README.md`
- [x] Удалить Tauri зависимости из `frontend/package.json`
- [x] Удалить Tauri скрипты из `frontend/package.json` (tauri, tauri:dev, tauri:build)
- [ ] Обновить CLAUDE.md (удалить секцию о Tauri)

#### Этап 2: Установка Electron и зависимостей
- [ ] Установить Electron: `npm install --save-dev electron`
- [ ] Установить Electron Builder: `npm install --save-dev electron-builder`
- [ ] Установить утилиты: `npm install --save-dev electron-devtools-installer`
- [ ] (Опционально) Установить Electron Forge для упрощенной настройки

#### Этап 3: Создание структуры проекта
```
frontend/
├── electron/
│   ├── main.js              # Главный процесс Electron
│   ├── preload.js           # Preload скрипт для безопасности
│   └── menu.js              # Настройка меню приложения (опционально)
├── src/                     # Vue.js исходники (без изменений)
├── public/                  # Статические файлы (без изменений)
├── dist/                    # Собранные файлы Vite (генерируется)
├── package.json             # Обновленный с Electron скриптами
└── vite.config.js           # Конфигурация Vite (проверить base path)
```

#### Этап 4: Конфигурация Electron

**Создать `frontend/electron/main.js`:**
- Настройка главного окна (BrowserWindow)
- Размеры окна: width: 1400, height: 900, minWidth: 1200, minHeight: 700
- Security: contextIsolation: true, nodeIntegration: false, sandbox: true
- Загрузка приложения:
  - Dev mode: loadURL('http://localhost:5173')
  - Production: loadFile('dist/index.html')
- Обработка жизненного цикла: app.on('ready'), app.on('window-all-closed')

**Создать `frontend/electron/preload.js`:**
- Безопасный мост между Electron и renderer process
- Использовать contextBridge API для экспозиции необходимых функций
- Пока минимальная реализация (расширить по необходимости)

#### Этап 5: Обновление package.json

**Добавить поля:**
```json
{
  "main": "electron/main.js",
  "author": "NazarovEvgn",
  "description": "Deltica - система управления метрологическим оборудованием"
}
```

**Добавить скрипты:**
```json
{
  "electron:dev": "concurrently \"npm run dev\" \"wait-on http://localhost:5173 && electron .\"",
  "electron:build": "npm run build && electron-builder",
  "electron:build:win": "npm run build && electron-builder --win --x64"
}
```

**Добавить конфигурацию electron-builder:**
```json
{
  "build": {
    "appId": "com.deltica.app",
    "productName": "Deltica",
    "directories": {
      "output": "dist-electron"
    },
    "files": [
      "dist/**/*",
      "electron/**/*",
      "package.json"
    ],
    "win": {
      "target": "nsis",
      "icon": "public/favicon.png"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
```

#### Этап 6: Установка дополнительных утилит
- [ ] Установить `concurrently` для одновременного запуска dev сервера и Electron:
  ```bash
  npm install --save-dev concurrently
  ```
- [ ] Установить `wait-on` для ожидания запуска dev сервера:
  ```bash
  npm install --save-dev wait-on
  ```

#### Этап 7: Тестирование
- [ ] Запустить в dev режиме: `npm run electron:dev`
- [ ] Проверить отображение RevoGrid таблицы
- [ ] Проверить работу всех функций (CRUD, фильтры, статистика, документы)
- [ ] Проверить аутентификацию и роли (admin/laborant)
- [ ] Тестировать генерацию документов (этикетки, акты)

#### Этап 8: Сборка production
- [ ] Собрать приложение: `npm run electron:build:win`
- [ ] Установить и протестировать .exe на чистой машине
- [ ] Проверить подключение к backend серверу
- [ ] Протестировать все критические функции

#### Этап 9: Документация
- [ ] Создать `frontend/ELECTRON_README.md` с инструкциями:
  - Требования (Node.js версия)
  - Запуск в dev режиме
  - Сборка для production
  - Troubleshooting
- [ ] Обновить CLAUDE.md с информацией об Electron
- [ ] Обновить основной README.md проекта (если есть)

#### Этап 10: Опциональные улучшения
- [ ] Настроить авто-обновление (electron-updater)
- [ ] Добавить splash screen при загрузке
- [ ] Настроить кастомное меню приложения
- [ ] Добавить горячие клавиши (Ctrl+R для перезагрузки в dev)
- [ ] Настроить иконки для разных разрешений
- [ ] Добавить tray icon (для сворачивания в трей)

### Важные замечания

**Backend сервер:**
- Backend (FastAPI) должен запускаться отдельно на `http://localhost:8000`
- Electron приложение - это только frontend обертка
- Нет планов встраивания Python backend в Electron (требует exe-wrapper)

**Безопасность:**
- Использовать contextIsolation и отключить nodeIntegration
- Минимизировать код в preload.js
- Валидировать все данные, передаваемые между процессами

**Размер установщика:**
- Ожидаемый размер: ~120-150 MB (включает Chromium + Node.js)
- Приемлемо для корпоративного сценария с внутренней сетью

**Совместимость:**
- Windows 10/11 (основная платформа)
- Возможность расширения на Linux/macOS в будущем

### Риски и митигации

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| Большой размер установщика | Высокая | Корпоративная среда - не критично |
| Медленный запуск | Средняя | Оптимизация main.js, lazy loading |
| Проблемы с auto-update | Средняя | Тестирование на staging окружении |
| Конфликты версий Node.js | Низкая | Фиксация версий в package.json |

### Альтернативы (если Electron не подойдет)
1. **NW.js** - аналог Electron, Node.js + Chromium
2. **PWA** - Progressive Web App с desktop install
3. **Neutralinojs** - легковесная альтернатива Electron

## Документация
- разработать документацию:
  - для специалиста отвечающего за deploy на сервере.
  - для пользователя.
  - общая для презентации приложения на GitHub.
  - общая техническая по функционалу и структуре.


## Docker
- добавить Docker контейниризацию в разработку
