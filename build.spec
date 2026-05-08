# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# Add src/ to analysis path so local modules can be found
src_dir = os.path.join(os.path.dirname(__file__), 'src')

block_cipher = None

a = Analysis(
    ['src/gui/main_gui.py'],
    pathex=[src_dir],
    binaries=[],
    datas=[],
    hiddenimports=[
        'metadata_utils',
        'qqmusic_api_client',
        'frida',
        'mutagen',
        'mutagen.flac',
        'mutagen.oggvorbis',
        'mutagen.id3',
        'mutagen.mp3',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter.test',
        'unittest',
        'email',
        'http.server',
        'pydoc',
    ],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='QQMusicDecryptor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=['_frida.pyd'],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=['_frida.pyd'],
    name='QQMusicDecryptor',
)
