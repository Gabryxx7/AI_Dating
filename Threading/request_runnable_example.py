from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class RequestRunnable(QRunnable):
    def __init__(self, url, json, dialog):
        QRunnable.__init__(self)
        self.mUrl = url
        self.mJson = json
        self.w = dialog

    def run(self):
        r = requests.post(self.mUrl, json=self.mJson)
        QMetaObject.invokeMethod(self.w, "setData",
                                 Qt.QueuedConnection,
                                 Q_ARG(str, r.text))


class Dialog(QDialog):
    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        self.setLayout(QVBoxLayout())
        btn = QPushButton("Submit", self)
        btn.clicked.connect(self.submit)
        self.spinner = QtWaitingSpinner(self)

        self.layout().addWidget(btn)
        self.layout().addWidget(self.spinner)

    def submit(self):
        self.spinner.start()
        runnable = RequestRunnable("https://api.github.com/some/endpoint",
                                   {'some': 'data'},
                                   self)
        QThreadPool.globalInstance().start(runnable)

    @Slot(str)
    def setData(self, data):
        print(data)
        self.spinner.stop()
        self.adjustSize()