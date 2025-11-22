# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Deltica Server Build Script - ÐšÐ¾Ð¼Ð¼ÐµÑ€Ñ‡ÐµÑÐºÐ¸Ð¹ Ñ€ÐµÐ»Ð¸Ð·
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host "  Deltica Server Build Script v1.1" -ForegroundColor Cyan
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

# ÐŸÑ€Ð¾Ð²ÐµÑ€ÐºÐ°, Ñ‡Ñ‚Ð¾ ÑÐºÑ€Ð¸Ð¿Ñ‚ Ð·Ð°Ð¿ÑƒÑ‰ÐµÐ½ Ð¸Ð· ÐºÐ¾Ñ€Ð½Ñ Ð¿Ñ€Ð¾ÐµÐºÑ‚Ð°
if (-not (Test-Path ".\backend")) {
    Write-Host "ÐžÐ¨Ð˜Ð‘ÐšÐ: Ð—Ð°Ð¿ÑƒÑÑ‚Ð¸Ñ‚Ðµ ÑÐºÑ€Ð¸Ð¿Ñ‚ Ð¸Ð· ÐºÐ¾Ñ€Ð½Ñ Ð¿Ñ€Ð¾ÐµÐºÑ‚Ð°" -ForegroundColor Red
    Write-Host "Ð¢ÐµÐºÑƒÑ‰Ð°Ñ Ð´Ð¸Ñ€ÐµÐºÑ‚Ð¾Ñ€Ð¸Ñ: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "ÐžÐ¶Ð¸Ð´Ð°ÐµÑ‚ÑÑ: C:\Projects\deltica\" -ForegroundColor Yellow
    exit 1
}

# ÐŸÐ¾Ð»ÑƒÑ‡ÐµÐ½Ð¸Ðµ Ð²ÐµÑ€ÑÐ¸Ð¸ Ð¸Ð· pyproject.toml
$version = "1.0.1"
if (Test-Path "pyproject.toml") {
    $content = Get-Content "pyproject.toml" -Raw
    if ($content -match 'version\s*=\s*"([^"]+)"') {
        $version = $matches[1]
    }
}

Write-Host "Ð’ÐµÑ€ÑÐ¸Ñ Ñ€ÐµÐ»Ð¸Ð·Ð°: $version" -ForegroundColor Green
Write-Host ""

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ð¨Ð°Ð³ 1: Ð¡Ð¾Ð·Ð´Ð°Ð½Ð¸Ðµ Ð´Ð°Ð¼Ð¿Ð° Ð±Ð°Ð·Ñ‹ Ð´Ð°Ð½Ð½Ñ‹Ñ…
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Write-Host "[1/8] Ð¡Ð¾Ð·Ð´Ð°Ð½Ð¸Ðµ Ð´Ð°Ð¼Ð¿Ð° Ñ‚ÐµÐºÑƒÑ‰ÐµÐ¹ Ð±Ð°Ð·Ñ‹ Ð´Ð°Ð½Ð½Ñ‹Ñ…..." -ForegroundColor Yellow

try {
    if (-not (Test-Path ".\.env")) {
        Write-Host "  âš  .env Ñ„Ð°Ð¹Ð» Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½, Ð¿Ñ€Ð¾Ð¿ÑƒÑÐº ÑÐ¾Ð·Ð´Ð°Ð½Ð¸Ñ Ð´Ð°Ð¼Ð¿Ð°" -ForegroundColor Yellow
    } else {
        $envContent = Get-Content ".\.env" -Raw
        $dbHost = if ($envContent -match 'DB_HOST=(.+)') { $matches[1].Trim() } else { "localhost" }
        $dbPort = if ($envContent -match 'DB_PORT=(.+)') { $matches[1].Trim() } else { "5432" }
        $dbUser = if ($envContent -match 'DB_USER=(.+)') { $matches[1].Trim() } else { "postgres" }
        $dbPassword = if ($envContent -match 'DB_PASSWORD=(.+)') { $matches[1].Trim() } else { "" }
        $dbName = if ($envContent -match 'DB_NAME=(.+)') { $matches[1].Trim() } else { "deltica_db" }

        if (-not (Test-Path ".\backend\database_dumps")) {
            New-Item -ItemType Directory -Path ".\backend\database_dumps" -Force | Out-Null
        }

        $pgDumpPath = "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"
        if (-not (Test-Path $pgDumpPath)) {
            $pgVersions = Get-ChildItem "C:\Program Files\PostgreSQL" -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending
            if ($pgVersions) {
                $pgDumpPath = Join-Path $pgVersions[0].FullName "bin\pg_dump.exe"
            }
        }

        if (Test-Path $pgDumpPath) {
            $env:PGPASSWORD = $dbPassword
            $dumpPath = ".\backend\database_dumps\deltica_initial.dump"
            & $pgDumpPath -h $dbHost -p $dbPort -U $dbUser -d $dbName -F c -b -f $dumpPath 2>&1 | Out-Null

            if (Test-Path $dumpPath) {
                $dumpSize = (Get-Item $dumpPath).Length / 1KB
                Write-Host ("  âœ“ Ð”Ð°Ð¼Ð¿ Ð‘Ð” ÑÐ¾Ð·Ð´Ð°Ð½: deltica_initial.dump ({0:N2} KB)" -f $dumpSize) -ForegroundColor Green
            } else {
                Write-Host "  âš  ÐÐµ ÑƒÐ´Ð°Ð»Ð¾ÑÑŒ ÑÐ¾Ð·Ð´Ð°Ñ‚ÑŒ Ð´Ð°Ð¼Ð¿ Ð‘Ð”" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  âš  pg_dump Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½, Ð¿Ñ€Ð¾Ð¿ÑƒÑÐº ÑÐ¾Ð·Ð´Ð°Ð½Ð¸Ñ Ð´Ð°Ð¼Ð¿Ð°" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  âš  ÐžÑˆÐ¸Ð±ÐºÐ° ÑÐ¾Ð·Ð´Ð°Ð½Ð¸Ñ Ð´Ð°Ð¼Ð¿Ð°: $_" -ForegroundColor Yellow
    Write-Host "  ÐŸÑ€Ð¾Ð´Ð¾Ð»Ð¶Ð°ÐµÐ¼ ÑÐ±Ð¾Ñ€ÐºÑƒ Ð±ÐµÐ· Ð´Ð°Ð¼Ð¿Ð° Ð‘Ð”" -ForegroundColor Yellow
}

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ð¨Ð°Ð³ 2: Ð£ÑÑ‚Ð°Ð½Ð¾Ð²ÐºÐ° PyInstaller
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Write-Host "[2/8] Ð£ÑÑ‚Ð°Ð½Ð¾Ð²ÐºÐ° PyInstaller..." -ForegroundColor Yellow
try {
    uv pip install pyinstaller
    Write-Host "  âœ“ PyInstaller ÑƒÑÑ‚Ð°Ð½Ð¾Ð²Ð»ÐµÐ½" -ForegroundColor Green
} catch {
    Write-Host "  âœ— ÐžÑˆÐ¸Ð±ÐºÐ° ÑƒÑÑ‚Ð°Ð½Ð¾Ð²ÐºÐ¸ PyInstaller: $_" -ForegroundColor Red
    exit 1
}

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ð¨Ð°Ð³ 3: ÐžÑ‡Ð¸ÑÑ‚ÐºÐ° ÑÑ‚Ð°Ñ€Ñ‹Ñ… ÑÐ±Ð¾Ñ€Ð¾Ðº
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Write-Host "[3/8] ÐžÑ‡Ð¸ÑÑ‚ÐºÐ° ÑÑ‚Ð°Ñ€Ñ‹Ñ… ÑÐ±Ð¾Ñ€Ð¾Ðº..." -ForegroundColor Yellow
if (Test-Path ".\dist\server") { Remove-Item -Recurse -Force ".\dist\server" }
if (Test-Path ".\build\server") { Remove-Item -Recurse -Force ".\build\server" }
if (Test-Path ".\deltica-server.spec") { Remove-Item -Force ".\deltica-server.spec" }
Write-Host "  âœ“ Ð¡Ñ‚Ð°Ñ€Ñ‹Ðµ ÑÐ±Ð¾Ñ€ÐºÐ¸ ÑƒÐ´Ð°Ð»ÐµÐ½Ñ‹" -ForegroundColor Green

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ð¨Ð°Ð³ 4: Ð¡Ð¾Ð·Ð´Ð°Ð½Ð¸Ðµ PyInstaller spec Ñ„Ð°Ð¹Ð»Ð°
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Write-Host "[4/8] Ð¡Ð¾Ð·Ð´Ð°Ð½Ð¸Ðµ PyInstaller spec Ñ„Ð°Ð¹Ð»Ð°..." -ForegroundColor Yellow

$specContent = @'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['backend/core/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('backend/app', 'app'),
        ('backend/core', 'core'),
        ('backend/routes', 'routes'),
        ('backend/services', 'services'),
        ('backend/middleware', 'middleware'),
        ('backend/utils', 'utils'),
        ('backend/scripts', 'scripts'),
    ],
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
'@

$specContent | Out-File -FilePath "deltica-server.spec" -Encoding UTF8
Write-Host "  âœ“ Spec Ñ„Ð°Ð¹Ð» ÑÐ¾Ð·Ð´Ð°Ð½: deltica-server.spec" -ForegroundColor Green

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ð¨Ð°Ð³ 5: ÐšÐ¾Ð¼Ð¿Ð¸Ð»ÑÑ†Ð¸Ñ backend Ð² .exe
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Write-Host "[5/8] ÐšÐ¾Ð¼Ð¿Ð¸Ð»ÑÑ†Ð¸Ñ backend Ð² .exe (2-5 Ð¼Ð¸Ð½ÑƒÑ‚)..." -ForegroundColor Yellow
Write-Host "  Ð­Ñ‚Ð¾ Ð¼Ð¾Ð¶ÐµÑ‚ Ð·Ð°Ð½ÑÑ‚ÑŒ Ð½ÐµÑÐºÐ¾Ð»ÑŒÐºÐ¾ Ð¼Ð¸Ð½ÑƒÑ‚, Ð¿Ð¾Ð´Ð¾Ð¶Ð´Ð¸Ñ‚Ðµ..." -ForegroundColor Gray

try {
    uv run pyinstaller deltica-server.spec --clean --distpath .\dist\server --workpath .\build\server

    if (-not (Test-Path ".\dist\server\deltica-server.exe")) {
        throw "Ð¤Ð°Ð¹Ð» deltica-server.exe Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½ Ð¿Ð¾ÑÐ»Ðµ ÑÐ±Ð¾Ñ€ÐºÐ¸"
    }

    $exeSize = (Get-Item ".\dist\server\deltica-server.exe").Length / 1MB
    Write-Host ("  âœ“ Backend ÑÐºÐ¾Ð¼Ð¿Ð¸Ð»Ð¸Ñ€Ð¾Ð²Ð°Ð½: deltica-server.exe ({0:N2} MB)" -f $exeSize) -ForegroundColor Green
} catch {
    Write-Host "  âœ— ÐžÑˆÐ¸Ð±ÐºÐ° ÐºÐ¾Ð¼Ð¿Ð¸Ð»ÑÑ†Ð¸Ð¸: $_" -ForegroundColor Red
    exit 1
}

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ð¨Ð°Ð³ 6: Ð¡Ð¾Ð·Ð´Ð°Ð½Ð¸Ðµ ÑÑ‚Ñ€ÑƒÐºÑ‚ÑƒÑ€Ñ‹ Ñ€ÐµÐ»Ð¸Ð·Ð°
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Write-Host "[6/8] Ð¡Ð¾Ð·Ð´Ð°Ð½Ð¸Ðµ ÑÑ‚Ñ€ÑƒÐºÑ‚ÑƒÑ€Ñ‹ Ñ€ÐµÐ»Ð¸Ð·Ð°..." -ForegroundColor Yellow

$releaseDir = ".\dist\Deltica-Server-v$version"
if (Test-Path $releaseDir) { Remove-Item -Recurse -Force $releaseDir }
New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null

Copy-Item ".\dist\server\deltica-server.exe" "$releaseDir\deltica-server.exe"
Write-Host "  âœ“ Ð¡ÐºÐ¾Ð¿Ð¸Ñ€Ð¾Ð²Ð°Ð½ deltica-server.exe" -ForegroundColor Green

New-Item -ItemType Directory -Path "$releaseDir\uploads" -Force | Out-Null
New-Item -ItemType Directory -Path "$releaseDir\logs" -Force | Out-Null
New-Item -ItemType Directory -Path "$releaseDir\backups" -Force | Out-Null
Write-Host "  âœ" Ð¡Ð¾Ð·Ð´Ð°Ð½Ñ‹ Ð¿Ð°Ð¿ÐºÐ¸: uploads, logs, backups" -ForegroundColor Green

# Ð¡ÐºÐ¾Ð¿Ð¸Ñ€Ð¾Ð²Ð°Ñ‚ÑŒ database_dumps Ð¿Ð°Ð¿ÐºÑƒ Ñ Ð´Ð°Ð¼Ð¿Ð¾Ð¼
if (Test-Path ".\backend\database_dumps\deltica_initial.dump") {
    New-Item -ItemType Directory -Path "$releaseDir\database_dumps" -Force | Out-Null
    Copy-Item ".\backend\database_dumps\deltica_initial.dump" "$releaseDir\database_dumps\deltica_initial.dump"
    $dumpSize = (Get-Item "$releaseDir\database_dumps\deltica_initial.dump").Length / 1KB
    Write-Host ("  âœ" Ð¡ÐºÐ¾Ð¿Ð¸Ñ€Ð¾Ð²Ð°Ð½ Ð´Ð°Ð¼Ð¿ Ð'Ð": deltica_initial.dump ({0:N2} KB)" -f $dumpSize) -ForegroundColor Green
} else {
    Write-Host "  âš  Ð'ÐÐ˜ÐœÐÐÐ˜Ð•: Ð"Ð°Ð¼Ð¿ Ð'Ð" Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½! Ð˜Ð½Ð¸Ñ†Ð¸Ð°Ð»Ð¸Ð·Ð°Ñ†Ð¸Ñ Ð'Ð" Ð½Ðµ Ñ€Ð°Ð±Ð¾Ñ‚Ð°ÐµÑ‚!" -ForegroundColor Yellow
}

# Ð¡ÐºÐ¾Ð¿Ð¸Ñ€Ð¾Ð²Ð°Ñ‚ÑŒ config Ð¿Ð°Ð¿ÐºÑƒ
if (Test-Path ".\config") {
    Copy-Item ".\config" "$releaseDir\config" -Recurse -Force
    Write-Host "  âœ" Ð¡ÐºÐ¾Ð¿Ð¸Ñ€Ð¾Ð²Ð°Ð½Ð° Ð¿Ð°Ð¿ÐºÐ°: config" -ForegroundColor Green
}

# Ð¡ÐºÐ¾Ð¿Ð¸Ñ€Ð¾Ð²Ð°Ñ‚ÑŒ docs Ð¿Ð°Ð¿ÐºÑƒ
if (Test-Path ".\docs") {
    Copy-Item ".\docs" "$releaseDir\docs" -Recurse -Force
    Write-Host "  âœ" Ð¡ÐºÐ¾Ð¿Ð¸Ñ€Ð¾Ð²Ð°Ð½Ð° Ð¿Ð°Ð¿ÐºÐ°: docs" -ForegroundColor Green
}

# Ð¡ÐºÐ¾Ð¿Ð¸Ñ€Ð¾Ð²Ð°Ñ‚ÑŒ migrations Ð¿Ð°Ð¿ÐºÑƒ
if (Test-Path ".\migrations") {
    Copy-Item ".\migrations" "$releaseDir\migrations" -Recurse -Force
    Write-Host "  âœ" Ð¡ÐºÐ¾Ð¿Ð¸Ñ€Ð¾Ð²Ð°Ð½Ð° Ð¿Ð°Ð¿ÐºÐ°: migrations" -ForegroundColor Green
}

# Ð¡ÐºÐ¾Ð¿Ð¸Ñ€Ð¾Ð²Ð°Ñ‚ÑŒ alembic.ini
if (Test-Path ".\alembic.ini") {
    Copy-Item ".\alembic.ini" "$releaseDir\alembic.ini"
    Write-Host "  âœ" Ð¡ÐºÐ¾Ð¿Ð¸Ñ€Ð¾Ð²Ð°Ð½: alembic.ini" -ForegroundColor Green
}

$envExample = @"
# Ð‘Ð°Ð·Ð° Ð´Ð°Ð½Ð½Ñ‹Ñ… PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=deltica_user
DB_PASSWORD=your_secure_password_here
DB_NAME=deltica_db
"@
$envExample | Out-File -FilePath "$releaseDir\.env.example" -Encoding UTF8
Write-Host "  âœ“ Ð¡Ð¾Ð·Ð´Ð°Ð½ .env.example" -ForegroundColor Green

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ð¨Ð°Ð³ 7: Ð¡Ð¾Ð·Ð´Ð°Ð½Ð¸Ðµ ÑÐºÑ€Ð¸Ð¿Ñ‚Ð¾Ð² Ð·Ð°Ð¿ÑƒÑÐºÐ° Ð¸ Ð¸Ð½Ð¸Ñ†Ð¸Ð°Ð»Ð¸Ð·Ð°Ñ†Ð¸Ð¸ Ð‘Ð”
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Write-Host "[7/8] Ð¡Ð¾Ð·Ð´Ð°Ð½Ð¸Ðµ ÑÐºÑ€Ð¸Ð¿Ñ‚Ð¾Ð² Ð·Ð°Ð¿ÑƒÑÐºÐ° Ð¸ Ð¸Ð½Ð¸Ñ†Ð¸Ð°Ð»Ð¸Ð·Ð°Ñ†Ð¸Ð¸ Ð‘Ð”..." -ForegroundColor Yellow

$startScript = @"
@echo off
chcp 65001 >nul
echo ========================================
echo   Deltica Server - Ð—Ð°Ð¿ÑƒÑÐº
echo ========================================
echo.

if not exist .env (
    echo [ÐžÐ¨Ð˜Ð‘ÐšÐ] Ð¤Ð°Ð¹Ð» .env Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½!
    echo Ð¡ÐºÐ¾Ð¿Ð¸Ñ€ÑƒÐ¹Ñ‚Ðµ .env.example Ð² .env Ð¸ Ð¾Ñ‚Ñ€ÐµÐ´Ð°ÐºÑ‚Ð¸Ñ€ÑƒÐ¹Ñ‚Ðµ
    pause
    exit /b 1
)

echo Ð—Ð°Ð¿ÑƒÑÐº Deltica Server...
echo API: http://localhost:8000
echo Swagger UI: http://localhost:8000/docs
echo.
deltica-server.exe

pause
"@
$startScript | Out-File -FilePath "$releaseDir\start.bat" -Encoding ASCII
Write-Host "  âœ“ Ð¡Ð¾Ð·Ð´Ð°Ð½ start.bat" -ForegroundColor Green

$initDbScript = @"
@echo off
chcp 65001 >nul
echo ========================================
echo   Ð˜Ð½Ð¸Ñ†Ð¸Ð°Ð»Ð¸Ð·Ð°Ñ†Ð¸Ñ Ð±Ð°Ð·Ñ‹ Ð´Ð°Ð½Ð½Ñ‹Ñ… Deltica
echo ========================================
echo.

if not exist .env (
    echo [ÐžÐ¨Ð˜Ð‘ÐšÐ] Ð¤Ð°Ð¹Ð» .env Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½!
    pause
    exit /b 1
)

for /f "tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="DB_HOST" set DB_HOST=%%b
    if "%%a"=="DB_PORT" set DB_PORT=%%b
    if "%%a"=="DB_USER" set DB_USER=%%b
    if "%%a"=="DB_PASSWORD" set DB_PASSWORD=%%b
    if "%%a"=="DB_NAME" set DB_NAME=%%b
)

echo [1/4] ÐŸÑ€Ð¾Ð²ÐµÑ€ÐºÐ° PostgreSQL...
set PGPASSWORD=%DB_PASSWORD%
pg_isready -h %DB_HOST% -p %DB_PORT% >nul 2>&1
if errorlevel 1 (
    echo [ÐžÐ¨Ð˜Ð‘ÐšÐ] PostgreSQL Ð½Ðµ Ð´Ð¾ÑÑ‚ÑƒÐ¿ÐµÐ½!
    pause
    exit /b 1
)
echo   OK PostgreSQL Ð´Ð¾ÑÑ‚ÑƒÐ¿ÐµÐ½

echo.
echo [2/4] ÐŸÑ€Ð¾Ð²ÐµÑ€ÐºÐ° Ð±Ð°Ð·Ñ‹ Ð´Ð°Ð½Ð½Ñ‹Ñ…...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -lqt 2>nul | find "%DB_NAME%" >nul 2>&1
if errorlevel 1 (
    echo   Ð‘Ð°Ð·Ð° Ð´Ð°Ð½Ð½Ñ‹Ñ… Ð½Ðµ ÑÑƒÑ‰ÐµÑÑ‚Ð²ÑƒÐµÑ‚, ÑÐ¾Ð·Ð´Ð°Ð½Ð¸Ðµ...
    createdb -h %DB_HOST% -p %DB_PORT% -U %DB_USER% %DB_NAME%
    echo   OK Ð‘Ð°Ð·Ð° Ð´Ð°Ð½Ð½Ñ‹Ñ… ÑÐ¾Ð·Ð´Ð°Ð½Ð°
) else (
    echo   OK Ð‘Ð°Ð·Ð° Ð´Ð°Ð½Ð½Ñ‹Ñ… ÑÑƒÑ‰ÐµÑÑ‚Ð²ÑƒÐµÑ‚
)

echo.
echo [3/4] ÐŸÑ€Ð¾Ð²ÐµÑ€ÐºÐ° Ñ‚Ð°Ð±Ð»Ð¸Ñ†...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -c "\dt" 2>nul | find "users" >nul 2>&1
if errorlevel 1 (
    echo   Ð¢Ð°Ð±Ð»Ð¸Ñ†Ñ‹ Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½Ñ‹, Ð²Ð¾ÑÑÑ‚Ð°Ð½Ð¾Ð²Ð»ÐµÐ½Ð¸Ðµ Ð¸Ð· Ð´Ð°Ð¼Ð¿Ð°...

    set PG_RESTORE=pg_restore
    if exist "C:\Program Files\PostgreSQL\17\bin\pg_restore.exe" set PG_RESTORE="C:\Program Files\PostgreSQL\17\bin\pg_restore.exe"
    if exist "C:\Program Files\PostgreSQL\16\bin\pg_restore.exe" set PG_RESTORE="C:\Program Files\PostgreSQL\16\bin\pg_restore.exe"

    %PG_RESTORE% -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% --clean --if-exists --no-owner database_dumps\deltica_initial.dump

    if errorlevel 1 (
        echo [ÐžÐ¨Ð˜Ð‘ÐšÐ] ÐÐµ ÑƒÐ´Ð°Ð»Ð¾ÑÑŒ Ð²Ð¾ÑÑÑ‚Ð°Ð½Ð¾Ð²Ð¸Ñ‚ÑŒ Ð‘Ð” Ð¸Ð· Ð´Ð°Ð¼Ð¿Ð°!
        pause
        exit /b 1
    )
    echo   OK Ð‘Ð°Ð·Ð° Ð´Ð°Ð½Ð½Ñ‹Ñ… Ð²Ð¾ÑÑÑ‚Ð°Ð½Ð¾Ð²Ð»ÐµÐ½Ð°
) else (
    echo   OK Ð¢Ð°Ð±Ð»Ð¸Ñ†Ñ‹ ÑƒÐ¶Ðµ ÑÑƒÑ‰ÐµÑÑ‚Ð²ÑƒÑŽÑ‚
)

echo.
echo [4/4] ÐŸÑ€Ð¾Ð²ÐµÑ€ÐºÐ° Ð´Ð°Ð½Ð½Ñ‹Ñ…...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -c "SELECT COUNT(*) FROM users" 2>nul | find "0" >nul 2>&1
if not errorlevel 1 (
    echo   Ð’ÐÐ˜ÐœÐÐÐ˜Ð•: Ð‘Ð°Ð·Ð° Ð´Ð°Ð½Ð½Ñ‹Ñ… Ð¿ÑƒÑÑ‚Ð°
)

echo.
echo ========================================
echo   Ð˜Ð½Ð¸Ñ†Ð¸Ð°Ð»Ð¸Ð·Ð°Ñ†Ð¸Ñ Ð·Ð°Ð²ÐµÑ€ÑˆÐµÐ½Ð° ÑƒÑÐ¿ÐµÑˆÐ½Ð¾!
echo ========================================
echo.
pause
"@
$initDbScript | Out-File -FilePath "$releaseDir\init-database.bat" -Encoding ASCII
Write-Host "  âœ“ Ð¡Ð¾Ð·Ð´Ð°Ð½ init-database.bat" -ForegroundColor Green

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ð¨Ð°Ð³ 8: Ð¡Ð¾Ð·Ð´Ð°Ð½Ð¸Ðµ README
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Write-Host "[8/8] Ð¡Ð¾Ð·Ð´Ð°Ð½Ð¸Ðµ Ð´Ð¾ÐºÑƒÐ¼ÐµÐ½Ñ‚Ð°Ñ†Ð¸Ð¸..." -ForegroundColor Yellow

$readme = @"
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
  Deltica Server v$version - Ð˜Ð½ÑÑ‚Ñ€ÑƒÐºÑ†Ð¸Ñ Ð¿Ð¾ ÑƒÑÑ‚Ð°Ð½Ð¾Ð²ÐºÐµ
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

Ð¡Ð˜Ð¡Ð¢Ð•ÐœÐÐ«Ð• Ð¢Ð Ð•Ð‘ÐžÐ’ÐÐÐ˜Ð¯:
- Windows Server 2016+ Ð¸Ð»Ð¸ Windows 10/11
- PostgreSQL 13+ (ÑƒÑÑ‚Ð°Ð½Ð¾Ð²Ð»ÐµÐ½ Ð¸ Ð·Ð°Ð¿ÑƒÑ‰ÐµÐ½)
- 2 GB RAM, 1 GB ÑÐ²Ð¾Ð±Ð¾Ð´Ð½Ð¾Ð³Ð¾ Ð¼ÐµÑÑ‚Ð°

Ð£Ð¡Ð¢ÐÐÐžÐ’ÐšÐ:

Ð¨Ð°Ð³ 1: Ð£ÑÑ‚Ð°Ð½Ð¾Ð²Ð¸Ñ‚Ðµ PostgreSQL
https://www.postgresql.org/download/windows/

Ð¨Ð°Ð³ 2: Ð¡Ð¾Ð·Ð´Ð°Ð¹Ñ‚Ðµ Ð¿Ð¾Ð»ÑŒÐ·Ð¾Ð²Ð°Ñ‚ÐµÐ»Ñ PostgreSQL
Ð’ pgAdmin Ð¸Ð»Ð¸ psql Ð²Ñ‹Ð¿Ð¾Ð»Ð½Ð¸Ñ‚Ðµ:
  CREATE USER deltica_user WITH PASSWORD 'Ð²Ð°Ñˆ_Ð¿Ð°Ñ€Ð¾Ð»ÑŒ' CREATEDB;

Ð¨Ð°Ð³ 3: ÐÐ°ÑÑ‚Ñ€Ð¾Ð¹Ñ‚Ðµ Deltica Server
1. Ð Ð°ÑÐ¿Ð°ÐºÑƒÐ¹Ñ‚Ðµ ÑÑ‚Ñƒ Ð¿Ð°Ð¿ÐºÑƒ Ð² C:\Deltica\
2. Ð¡ÐºÐ¾Ð¿Ð¸Ñ€ÑƒÐ¹Ñ‚Ðµ .env.example Ð² .env
3. ÐžÑ‚Ñ€ÐµÐ´Ð°ÐºÑ‚Ð¸Ñ€ÑƒÐ¹Ñ‚Ðµ .env (ÑƒÐºÐ°Ð¶Ð¸Ñ‚Ðµ Ð¿Ð°Ñ€Ð¾Ð»ÑŒ)

Ð¨Ð°Ð³ 4: Ð˜Ð½Ð¸Ñ†Ð¸Ð°Ð»Ð¸Ð·Ð°Ñ†Ð¸Ñ Ð‘Ð” (ÐžÐ”Ð˜Ð Ð ÐÐ—!)
Ð—Ð°Ð¿ÑƒÑÑ‚Ð¸Ñ‚Ðµ: init-database.bat

Ð¡ÐºÑ€Ð¸Ð¿Ñ‚ Ð°Ð²Ñ‚Ð¾Ð¼Ð°Ñ‚Ð¸Ñ‡ÐµÑÐºÐ¸:
- Ð¡Ð¾Ð·Ð´Ð°ÑÑ‚ Ð±Ð°Ð·Ñƒ Ð´Ð°Ð½Ð½Ñ‹Ñ… deltica_db
- Ð’Ð¾ÑÑÑ‚Ð°Ð½Ð¾Ð²Ð¸Ñ‚ ÑÑ‚Ñ€ÑƒÐºÑ‚ÑƒÑ€Ñƒ Ñ‚Ð°Ð±Ð»Ð¸Ñ†
- Ð˜Ð¼Ð¿Ð¾Ñ€Ñ‚Ð¸Ñ€ÑƒÐµÑ‚ Ð²ÑÐµ Ð´Ð°Ð½Ð½Ñ‹Ðµ

Ð¨Ð°Ð³ 5: Ð—Ð°Ð¿ÑƒÑÐº ÑÐµÑ€Ð²ÐµÑ€Ð°
Ð—Ð°Ð¿ÑƒÑÑ‚Ð¸Ñ‚Ðµ: start.bat

ÐŸÑ€Ð¾Ð²ÐµÑ€ÑŒÑ‚Ðµ: http://localhost:8000/docs

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

Ð¡Ð¢Ð Ð£ÐšÐ¢Ð£Ð Ð:
C:\Deltica\
â”œâ”€â”€ deltica-server.exe       - ÐžÑÐ½Ð¾Ð²Ð½Ð¾Ðµ Ð¿Ñ€Ð¸Ð»Ð¾Ð¶ÐµÐ½Ð¸Ðµ
â”œâ”€â”€ .env                      - ÐšÐ¾Ð½Ñ„Ð¸Ð³ÑƒÑ€Ð°Ñ†Ð¸Ñ
â”œâ”€â”€ init-database.bat         - Ð˜Ð½Ð¸Ñ†Ð¸Ð°Ð»Ð¸Ð·Ð°Ñ†Ð¸Ñ Ð‘Ð” (Ð¾Ð´Ð¸Ð½ Ñ€Ð°Ð·)
â”œâ”€â”€ start.bat                 - Ð—Ð°Ð¿ÑƒÑÐº ÑÐµÑ€Ð²ÐµÑ€Ð°
â”œâ”€â”€ database_dumps\           - Ð”Ð°Ð¼Ð¿ Ð‘Ð”
â”œâ”€â”€ uploads\                  - Ð—Ð°Ð³Ñ€ÑƒÐ¶ÐµÐ½Ð½Ñ‹Ðµ Ñ„Ð°Ð¹Ð»Ñ‹
â”œâ”€â”€ logs\                     - Ð›Ð¾Ð³Ð¸
â””â”€â”€ backups\                  - Ð ÐµÐ·ÐµÑ€Ð²Ð½Ñ‹Ðµ ÐºÐ¾Ð¿Ð¸Ð¸

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

Ð’ÐµÑ€ÑÐ¸Ñ: $version
Ð”Ð°Ñ‚Ð°: $(Get-Date -Format "yyyy-MM-dd")
"@
$readme | Out-File -FilePath "$releaseDir\README.txt" -Encoding UTF8
Write-Host "  âœ“ Ð¡Ð¾Ð·Ð´Ð°Ð½ README.txt" -ForegroundColor Green

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ð¡Ð¾Ð·Ð´Ð°Ð½Ð¸Ðµ ZIP Ð°Ñ€Ñ…Ð¸Ð²Ð°
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Write-Host ""
Write-Host "Ð¡Ð¾Ð·Ð´Ð°Ð½Ð¸Ðµ ZIP Ð°Ñ€Ñ…Ð¸Ð²Ð°..." -ForegroundColor Yellow

$zipPath = ".\dist\Deltica-Server-v$version.zip"
if (Test-Path $zipPath) { Remove-Item -Force $zipPath }

try {
    Compress-Archive -Path "$releaseDir\*" -DestinationPath $zipPath -CompressionLevel Optimal -Force
    $zipSize = (Get-Item $zipPath).Length / 1MB
    Write-Host ("  âœ“ ZIP ÑÐ¾Ð·Ð´Ð°Ð½: Deltica-Server-v{0}.zip ({1:N2} MB)" -f $version, $zipSize) -ForegroundColor Green
} catch {
    Write-Host "  âœ— ÐžÑˆÐ¸Ð±ÐºÐ° ÑÐ¾Ð·Ð´Ð°Ð½Ð¸Ñ ZIP: $_" -ForegroundColor Red
    exit 1
}

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ð˜Ñ‚Ð¾Ð³Ð¾Ð²Ð°Ñ Ð¸Ð½Ñ„Ð¾Ñ€Ð¼Ð°Ñ†Ð¸Ñ
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Write-Host ""
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Green
Write-Host "  âœ… Ð¡Ð‘ÐžÐ ÐšÐ Ð¡Ð•Ð Ð’Ð•Ð Ð Ð—ÐÐ’Ð•Ð Ð¨Ð•ÐÐ Ð£Ð¡ÐŸÐ•Ð¨ÐÐž!" -ForegroundColor Green
Write-Host "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Green
Write-Host ""
Write-Host "Ð ÐµÐ·ÑƒÐ»ÑŒÑ‚Ð°Ñ‚Ñ‹ ÑÐ±Ð¾Ñ€ÐºÐ¸:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ðŸ“¦ ZIP Ñ€ÐµÐ»Ð¸Ð·:     .\dist\Deltica-Server-v$version.zip" -ForegroundColor White
Write-Host "  ðŸ“ ÐŸÐ°Ð¿ÐºÐ° Ñ€ÐµÐ»Ð¸Ð·Ð°:  .\dist\Deltica-Server-v$version\" -ForegroundColor White
Write-Host ("  ðŸ’¾ Ð Ð°Ð·Ð¼ÐµÑ€ .exe:   {0:N2} MB" -f $exeSize) -ForegroundColor White
Write-Host ("  ðŸ’¾ Ð Ð°Ð·Ð¼ÐµÑ€ ZIP:    {0:N2} MB" -f $zipSize) -ForegroundColor White
Write-Host ""
Write-Host "Ð¡Ð¾Ð´ÐµÑ€Ð¶Ð¸Ð¼Ð¾Ðµ Ñ€ÐµÐ»Ð¸Ð·Ð°:" -ForegroundColor Cyan
Write-Host "  âœ“ deltica-server.exe       - Ð¡ÐºÐ¾Ð¼Ð¿Ð¸Ð»Ð¸Ñ€Ð¾Ð²Ð°Ð½Ð½Ñ‹Ð¹ backend" -ForegroundColor Gray
Write-Host "  âœ“ .env.example             - Ð¨Ð°Ð±Ð»Ð¾Ð½ ÐºÐ¾Ð½Ñ„Ð¸Ð³ÑƒÑ€Ð°Ñ†Ð¸Ð¸" -ForegroundColor Gray
Write-Host "  âœ“ init-database.bat        - Ð˜Ð½Ð¸Ñ†Ð¸Ð°Ð»Ð¸Ð·Ð°Ñ†Ð¸Ñ Ð‘Ð” (Ð¿ÐµÑ€Ð²Ñ‹Ð¹ Ð·Ð°Ð¿ÑƒÑÐº)" -ForegroundColor Gray
Write-Host "  âœ“ start.bat                - Ð¡ÐºÑ€Ð¸Ð¿Ñ‚ Ð·Ð°Ð¿ÑƒÑÐºÐ° ÑÐµÑ€Ð²ÐµÑ€Ð°" -ForegroundColor Gray
Write-Host "  âœ“ database_dumps\          - Ð”Ð°Ð¼Ð¿ Ð‘Ð” Ñ Ñ‚ÐµÐºÑƒÑ‰Ð¸Ð¼Ð¸ Ð´Ð°Ð½Ð½Ñ‹Ð¼Ð¸" -ForegroundColor Gray
Write-Host "  âœ“ README.txt               - Ð˜Ð½ÑÑ‚Ñ€ÑƒÐºÑ†Ð¸Ñ Ð¿Ð¾ ÑƒÑÑ‚Ð°Ð½Ð¾Ð²ÐºÐµ" -ForegroundColor Gray
Write-Host ""
Write-Host "Ð¡Ð»ÐµÐ´ÑƒÑŽÑ‰Ð¸Ðµ ÑˆÐ°Ð³Ð¸:" -ForegroundColor Yellow
Write-Host "  1. ÐŸÑ€Ð¾Ñ‚ÐµÑÑ‚Ð¸Ñ€ÑƒÐ¹Ñ‚Ðµ Ñ€ÐµÐ»Ð¸Ð· Ð½Ð° Ñ‚ÐµÑÑ‚Ð¾Ð²Ð¾Ð¼ ÑÐµÑ€Ð²ÐµÑ€Ðµ" -ForegroundColor White
Write-Host "  2. ÐŸÐµÑ€ÐµÐ´Ð°Ð¹Ñ‚Ðµ ZIP Ñ„Ð°Ð¹Ð» Ð·Ð°ÐºÐ°Ð·Ñ‡Ð¸ÐºÑƒ" -ForegroundColor White
Write-Host ""


