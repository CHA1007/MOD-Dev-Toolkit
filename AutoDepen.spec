# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all

datas = [('requirements.txt', '.')]
binaries = []
hiddenimports = ['customtkinter', 'customtkinter.windows', 'customtkinter.windows.widgets', 'customtkinter.windows.widgets.core_widget_classes', 'customtkinter.windows.ctk_toplevel', 'customtkinter.windows.ctk_tk', 'customtkinter.windows.widgets.ctk_button', 'customtkinter.windows.widgets.ctk_entry', 'customtkinter.windows.widgets.ctk_label', 'customtkinter.windows.widgets.ctk_textbox', 'customtkinter.windows.widgets.ctk_frame', 'customtkinter.windows.widgets.ctk_scrollbar', 'PIL', 'PIL._tkinter_finder', 'PIL.Image', 'PIL.ImageTk', 'requests', 'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox']
hiddenimports += collect_submodules('customtkinter')
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('PIL')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='AutoDepen',
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
    icon='NONE',
)
