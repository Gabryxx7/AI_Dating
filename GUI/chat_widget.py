from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from GUI.log import log

class MessageBubble(QLabel):
    def __init__(self, text, color=None, text_color=None, border_radius=10):
        super(MessageBubble,self).__init__(text)
        margin = border_radius*0.3
        self.setContentsMargins(margin, margin, margin, margin)
        self.color = color
        self.text_color = text_color
        self.border_radius = border_radius
        self.setWordWrap(True)
        self.setStyleSheet("""
            QLabel{
                border: 0px;
                font-size: 12pt;
                background-color: transparent;
                color: %s;
            }
        """ % (text_color))

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing,True)
        p.setBackground(Qt.transparent)
        if self.color is not None:
            brush = QBrush(QColor(self.color))
            p.setBrush(brush)
        p.drawRoundedRect(0, 0, self.width()-1, self.height()-1 , self.border_radius, self.border_radius)
        super(MessageBubble, self).paintEvent(e)

    def updateBubble(self, color=None, text_color=None, border_radius=None):
        if color:
            self.color = color
        if text_color:
            self.text_color = text_color
        if border_radius:
            self.border_radius = border_radius
        margin = border_radius*0.3
        self.setContentsMargins(margin, margin, margin, margin)
        self.repaint()

class MessageWidget(QWidget):
    def __init__(self,text, left=True, color=None, text_color=None):
        super(MessageWidget,self).__init__()

        self.setContentsMargins(0,0,0,0)
        self.left = left

        hbox = QHBoxLayout()
        self.bubble = MessageBubble(text, color, text_color, border_radius=10)

        if not self.left:
            hbox.addSpacerItem(QSpacerItem(1,1,QSizePolicy.Expanding,QSizePolicy.Preferred))
        hbox.addWidget(self.bubble)
        if self.left:
            hbox.addSpacerItem(QSpacerItem(1,1,QSizePolicy.Expanding,QSizePolicy.Preferred))
        hbox.setContentsMargins(0,0,0,0)
        self.setLayout(hbox)
        self.setStyleSheet("""
            .QWidget{
                border: 5px solid blue;
                background-color: yellow;
            }
        """)

    def updateBubble(self, left=None, color=None, text_color=None, border_radius=None):
        if left:
            self.left = left
        self.bubble.updateBubble(color, text_color, border_radius)

class ChatWidget(QWidget):
    def __init__(self, parent, messages_list=None,
                 left_id=None, left_color=None, left_text_color=None,
                 right_id=None, right_color=None,  right_text_color=None,
                 chat_box_enabled=True,
                 controls_enabled=True):
        super(ChatWidget, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.controls_enabled = controls_enabled
        if self.controls_enabled:
            self.setControls()

        self.scroll_area = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)

        self.main_layout.addWidget(self.scroll_area)

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_widget.setLayout(self.chat_layout)
        self.scroll_area.setWidget(self.chat_widget)

        self.chat_box_enabled = chat_box_enabled
        if chat_box_enabled:
            self.set_chat_box()

        self.parent = parent
        self.app = parent.app
        self.config = self.parent.app.config
        self.config_file = self.parent.app.config_file
        self.statusBar = self.parent.statusBar

        # if left_color is not None and not isinstance(left_color, str):
        #     left_color = left_color.name()
        # if left_text_color is not None and not isinstance(left_text_color, str):
        #     left_text_color = left_text_color.name()
        # if right_color is not None and not isinstance(right_color, str):
        #     right_color = right_color.name()
        # if right_text_color is not None and not isinstance(right_text_color, str):
        #     right_text_color = right_text_color.name()

        self.left_id = left_id
        self.left_color = left_color
        self.left_text_color = left_text_color
        self.right_id = right_id
        self.right_color = right_color
        self.right_text_color = right_text_color

        # self.addMessages(messages_list)

    def clearMessages(self):
        for i in reversed(range(self.chat_layout.count())):
            widgetToRemove = self.chat_layout.itemAt(i).widget()
            # remove it from the layout list
            self.chat_layout.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)

    def addMessage(self, text, left=False, color=None, text_color=None):
        # if left:
        #     log.d("CHAT", "Adding left " + str(color) +" Message: " +text)
        # else:
        #     log.d("CHAT", "Adding right " + str(color) +" Message: " +text)
        self.chat_layout.addWidget(MessageWidget(text, left, color, text_color))

    def setLeftId(self, id):
        self.left_id = id
    def setLeftColor(self, color):
        self.left_color = color
    def setLeftTextColor(self, color):
        self.left_text_color = color
    def setrightId(self, id):
        self.right_id = id
    def setrightColor(self, color):
        self.right_color = color
    def setrightTextColor(self, color):
        self.right_text_color = color

    def addMessages(self, messages_list, clear_messages=True,
                    new_left_id=None, new_left_color=None, new_left_text_color=None,
                    new_right_id=None, new_right_color=None, new_right_text_color=None):
        right_id = None
        left_id = None
        right_color = None
        left_color = None
        right_text_color = None
        left_text_color = None
        if clear_messages:
            self.clearMessages()
        if messages_list is not None:
            for message in reversed(messages_list):
                if isinstance(message, str):
                    self.addMessage(message)
                elif isinstance(message, dict):

                    # If we haven't set the ids yet (only for the first message)
                    # order of ids: new_id -> self.id -> message_to/from
                    if right_id is None and left_id is None:
                        # log.d("CHAT2", "new_left_id " + str(new_left_id) + "\tself.left_id " + str(self.left_id))
                        # log.d("CHAT2", "new_right_id " + str(new_right_id) + "\tself.right_id " + str(self.right_id))
                        # log.d("CHAT2", "new_left_color " + str(new_left_color) + "\tself.left_color " + str(self.left_color))
                        # log.d("CHAT2", "new_right_color " + str(new_right_color) + "\tself.right_color " + str(self.right_color))
                        # log.d("CHAT2", "new_left_text_color " + str(new_left_text_color) + "\tself.left_text_color " + str(self.left_text_color))
                        # log.d("CHAT2", "new_right_text_color " + str(new_right_text_color) + "\tself.right_text_color " + str(self.right_text_color))
                        right_id = new_right_id
                        if right_id is None:
                            right_id = self.right_id
                        left_id = new_left_id
                        if new_left_id is None:  # if there is no new left id
                            left_id = self.left_id
                        # if one of the two is still None then we have to decide the other id
                        right_id, left_id = self.get_other_id(right_id, left_id, message['to'], message['from'])

                        right_color = self.get_final_color(new_right_color, self.right_color)
                        left_color = self.get_final_color(new_left_color, self.left_color)
                        right_text_color = self.get_final_color(new_right_text_color, self.right_text_color)
                        left_text_color = self.get_final_color(new_left_text_color, self.left_text_color)

                        # log.d("CHAT", "")
                        # log.d("CHAT2", "left_id " + str(left_id))
                        # log.d("CHAT2", "right_id " + str(right_id))
                        # log.d("CHAT2", "left_color " + str(left_color))
                        # log.d("CHAT2", "right_color " + str(right_color))
                        # log.d("CHAT2", "left_text_color " + str(left_text_color))
                        # log.d("CHAT2", "right_text_color " + str(right_text_color))

                    if str(message['from']) in right_id:
                        self.addMessage(message['message'], left=True, color=left_color, text_color=left_text_color)
                    else:
                        self.addMessage(message['message'], left=False, color=right_color, text_color=right_text_color)

    def get_other_id(self, left_id, right_id, to_id, from_id):
        # So the first person to send a message will be the one on the left
        if right_id is None and left_id is not None:
            if left_id == to_id:
                right_id = from_id
            else:
                right_id = to_id
        else:
            if right_id == to_id:
                left_id = from_id
            else:
                left_id = to_id
        return left_id, right_id

    def get_final_color(self, first_color, second_color):
        final_color = first_color
        if final_color is None:
            final_color = second_color
        return final_color
    
    def setControls(self):
        self.controls_layout = QHBoxLayout()

        self.radius_slider_label = QLabel("Border Radius")

        self.radius_slider = QSlider(Qt.Horizontal)
        self.radius_slider.setRange(0, 100)
        self.radius_slider.valueChanged.connect(self.update_chat)

        # self.left_color_selector_label = QLabel()
        # self.left_color_selector_label.setAutoFillBackground(True)
        # self.left_color_selector_label.setFixedSize(100, 100)

        self.left_color_selector_button = QPushButton("Left Color")
        self.left_color_selector_button.clicked.connect(self.pick_left_color)

        # self.right_color_selector_label = QLabel()
        # self.right_color_selector_label.setAutoFillBackground(True)
        # self.right_color_selector_label.setFixedSize(100, 100)

        self.right_color_selector_button = QPushButton("Right Color")
        self.right_color_selector_button.clicked.connect(self.pick_right_color)

        self.controls_layout.addWidget(self.radius_slider_label)
        self.controls_layout.addWidget(self.radius_slider)

        # self.controls_layout.addWidget(self.left_color_selector_label)
        self.controls_layout.addWidget(self.left_color_selector_button)

        # self.controls_layout.addWidget(self.right_color_selector_label)
        self.controls_layout.addWidget(self.right_color_selector_button)

        self.main_layout.addLayout(self.controls_layout)

    def pick_left_color(self):
        self.color_chooser = QColorDialog()
        # self.color_chooser.currentColorChanged()
        self.color_chooser.currentColorChanged.connect(self.left_color_picked)
        self.color_chooser.show()
        # self.left_color_picked(QColorDialog().getColor())

    def left_color_picked(self, color):
        if color.isValid():
            # palette = self.left_color_selector_label.palette()
            # palette.setColor(QPalette.Background, color)
            # self.left_color_selector_label.setPalette(palette)
            self.left_color = color
            self.update_chat()

    def pick_right_color(self):
        self.color_chooser = QColorDialog()
        self.color_chooser.currentColorChanged.connect(self.right_color_picked)
        self.color_chooser.show()
        # self.right_color_picked(QColorDialog().getColor())

    def right_color_picked(self, color):
        if color.isValid():
            # palette = self.right_color_selector_label.palette()
            # palette.setColor(QPalette.Background, color)
            # self.right_color_selector_label.setPalette(palette)
            self.right_color = color
            self.update_chat()

    def update_chat(self):
        items = (self.chat_layout.itemAt(i) for i in range(self.chat_layout.count()))
        for w in items:
            if type(w.widget()) == MessageWidget:
                if w.widget().left:
                    w.widget().updateBubble(color=self.left_color,border_radius=int(self.radius_slider.value()))
                else:
                    w.widget().updateBubble(color=self.right_color, border_radius=int(self.radius_slider.value()))

    def set_chat_box(self):
        self.chat_box = QTextEdit()
        self.chat_box.setMaximumHeight(50)
        self.chat_box.setPlaceholderText("Write your message...")
        self.chat_box.installEventFilter(self)
        self.main_layout.addWidget(self.chat_box)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and obj is self.chat_box:
            if event.key() == Qt.Key_Return and self.chat_box.hasFocus():
                self.send_message()
        return super().eventFilter(obj, event)
    def send_message(self):
        text = self.chat_box.toPlainText()
        print("Sending: " +text)
        self.addMessage(text, left=True, color=self.left_color, text_color=self.left_text_color)
        self.chat_box.setText("")