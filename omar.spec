# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['omar.py'],
    pathex=[],
    binaries=[],
    datas=[('data/my_icon.ico', '.'), ('Lib/site-packages/selenium_stealth/js', 'selenium_stealth/js')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='채재선정 전율미궁 프리퀄 자동 예매',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['data/my_icon.ico'],
)
