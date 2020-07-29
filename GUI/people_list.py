from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from GUI.log import log
from GUI.person_preview_widget import PersonPreviewWidget
from Threading.data_reloader import ImgLoader


class PeopleList(QWidget):
    def __init__(self, parent, title, json_viewer=None):
        super(PeopleList, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.app = parent.app
        self.config = self.parent.app.config
        self.config_file = self.parent.app.config_file
        self.statusBar = self.parent.statusBar

        self.json_viewer = json_viewer
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignTop)
        # self.layout.addWidget(self.title_label)

        """ List as a Widget + QScrollArea"""
        # self.list = QWidget() # Widget that contains the collection of Vertical Box
        # # PersonPreviewWidget() # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        # self.list_layout = QVBoxLayout()
        # self.list_layout.setSpacing(0)
        # self.list.setLayout(self.list_layout)
        #
        # self.scroll = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        # self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.scroll.setWidgetResizable(True)
        # self.scroll.setWidget(self.list)
        # self.layout.addWidget(self.scroll)

        """ List as a QlistWidget """
        self.list = QListWidget() # Widget that contains the collection of Vertical Box
        self.list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.layout.addWidget(self.list)
        self.layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)

        self.list.itemSelectionChanged.connect(self.itemSelected)

        self.setStyleSheet("""
            QListWidget {
            border-style: none;
            margin: 0px
            }
            /*QListWidget::item{
                border-bottom: 0.5px solid #CDCDCD;
                border-top: 0.5px solid #CDCDCD;
                padding: 1%
            }*/

            """)

        # self.thread = QThread()  # 1a - create Worker and Thread inside the Form. No parent!
        # self.obj = worker.Worker()  # no parent!
        # self.thread_pool = QThreadPool()   # 1b - create a ThreadPool and then create the Workers when you need!
        # self.thread_pool.setMaxThreadCount(10)
    def itemSelected(self):
        selectedItems = self.list.selectedItems()
        if len(selectedItems) > 0:
            item_widget = self.list.itemWidget(selectedItems[0])
            self.json_viewer.load_data(item_widget.base_path+"/data.yaml")

    def update_list(self, data_list):
        if data_list is not None:
            photos_path_list = []
            for data in data_list:
                try:
                    person_widget = PersonPreviewWidget(self, data=data, json_viewer=self.json_viewer)
                    itemN = QListWidgetItem()
                    # Add widget to QListWidget funList
                    itemN.setSizeHint(person_widget.sizeHint())
                    self.list.addItem(itemN)
                    self.list.setItemWidget(itemN, person_widget)
                    # self.list_layout.addWidget(person_widget) # If I was using a QScrollArea
                    if person_widget.photos is not None:
                        photos_path_list.append(person_widget.photos[0])
                except Exception as e:
                    print("WUT " +str(e))
            self.photos_path_list = photos_path_list
            self.load_images_async()

    def load_images_async(self):
        obj = ImgLoader(self.photos_path_list)  # no parent!
        obj.signals.imgLoaded.connect(self.onImgLoaded)  # 2 - Connect Worker`s Signals to Form method slots to post data.
        obj.signals.finished.connect(self.onImgLoaderFinished)
        self.app.addBackgroundTask(obj, "ImgLoader started")

    def onImgLoaderFinished(self, tag=None):
        self.app.completeBackgroundTask("Images loading completed", tag=tag)

    def onImgLoaded(self, image, index):
        item = self.list.item(index)
        item_widget = self.list.itemWidget(item)
        pixmap = QPixmap.fromImage(image)
        item_widget.updatePicture(pixmap)
        self.app.updateBackgroundTaskInfo("Updated image " +str(index))

