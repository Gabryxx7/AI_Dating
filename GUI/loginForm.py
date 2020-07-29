from PySide2.QtWidgets import *
from PySide2.QtCore import Slot

import oyaml as yaml
from GUI.log import log
from Threading.data_reloader import APIBackgroundWorker
from GUI.customwaitingwidget import QtCustomWaitingSpinner


class LoginForm(QWidget):
    def __init__(self, parent):
        super(LoginForm, self).__init__(parent)
        self.layout = QGridLayout()
        self.parent = parent
        self.app = parent.app
        self.config = self.parent.app.config
        self.config_file = self.parent.app.config_file
        self.statusBar = self.parent.statusBar

        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText('FB email')
        self.lineEdit_username.textChanged.connect(self.fb_credentials_inserted)
        # label_name = QLabel('<font size="4"> FB email </font>')

        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        self.lineEdit_password.setPlaceholderText('FB Password')
        self.lineEdit_password.textChanged.connect(self.fb_credentials_inserted)
        # label_password = QLabel('<font size="4"> FB Password </font>')

        self.remember_me_checkbox = QCheckBox("Remember me")
        self.remember_me_checkbox.setChecked(True)

        self.button_fb_access_token = QPushButton('Get FB Access Token')
        self.button_fb_access_token.setEnabled(False)
        self.button_fb_access_token.clicked.connect(lambda: self.get_fb_access_token(True))
        self.button_fb_spinner = QtCustomWaitingSpinner(self, centerOnParent=False)
        self.button_fb_spinner.hideSpinner()

        self.linedEdit_fb_token = QTextEdit()
        self.linedEdit_fb_token.setAcceptRichText(False);
        self.linedEdit_fb_token.setPlaceholderText('FB Auth Token')
        self.linedEdit_fb_token.textChanged.connect(self.fb_token_user_inserted)

        self.button_user_id = QPushButton('Get User ID')
        self.button_user_id.setEnabled(False)
        self.button_user_id.clicked.connect(lambda: self.get_user_id(True))

        self.linedEdit_fb_user_id = QLineEdit()
        self.linedEdit_fb_user_id.setPlaceholderText('FB User ID')
        self.linedEdit_fb_user_id.textChanged.connect(self.fb_token_user_inserted)

        self.button_tinder_access_token = QPushButton('Get Tinder Access Token')
        self.button_tinder_access_token.setEnabled(False)
        self.button_tinder_access_token.clicked.connect(lambda: self.get_tinder_access_token(True))

        self.linedEdit_tinder_token = QLineEdit()
        self.linedEdit_tinder_token.setPlaceholderText('Tinder Auth Token')
        # self.linedEdit_tinder_token.textChanged.connect(self.tinder_token_inserted)

        self.button_verify = QPushButton('Login')
        self.button_verify.clicked.connect(self.verify_login)
        self.button_verify_spinner = QtCustomWaitingSpinner(self, centerOnParent=False)
        self.button_verify_spinner.hideSpinner()

        self.button_save = QPushButton('Save Settings')
        self.button_save.clicked.connect(self.save_to_yaml)
        self.button_next = QPushButton('Use Offline')
        self.button_next.clicked.connect(self.app.startMainWindow)
        # self.button_next.clicked.connect(self.save_to_yaml)

        self.statusBar.showMessage("Please Insert FB email and Password...")
        if not self.config:
            self.config = {}
        try:
            self.lineEdit_username.setText(self.config['facebook']['email'])
            self.lineEdit_password.setText(self.config['facebook']['password'])  # Careful here!
            self.linedEdit_fb_token.setText(self.config['facebook']['auth_token'])
            self.linedEdit_fb_user_id.setText(self.config['facebook']['user_id'])
        except Exception:
            self.config['facebook'] = {}
        try:
            self.linedEdit_tinder_token.setText(self.config['tinder']['auth_token'])
        except Exception:
            self.config['host'] = 'https://api.gotinder.com'
            self.config['tinder'] = {}

        self.layout.setRowMinimumHeight(2, 40)
        row = 0
        # layout.addWidget(label_name, 0, 0)
        self.layout.addWidget(self.lineEdit_username, row, 0, 1, 2)
        row += 1
        # layout.addWidget(label_password, 1, 0)
        self.layout.addWidget(self.lineEdit_password, row, 0, 1, 2)
        row += 1
        self.layout.addWidget(self.remember_me_checkbox, row, 0, 1, 2)
        row += 1
        self.layout.addWidget(self.button_fb_access_token, row, 0, 1, 1)
        self.layout.addWidget(self.button_fb_spinner, row, 1, 1, 1)
        row += 1
        self.layout.addWidget(self.linedEdit_fb_token, row, 0, 1, 2)
        row += 1
        self.layout.addWidget(self.button_user_id, row, 0, 1, 2)
        row += 1
        self.layout.addWidget(self.linedEdit_fb_user_id, row, 0, 1, 2)
        row += 1
        self.layout.addWidget(self.button_tinder_access_token, row, 0, 1, 2)
        row += 1
        self.layout.addWidget(self.linedEdit_tinder_token, row, 0, 1, 2)
        row += 1
        self.layout.addWidget(self.button_verify, row, 0, 1, 1)
        self.layout.addWidget(self.button_verify_spinner, row, 1, 1, 1)
        row += 1
        self.layout.addWidget(self.button_save, row, 0, 1, 1)
        self.layout.addWidget(self.button_next, row, 1, 1, 1)

        self.setLayout(self.layout)

    @Slot()
    def fb_credentials_inserted(self):
        self.button_fb_access_token.setEnabled(
            len(self.lineEdit_username.text()) > 0 and len(self.lineEdit_password.text()) > 0)
        QApplication.processEvents()

    @Slot()
    def get_fb_access_token(self, doAsync=True):
        print(self.config)
        log.i("LOGIN_F", "Retreiving token from FB...")
        self.statusBar.showMessage("Retreiving token from FB...")
        self.config['facebook']['email'] = self.lineEdit_username.text()
        self.config['facebook']['password'] = self.lineEdit_password.text()
        self.app.get_api_data(doAsync, self.app.tinder_api.get_fb_access_token,
                          [self.config['facebook']['email'], self.config['facebook']['password']],
                          {},
                          finished_callback=self.update_fb_token,
                          info="Getting FB auth token",
                          tag="FbTokenThread")

    def update_fb_token(self, token):
        print(self.config)
        try:
            self.config['facebook']['auth_token'] = token
            log.d("LOGIN_F", self.config)
            if 'error' in self.config['facebook']['auth_token']:
                Exception("Error: " + self.config['facebook']['auth_token'])
            self.linedEdit_fb_token.setText(self.config['facebook']['auth_token'])
            self.button_fb_spinner.hideSpinner()
        except Exception as e:
            log.e("LOGIN_F", "Exception Getting token: " + str(e))
            self.config['facebook']['auth_token'] = ""
            self.linedEdit_fb_token.setText("ERROR")
        QApplication.processEvents()
        self.statusBar.clearMessage()

    @Slot()
    def get_user_id(self, doAsync=True):
        print(self.config)
        log.i("LOGIN_F", "Retreiving Facebook user id...")
        self.statusBar.showMessage("Retreiving user id from FB...")
        self.app.get_api_data(doAsync, self.app.tinder_api.get_fb_user_id,
                              [self.config['facebook']['auth_token']],
                              {},
                              finished_callback=self.update_user_id,
                              info="Getting FB auth token",
                              tag="FBUserIdThread")

    def update_user_id(self, data):
        self.config['facebook']['user_id'] = data
        if 'error' in self.config['facebook']['user_id']:
            log.i("LOGIN_F", "Error retreiving user id")
            self.linedEdit_fb_user_id.setText("ERROR!")
            self.config['facebook']['user_id'] = ''
        else:
            log.i("LOGIN_F", "User id received: " + str(self.config['facebook']['user_id']))
            self.linedEdit_fb_user_id.setText(self.config['facebook']['user_id'])
        QApplication.processEvents()
        self.statusBar.clearMessage()

    @Slot()
    def fb_token_user_inserted(self):
        print(self.config)
        self.button_user_id.setEnabled(len(self.linedEdit_fb_token.toPlainText()) > 0)
        self.button_tinder_access_token.setEnabled(
            len(self.linedEdit_fb_token.toPlainText()) > 0 and len(self.linedEdit_fb_user_id.text()) > 0)
        QApplication.processEvents()
        # docHeight = self.linedEdit_fb_token.document().size().height()
        # log.d("LOGIN_F", "Height" + str(docHeight))
        # if docHeight > 0 and self.linedEdit_fb_token.minimumHeight() <= docHeight <= self.linedEdit_fb_token.maximumHeight():
        #     self.linedEdit_fb_token.setMinimumHeight(int(docHeight))

    @Slot()
    def get_tinder_access_token(self, doAsync=True):
        log.i("LOGIN_F", "Retreiving token from Tinder...")
        self.statusBar.showMessage("Retreiving token from Tinder...")
        self.app.get_api_data(doAsync, self.app.tinder_api.get_auth_token,
                          [self.config['facebook']['auth_token'], self.config['facebook']['user_id']],
                          {},
                          finished_callback=self.update_tinder_token,
                          info="Getting Tinder auth token",
                          tag="TinderTokenThread")
    def update_tinder_token(self, data):
        self.config['tinder']['auth_token'] = data
        log.i("LOGIN_F", "Tinder Token: " + str(self.config['tinder']['auth_token']))
        if 'error' in self.config['tinder']['auth_token']:
            log.e("LOGIN_F", "Error in retreiving token")
            self.config['tinder']['auth_token'] = ''
            self.statusBar.showMessage("ERROR")
        else:
            self.linedEdit_tinder_token.setText(self.config['tinder']['auth_token'])
            self.statusBar.showMessage("SUCCESS!: " + self.config['tinder']['auth_token'])
        QApplication.processEvents()

    @Slot()
    def tinder_token_inserted(self, token):
        QApplication.processEvents()
        pass

    def save_to_yaml(self):
        try:
            print("Saving yaml...")
            log.i("LOGIN_F", self.config_file)
            log.d("LOGIN_F", self.config)
            with open(self.config_file, 'w') as fy:
                yaml.dump(self.config, fy)
            self.statusBar.showMessage("Credentials Saved to " + str(self.config_file))
        except Exception as e:
            log.e("LOGIN_F", "Exceptipn: " + str(e))

    @Slot()
    def verify_login(self, doAsync=True):
        self.app.config = self.config
        self.app.verify_login(doAsync, self.login_verified)
        if doAsync:
            self.button_verify_spinner.showSpinner()

    def login_verified(self, isVerified):
        self.button_verify_spinner.hideSpinner()
        self.app.login_verified(isVerified, True)
