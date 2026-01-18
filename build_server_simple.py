#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Простой скрипт сборки сервера без PowerShell"""

import subprocess
import sys
import os
from pathlib import Path

# PyInstaller spec content
SPEC_CONTENT = """# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
import os

block_cipher = None

# Функция для сбора файлов backend БЕЗ папки uploads
# ВАЖНО: uploads/ намеренно НЕ включена в сборку!
# Причина: runtime папка для файлов пользователей, должна быть пустой при установке
def get_backend_datas():
    datas = []
    # uploads НАМЕРЕННО отсутствует в списке - это runtime папка
    backend_subdirs = ['app', 'core', 'routes', 'services', 'middleware', 'utils', 'database_dumps']

    for subdir in backend_subdirs:
        src_path = os.path.join('backend', subdir)
        if os.path.exists(src_path):
            datas.append((src_path, os.path.join('backend', subdir)))

    return datas

a = Analysis(
    ['backend/core/main.py'],
    pathex=[],
    binaries=[],
    datas=get_backend_datas(),
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'passlib.handlers.bcrypt',
        'sqlalchemy.sql.default_comparator',
        'pydantic_settings',
        'dateutil',
        'dateutil.relativedelta',
        'jose',
        'jose.jwt',
        'jose.jws',
        'jose.jwk',
        'jose.exceptions',
        'pandas',
        'psycopg',
        'psycopg2',
        'alembic.operations',
        'docxtpl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy.tests',
        'scipy',
        'pytest',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='deltica-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

def main():
    print("=" * 60)
    print("  Deltica Server Build Script (Python)")
    print("=" * 60)
    print()

    # Check we're in project root
    if not Path("backend").exists():
        print("ERROR: Run from project root!")
        return 1

    # Step 1: Install PyInstaller
    print("[1/4] Installing PyInstaller...")
    try:
        subprocess.run(["uv", "pip", "install", "pyinstaller"], check=True)
        print("  [OK] PyInstaller installed")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Error installing PyInstaller: {e}")
        return 1

    # Step 2: Create spec file
    print("\n[2/4] Creating PyInstaller spec...")
    with open("deltica-server.spec", "w", encoding="utf-8") as f:
        f.write(SPEC_CONTENT)
    print("  [OK] Spec file created")

    # Step 3: Run PyInstaller
    print("\n[3/4] Compiling backend to .exe (2-5 minutes)...")
    print("  This may take a few minutes, please wait...")
    try:
        subprocess.run([
            "uv", "run", "pyinstaller",
            "deltica-server.spec",
            "--clean",
            "--distpath", "./dist/server",
            "--workpath", "./build/server"
        ], check=True)

        exe_path = Path("dist/server/deltica-server.exe")
        if not exe_path.exists():
            print("  [ERROR] deltica-server.exe not found after build!")
            return 1

        exe_size = exe_path.stat().st_size / (1024 * 1024)
        print(f"  [OK] Backend compiled: deltica-server.exe ({exe_size:.2f} MB)")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Compilation error: {e}")
        return 1

    # Step 4: Create release structure
    print("\n[4/4] Creating release structure...")

    release_dir = Path("dist/Deltica-Server-v1.0.6")
    if release_dir.exists():
        import shutil
        shutil.rmtree(release_dir)
    release_dir.mkdir(parents=True)

    # Copy exe
    import shutil
    shutil.copy("dist/server/deltica-server.exe", release_dir / "deltica-server.exe")
    print("  [OK] Copied deltica-server.exe")

    # Create directories
    (release_dir / "uploads").mkdir()
    (release_dir / "logs").mkdir()
    (release_dir / "backups").mkdir()
    print("  [OK] Created directories: uploads, logs, backups")

    # Copy database dump
    dump_src = Path("backend/database_dumps/deltica_initial.dump")
    if dump_src.exists():
        dump_dir = release_dir / "database_dumps"
        dump_dir.mkdir()
        shutil.copy(dump_src, dump_dir / "deltica_initial.dump")
        dump_size = (dump_dir / "deltica_initial.dump").stat().st_size / 1024
        print(f"  [OK] Copied database dump: deltica_initial.dump ({dump_size:.2f} KB)")
    else:
        print("  [WARNING] Database dump not found!")

    # Copy config, docs, migrations, alembic.ini
    for item in ["config", "docs", "migrations"]:
        if Path(item).exists():
            shutil.copytree(item, release_dir / item)
            print(f"  [OK] Copied folder: {item}")

    if Path("alembic.ini").exists():
        shutil.copy("alembic.ini", release_dir / "alembic.ini")
        print("  [OK] Copied: alembic.ini")

    # Create .env.example
    env_example = """# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=deltica_user
DB_PASSWORD=your_secure_password_here
DB_NAME=deltica_db
"""
    (release_dir / ".env.example").write_text(env_example, encoding="utf-8")
    print("  [OK] Created .env.example")

    # Create production .env with real credentials
    env_production = """# Database Configuration - Production
DB_HOST=10.190.168.78
DB_PORT=5432
DB_USER=deltica_user
DB_PASSWORD=deltica123
DB_NAME=deltica_db
"""
    (release_dir / ".env").write_text(env_production, encoding="utf-8")
    print("  [OK] Created .env (production-ready)")

    # Create start.bat
    start_bat = """@echo off
chcp 65001 >nul
echo ========================================
echo   Deltica Server - Zapusk
echo ========================================
echo.

if not exist .env (
    echo [ERROR] File .env not found!
    echo Copy .env.example to .env and edit
    pause
    exit /b 1
)

echo Starting Deltica Server...
echo API: http://localhost:8000
echo Swagger UI: http://localhost:8000/docs
echo.
deltica-server.exe

pause
"""
    (release_dir / "start.bat").write_text(start_bat, encoding="utf-8")
    print("  [OK] Created start.bat")

    print()
    print("=" * 60)
    print("  SERVER BUILD COMPLETED!")
    print("=" * 60)
    print()
    print(f"Release location: {release_dir}")
    print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
