from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from GUI.log import log
from GUI.avatar_label import AvatarLabel
from Threading.data_reloader import ImgLoader
from datetime import datetime
import dateutil.parser

class MessagePreviewLabel(QLabel):
    def paintEvent( self, event ):
        painter = QPainter(self)

        metrics = QFontMetrics(self.font())
        elided  = metrics.elidedText(self.text(), Qt.ElideRight, self.width())

        painter.drawText(self.rect(), self.alignment(), elided)

class PersonPreviewWidget(QWidget):
    def __init__(self, parent, data=None, load_images=False, json_viewer=None, chat_widget=None, data_dashboard=None):
        super(PersonPreviewWidget, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_hlayout = QHBoxLayout()
        self.main_hlayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.main_hlayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_hlayout)

        self.load_images = load_images

        self.parent = parent
        self.app = parent.app
        self.config = self.parent.app.config
        self.config_file = self.parent.app.config_file
        self.statusBar = self.parent.statusBar

        self.json_viewer = json_viewer
        self.chat_widget = chat_widget
        self.data_dashboard = data_dashboard

        self.data = data
        self.base_path = ""
        self.photos = None
        self.photos_pixmap = None
        self.processed_photos = None
        self.processed_photos_pixmap = None
        self.name = ""
        self.id = ""
        self.preview_message = ""
        self.match_id = None
        self.messages = None

        self.profile_pic = AvatarLabel("", QSize(100,100))
        self.profile_pic.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.profile_pic.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #
        # self.get_msgs_button = QPushButton("Messages")
        # self.get_msgs_button.setVisible(False)
        # self.get_msgs_button.clicked.connect(self.get_messages)
        # # self.get_msgs_button.setAlignment(Qt.AlignRights | Qt.AlignVCenter)
        #
        # self.info_button = QPushButton("Get info")
        # self.info_button.setVisible(False)
        # self.info_button.clicked.connect(self.get_match_info)

        self.name_label = QLabel(self.name)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.name_label.setStyleSheet("""
                /* font-weight: bold; */
                font-size: 12pt;
            """)

        self.message_preview = QLabel()
        self.message_preview.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.message_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.message_preview.setStyleSheet("""
                        font-size: 9pt;
                        color: #ABABAB;
                    """)

        self.message_preview_time = QLabel()
        self.message_preview_time.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.message_preview_time.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.message_preview_time.setStyleSheet("""
                        font-size: 8pt;
                        color: #bcb2d1;
                    """)

        self.main_hlayout.addWidget(self.profile_pic)
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(10,15,10,15)

        name_time_layout = QHBoxLayout()
        name_time_layout.addWidget(self.name_label)
        name_time_layout.addStretch(1)
        name_time_layout.addWidget(self.message_preview_time)

        message_layout = QHBoxLayout()
        message_layout.addWidget(self.message_preview)
        message_layout.addStretch(1)

        preview_layout.addLayout(name_time_layout)
        preview_layout.addLayout(message_layout)
        self.main_hlayout.addLayout(preview_layout)
        # self.main_hlayout.addWidget(self.get_msgs_button)
        # self.main_hlayout.addWidget(self.info_button)

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
                    self.preview_message = data['messages'][0]
                else:
                    self.messages = None
                    self.preview_message = None
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
        if self.preview_message is not None:
            msg = self.preview_message['message']
            if self.preview_message["from"] in self.app.profile_info["_id"]:
                msg = "<font color='#8389b4'> You: </font>" + msg
            self.message_preview.setText(msg)
            try:
                # 2020-04-30T05:48:05.684Z
                date_obj = dateutil.parser.isoparse(self.preview_message['sent_date'])
                self.message_preview_time.setText(date_obj.strftime("%m.%d.%y %H:%M"))
            except Exception as e:
                print("EXCEPTION: " +str(e))
                self.message_preview_time.setText("")
        # self.info_button.setVisible(self.json_viewer is not None and person is not None)
        # self.get_msgs_button.setVisible(self.match_id is not None)

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
        if self.data_dashboard is not None and self.messages is not None:
            self.data_dashboard.update_messages(self.messages, self.app.profile_info['_id'])
        self.adjustSize()