# -*- mode: python ; coding: utf-8 -*-
# ClipForge PyInstaller Spec File

import os
from pathlib import Path

# Find icon file (checks root first, then assets folder)
icon_path = None
if os.path.exists('icon.ico'):
    icon_path = 'icon.ico'
elif os.path.exists('assets/clipforge.ico'):
    icon_path = 'assets/clipforge.ico'

# Collect assets if directory exists
datas = []
if os.path.exists('assets'):
    datas.append(('assets', 'assets'))

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['sqlalchemy', 'pytest', 'unittest', 'test'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ClipForge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path if icon_path else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ClipForge',
)

# Output structure: dist/ClipForge/ClipForge.exe and files
