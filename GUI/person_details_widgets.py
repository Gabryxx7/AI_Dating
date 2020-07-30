from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import utils
from GUI.log import log
from GUI.avatar_label import AvatarLabel
from Threading.data_reloader import ImgLoader

class PersonDetailsWidget(QWidget):
    def __init__(self, parent, data=None, load_images=False):
        super(PersonDetailsWidget, self).__init__(parent)
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

        self.base_path = ""
        self.photos = None
        self.photos_pixmap = None
        self.processed_photos = None
        self.processed_photos_pixmap = None
        self.name = ""
        self.id = ""
        self.bio = ""

        self.name_label = QLabel(self.name)
        self.name_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.name_label.setContentsMargins(10,0,10,0)
        self.name_label.setStyleSheet("""
            .QLabel{
                font-weight: bold;
                font-size: 18%;
            }""")

        self.bio_label = QLabel(self.bio)
        self.bio_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.bio_label.setContentsMargins(10,0,10,0)
        self.bio_label.setStyleSheet("""
                    .QLabel{
                        font-size: 11%;
                    }""")

        self.profile_pic = AvatarLabel("", QSize(250,250))
        self.profile_pic.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.profile_pic.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.hlayout = QVBoxLayout()
        self.hlayout.addWidget(self.name_label)
        self.hlayout.addWidget(self.profile_pic)
        self.layout.addLayout(self.hlayout)
        self.layout.addWidget(self.bio_label)

        self.setStyleSheet("""
            QWidget > QWidget{
                background-color: transparent;
            }
            """)

        self.set_data(data, self.load_images)

    def set_data(self, data, load_profile_pic=True, load_processed_profile_pic=False, load_images=False, load_processed_images=False):
        if data is None:
            self.base_path = ""
            self.photos = None
            self.photos_pixmap = None
            self.processed_photos = None
            self.processed_photos_pixmap = None
            self.name = ""
            self.id = ""
            self.bio = ""
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
                    if 'bio' in person:
                        self.bio = person['bio']
                    else:
                        self.bio = ""

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
                log.e("PersonWidget", "Exception setting person's data: " + str(e))

        self.name_label.setText(self.name)
        self.bio_label.setText(self.bio)

    def load_images_async(self, photos_paths, imgLoadedCallback):
        obj = ImgLoader(photos_paths)  # no parent!
        obj.signals.imgLoaded.connect(imgLoadedCallback)  # 2 - Connect Worker`s Signals to Form method slots to post data.
        obj.signals.finished.connect(self.onImgLoaderFinished)
        self.app.addBackgroundTask(obj, "ImgLoader Details started")

    def onImgLoaderFinished(self, tag=None):
        self.app.completeBackgroundTask("Images loading completed", tag=tag)

    def onProfilePicLoaded(self, image, index):
        pixmap = QPixmap.fromImage(image)
        self.updateProfilePicture(pixmap)
        self.app.updateBackgroundTaskInfo("Updated profile image " + str(index))

    def onImgLoaded(self, image, index):
        pixmap = QPixmap.fromImage(image)
        if self.photos_pixmap is None:
            self.photos_pixmap = [pixmap]
            self.updateProfilePicture(pixmap)
            self.app.updateBackgroundTaskInfo("Updated profile image " +str(index))

    def onProcImgLoaded(self, image, index):
        pixmap = QPixmap.fromImage(image)
        if self.processed_photos_pixmap is None:
            self.processed_photos_pixmap = [pixmap]

    def updateProfilePicture(self, pixmap):
        if isinstance(pixmap, str):
            self.profile_pic.setPicturePath(pixmap)
        else:
            self.profile_pic.setPicturePixmap(pixmap)