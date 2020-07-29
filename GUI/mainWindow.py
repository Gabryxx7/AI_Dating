from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
import json
from GUI.people_list import PeopleList
from GUI.log_widget import LogWidget
from GUI.features_button_list import FeaturesButtonList
from GUI.log import log
from GUI.json_viewer import JsonViewWidget
from Threading.worker_thread import ListUpdateWorker, ResultObj
from GUI.customwaitingwidget import QtCustomWaitingSpinner
from GUI.vline_widget import VLine
from GUI.waitingspinnerwidget import QtWaitingSpinner

# Subclass QMainWindow to customise your application's main window
class MainWindow(QMainWindow):
    def __init__(self, app, background_info, background_count_label, spinner, parsed_args):
        super(MainWindow, self).__init__()
        self.app = app
        self.parsed_args = parsed_args
        self.config = self.app.config
        self.config_file = self.app.config_file

        self.background_info = background_info
        self.background_count_label =background_count_label
        self.spinner = spinner

        self.statusBar = QStatusBar(self)
        self.statusBar.addPermanentWidget(VLine())
        self.statusBar.addPermanentWidget(self.background_info)
        self.statusBar.addPermanentWidget(self.spinner)
        self.statusBar.addPermanentWidget(self.background_count_label)
        self.setStatusBar(self.statusBar)

        self.setWindowTitle("TinderAI")
        self.setMinimumSize(600, 600)

        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # button_action = QAction(QIcon("./icons/tinder.png"), "Update Style", self)
        button_action = QAction("Login", self)
        button_action.setStatusTip("Login")
        button_action.triggered.connect(self.verify_login)
        toolbar.addAction(button_action)
        toolbar.addSeparator()

        self.json_view = JsonViewWidget(self, None)

        matches_json_button = QAction("Matches JSON", self)
        recommendations_json_button = QAction("Recommendations JSON", self)
        profile_button = QAction("See Profile", self)
        matches_json_button.triggered.connect(self.json_view.load_matches)
        recommendations_json_button.triggered.connect(self.json_view.load_recommendations)
        profile_button.triggered.connect(self.json_view.load_profile)
        toolbar.addAction(matches_json_button)
        toolbar.addAction(recommendations_json_button)
        toolbar.addAction(profile_button)

        # button_action2 = QAction(QIcon("bug.png"), "Your button2", self)
        # button_action2.setStatusTip("This is your button2")
        # # button_action2.triggered.connect(self.onMyToolBarButtonClick)
        # button_action2.setCheckable(True)
        # toolbar.addAction(button_action2)
        # toolbar.addWidget(QLabel("Hello"))
        # toolbar.addWidget(QCheckBox())

        # self.json_view = JsonViewWidget(self, fpath="C:\\Users\\Gabryxx7\\PycharmProjects\\Tinder\\Data\\recommendations.json")

        self.main_widget = QWidget()
        self.main_hlayout = QHBoxLayout()
        self.main_hlayout.setContentsMargins(0,0,0,0)
        self.main_vlayout = QVBoxLayout()
        self.main_vlayout.setContentsMargins(0,0,0,0)
        self.lists_hlayout = QHBoxLayout()
        self.lists_hlayout.setContentsMargins(0,0,0,0)

        self.recommendations_list = PeopleList(self, "Recommendations", json_viewer=self.json_view)
        self.matches_list = PeopleList(self, "Matches", json_viewer=self.json_view)
        self.features_panel = FeaturesButtonList(self)

        self.lists_hlayout.addWidget(self.recommendations_list)

        self.main_vlayout.addLayout(self.lists_hlayout, 70)
        self.main_vlayout.addWidget(log.logWidget, 30)

        self.main_hlayout.addWidget(self.matches_list, 45)
        self.main_hlayout.addWidget(self.json_view, 15)
        self.main_hlayout.addLayout(self.main_vlayout, 25)
        self.main_hlayout.addWidget(self.features_panel, 15)

        self.main_widget.setLayout(self.main_hlayout)
        self.setCentralWidget(self.main_widget)
        self.centralWidget().layout().setContentsMargins(0,0,0,0)
        self.centralWidget().setContentsMargins(0,0,0,0)

        self.setStyleSheet("""
            QMainWindow {
                padding: 0px
            }

            """)

    def verify_login(self):
        self.app.verify_login(True, self.app.login_verified)



