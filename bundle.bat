# Known issue https://github.com/pyinstaller/pyinstaller/issues/3630
# install develop branch: pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip

& 'C:\ProgramData\Anaconda3\envs\Tinder\python.exe' -m PyInstaller --onefile --noconsole --windowed C:\Users\Gabryxx7\PycharmProjects\Tinder\tinderApp.py --hidden-import PySide2.sip --hidden-import GUI --hidden-import GUI.windows --hidden-import API --hidden-import Threading

& 'C:\ProgramData\Anaconda3\envs\Tinder\python.exe' -m PyInstaller -F C:\Users\Gabryxx7\PycharmProjects\Tinder\tinderApp.py --hidden-import PySide2.sip --hidden-import GUI --hidden-import GUI.windows --hidden-import API --hidden-import Threading


& 'C:\ProgramData\Anaconda3\envs\Tinder\python.exe' -m PyInstaller C:\Users\Gabryxx7\PycharmProjects\Tinder\tinderApp.spec


& python -m PyInstaller C:\Users\Gabryxx7\PycharmProjects\Tinder\tinderApp.spec
