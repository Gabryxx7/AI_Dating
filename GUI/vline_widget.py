from PySide2.QtWidgets import *

class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine)
        self.setFrameShadow(self.Sunken)