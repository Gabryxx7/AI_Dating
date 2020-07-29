from PySide2.QtWidgets import *
from PySide2.QtCore import *
import json
from GUI.log import log

class FeaturesButtonList(QWidget):
    def __init__(self, parent):
        super(FeaturesButtonList, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.app = parent.app
        self.config = self.parent.app.config
        self.config_file = self.parent.app.config_file
        self.statusBar = self.parent.statusBar

        self.matches_info_button = QPushButton('Get Match Info')
        self.matches_info_button.setEnabled(self.app.logged_in)
        self.matches_info_button.clicked.connect(self.app.tinder_api.get_match_info)

        self.get_matches_id_by_name_button = QPushButton('Get Match ID by name')
        self.get_matches_id_by_name_button.setEnabled(self.app.logged_in)
        self.get_matches_id_by_name_button.clicked.connect(self.app.tinder_api.get_match_id_by_name)

        self.get_photos_button = QPushButton('Get Photos')
        self.get_photos_button.setEnabled(self.app.logged_in)
        self.get_photos_button.clicked.connect(self.app.tinder_api.get_photos)

        self.get_avg_success_rate_button = QPushButton('Get Person Avg Success Rate')
        self.get_avg_success_rate_button.setEnabled(self.app.logged_in)
        self.get_avg_success_rate_button.clicked.connect(self.app.tinder_api.get_avg_successRate)

        self.see_friends_button = QPushButton('See friends')
        self.see_friends_button.setEnabled(self.app.logged_in)
        self.see_friends_button.clicked.connect(self.app.tinder_api.see_friends)

        self.see_friends_profile_button = QPushButton('See Friends Profile')
        self.see_friends_profile_button.setEnabled(self.app.logged_in)
        self.see_friends_profile_button.clicked.connect(self.app.tinder_api.see_friends_profiles)

        self.get_last_activity_button = QPushButton('Get Last Activity Date')
        self.get_last_activity_button.setEnabled(self.app.logged_in)
        self.get_last_activity_button.clicked.connect(self.app.tinder_api.get_last_activity_date)

        self.recommendations_title = QLabel('Recommendations')
        self.recommendations_title.setAlignment(Qt.AlignCenter)

        self.get_recommendations_button = QPushButton('Get List')
        self.get_recommendations_button.setStatusTip("Gets list of recommended profiles from Tinder")
        self.get_recommendations_button.setEnabled(self.app.logged_in)
        self.get_recommendations_button.clicked.connect(self.app.get_recommendations)

        self.reload_recommendations_button = QPushButton('Read from folder')
        self.reload_recommendations_button.setStatusTip("Check the recommendations stored in the Data folder")
        self.reload_recommendations_button.clicked.connect(self.reload_recommendations)
        self.recommendations_counter = QLabel('0')
        self.recommendations_new_counter = QLabel('0')
        self.recommendations_new_counter.setStyleSheet("QLabel { color : green;}")

        self.rename_recommendations_images_checkbox = QCheckBox("Rename images")
        self.rename_recommendations_images_checkbox.setStatusTip("Do you want to rename the pics to 1.jpg, 2.jpg ecc...?")
        self.rename_recommendations_images_checkbox.setChecked(True)
        self.rename_recommendations_images_checkbox.setEnabled(False)

        self.force_recommendations_download_checkbox = QCheckBox("Force overwrite")
        self.force_recommendations_download_checkbox.setStatusTip("Overwrites files if they exist already")
        self.force_recommendations_download_checkbox.setChecked(False)
        self.force_recommendations_download_checkbox.setEnabled(False)
        
        self.recommendations_photos_checkbox = QCheckBox("Photos")
        self.recommendations_photos_checkbox.setChecked(True)
        self.recommendations_photos_checkbox.setEnabled(False)

        self.recommendations_instagram_checkbox = QCheckBox("Instagram")
        self.recommendations_instagram_checkbox.setChecked(True)
        self.recommendations_instagram_checkbox.setEnabled(False)

        self.download_recommendations_amount = QSpinBox()
        self.download_recommendations_amount.setStatusTip("How many recommendations to download? (0 for all)")
        self.download_recommendations_amount.setRange(0, 30)
        self.download_recommendations_amount.setValue(0)
        self.download_recommendations_amount.setEnabled(False)

        self.download_recommendations_data_button = QPushButton('Download Data')
        self.download_recommendations_data_button.setStatusTip("Goes through the new recommended profile and downloads their Data and pics")
        self.download_recommendations_data_button.setEnabled(False)
        self.download_recommendations_data_button.clicked.connect(self.download_recommendations)

        self.recommendations_download_widget = QWidget()
        self.recommendations_download_layout = QVBoxLayout()
        self.recommendations_download_widget.setLayout(self.recommendations_download_layout)

        self.recommendations_download_layout.addWidget(self.recommendations_title)
        self.recommendations_download_layout.addWidget(self.get_recommendations_button)
        self.recommendations_download_layout.addWidget(self.reload_recommendations_button)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.recommendations_counter)
        h_layout.addWidget(self.recommendations_new_counter)
        self.recommendations_download_layout.addLayout(h_layout)
        valyout1 = QVBoxLayout()
        valyout2 = QVBoxLayout()
        halyout1 = QHBoxLayout()
        valyout1.addWidget(self.rename_recommendations_images_checkbox)
        valyout1.addWidget(self.force_recommendations_download_checkbox)
        valyout2.addWidget(self.recommendations_photos_checkbox)
        valyout2.addWidget(self.recommendations_instagram_checkbox)
        halyout1.addLayout(valyout1)
        halyout1.addLayout(valyout2)
        self.recommendations_download_layout.addLayout(halyout1)
        self.recommendations_download_layout.addWidget(self.download_recommendations_amount)
        self.recommendations_download_layout.addWidget(self.download_recommendations_data_button)

        self.recommendations_download_widget.setStyleSheet("""
            .QWidget{
                border: 0.5px solid #777777;
                border-radius: 5px;
            }
            """)

        self.matches_title = QLabel('Matches')
        self.matches_title.setAlignment(Qt.AlignCenter)

        self.get_matches_button = QPushButton('Get List')
        self.get_matches_button.setStatusTip("Gets list of matches from Tinder")
        self.get_matches_button.setEnabled(self.app.logged_in)
        self.get_matches_button.clicked.connect(self.app.get_matches)

        self.reload_matches_button = QPushButton('Read from folder')
        self.reload_matches_button.setStatusTip("Check the recommendations stored in the Data folder")
        self.reload_matches_button.clicked.connect(self.reload_matches)
        self.matches_counter = QLabel('0')
        self.matches_new_counter = QLabel('0')
        self.matches_new_counter.setStyleSheet("QLabel { color : green;}")

        self.rename_matches_images_checkbox = QCheckBox("Rename images")
        self.rename_matches_images_checkbox.setStatusTip("Do you want to rename the pics to 1.jpg, 2.jpg ecc...?")
        self.rename_matches_images_checkbox.setChecked(True)
        self.rename_matches_images_checkbox.setEnabled(False)

        self.force_matches_download_checkbox = QCheckBox("Force overwrite")
        self.force_matches_download_checkbox.setStatusTip("Overwrites files if they exist already")
        self.force_matches_download_checkbox.setChecked(False)
        self.force_matches_download_checkbox.setEnabled(False)

        self.matches_photos_checkbox = QCheckBox("Photos")
        self.matches_photos_checkbox.setChecked(True)
        self.matches_photos_checkbox.setEnabled(False)

        self.matches_instagram_checkbox = QCheckBox("Instagram")
        self.matches_instagram_checkbox.setChecked(True)
        self.matches_instagram_checkbox.setEnabled(False)

        self.matches_messages_checkbox = QCheckBox("Messages")
        self.matches_messages_checkbox.setChecked(True)
        self.matches_messages_checkbox.setEnabled(False)

        self.download_matches_amount = QSpinBox()
        self.download_matches_amount.setStatusTip("How many matches to download? (0 for all)")
        self.download_matches_amount.setRange(0, 30)
        self.download_matches_amount.setValue(0)
        self.download_matches_amount.setEnabled(False)

        self.download_matches_data_button = QPushButton('Download Data')
        self.download_matches_data_button.setStatusTip("Goes through the new matches downloads their Data and pics")
        self.download_matches_data_button.setEnabled(False)
        self.download_matches_data_button.clicked.connect(self.download_matches)

        self.matches_download_widget = QWidget()
        self.matches_download_layout = QVBoxLayout()
        self.matches_download_widget.setLayout(self.matches_download_layout)

        self.matches_download_layout.addWidget(self.matches_title)
        self.matches_download_layout.addWidget(self.get_matches_button)
        self.matches_download_layout.addWidget(self.reload_matches_button)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.matches_counter)
        h_layout.addWidget(self.matches_new_counter)
        self.matches_download_layout.addLayout(h_layout)
        valyout1 = QVBoxLayout()
        valyout2 = QVBoxLayout()
        halyout1 = QHBoxLayout()
        valyout1.addWidget(self.rename_matches_images_checkbox)
        valyout1.addWidget(self.force_matches_download_checkbox)
        valyout2.addWidget(self.matches_photos_checkbox)
        valyout2.addWidget(self.matches_instagram_checkbox)
        valyout2.addWidget(self.matches_messages_checkbox)
        halyout1.addLayout(valyout1)
        halyout1.addLayout(valyout2)
        self.matches_download_layout.addLayout(halyout1)
        self.matches_download_layout.addWidget(self.download_matches_amount)
        self.matches_download_layout.addWidget(self.download_matches_data_button)

        self.matches_download_widget.setStyleSheet("""
        .QWidget{
            border: 0.5px solid #777777;
            border-radius: 5px;
        }
        """)

        self.layout.setAlignment(Qt.AlignTop)
        self.layout.addWidget(self.recommendations_download_widget)
        self.layout.addWidget(self.matches_download_widget)
        self.layout.addWidget(self.matches_info_button)
        self.layout.addWidget(self.get_matches_id_by_name_button)
        self.layout.addWidget(self.get_photos_button)
        self.layout.addWidget(self.get_avg_success_rate_button)
        self.layout.addWidget(self.see_friends_button)
        self.layout.addWidget(self.see_friends_profile_button)
        self.layout.addWidget(self.get_last_activity_button)

        self.setLayout(self.layout)

    def update_matches_widgets(self):
        log.d("FEATURES", str("Updating Matches widgets"))
        self.update_widgets(self.app.matches, self.app.new_matches, self.get_matches_button,
                            self.reload_matches_button, self.download_matches_data_button,
                            self.download_matches_amount, self.rename_matches_images_checkbox,
                            self.force_matches_download_checkbox, self.matches_new_counter, self.matches_counter,
                            self.matches_photos_checkbox, self.matches_instagram_checkbox)
        self.matches_messages_checkbox.setEnabled(self.download_matches_data_button.isEnabled())

    def update_recommendations_widgets(self):
        log.d("FEATURES", str("Updating Recommendations Widgets"))
        self.update_widgets(self.app.recommendations, self.app.new_recommendations, self.get_recommendations_button,
                            self.reload_recommendations_button, self.download_recommendations_data_button,
                            self.download_recommendations_amount, self.rename_recommendations_images_checkbox,
                            self.force_recommendations_download_checkbox, self.recommendations_new_counter, self.recommendations_counter,
                            self.recommendations_photos_checkbox, self.recommendations_instagram_checkbox)

    def update_widgets(self, data, new_data, get_button, reload_button, download_button, amount_spinner, rename_checkbox, force_checkbox, new_data_counter, data_counter, photo_checkbox, insta_checkbox):
        download_button.setEnabled(new_data is not None)
        amount_spinner.setEnabled(download_button.isEnabled())
        rename_checkbox.setEnabled(download_button.isEnabled())
        force_checkbox.setEnabled(download_button.isEnabled())
        photo_checkbox.setEnabled(download_button.isEnabled())
        insta_checkbox.setEnabled(download_button.isEnabled())
        if new_data is not None:
            new_data_counter.setText(str(len(new_data)))
            get_button.setText('Update List')
        else:
            new_data_counter.setText(0)
            get_button.setText('Get New')
        if data is not None:
            data_counter.setText(str(len(data)))
        else:
            data_counter.setText(0)


    def download_recommendations(self):
        self.app.download_new_recommendations(self.recommendations_photos_checkbox.isChecked(),
                                            self.recommendations_instagram_checkbox.isChecked(),
                                              self.rename_recommendations_images_checkbox.isChecked(),
                                              self.download_recommendations_amount.value(),
                                              self.force_recommendations_download_checkbox.isChecked())
        # self.download_recommendations_data_button.setText("Stop")
        # self.download_recommendations_data_button.setStyleSheet("QPushButton{background-color: red;}")

    def download_matches(self):
        self.app.download_new_matches(self.matches_photos_checkbox.isChecked(),
                                      self.matches_instagram_checkbox.isChecked(),
                                      self.matches_messages_checkbox.isChecked(),
                                      self.rename_matches_images_checkbox.isChecked(),
                                      self.download_matches_amount.value(),
                                      self.force_matches_download_checkbox.isChecked())
        # self.download_matches_data_button.setText("Stop")
        # self.download_matches_data_button.setStyleSheet("QPushButton{background-color: red;}")

    def reload_recommendations(self):
        self.app.reload_recommendations(True, self.recommendations_photos_checkbox.isChecked(),
                                    self.recommendations_instagram_checkbox.isChecked(),
                                        self.force_matches_download_checkbox.isChecked())

    def reload_matches(self):
        self.app.reload_matches(True, self.matches_photos_checkbox.isChecked(),
                                      self.matches_instagram_checkbox.isChecked(),
                                      self.matches_messages_checkbox.isChecked(),
                                    self.force_matches_download_checkbox.isChecked())

