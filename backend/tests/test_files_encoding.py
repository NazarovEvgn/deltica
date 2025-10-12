# deltica/backend/tests/test_files_encoding.py

import pytest
from io import BytesIO
from urllib.parse import unquote


class TestCyrillicFilenames:
    """Тесты работы с кириллическими именами файлов."""

    def test_upload_cyrillic_filename(self, client, test_equipment, temp_upload_dir, sample_cyrillic_file):
        """Загрузка файла с кириллическим именем."""
        filename, content, mime_type = sample_cyrillic_file

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "certificate"}
        )

        assert response.status_code == 200
        data = response.json()
        # Оригинальное имя должно быть сохранено в БД
        assert data["file_name"] == filename

    def test_view_cyrillic_filename(self, client, test_equipment, sample_cyrillic_file):
        """Просмотр файла с кириллическим именем."""
        filename, content, mime_type = sample_cyrillic_file

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

        # Проверяем заголовок Content-Disposition с правильной кодировкой
        content_disposition = view_response.headers.get("content-disposition", "")
        assert "inline" in content_disposition
        assert "UTF-8''" in content_disposition or "utf-8''" in content_disposition.lower()

    def test_download_cyrillic_filename(self, client, test_equipment, sample_cyrillic_file):
        """Скачивание файла с кириллическим именем."""
        filename, content, mime_type = sample_cyrillic_file

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

        # Проверяем заголовок Content-Disposition
        content_disposition = download_response.headers.get("content-disposition", "")
        assert "attachment" in content_disposition
        assert "UTF-8''" in content_disposition or "utf-8''" in content_disposition.lower()

    def test_cyrillic_filename_preserved_in_database(self, client, test_equipment, db_session, sample_cyrillic_file):
        """Кириллическое имя должно сохраниться в БД без искажений."""
        filename, content, mime_type = sample_cyrillic_file

        # Загружаем файл
        upload_response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "certificate"}
        )
        file_id = upload_response.json()["id"]

        # Читаем из БД напрямую
        from backend.app.models import EquipmentFile
        db_file = db_session.query(EquipmentFile).filter(EquipmentFile.id == file_id).first()

        assert db_file is not None
        assert db_file.file_name == filename
        # Проверяем, что кириллица не повреждена
        assert "Сертификат" in db_file.file_name
        assert "поверки" in db_file.file_name


class TestMixedLanguageFilenames:
    """Тесты файлов со смешанными языками в имени."""

    @pytest.mark.parametrize("filename", [
        "Certificate Сертификат №123.pdf",
        "Паспорт Device Model-2023.pdf",
        "Документация_Equipment_v1.0.pdf",
        "Отчет Report 2024-01-15.pdf",
    ])
    def test_mixed_language_upload(self, client, test_equipment, filename):
        """Загрузка файлов со смешанными языками в имени."""
        content = b"test content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), "application/pdf")},
            data={"file_type": "other"}
        )

        assert response.status_code == 200
        # Оригинальное имя должно быть сохранено
        assert response.json()["file_name"] == filename


class TestSpecialCyrillicCharacters:
    """Тесты специальных кириллических символов."""

    def test_cyrillic_with_numbers(self, client, test_equipment):
        """Кириллица с числами в имени файла."""
        filename = "Сертификат №12345 от 2024.pdf"
        content = b"test content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), "application/pdf")},
            data={"file_type": "certificate"}
        )

        assert response.status_code == 200
        assert response.json()["file_name"] == filename

    def test_cyrillic_with_spaces(self, client, test_equipment):
        """Кириллица с пробелами."""
        filename = "Техническая документация оборудования.pdf"
        content = b"test content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), "application/pdf")},
            data={"file_type": "technical_doc"}
        )

        assert response.status_code == 200
        assert response.json()["file_name"] == filename

    def test_cyrillic_with_parentheses(self, client, test_equipment):
        """Кириллица со скобками."""
        filename = "Паспорт (копия) 2024.pdf"
        content = b"test content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), "application/pdf")},
            data={"file_type": "passport"}
        )

        assert response.status_code == 200
        assert response.json()["file_name"] == filename


class TestFileListEncoding:
    """Тесты правильного отображения списка файлов с кириллицей."""

    def test_list_multiple_cyrillic_files(self, client, test_equipment):
        """Список нескольких файлов с кириллическими именами."""
        files_data = [
            ("Сертификат №1.pdf", b"content1"),
            ("Паспорт №2.pdf", b"content2"),
            ("Документация №3.pdf", b"content3"),
        ]

        # Загружаем файлы
        for filename, content in files_data:
            client.post(
                f"/files/upload/{test_equipment.id}",
                files={"file": (filename, BytesIO(content), "application/pdf")},
                data={"file_type": "other"}
            )

        # Получаем список
        response = client.get(f"/files/equipment/{test_equipment.id}")

        assert response.status_code == 200
        files = response.json()
        assert len(files) == 3

        # Проверяем, что все имена корректны
        filenames = [f["file_name"] for f in files]
        for original_filename, _ in files_data:
            assert original_filename in filenames


class TestEncodingEdgeCases:
    """Граничные случаи кодировки."""

    def test_long_cyrillic_filename(self, client, test_equipment):
        """Длинное кириллическое имя файла."""
        # Длинное имя (100+ символов кириллицы)
        long_name = "Сертификат о поверке средства измерения с очень длинным названием для проверки корректности обработки" + ".pdf"
        content = b"test content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (long_name, BytesIO(content), "application/pdf")},
            data={"file_type": "certificate"}
        )

        assert response.status_code == 200
        assert response.json()["file_name"] == long_name

    def test_cyrillic_only_filename(self, client, test_equipment):
        """Имя файла только из кириллицы (без латиницы)."""
        filename = "Сертификат.pdf"
        content = b"test content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), "application/pdf")},
            data={"file_type": "certificate"}
        )

        assert response.status_code == 200
        assert response.json()["file_name"] == filename

    def test_latin_only_filename(self, client, test_equipment):
        """Имя файла только из латиницы (для сравнения)."""
        filename = "Certificate.pdf"
        content = b"test content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), "application/pdf")},
            data={"file_type": "certificate"}
        )

        assert response.status_code == 200
        assert response.json()["file_name"] == filename


class TestContentDispositionHeader:
    """Тесты корректности заголовка Content-Disposition."""

    def test_content_disposition_rfc5987_format(self, client, test_equipment, sample_cyrillic_file):
        """Content-Disposition должен соответствовать RFC 5987."""
        filename, content, mime_type = sample_cyrillic_file

        # Загружаем файл
        upload_response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "certificate"}
        )
        file_id = upload_response.json()["id"]

        # Проверяем заголовок при просмотре
        view_response = client.get(f"/files/view/{file_id}")
        content_disposition = view_response.headers.get("content-disposition", "")

        # Формат должен быть: inline; filename*=UTF-8''%encoded%name
        assert "inline" in content_disposition
        assert "filename*=" in content_disposition
        assert "UTF-8''" in content_disposition or "utf-8''" in content_disposition.lower()

    def test_content_disposition_inline_vs_attachment(self, client, test_equipment, sample_cyrillic_file):
        """Разница между inline (просмотр) и attachment (скачивание)."""
        filename, content, mime_type = sample_cyrillic_file

        # Загружаем файл
        upload_response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), mime_type)},
            data={"file_type": "certificate"}
        )
        file_id = upload_response.json()["id"]

        # Проверяем заголовок при просмотре
        view_response = client.get(f"/files/view/{file_id}")
        view_disposition = view_response.headers.get("content-disposition", "")
        assert "inline" in view_disposition

        # Проверяем заголовок при скачивании
        download_response = client.get(f"/files/download/{file_id}")
        download_disposition = download_response.headers.get("content-disposition", "")
        assert "attachment" in download_disposition
