from GUI.log import log
import time
from PySide2.QtCore import *
from PySide2.QtGui import *

class APIBackgroundWorkerSignals(QObject):
    dataUpdate = Signal(object)
    dataReceived = Signal(object, object, object, object, object)

"""
Here is the trick:
- *args is just a list of data, when passed with *args it gets unfolded and can be passed as argument to a function
- **kwargs was similar but it's a dict with tuples (var_name, var_val)

when a function has *args and **kwargs as paramters they can be used just as normal lists or dictionaries
by removing the *

so args[0] will give the first positional argument and kwargs["var_name"] will give the value of the argument

They can be passed along to other functions like:
def fun2(*args, **kwargs):
    print(args)
    print(kwargs)
def fun1(*args, **kwargs):
    args.append(1)
    kwargs["new_var] = 1
    fun2(*args, **kwargs)
    

"""
class APIBackgroundWorker(QRunnable):
    def __init__(self, api_fun, args, kwargs, callback=None, tag="APIBackgroundWorker"):
        super(APIBackgroundWorker, self).__init__()
        self.api_fun = api_fun
        # self.kwargs = kwargs
        self.callback = callback
        self.time_started = time.time()
        self.signals = APIBackgroundWorkerSignals()
        self.tag = tag
        self.args = args
        kwargs["log_to_widget"] = False
        kwargs["thread_update_signal"] = self.signals.dataUpdate
        self.kwargs = kwargs

    @Slot()
    def run(self): # A slot takes no params
        # This thing of python args is freaking awesome!
        # print(self.args)
        # print(self.kwargs)
        data = self.api_fun(*(self.args),**(self.kwargs))
        self.signals.dataReceived.emit(data, self.callback, "APIBackgroundWorker", self.time_started, self.tag)

class DataDownloaderSignals(QObject):
    dataDownloaded = Signal(object, object, object, object, object)
    dataDownloaderUpdate = Signal(object)
    finished = Signal()

class DataDownloader(QRunnable):
    def __init__(self, download_fun, new_data, folder_path, rename_images, amount, force_overwrite=False, callback=None, tag="DataDownloader"):
        super(DataDownloader, self).__init__()
        self.download_fun = download_fun
        self.new_data = new_data
        self.folder_path = folder_path
        self.rename_images = rename_images
        self.amount = amount
        self.callback = callback
        self.force_overwrite = force_overwrite
        self.signals = DataDownloaderSignals()
        self.time_started = time.time()
        self.tag = tag

    @Slot()
    def run(self): # A slot takes no params
        # print("AMOUNT " +str(self.amount))
        downloaded_data = self.download_fun(self.new_data, self.folder_path,
                                            self.rename_images, self.amount, force_overwrite=self.force_overwrite,
                                            thread_update_signal=self.signals.dataDownloaderUpdate, log_to_widget=False)
        self.signals.dataDownloaded.emit(downloaded_data, self.callback, "DataDownloader", self.time_started, self.tag)
        self.signals.finished.emit()


class ImgLoaderSignals(QObject):
    imgLoaded = Signal(QImage, int)
    imgLoadedMessage = Signal(str, object)
    finished = Signal(str)

class ImgLoader(QRunnable):
    def __init__(self, photo_path_list=[], tag="ImgLoader"):
        super(ImgLoader, self).__init__()
        self.photos_path_list = photo_path_list
        if not isinstance(photo_path_list, list):
            self.photos_path_list = [photo_path_list]
        self.signals = ImgLoaderSignals()
        self.tag = tag

    @Slot()
    def run(self): # A slot takes no params
        for i in range(len(self.photos_path_list)):
            image = QImage(self.photos_path_list[i]) #QPixmap cannot be created outside of the main thread so I'll load a QImage which can return a pixmap
            self.signals.imgLoaded.emit(image, i)
            # self.signals.imgLoadedMessage.emit("Loaded image: " +str(i) +"/"+str(len(self.photos_path_list)))
        self.signals.finished.emit(self.tag)