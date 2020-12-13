# -*- mode: python -*-
from kivymd import hooks_path as kivymd_hooks_path

block_cipher = None


a = Analysis(['app/main.py'],
             pathex=['/Users/mohammednadeem/Documents/Muezzin'],
             binaries=[],
             datas=[('/Users/mohammednadeem/Documents/Muezzin/app/res/*', './res/')],
             hiddenimports=[],
             hookspath=[kivymd_hooks_path],
             runtime_hooks=[],
             excludes=['_tkinter', 'Tkinter', 'enchant', 'twisted'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='muezzin',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='muezzin')
app = BUNDLE(coll,
             name='muezzin.app',
             icon='/Users/mohammednadeem/Documents/Muezzin/app/res/mosque_green.png',
             bundle_identifier=None)
