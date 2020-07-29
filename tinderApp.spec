# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

pf_foldr='C:\\Users\\Gabryxx7\\anaconda3\\envs\\Tinder\\Library\\plugins\\platforms\\'

a = Analysis(['C:\\Users\\Gabryxx7\\PycharmProjects\\Tinder\\tinderApp.py'],
             pathex=['C:\\Users\\Gabryxx7\\PycharmProjects\\Tinder\\'],
             binaries=[(pf_foldr+'qwindows.dll', 'platforms\\qwindows.dll'),
             (pf_foldr+'qdirect2d.dll', 'platforms\\qdirect.dll'),
             (pf_foldr+'qoffscreen.dll', 'platforms\\qoffscreen.dll'),
             (pf_foldr+'qwebgl.dll', 'platforms\\qwebgl.dll')
             ],
             datas=[],
             hiddenimports=[    'GUI', 'API', 'Threading', 'ssl', 'pyodbc'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='tinderApp',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True ) # False to avoid the console
