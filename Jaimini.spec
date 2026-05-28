# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

PROJECT_ROOT = Path(SPECPATH)

a = Analysis(
    [str(PROJECT_ROOT / 'jaimini_gui.py')],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[
        (str(PROJECT_ROOT / 'jaimini' / 'data' / 'de421.bsp'), 'jaimini/data'),
    ],
    hiddenimports=[
        'skyfield',
        'skyfield.timelib',
        'numpy',
        'jaimini',
        'jaimini.engine',
        'jaimini.engine.ephemeris',
        'jaimini.engine.time_utils',
        'jaimini.engine.houses',
        'jaimini.core',
        'jaimini.core.karakas',
        'jaimini.core.dashas',
        'jaimini.core.padas',
        'jaimini.core.lagnas',
        'jaimini.core.divisions',
        'jaimini.core.argala',
        'jaimini.chart',
        'jaimini.chart.chart',
        'jaimini.cli',
        'jaimini.cli.main',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='Jaimini',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
