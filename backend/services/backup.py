# deltica/backend/services/backup.py

import os
import subprocess
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models import BackupHistory
from backend.core.config import settings


class BackupService:
    """Сервис для создания и управления резервными копиями БД"""

    BACKUP_DIR = Path("backend/backups")

    def __init__(self):
        """Инициализация сервиса backup"""
        # Создаем директорию для backup, если её нет
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    def _find_pg_dump(self) -> Optional[str]:
        """
        Поиск pg_dump в системе (Windows/Linux).

        Returns:
            Optional[str]: Путь к pg_dump или None
        """
        # Сначала проверяем PATH
        pg_dump_path = shutil.which('pg_dump')
        if pg_dump_path:
            return pg_dump_path

        # Для Windows ищем в стандартных местах установки PostgreSQL
        if os.name == 'nt':  # Windows
            possible_paths = [
                r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe",
                r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
                r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
                r"C:\Program Files\PostgreSQL\14\bin\pg_dump.exe",
                r"C:\Program Files\PostgreSQL\13\bin\pg_dump.exe",
                r"C:\Program Files (x86)\PostgreSQL\17\bin\pg_dump.exe",
                r"C:\Program Files (x86)\PostgreSQL\16\bin\pg_dump.exe",
                r"C:\Program Files (x86)\PostgreSQL\15\bin\pg_dump.exe",
                r"C:\Program Files (x86)\PostgreSQL\14\bin\pg_dump.exe",
            ]

            for path in possible_paths:
                if Path(path).exists():
                    return path

        return None

    def can_create_backup(self, db: Session) -> tuple[bool, Optional[str]]:
        """
        Проверка возможности создания backup (не чаще 1 раза в месяц).

        Returns:
            tuple[bool, Optional[str]]: (можно ли создать backup, сообщение об ошибке)
        """
        # Получаем последний успешный backup
        last_backup = db.query(BackupHistory).filter(
            BackupHistory.status == 'success'
        ).order_by(BackupHistory.created_at.desc()).first()

        if last_backup:
            # Проверяем, прошел ли месяц с последнего backup
            one_month_ago = datetime.now() - timedelta(days=30)
            if last_backup.created_at.replace(tzinfo=None) > one_month_ago:
                return False, f"Backup уже создан {last_backup.created_at.strftime('%d.%m.%Y %H:%M')}. Следующий backup можно создать не ранее {(last_backup.created_at + timedelta(days=30)).strftime('%d.%m.%Y')}"

        return True, None

    def create_backup(self, db: Session, username: str) -> BackupHistory:
        """
        Создание резервной копии БД с помощью pg_dump.

        Args:
            db: Сессия БД
            username: Username администратора, создающего backup

        Returns:
            BackupHistory: Запись о созданном backup
        """
        # Генерируем имя файла с датой и временем
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"deltica_backup_{timestamp}.sql"
        file_path = self.BACKUP_DIR / file_name

        # Ищем pg_dump
        pg_dump_exe = self._find_pg_dump()
        if not pg_dump_exe:
            error_msg = "pg_dump не найден в системе. Установите PostgreSQL или добавьте pg_dump в PATH."
            backup_record = BackupHistory(
                file_name=file_name,
                file_path="",
                file_size=0,
                created_by=username,
                status='failed',
                error_message=error_msg
            )
            db.add(backup_record)
            db.commit()
            db.refresh(backup_record)
            raise Exception(error_msg)

        # Подготовка переменных окружения для pg_dump (для аутентификации)
        env = os.environ.copy()
        env['PGPASSWORD'] = settings.DB_PASSWORD

        # Команда pg_dump для создания backup
        pg_dump_cmd = [
            pg_dump_exe,
            '-h', settings.DB_HOST,
            '-p', str(settings.DB_PORT),
            '-U', settings.DB_USER,
            '-d', settings.DB_NAME,
            '-F', 'p',  # plain text format (SQL)
            '-f', str(file_path)
        ]

        try:
            # Выполняем pg_dump
            result = subprocess.run(
                pg_dump_cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )

            # Получаем размер файла
            file_size = file_path.stat().st_size

            # Создаем запись в истории backup
            backup_record = BackupHistory(
                file_name=file_name,
                file_path=str(file_path),
                file_size=file_size,
                created_by=username,
                status='success'
            )
            db.add(backup_record)
            db.commit()
            db.refresh(backup_record)

            return backup_record

        except subprocess.CalledProcessError as e:
            # В случае ошибки создаем запись с failed status
            error_msg = f"Ошибка выполнения pg_dump: {e.stderr}"

            backup_record = BackupHistory(
                file_name=file_name,
                file_path=str(file_path) if file_path.exists() else "",
                file_size=0,
                created_by=username,
                status='failed',
                error_message=error_msg
            )
            db.add(backup_record)
            db.commit()
            db.refresh(backup_record)

            # Удаляем неполный файл, если он был создан
            if file_path.exists():
                file_path.unlink()

            raise Exception(error_msg)

        except Exception as e:
            # Обработка других ошибок
            error_msg = f"Неизвестная ошибка при создании backup: {str(e)}"

            backup_record = BackupHistory(
                file_name=file_name,
                file_path=str(file_path) if file_path.exists() else "",
                file_size=0,
                created_by=username,
                status='failed',
                error_message=error_msg
            )
            db.add(backup_record)
            db.commit()
            db.refresh(backup_record)

            # Удаляем неполный файл, если он был создан
            if file_path.exists():
                file_path.unlink()

            raise Exception(error_msg)

    def get_backup_history(self, db: Session, limit: int = 20) -> List[BackupHistory]:
        """
        Получить историю backup (последние N записей).

        Args:
            db: Сессия БД
            limit: Максимальное количество записей

        Returns:
            List[BackupHistory]: Список записей истории backup
        """
        return db.query(BackupHistory).order_by(
            BackupHistory.created_at.desc()
        ).limit(limit).all()

    def get_backup_by_id(self, db: Session, backup_id: int) -> Optional[BackupHistory]:
        """
        Получить запись о backup по ID.

        Args:
            db: Сессия БД
            backup_id: ID записи backup

        Returns:
            Optional[BackupHistory]: Запись о backup или None
        """
        return db.query(BackupHistory).filter(BackupHistory.id == backup_id).first()

    def delete_backup(self, db: Session, backup_id: int) -> bool:
        """
        Удалить backup файл и запись из истории.

        Args:
            db: Сессия БД
            backup_id: ID записи backup

        Returns:
            bool: True если успешно удален
        """
        backup = self.get_backup_by_id(db, backup_id)
        if not backup:
            return False

        # Удаляем файл, если он существует
        file_path = Path(backup.file_path)
        if file_path.exists():
            file_path.unlink()

        # Удаляем запись из БД
        db.delete(backup)
        db.commit()

        return True
