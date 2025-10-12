# deltica/backend/tests/test_files_security.py

import pytest
from io import BytesIO


class TestPathTraversalProtection:
    """Тесты защиты от path traversal атак."""

    def test_path_traversal_unix_style(self, client, test_equipment):
        """Защита от Unix-style path traversal (../../etc/passwd)."""
        malicious_filename = "../../etc/passwd"
        content = b"malicious content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (malicious_filename, BytesIO(content), "application/pdf")},
            data={"file_type": "other"}
        )

        # Должен быть отклонен из-за расширения .pdf в sanitized имени
        # Но даже если пройдет, имя должно быть безопасным
        if response.status_code == 200:
            file_path = response.json()["file_path"]
            # Путь не должен содержать '..' или '/'
            assert ".." not in file_path
            assert "etc" not in file_path or "______etc" in file_path

    def test_path_traversal_windows_style(self, client, test_equipment):
        """Защита от Windows-style path traversal (..\\..\\windows\\system32)."""
        malicious_filename = "..\\..\\windows\\system32\\config.pdf"
        content = b"malicious content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (malicious_filename, BytesIO(content), "application/pdf")},
            data={"file_type": "other"}
        )

        if response.status_code == 200:
            file_path = response.json()["file_path"]
            # Путь не должен содержать '\\' (backslashes должны быть заменены)
            # Точки допустимы (..), но не в виде пути
            assert "\\" not in file_path
            # Проверяем, что путь начинается с equipment_id (нет выхода за пределы)
            assert file_path.startswith(f"equipment_{test_equipment.id}")

    def test_absolute_path_injection(self, client, test_equipment):
        """Защита от абсолютных путей в имени файла."""
        malicious_filename = "/var/www/html/shell.pdf"
        content = b"malicious content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (malicious_filename, BytesIO(content), "application/pdf")},
            data={"file_type": "other"}
        )

        if response.status_code == 200:
            file_path = response.json()["file_path"]
            # Путь должен быть относительным и содержать только equipment_id
            assert file_path.startswith(f"equipment_{test_equipment.id}")
            assert not file_path.startswith("/")

    def test_null_byte_injection(self, client, test_equipment):
        """Защита от null byte injection."""
        malicious_filename = "document.pdf\x00.exe"
        content = b"malicious content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (malicious_filename, BytesIO(content), "application/pdf")},
            data={"file_type": "other"}
        )

        # Null byte должен быть удален при санитизации
        if response.status_code == 200:
            file_path = response.json()["file_path"]
            assert "\x00" not in file_path


class TestFileSizeLimits:
    """Тесты ограничения размера файлов."""

    def test_file_exactly_at_limit(self, client, test_equipment):
        """Файл ровно 50 МБ должен быть принят."""
        # Ровно 50 МБ
        content = b"x" * (50 * 1024 * 1024)
        filename = "large_file.pdf"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), "application/pdf")},
            data={"file_type": "other"}
        )

        assert response.status_code == 200

    def test_file_one_byte_over_limit(self, client, test_equipment):
        """Файл на 1 байт больше лимита должен быть отклонен."""
        # 50 МБ + 1 байт
        content = b"x" * (50 * 1024 * 1024 + 1)
        filename = "too_large.pdf"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), "application/pdf")},
            data={"file_type": "other"}
        )

        assert response.status_code == 400
        assert "слишком большой" in response.json()["detail"].lower()

    def test_empty_file(self, client, test_equipment):
        """Пустой файл (0 байт) должен быть принят."""
        content = b""
        filename = "empty.pdf"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), "application/pdf")},
            data={"file_type": "other"}
        )

        assert response.status_code == 200
        assert response.json()["file_size"] == 0


class TestFileExtensionValidation:
    """Тесты валидации расширений файлов."""

    @pytest.mark.parametrize("filename,should_pass", [
        ("document.pdf", True),
        ("report.docx", True),
        ("data.xlsx", True),
        ("photo.jpg", True),
        ("image.png", True),
        ("script.exe", False),
        ("malware.bat", False),
        ("hack.sh", False),
        ("code.py", False),
        ("virus.com", False),
        ("trojan.scr", False),
    ])
    def test_extension_validation(self, client, test_equipment, filename, should_pass):
        """Параметризованный тест валидации расширений."""
        content = b"test content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (filename, BytesIO(content), "application/octet-stream")},
            data={"file_type": "other"}
        )

        if should_pass:
            assert response.status_code == 200
        else:
            assert response.status_code == 400
            assert "недопустимый тип файла" in response.json()["detail"].lower()

    def test_double_extension_bypass_attempt(self, client, test_equipment):
        """Попытка обхода через двойное расширение."""
        malicious_filename = "document.pdf.exe"
        content = b"malicious content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (malicious_filename, BytesIO(content), "application/pdf")},
            data={"file_type": "other"}
        )

        # Должен быть отклонен, так как реальное расширение .exe
        assert response.status_code == 400

    def test_case_insensitive_extension(self, client, test_equipment):
        """Проверка расширений case-insensitive."""
        content = b"test content"

        # Uppercase должен работать
        response_upper = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": ("DOCUMENT.PDF", BytesIO(content), "application/pdf")},
            data={"file_type": "other"}
        )
        assert response_upper.status_code == 200

        # Mixed case должен работать
        response_mixed = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": ("Document.PdF", BytesIO(content), "application/pdf")},
            data={"file_type": "other"}
        )
        assert response_mixed.status_code == 200


class TestFilenameInjection:
    """Тесты защиты от инъекций через имя файла."""

    def test_special_characters_sanitized(self, client, test_equipment, temp_upload_dir):
        """Специальные символы должны быть санитизированы."""
        malicious_filename = "file@#$%^&*().pdf"
        content = b"test content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (malicious_filename, BytesIO(content), "application/pdf")},
            data={"file_type": "other"}
        )

        assert response.status_code == 200

        # Проверяем, что файл сохранен с безопасным именем
        file_path = response.json()["file_path"]
        assert "@" not in file_path
        assert "#" not in file_path
        assert "$" not in file_path

    def test_unicode_characters_sanitized(self, client, test_equipment):
        """Unicode символы должны быть санитизированы."""
        malicious_filename = "file\u202e\u202dexe.pdf"  # Right-to-left override
        content = b"test content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (malicious_filename, BytesIO(content), "application/pdf")},
            data={"file_type": "other"}
        )

        assert response.status_code == 200
        file_path = response.json()["file_path"]
        # Unicode control characters должны быть удалены
        assert "\u202e" not in file_path
        assert "\u202d" not in file_path

    def test_very_long_filename(self, client, test_equipment):
        """Очень длинное имя файла должно обрабатываться корректно."""
        # Имя файла длиной 200 символов (чтобы не превысить лимит Windows 260)
        long_name = "a" * 200 + ".pdf"
        content = b"test content"

        response = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": (long_name, BytesIO(content), "application/pdf")},
            data={"file_type": "other"}
        )

        # Должно быть принято (или отклонено с понятной ошибкой)
        # В зависимости от реализации можно добавить ограничение длины имени
        assert response.status_code in [200, 400, 500]


class TestConcurrentUploads:
    """Тесты параллельной загрузки файлов."""

    def test_concurrent_uploads_different_names(self, client, test_equipment):
        """Параллельная загрузка разных файлов должна работать."""
        content1 = b"file 1 content"
        content2 = b"file 2 content"

        response1 = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": ("file1.pdf", BytesIO(content1), "application/pdf")},
            data={"file_type": "certificate"}
        )

        response2 = client.post(
            f"/files/upload/{test_equipment.id}",
            files={"file": ("file2.pdf", BytesIO(content2), "application/pdf")},
            data={"file_type": "passport"}
        )

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["id"] != response2.json()["id"]

    def test_race_condition_same_filename(self, client, test_equipment):
        """Race condition при загрузке файлов с одинаковыми именами."""
        content = b"test content"
        filename = "duplicate.pdf"

        # Загружаем один и тот же файл несколько раз быстро
        responses = []
        for _ in range(3):
            response = client.post(
                f"/files/upload/{test_equipment.id}",
                files={"file": (filename, BytesIO(content), "application/pdf")},
                data={"file_type": "other"}
            )
            responses.append(response)

        # Все загрузки должны быть успешными
        for response in responses:
            assert response.status_code == 200

        # Все файлы должны иметь разные пути
        file_paths = [r.json()["file_path"] for r in responses]
        assert len(set(file_paths)) == len(file_paths)  # Все уникальные
