# deltica/backend/core/logging_config.py

import logging
import sys
import os
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
import json
from datetime import datetime
from typing import Any, Dict


def get_logs_dir() -> Path:
    """
    Получить директорию для логов.

    - Для PyInstaller exe: папка logs/ рядом с exe
    - Fallback при отсутствии прав (Program Files): AppData/Local/Deltica/logs
    - Для разработки: backend/logs/
    """
    if getattr(sys, 'frozen', False):
        # Запущено из PyInstaller exe
        exe_dir = Path(sys.executable).parent
        logs_dir = exe_dir / "logs"

        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
            # Проверяем права на запись
            test_file = logs_dir / ".write_test"
            test_file.touch()
            test_file.unlink()
            return logs_dir
        except (PermissionError, OSError):
            # Нет прав на запись (например, Program Files)
            # Fallback в AppData
            appdata = Path(os.environ.get('LOCALAPPDATA', os.environ.get('APPDATA', '.')))
            logs_dir = appdata / "Deltica" / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            print(f"[WARNING] No write permission in exe directory, using: {logs_dir}")
            return logs_dir
    else:
        # Development mode
        logs_dir = Path("backend/logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir


class JSONFormatter(logging.Formatter):
    """
    Форматтер для вывода логов в JSON формате.
    Удобно для парсинга и анализа.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Форматирование записи лога в JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Добавляем дополнительные поля из record
        if hasattr(record, "event"):
            log_data["event"] = record.event
        if hasattr(record, "user"):
            log_data["user"] = record.user
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "ip"):
            log_data["ip"] = record.ip
        if hasattr(record, "equipment_id"):
            log_data["equipment_id"] = record.equipment_id

        # Добавляем информацию об ошибке если есть
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging():
    """
    Настройка системы логирования приложения.

    - JSON формат логов
    - Ротация: ежедневная, хранить 30 дней
    - Логи: рядом с exe (или AppData при отсутствии прав), для dev - backend/logs/
    - Дублирование в console (для разработки)
    """
    # Получаем директорию для логов (с учётом прав доступа)
    logs_dir = get_logs_dir()

    # Получаем root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Очищаем существующие handlers (если есть)
    logger.handlers.clear()

    # === File Handler с ротацией ===
    log_file = logs_dir / "deltica.log"

    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",  # Ротация в полночь
        interval=1,       # Каждый день
        backupCount=30,   # Хранить 30 дней
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    # === Console Handler (для разработки) ===
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Для консоли используем простой формат (не JSON)
    console_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # Логируем старт приложения
    logger.info("Logging system initialized", extra={"event": "app_startup"})

    return logger


# Вспомогательная функция для логирования с дополнительными полями
def log_event(
    logger: logging.Logger,
    level: str,
    message: str,
    **kwargs
):
    """
    Логирование события с дополнительными полями.

    Args:
        logger: Logger instance
        level: Уровень логирования ('info', 'warning', 'error')
        message: Сообщение
        **kwargs: Дополнительные поля для лога
    """
    log_method = getattr(logger, level.lower())
    log_method(message, extra=kwargs)
