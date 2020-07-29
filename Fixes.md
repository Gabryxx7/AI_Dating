```{py}
# the path is echoed in the error message
cd  %USERPROFILE%\AppData\Local\Continuum\miniconda3\pkgs\
# remove all openssl* files. If you don't have bash in windows `DEL /Q /F /S "openssl*"`
rm -rf openssl*

# install openssl from libarchive on my base env
conda install -c conda-forge libarchive


add .utils to the browser.py import
```
# Bundles
`& python -m PyInstaller C:\Users\Gabryxx7\PycharmProjects\Tinder\tinderApp.spec`

Better not to use Anaconda and virtual environments (`venv`)
On mac you can check which python or pip you are using by typing

`where python`

or

`where pip`

in the windows powershell you can type
`Get-Command python3`

`Get-Command pip`

`Get-Command pip3`

Make sure all the pip and pythons are from the same path so you know you are
installing the packages to the same distribution

Finally make sure PyCharm is using the correct interpreter folder

You can install all the requirements with

`pip install -r requirements.txt`

or

`python -m pip install -r requirements.txt`

You can create a bundle with

`pyinstaller file.py`

or (notice the case!)

`python -m PyInstaller  file.py`


Finally, an important fix for creating the .exe is to properly set up the .dll path. I am not sure where they are supposed to be but sometimes you can find them
in `C:\\Users\\Gabryxx7\\anaconda3\\envs\\<env_name>\\Library\\plugins\\platforms\\` other times apparently they can be in
`C:\\Users\\Gabryxx7\\anaconda3\\Libs\\site-packages\\PyQt5\\plugins\\platforms\\`. After you locate `qwindows.dll` in your python/Anaconda path try the following things:


* copy platform directory to directory of your executable.You'll find the platform directory at a location like `C:\Users\<username>\envs\<environmentname>\Library\plugins\platforms`
So in the end you should have a `platforms `folder with all the dlls in the same folder as your .exe
* Create a new environment variable `QT_QPA_PLATFORM_PLUGIN_PATH="C:\Users\<username>\envs\<environmentname>\Library\plugins\platforms"`
* Finally, the best solution is to actually edit the spec file so that it automatically copies the `.dlls` over with the right path:
The final `spec` file looks something like this:
```
a = Analysis(['C:\\Users\\Gabryxx7\\PycharmProjects\\Tinder\\tinderApp.py'],
             pathex=['C:\\Users\\Gabryxx7\\PycharmProjects\\Tinder\\'],
             binaries=[('C:\\Users\\Gabryxx7\\anaconda3\\envs\\Tinder\\Library\\plugins\\platforms\\qwindows.dll', 'platforms\\qwindows.dll'),
             ('C:\\Users\\Gabryxx7\\anaconda3\\envs\\Tinder\\Library\\plugins\\platforms\\qdirect2d.dll', 'platforms\\qdirect.dll'),
             ('C:\\Users\\Gabryxx7\\anaconda3\\envs\\Tinder\\Library\\plugins\\platforms\\qoffscreen.dll', 'platforms\\qoffscreen.dll'),
             ('C:\\Users\\Gabryxx7\\anaconda3\\envs\\Tinder\\Library\\plugins\\platforms\\qwebgl.dll', 'platforms\\qwebgl.dll')
             ],
             datas=[],
             hiddenimports=['GUI', 'API', 'Threading', 'ssl', 'pyodbc'],
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
          console=True )
```
And the .exe can be easily generated with
`python -m PyInstaller tinderApp.spec` or
`pyinstaller tinderApp.spec`