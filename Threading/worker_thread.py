import math, random, sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import time

class ResultObj(QObject):
    def __init__(self, valStr, valNum):
        self.valStr = valStr
        self.valNum = valNum
        print("ResultObj 4")

class ListUpdateWorker(QThread):
    output = Signal(object)
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False

    @Slot()
    def __del__(self):
        self.exiting = True
        self.wait()

    @Slot(object, object, object)
    def render(self, list_widget, list, name):
        self.list_widget = list_widget
        self.list = list
        self.name = name
        self.start()

    @Slot()
    def run(self):
        # Note: This is never called directly. It is called by Qt once the
        # thread environment has been set up.
        if not self.exiting:
            self.list_widget.update_list(self.list)
            self.output.emit(ResultObj("FINISHED " +self.name, 0))