# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

audio_files = [
    (os.path.join('assets', 'audio', f), os.path.join('assets', 'audio'))
    for f in os.listdir(os.path.join('assets', 'audio'))
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=audio_files,
    hiddenimports=[
        'pygame', 'pygame.mixer', 'pygame.font', 'pygame.display',
        'OpenGL', 'OpenGL.GL', 'OpenGL.GLU',
        'OpenGL.arrays', 'OpenGL.arrays.vbo',
        'OpenGL.platform', 'OpenGL.platform.win32',
        'OpenGL.converters', 'ctypes', 'ctypes.util',
    ] + collect_submodules('OpenGL') + collect_submodules('pygame'),
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy'],
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
    name='TheBlueLightMirror',
    debug=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    onefile=True,
)
