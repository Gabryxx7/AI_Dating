from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from GUI.waitingspinnerwidget import QtWaitingSpinner


class QtCustomWaitingSpinner(QWidget):
    def __init__(self, parent, centerOnParent=True, disableParentWhenSpinning=False, modality=Qt.NonModal):
        super().__init__()
        self.spinner = QtWaitingSpinner(self, centerOnParent, disableParentWhenSpinning, modality)
        self.parent = parent
        self.spinner.setRoundness(100.00)
        self.spinner.setMinimumTrailOpacity(15.00)
        self.spinner.setTrailFadePercentage(50.00)
        self.spinner.setNumberOfLines(21)
        self.spinner.setLineLength(4.00)
        self.spinner.setLineWidth(10.00)
        self.spinner.setInnerRadius(11.00)
        self.spinner.setRevolutionsPerSecond(1.00)
        self.spinner.setColor("#4455ff")

    def showSpinner(self):
        self.spinner.start()
        self.spinner.setVisible(True)

    def hideSpinner(self):
        self.spinner.stop()
        self.spinner.setVisible(False)

    def updateSize(self, size):
        self.setMinimumSize(size.height(), size.width())