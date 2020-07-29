from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
import GUI.loginForm as lf
from GUI.log import log
from GUI.vline_widget import VLine

# Subclass QMainWindow to customise your application's main window
class LoginWindow(QMainWindow):
    def __init__(self, app, background_info, background_count_label, spinner, parsed_args):
        super(LoginWindow, self).__init__()
        self.app = app
        self.parsed_args = parsed_args
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        self.setWindowTitle("TinderAI")
        self.setMinimumSize(500, 500)
        self.statusBar = QStatusBar(self)

        self.background_info = background_info
        self.background_count_label =background_count_label

        self.statusBar.addPermanentWidget(VLine())
        self.statusBar.addPermanentWidget(self.background_info)
        self.statusBar.addPermanentWidget(self.background_count_label)
        self.setStatusBar(self.statusBar)

        self.spinner = spinner
        self.statusBar.addPermanentWidget(self.spinner)

        self.form_widget = lf.LoginForm(self)
        self.setCentralWidget(self.form_widget)
        # label = QLabel("THIS IS AWESOME!!!")
        #
        # # The `Qt` namespace has a lot of attributes to customise
        # # widgets. See: http://doc.qt.io/qt-5/qt.html
        # label.setAlignment(Qt.AlignCenter)
        #
        # # Set the central widget of the Window. Widget will expand
        # # to take up all the space in the window by default.
        # self.setCentralWidget(label)

    def enterEvent(self, e):
        if self.parsed_args.css:
            log.d("LOGIN_W", "Enter!")
            self.app.updateStyle()
        # Do something with the event here
        super(LoginWindow, self).enterEvent(e)  # Do the default action on the parent class QLineEdit

    def focusInEvent(self, e):
        if self.parsed_args.css:
            log.d("LOGIN_W", "Focus IN!")
            self.app.updateStyle()
        # Do something with the event here
        super(LoginWindow, self).focusInEvent(e)  # Do the default action on the parent class QLineEdit

    def focusOutEvent(self, e):
        if self.parsed_args.css:
            log.d("LOGIN_W", "Focus Out!")
            self.app.updateStyle()
        # Do something with the event here
        super(LoginWindow, self).focusOutEvent(e)  # Do the default action on the parent class QLineEdit

    def hideEvent(self, e):
        if self.parsed_args.css:
            log.d("LOGIN_W", "Hidden!")
        # Do something with the event here
        super(LoginWindow, self).hideEvent(e)  # Do the default action on the parent class QLineEdit

    def showEvent(self, e):
        if self.parsed_args.css:
            log.d("LOGIN_W", "Shown!")
        # Do something with the event here
        super(LoginWindow, self).showEvent(e)  # Do the default action on the parent class QLineEdit