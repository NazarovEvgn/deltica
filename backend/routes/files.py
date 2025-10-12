# deltica/backend/routes/files.py

import os
import shutil
from pathlib import Path
from typing import List
from urllib.parse import quote
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.app.models import EquipmentFile, Equipment
from backend.app.schemas import EquipmentFileResponse

router = APIRouter(prefix="/files", tags=["files"])

# Константы
UPLOAD_DIR = Path("backend/uploads")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 МБ в байтах
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".xls", ".xlsx"}


def get_file_extension(filename: str) -> str:
    """Получить расширение файла."""
    return Path(filename).suffix.lower()


def is_allowed_file(filename: str) -> bool:
    """Проверить, разрешено ли расширение файла."""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def sanitize_filename(filename: str) -> str:
    """Санитизация имени файла для безопасности."""
    # Удаляем опасные символы и оставляем только безопасные
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.")
    safe_filename = "".join(c if c in safe_chars else "_" for c in filename)
    return safe_filename


def get_media_type(filename: str) -> str:
    """Определить MIME-тип файла по расширению."""
    ext = get_file_extension(filename)

    mime_types = {
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
    }

    return mime_types.get(ext, 'application/octet-stream')


@router.post("/upload/{equipment_id}", response_model=EquipmentFileResponse)
async def upload_file(
    equipment_id: int,
    file: UploadFile = File(...),
    file_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Загрузить файл для оборудования.

    - **equipment_id**: ID оборудования
    - **file**: Загружаемый файл
    - **file_type**: Тип файла (certificate, passport, technical_doc, other)
    """
    # Проверка существования оборудования
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Оборудование не найдено")

    # Проверка расширения файла
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый тип файла. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Чтение файла и проверка размера
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE / (1024*1024):.0f} МБ"
        )

    # Создание директории для оборудования
    equipment_dir = UPLOAD_DIR / f"equipment_{equipment_id}"
    equipment_dir.mkdir(parents=True, exist_ok=True)

    # Санитизация имени файла
    safe_filename = sanitize_filename(file.filename)

    # Проверка на уникальность имени файла
    file_path = equipment_dir / safe_filename
    counter = 1
    original_stem = Path(safe_filename).stem
    original_ext = Path(safe_filename).suffix

    while file_path.exists():
        safe_filename = f"{original_stem}_{counter}{original_ext}"
        file_path = equipment_dir / safe_filename
        counter += 1

    # Сохранение файла на диск
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Сохранение информации о файле в БД
    relative_path = f"equipment_{equipment_id}/{safe_filename}"

    db_file = EquipmentFile(
        equipment_id=equipment_id,
        file_name=file.filename,  # Оригинальное имя
        file_path=relative_path,
        file_type=file_type,
        file_size=file_size
    )

    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return db_file


@router.get("/equipment/{equipment_id}", response_model=List[EquipmentFileResponse])
def get_equipment_files(equipment_id: int, db: Session = Depends(get_db)):
    """Получить список всех файлов для оборудования."""
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Оборудование не найдено")

    files = db.query(EquipmentFile).filter(EquipmentFile.equipment_id == equipment_id).all()
    return files


@router.get("/view/{file_id}")
def view_file(file_id: int, db: Session = Depends(get_db)):
    """Открыть файл для просмотра в браузере."""
    db_file = db.query(EquipmentFile).filter(EquipmentFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не найден")

    file_path = UPLOAD_DIR / db_file.file_path

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден на диске")

    # Определяем MIME-тип для правильного отображения в браузере
    media_type = get_media_type(db_file.file_name)

    # Кодируем имя файла для корректной работы с кириллицей
    encoded_filename = quote(db_file.file_name)

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{encoded_filename}"
        }
    )


@router.get("/download/{file_id}")
def download_file(file_id: int, db: Session = Depends(get_db)):
    """Скачать файл по ID (принудительное скачивание)."""
    db_file = db.query(EquipmentFile).filter(EquipmentFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не найден")

    file_path = UPLOAD_DIR / db_file.file_path

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден на диске")

    # Кодируем имя файла для корректной работы с кириллицей
    encoded_filename = quote(db_file.file_name)

    return FileResponse(
        path=str(file_path),
        filename=db_file.file_name,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )


@router.delete("/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    """Удалить файл по ID."""
    db_file = db.query(EquipmentFile).filter(EquipmentFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Файл не найден")

    # Удаление файла с диска
    file_path = UPLOAD_DIR / db_file.file_path
    if file_path.exists():
        file_path.unlink()

    # Проверка, если директория оборудования пуста - удаляем её
    equipment_dir = file_path.parent
    if equipment_dir.exists() and not any(equipment_dir.iterdir()):
        equipment_dir.rmdir()

    # Удаление записи из БД
    db.delete(db_file)
    db.commit()

    return {"message": "Файл успешно удален"}
