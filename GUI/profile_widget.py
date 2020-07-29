from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from GUI.log import log
from GUI.avatar_label import AvatarLabel

class ProfileWidget(QWidget, profile_info):
    def __init__(self, parent, profile_info):
        super(ProfileWidget, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.parent = parent
        self.app = parent.app
        self.config = self.parent.app.config
        self.config_file = self.parent.app.config_file
        self.statusBar = self.parent.statusBar

        self.profile_info = profile_info
