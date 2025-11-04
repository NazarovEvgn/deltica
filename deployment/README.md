# Руководство по деплою Deltica на Windows Server

## Архитектура

```
Windows Server (PostgreSQL 17)
    ↓ (локальная сеть)
Backend (FastAPI как Windows Service, порт 8000)
    ↓ (HTTP/HTTPS)
Рабочие места (Electron клиенты)
```

## Требования к серверу

- Windows Server 2016/2019/2022
- PostgreSQL 17 (уже установлен ✅)
- Python 3.13
- uv (менеджер пакетов Python)
- NSSM (для запуска backend как Windows Service)

## Требования к клиентам

- Windows 10/11
- Сетевой доступ к серверу
- 100 МБ свободного места

## Установка на сервер

### 1. Подготовка backend

1. Скопируйте папку проекта на сервер (C:\Deltica\)

2. Установите Python 3.13:
   - Скачайте с https://www.python.org/downloads/
   - Установите с галочкой "Add to PATH"

3. Установите uv:
   ```cmd
   pip install uv
   ```

4. Установите зависимости backend:
   ```cmd
   cd C:\Deltica
   uv sync
   ```

5. Создайте .env файл:
   ```cmd
   copy .env.example .env
   notepad .env
   ```

6. Отредактируйте .env:
   ```env
   DB_USER=postgres
   DB_PASSWORD=ваш_пароль_postgres
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=deltica_db

   BACKEND_HOST=0.0.0.0
   BACKEND_PORT=8000

   JWT_SECRET_KEY=ваш-случайный-секретный-ключ-минимум-32-символа
   JWT_ALGORITHM=HS256
   JWT_EXPIRE_MINUTES=1440

   CORS_ORIGINS=null
   ENVIRONMENT=production
   ```

7. Создайте базу данных:
   ```cmd
   cd C:\Deltica\deployment
   run_migrations.bat
   ```

8. Синхронизируйте пользователей:
   ```cmd
   sync_users.bat
   ```

### 2. Установка backend как Windows Service

1. Скачайте NSSM: https://nssm.cc/download
2. Распакуйте nssm.exe в C:\Deltica\deployment\

3. Установите службу:
   ```cmd
   cd C:\Deltica\deployment
   install_service.bat
   ```

4. Служба "DelticaBackend" будет запущена автоматически

5. Проверьте работу:
   - Откройте браузер: http://localhost:8000/docs
   - Должна открыться документация API

### 3. Настройка файрвола

Откройте порт 8000 для локальной сети:
```cmd
netsh advfirewall firewall add rule name="Deltica Backend" dir=in action=allow protocol=TCP localport=8000
```

### 4. Узнайте IP-адрес сервера

```cmd
ipconfig
```

Запишите IPv4 адрес (например: 192.168.1.100)

## Установка на клиентские машины

### 1. Подготовка установщика

На машине разработчика:
```cmd
cd C:\Projects\deltica\frontend
npm run electron:build:win
```

Установщик будет в `frontend\dist-electron\Deltica-Setup-0.0.0.exe`

### 2. Настройка config.json

Перед установкой на клиентах отредактируйте `frontend\dist\config.json`:
```json
{
  "apiUrl": "http://192.168.1.100:8000"
}
```
Замените 192.168.1.100 на IP вашего сервера

### 3. Установка на клиентах

1. Скопируйте `Deltica-Setup-0.0.0.exe` на клиентские машины
2. Запустите установщик
3. Следуйте инструкциям установщика
4. Запустите Deltica с рабочего стола

### 4. Первый вход

- Пользователи будут автоматически входить через Windows SSO
- Если username не настроен - потребуется ввести логин/пароль вручную

## Управление backend service

Запуск:
```cmd
net start DelticaBackend
```

Остановка:
```cmd
net stop DelticaBackend
```

Перезапуск:
```cmd
net stop DelticaBackend && net start DelticaBackend
```

Просмотр логов:
```cmd
C:\Deltica\backend\logs\deltica.log
```

## Обновление приложения

### Backend (на сервере):

1. Остановите службу:
   ```cmd
   net stop DelticaBackend
   ```

2. Обновите код:
   ```cmd
   cd C:\Deltica
   git pull
   uv sync
   ```

3. Примените миграции:
   ```cmd
   cd deployment
   run_migrations.bat
   ```

4. Запустите службу:
   ```cmd
   net start DelticaBackend
   ```

### Клиенты:

1. Соберите новый установщик
2. Удалите старую версию Deltica
3. Установите новую версию

## Резервное копирование

### Автоматическое (встроенное в приложение):

Администратор может создать backup через интерфейс приложения:
- Кнопка "Backup БД" в админ-панели
- Файлы сохраняются в `C:\Deltica\backend\backups\`

### Ручное (PostgreSQL):

```cmd
pg_dump -U postgres -d deltica_db > C:\Backups\deltica_backup_%date%.sql
```

## Устранение неполадок

### Backend не запускается:

1. Проверьте логи: `C:\Deltica\backend\logs\deltica.log`
2. Проверьте .env файл
3. Проверьте доступ к PostgreSQL

### Клиент не подключается:

1. Проверьте config.json (правильный IP сервера?)
2. Проверьте доступность сервера: `ping 192.168.1.100`
3. Проверьте порт: `telnet 192.168.1.100 8000`
4. Проверьте файрвол на сервере

### Windows SSO не работает:

1. Проверьте, что username пользователя настроен в `config/users_config.yaml`
2. Запустите синхронизацию: `cd deployment && sync_users.bat`
3. Проверьте логи backend

## Контакты

При возникновении проблем обратитесь к администратору системы.
