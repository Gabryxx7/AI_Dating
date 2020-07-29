I have been looking to start a fun project in python for a while now. 
I haven't used python much except for simple scripts to quickly deal with a large amount of files.

This time I decided to make a slighly more complex project, more specifically I wanted to work with:
- GUI
- Multithreading
- Network
- Data Scarping
- Machine learning and AI
- Bundle up and release a python program

So far I managed to implement a simple GUI using `Qt for Python` started with `PyQt5` and moved to `PySide2` halfway.

The GUI is responsive and everything is done in the background through `QThread`s and `QThreadPool`.

The API is a reworked and extended version of: https://github.com/fbessez/Tinder

So far this tool is nothing but a horrible Desktop version of Tinder.

### [WIP] List of features:
- Download recommendations in the area
    - Get profiles' metadata and pictures
- Download your own matches:
    - Get profiles' metadata, pictures and messages
- Download own profile data

### [WIP] GUI
- Heaps of stuff to do, so far I have the skeleton of a simple list with a circular avatar


### [WIP] Technicalities:
I always like to write down what I have implemented so in the future I can look back at how I had done it:
- The GUI is developed in PySide2
    - Every widget such as lists and feature buttons are new widgets
- I tried to keep the API as close to the original as possible but I ended up changing a few things
    - In praticular I added logs and callbacks to call its functions in the background
    - The bakground worker can call any API method and pass an arbitrary number of parameters (both positional and keyword)
- General unhandled exceptions are handled through `sys.excepthook0`
- When developing with `PyQt` especially with multithreading it's often the case that errors and traceback
are not printed. I decided to use a library called `faulthandler` which handles crashes and prints a traceback
- The app can be bundled to an `.app` or `.exe` executable through `pyInstaller`.
Oh man what a headache to get this working on Windows with its `.dlls` which are NEVER where they are supposed to be and can never be found!

### [WIP] AI Features
- Mmmmh... There's a lot of `if-else` statements if that's the kinda AI you thought you'd find
- Going to implement some NLP to getter a better idea of what the general bios are. The most common sentiment, topic etc...
- Similarly, I'd like to add some face recognition to get features like: ethnicity, hair color, type of pics (selfie, professional) etc...
- In the future it'd be cool to have an AI which can learn fro my likes/dislikes and only swipe on the best matches but this is not the purpose of the project anyway

# Instructions
I only tested this on my macbook and personal laptop so not sure about other systems.

I use Anaconda since it has a `qt` package with the qt plugin needed to bundle the program to an executable. Either way you'll need `PySide2, robobrowser, oyaml, qdarkstyle, faulthandler` or just install the requirements with `pip -r requirements.txt` or `conda install --file requirements.txt` and pray for the best!
That should actually be it, you can just run it with:
```
python tinderapp.py
```
There might be a few fixes to make before it can, first and foremost there is some incompatibility with the library `werkzeug` used by `roborowser/browser.py`
If that happens you can run
```
python fix_werkzeug_robobrowser.py
```
And it should fix it for you, otherwise you can do it manually: Open `[site-packages]\robobrowser\browser.py\` and edit the following line:
```
from werkzeug import 
```
to
```
from werkzeug.utils import 
```

Stay tuned!
