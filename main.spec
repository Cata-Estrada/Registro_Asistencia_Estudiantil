# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

# Raíz del proyecto (ejecuta pyinstaller main.spec desde esta carpeta)
project_root = Path(".").resolve()

# Carpeta de vistas (.ui) y, si aplica, assets/icons
datas = [
    (str(project_root / "views"), "views"),
    # (str(project_root / "assets"), "assets"),  # descomenta si tienes esta carpeta
    # (str(project_root / "icons"), "icons"),    # ejemplo adicional
]

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # agrega módulos de Qt adicionales si los usas:
        # "PyQt5.QtSvg",
        # "PyQt5.QtMultimedia",
        # "PyQt5.QtMultimediaWidgets",
        # "PyQt5.QtWebEngineWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RegistroAsistencia',    # nombre del ejecutable
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,                # GUI: sin consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon=str(project_root / "app.ico"),       # descomenta si tienes icono
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='RegistroAsistencia',
)
