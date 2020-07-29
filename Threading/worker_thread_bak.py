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

class Worker(QThread):
    output = Signal(object)
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.exiting = False

    def __del__(self):
        self.exiting = True
        self.wait()

    def render(self, text, count):
        self.run_times = count
        self.text = text
        self.start()

    def run(self):
        # Note: This is never called directly. It is called by Qt once the
        # thread environment has been set up.
        random.seed()
        n = self.run_times
        while not self.exiting and n > 0:
            time.sleep(1)
            # self.output.emit(QRect(x - self.outerRadius, y - self.outerRadius, self.outerRadius * 2, self.outerRadius * 2), image)
            print("OUTPUTTING 1")
            randint = random.randint(1, 100)
            print("OUTPUTTING 2")
            string = self.text+", Sleeping: " +str(self.run_times - n)+"/"+str(self.run_times)
            print("OUTPUTTING 3")
            self.output.emit(ResultObj(string, randint))
            n -= 1