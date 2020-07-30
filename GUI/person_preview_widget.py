from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import utils
from GUI.log import log
from GUI.avatar_label import AvatarLabel
from Threading.data_reloader import ImgLoader

class PersonPreviewWidget(QWidget):
    def __init__(self, parent, data=None, load_images=False, json_viewer=None, chat_widget=None):
        super(PersonPreviewWidget, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.load_images = load_images

        self.parent = parent
        self.app = parent.app
        self.config = self.parent.app.config
        self.config_file = self.parent.app.config_file
        self.statusBar = self.parent.statusBar

        self.json_viewer = json_viewer
        self.chat_widget = chat_widget

        self.data = data
        self.base_path = ""
        self.photos = None
        self.photos_pixmap = None
        self.processed_photos = None
        self.processed_photos_pixmap = None
        self.name = ""
        self.id = ""
        self.first_message = ""
        self.match_id = None
        self.messages = None

        self.get_msgs_button = QPushButton("Messages")
        self.get_msgs_button.setVisible(False)
        self.get_msgs_button.clicked.connect(self.get_messages)
        # self.get_msgs_button.setAlignment(Qt.AlignRights | Qt.AlignVCenter)

        self.info_button = QPushButton("Get info")
        self.info_button.setVisible(False)
        self.info_button.clicked.connect(self.get_match_info)

        self.name_label = QLabel(self.name)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.name_label.setContentsMargins(10,0,10,0)
        self.name_label.setStyleSheet("""
            .QLabel{
                font-weight: bold;
                font-size: 18px;
            }""")

        self.message_preview = QLabel(self.first_message)
        self.message_preview.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.message_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.message_preview.setContentsMargins(10,0,10,0)
        self.message_preview.setStyleSheet("""
                    .QLabel{
                        font-size: 14px;
                    }""")

        self.profile_pic = AvatarLabel("", QSize(100,100))
        self.profile_pic.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.profile_pic.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout.addWidget(self.profile_pic)
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(self.name_label)
        preview_layout.addWidget(self.message_preview)
        self.layout.addLayout(preview_layout)
        self.layout.addStretch(1)
        self.layout.addWidget(self.get_msgs_button)
        self.layout.addWidget(self.info_button)
        self.layout.addStretch(2)

        self.setStyleSheet("""
            QWidget > QWidget{
                background-color: transparent;
            }
            """)

        self.set_data(data, load_images)

    def resizeEvent(self, e):
        # self.profile_pic.update_avatar_size(self.size())
        super(PersonPreviewWidget, self).resizeEvent(e)  # Do the default action on the parent class QLineEdit

    def get_messages(self):
        if self.messages is None:
            self.app.get_messages(self.data, self.messagesReceived, self.name)

    def messagesReceived(self, data):
        print(data)
        if 'data' in data:
            self.messages = data['data']['messages']

    def set_data(self, data, load_profile_pic=True, load_processed_profile_pic=False, load_images=False, load_processed_images=False):
        if data is None:
            self.base_path = ""
            self.photos = None
            self.photos_pixmap = None
            self.processed_photos = None
            self.processed_photos_pixmap = None
            self.name = ""
            self.id = ""
            self.match_id = None
            self.messages = None
        else:
            try:
                person, type = self.app.tinder_api.get_person_data(data)
                if person is not None:
                    if 'local_path' in person:
                        self.base_path = person['local_path']
                    if "photos" in person:
                        for photo in person["photos"]:
                            if 'local_path' in photo:
                                if self.photos is None:
                                    self.photos = []
                                self.photos.append(photo['local_path'])
                            if 'processedFiles' in photo:
                                for processed_file in photo['processedFiles']:
                                    if 'local_path' in processed_file:
                                        if self.processed_photos is None:
                                            self.processed_photos = []
                                        self.processed_photos.append(processed_file['local_path'])
                    if 'name' in person:
                        self.name = person['name']
                    if '_id' in person:
                        self.id = person['_id']
                if 'messages' in data and len(data['messages']) > 0:
                    self.messages = data['messages']
                    self.first_message = data['messages'][0]['message']
                else:
                    self.messages = None
                    self.first_message = ""
                if "message_count" in data: # for unread messages
                    self.match_id = data["_id"]

                if self.photos_pixmap is None:
                    if load_images:
                        self.load_images_async(self.photos, self.onImgLoaded)
                    elif load_profile_pic:
                        self.load_images_async(self.photos[0], self.onProfilePicLoaded)
                if self.processed_photos_pixmap is None:
                    if load_processed_images:
                        self.load_images_async(self.processed_photos, self.onProcImgLoaded)
                    elif load_processed_profile_pic:
                        self.load_images_async(self.processed_photos[0], self.onProfilePicLoaded)
            except Exception as e:
                log.e("PersonWidget", "Exception list person's data: " + str(e))

        self.name_label.setText(self.name)
        self.message_preview.setText(self.first_message)
        # self.info_button.setVisible(self.json_viewer is not None and person is not None)
        self.get_msgs_button.setVisible(self.match_id is not None)

    def load_images_async(self, photos_paths, imgLoadedCallback):
        obj = ImgLoader(photos_paths)  # no parent!
        obj.signals.imgLoaded.connect(imgLoadedCallback)  # 2 - Connect Worker`s Signals to Form method slots to post data.
        obj.signals.finished.connect(self.onImgLoaderFinished)
        self.app.addBackgroundTask(obj, "ImgLoader preview started")

    def onImgLoaderFinished(self, tag=None):
        self.app.completeBackgroundTask("Images loading completed", tag=tag)

    def onImgLoaded(self, image, index):
        pixmap = QPixmap.fromImage(image)
        if self.photos_pixmap is None:
            self.photos_pixmap = [pixmap]
            self.updateProfilePicture(pixmap)
            self.app.updateBackgroundTaskInfo("Updated profile image " +str(index))

    def onProfilePicLoaded(self, image, index):
        pixmap = QPixmap.fromImage(image)
        self.updateProfilePicture(pixmap)
        self.app.updateBackgroundTaskInfo("Updated profile image " + str(index))

    def onProcImgLoaded(self, image, index):
        pixmap = QPixmap.fromImage(image)
        if self.processed_photos_pixmap is None:
            self.processed_photos_pixmap = [pixmap]

    def updatePicture(self, pixmap):
        self.profile_pic.setPicturePixmap(pixmap)

    def get_match_info(self):
        self.app.get_match_info(self.id, self.name)

    def itemSelected(self):
        if self.json_viewer is not None:
            self.json_viewer.load_data(self.base_path+"/data.yaml")
        if self.chat_widget is not None:
            self.chat_widget.addMessages(messages_list=self.messages, clear_messages=True)
            # self.chat_widget.addMessages(messages_list=self.messages, clear_messages=True)