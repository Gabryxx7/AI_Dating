from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import sys
import Queue as queue

class ResultObj(QObject):
    def __init__(self, val):
        self.val = val

class SimpleThread(QThread):
    finished = Signal(object)

    def __init__(self, queue, callback, parent=None):
        QThread.__init__(self, parent)
        self.queue = queue
        self.finished.connect(callback)

    def run(self):
        while True:
            arg = self.queue.get()
            if arg is None: # None means exit
                print("Shutting down")
                return
            self.fun(arg)

    def fun(self, arg):
        for i in range(3):
            print('fun: %s' % i)
            self.sleep(1)
        self.finished.emit(ResultObj(arg+1))