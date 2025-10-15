# Быстрый запуск Deltica

## Способ 1: Из любой директории (через алиас)

### Настройка (один раз):

1. Откройте PowerShell от имени администратора
2. Выполните команды:

```powershell
# Разрешить выполнение скриптов (если еще не разрешено)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Открыть профиль PowerShell для редактирования
notepad $PROFILE
```

3. Если файл не существует, нажмите "Да" для создания
4. Добавьте в файл:

```powershell
# Deltica quick start
function Start-Deltica {
    Set-Location C:\Projects\deltica
    .\start.ps1
}
Set-Alias deltica Start-Deltica
```

5. Сохраните и закройте notepad
6. Перезапустите PowerShell

### Использование:

Теперь из **любой** директории просто введите:

```powershell
deltica
```

---

## Способ 2: Двойной клик (ярлык на рабочем столе)

### Настройка:

1. Создайте ярлык на рабочем столе:
   - Правый клик на рабочем столе → Создать → Ярлык
   - Укажите путь: `C:\Projects\deltica\deltica-start.bat`
   - Назовите: "Deltica"

2. (Опционально) Измените иконку:
   - Правый клик на ярлык → Свойства → Сменить значок

### Использование:

Просто **двойной клик** по ярлыку на рабочем столе!

---

## Способ 3: Из любого места через .bat файл

Уже создан файл `C:\Projects\deltica\deltica-start.bat`

Можно:
1. Добавить `C:\Projects\deltica` в PATH
2. Или создать ярлык в удобном месте

Тогда можно запускать:

```cmd
deltica-start.bat
```

---

## Способ 4: Windows Terminal (если используете)

Добавьте в настройки Windows Terminal новый профиль:

```json
{
    "name": "Deltica",
    "commandline": "powershell.exe -NoExit -Command \"cd C:\\Projects\\deltica; .\\start.ps1\"",
    "icon": "C:\\Projects\\deltica\\icon.ico",
    "startingDirectory": "C:\\Projects\\deltica"
}
```

---

## Что делает start.ps1?

Скрипт автоматически:
1. Запускает backend (uvicorn) в отдельном окне
2. Запускает frontend (npm run dev) в отдельном окне
3. Оба процесса работают параллельно

Для остановки просто закройте окна PowerShell.

---

## Рекомендация

**Лучший вариант**: Способ 1 (алиас) - самый удобный для разработки.

Просто открываете PowerShell и пишете `deltica` - всё запускается!
