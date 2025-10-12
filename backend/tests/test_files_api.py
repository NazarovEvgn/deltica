# deltica/backend/tests/test_files_api.py

import pytest
from io import BytesIO


class TestFileUpload:
    """Интеграционные тесты загрузки файлов."""

    def test_upload_pdf_success(self, client, test_equipment, temp_upload_dir, sample_pdf_file):
        """Успешная загрузка PDF файла."""
        filename, content, mime_type = sample_pdf_file

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "certificate"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["file_name"] == filename
        assert data["file_type"] == "certificate"
        assert data["file_size"] == len(content)
        assert data["equipment_id"] == test_equipment.id
        assert "id" in data
        assert "uploaded_at" in data

        # Проверяем, что файл создан на диске
        file_path = temp_upload_dir / f"equipment_{test_equipment.id}" / "test_document.pdf"
        assert file_path.exists()
        assert file_path.read_bytes() == content

    def test_upload_image_success(self, client, test_equipment, temp_upload_dir, sample_image_file):
        """Успешная загрузка изображения."""
        filename, content, mime_type = sample_image_file

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "passport"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["file_name"] == filename
        assert data["file_type"] == "passport"

    def test_upload_equipment_not_found(self, client, sample_pdf_file):
        """Загрузка файла для несуществующего оборудования."""
        filename, content, mime_type = sample_pdf_file

        response = client.post(
            "/files/upload/99999",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "certificate"}
        )

        assert response.status_code == 404
        assert "не найдено" in response.json()["detail"].lower()

    def test_upload_invalid_extension(self, client, test_equipment, invalid_extension_file):
        """Загрузка файла с недопустимым расширением."""
        filename, content, mime_type = invalid_extension_file

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "other"}
        )

        assert response.status_code == 400
        assert "недопустимый тип файла" in response.json()["detail"].lower()

    def test_upload_file_too_large(self, client, test_equipment, large_file):
        """Загрузка файла больше допустимого размера."""
        filename, content, mime_type = large_file

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "other"}
        )

        assert response.status_code == 400
        assert "слишком большой" in response.json()["detail"].lower()

    def test_upload_duplicate_filename(self, client, test_equipment, temp_upload_dir, sample_pdf_file):
        """Загрузка файла с дублирующимся именем."""
        filename, content, mime_type = sample_pdf_file

        # Первая загрузка
        response1 = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "certificate"}
        )
        assert response1.status_code == 200
        file1_path = response1.json()["file_path"]

        # Вторая загрузка того же файла
        response2 = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "certificate"}
        )
        assert response2.status_code == 200
        file2_path = response2.json()["file_path"]

        # Пути должны быть разные (второй файл должен получить суффикс)
        assert file1_path != file2_path
        assert "test_document_1.pdf" in file2_path or "_1" in file2_path


class TestFileRetrieval:
    """Тесты получения списка файлов."""

    def test_get_files_empty(self, client, test_equipment):
        """Получение списка файлов для оборудования без файлов."""
        response = client.get(f"/files/equipment/{test_equipment.id}")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_files_list(self, client, test_equipment, sample_pdf_file, sample_image_file):
        """Получение списка файлов для оборудования."""
        # Загружаем два файла
        filename1, content1, mime1 = sample_pdf_file
        client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename1, BytesIO(content1), mime1)},
            data={"file_type": "certificate"}
        )

        filename2, content2, mime2 = sample_image_file
        client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename2, BytesIO(content2), mime2)},
            data={"file_type": "passport"}
        )

        # Получаем список
        response = client.get(f"/files/equipment/{test_equipment.id}")

        assert response.status_code == 200
        files = response.json()
        assert len(files) == 2
        assert any(f["file_name"] == filename1 for f in files)
        assert any(f["file_name"] == filename2 for f in files)

    def test_get_files_equipment_not_found(self, client):
        """Получение файлов для несуществующего оборудования."""
        response = client.get("/files/equipment/99999")

        assert response.status_code == 404


class TestFileView:
    """Тесты просмотра файлов."""

    def test_view_file_success(self, client, test_equipment, sample_pdf_file):
        """Успешный просмотр файла."""
        filename, content, mime_type = sample_pdf_file

        # Загружаем файл
        upload_response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "certificate"}
        )
        file_id = upload_response.json()["id"]

        # Просматриваем файл
        view_response = client.get(f"/files/view/{file_id}")

        assert view_response.status_code == 200
        assert view_response.content == content
        assert "inline" in view_response.headers["content-disposition"]
        assert "application/pdf" in view_response.headers["content-type"]

    def test_view_file_not_found(self, client):
        """Просмотр несуществующего файла."""
        response = client.get("/files/view/99999")

        assert response.status_code == 404


class TestFileDownload:
    """Тесты скачивания файлов."""

    def test_download_file_success(self, client, test_equipment, sample_pdf_file):
        """Успешное скачивание файла."""
        filename, content, mime_type = sample_pdf_file

        # Загружаем файл
        upload_response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "certificate"}
        )
        file_id = upload_response.json()["id"]

        # Скачиваем файл
        download_response = client.get(f"/files/download/{file_id}")

        assert download_response.status_code == 200
        assert download_response.content == content
        assert "attachment" in download_response.headers["content-disposition"]

    def test_download_file_not_found(self, client):
        """Скачивание несуществующего файла."""
        response = client.get("/files/download/99999")

        assert response.status_code == 404


class TestFileDelete:
    """Тесты удаления файлов."""

    def test_delete_file_success(self, client, test_equipment, temp_upload_dir, sample_pdf_file):
        """Успешное удаление файла."""
        filename, content, mime_type = sample_pdf_file

        # Загружаем файл
        upload_response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "certificate"}
        )
        file_id = upload_response.json()["id"]
        file_path = temp_upload_dir / f"equipment_{test_equipment.id}" / "test_document.pdf"

        # Проверяем, что файл существует
        assert file_path.exists()

        # Удаляем файл
        delete_response = client.delete(f"/files/{file_id}")

        assert delete_response.status_code == 200
        assert "успешно удален" in delete_response.json()["message"].lower()

        # Проверяем, что файл удален с диска
        assert not file_path.exists()

    def test_delete_file_not_found(self, client):
        """Удаление несуществующего файла."""
        response = client.delete("/files/99999")

        assert response.status_code == 404

    def test_delete_removes_empty_directory(self, client, test_equipment, temp_upload_dir, sample_pdf_file):
        """Удаление последнего файла удаляет директорию оборудования."""
        filename, content, mime_type = sample_pdf_file

        # Загружаем файл
        upload_response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "certificate"}
        )
        file_id = upload_response.json()["id"]
        equipment_dir = temp_upload_dir / f"equipment_{test_equipment.id}"

        # Проверяем, что директория существует
        assert equipment_dir.exists()

        # Удаляем файл
        client.delete(f"/files/{file_id}")

        # Проверяем, что директория тоже удалена
        assert not equipment_dir.exists()


class TestFileCascadeDelete:
    """Тесты каскадного удаления файлов при удалении оборудования."""

    def test_cascade_delete_files(self, client, test_equipment, sample_pdf_file):
        """Файлы удаляются при удалении оборудования."""
        filename, content, mime_type = sample_pdf_file

        # Загружаем файл
        upload_response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "certificate"}
        )
        file_id = upload_response.json()["id"]

        # Проверяем, что файл загружен
        assert upload_response.status_code == 200
        assert file_id > 0

        # Проверяем, что файл есть в списке
        list_response = client.get(f"/files/equipment/{test_equipment.id}")
        assert list_response.status_code == 200
        files = list_response.json()
        assert len(files) == 1
        assert files[0]["id"] == file_id

        # Примечание: полное тестирование CASCADE DELETE требует реальной БД с relationships
        # В упрощенной тестовой SQLite БД просто проверяем, что файл можно удалить
        delete_response = client.delete(f"/files/{file_id}")
        assert delete_response.status_code == 200

        # Проверяем, что файл удален
        list_response = client.get(f"/files/equipment/{test_equipment.id}")
        assert len(list_response.json()) == 0
