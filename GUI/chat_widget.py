from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from GUI.message_bubble import MessageWidget, default_theme, Side
from datetime import datetime
import dateutil.parser
import os
import oyaml as yaml


class ChatWidget(QWidget):
    def __init__(self, parent, messages_list=None, theme=None,
                 left_id=None, right_id=None,
                 chat_box_enabled=True, controls_enabled=True):
        super(ChatWidget, self).__init__(parent)
        self.theme_data = {}
        print("Theme data1 is" +str(theme))
        if isinstance(theme, str):
            try:
                with open(theme, "r") as tf:
                    self.theme_data = yaml.safe_load(tf)
                    print("Theme data is" +str(self.theme_data))
            except Exception as e:
                print("Exception reading theme file: " +str(e))
                pass
        elif isinstance(theme, dict):
            self.theme_data = theme
        if self.theme_data is None:
            self.theme_data = default_theme
        else:
            for key in default_theme.keys():
                if key not in self.theme_data:
                    self.theme_data[key] = default_theme[key]

        self.left_color = self.theme_data['left_color']
        self.left_text_color = self.theme_data['left_text_color']
        self.right_color = self.theme_data['right_color']
        self.right_text_color = self.theme_data['right_text_color']
        self.sent_date_font_size = self.theme_data['sent_date_font_size']
        self.sent_date_text_color = self.theme_data['sent_date_text_color']
        self.font_size = self.theme_data['font_size']
        self.day_color = self.theme_data['day_color']
        self.day_text_color = self.theme_data['day_text_color']
        self.day_font_size = self.theme_data['day_font_size']
        self.border_radius = self.theme_data['border_radius']
        self.bg_color = self.theme_data['bg_color']
        self.draw_bubble_triangle = self.theme_data['draw_bubble_triangle']
        self.bubble_triangle_pos = self.theme_data['bubble_triangle_pos']

        self.left_id = left_id
        self.right_id = right_id

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

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.addStretch(1)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_widget.setLayout(self.chat_layout)
        self.scroll_area.setWidget(self.chat_widget)
        self.main_layout.addWidget(self.scroll_area)

        self.showing_date_layout = QVBoxLayout(self.chat_widget)
        self.showing_date = MessageWidget(self.chat_widget, "Date")
        self.showing_date.setVisible(False)
        self.showing_date_layout.addWidget(self.showing_date)
        self.chat_layout.addLayout(self.showing_date_layout)

        if self.bg_color:
            self.chat_widget.setStyleSheet("background-color: %s;" % (self.bg_color))

        self.chat_box_enabled = chat_box_enabled
        if chat_box_enabled:
            self.set_chat_box()

        self.parent = parent
        self.app = parent.app
        self.config = self.parent.app.config
        self.config_file = self.parent.app.config_file
        self.statusBar = self.parent.statusBar

    def clearMessages(self):
        for i in reversed(range(self.chat_layout.count())):
            widgetToRemove = self.chat_layout.itemAt(i).widget()
            if isinstance(widgetToRemove, MessageWidget):
                # remove it from the layout list
                self.chat_layout.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)
            # else it might be the addStretch and we don't want to remove it

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

    def addBubble(self, message=None, side=Side.left,
                    left_color=None, left_text_color=None,
                    right_color=None, right_text_color=None,
                    sent_date_font_size=None, sent_date_text_color=None,
                    day_color=None, day_text_color=None, day_font_size=None,
                    bg_color=None, font_size=None,
                    border_radius=None,
                    draw_bubble_triangle=None, bubble_triangle_pos=None):

        # Precedence: new_value > self.value
        left_color = self.get_final_value(left_color, self.left_color)
        left_text_color = self.get_final_value(left_text_color, self.left_text_color)
        right_color = self.get_final_value(right_color, self.right_color)
        right_text_color = self.get_final_value(right_text_color, self.right_text_color)
        sent_date_font_size = self.get_final_value(sent_date_font_size, self.sent_date_font_size)
        sent_date_text_color = self.get_final_value(sent_date_text_color, self.sent_date_text_color)
        day_color = self.get_final_value(day_color, self.day_color)
        day_text_color = self.get_final_value(day_text_color, self.day_text_color)
        day_font_size = self.get_final_value(day_font_size, self.day_font_size)
        bg_color = self.get_final_value(bg_color, self.bg_color)
        draw_bubble_triangle = self.get_final_value(draw_bubble_triangle, self.draw_bubble_triangle)
        bubble_triangle_pos = self.get_final_value(bubble_triangle_pos, self.bubble_triangle_pos)
        font_size = self.get_final_value(font_size, self.font_size)
        border_radius = self.get_final_value(border_radius, self.border_radius)

        if side == Side.left:
            color = left_color
            text_color = left_text_color
        elif side == Side.right:
            color = right_color
            text_color = right_text_color
        else:
            color = day_color
            text_color = day_text_color

        message_widget = MessageWidget(message=message, side=side,
                 color=color, text_color=text_color, font_size=font_size,
                 sent_date_font_size=sent_date_font_size, sent_date_text_color=sent_date_text_color,
                 border_radius=border_radius,
                 draw_bubble_triangle=draw_bubble_triangle, bubble_triangle_pos=bubble_triangle_pos)
        # if side == Side.center:
        #     message_widget.signal_shown.connect(self.message_visible)
        self.chat_layout.addWidget(message_widget)

    def wheelEvent(self, event):
        widget = None
        for i in range(self.chat_layout.count()):
            item = self.chat_layout.itemAt(i)
            if type(item.widget()) == MessageWidget:
                if item.widget().side == Side.center and not item.widget().visibleRegion().isEmpty():
                    widget = item.widget()
        if widget is not None and  widget.bubble.message != self.showing_date.bubble.message:
            self.showing_date.copyBubble(widget.bubble)
            self.showing_date.adjustSize()
            self.showing_date.repaint()
            print("Showing " + str(widget.bubble.message))
        event.ignore()

    def addMessages(self, messages_list, clear_messages=True, left_id=None, right_id=None,
                    left_color=None, left_text_color=None,
                    right_color=None, right_text_color=None,
                    sent_date_font_size=None, sent_date_text_color=None,
                    day_color=None, day_text_color=None, day_font_size=None,
                    bg_color=None, font_size=None,
                    border_radius=None,
                    draw_bubble_triangle=None, bubble_triangle_pos=None):
        if clear_messages:
            self.clearMessages()
        if messages_list is not None:
            date=None
            side=None
            bubble_triangle_pos = self.get_final_value(bubble_triangle_pos, self.bubble_triangle_pos)
            for i in reversed(range(len(messages_list))):
                message = messages_list[i]
                if isinstance(message, dict):
                    # If we haven't set the ids yet (only for the first message)
                    # order of ids: new_id -> self.id -> message_to/from
                    if right_id is None and left_id is None:
                        right_id = self.get_final_value(right_id, self.right_id)
                        left_id = self.get_final_value(left_id, self.left_id)
                        # if one of the two is still None then we have to decide the other id
                        right_id, left_id = self.get_other_id(right_id, left_id, message['to'], message['from'])

                    new_date = dateutil.parser.isoparse(message['sent_date'])
                    if date is None or date.date() < new_date.date():
                        date = new_date
                        self.addBubble(date.strftime("%d %B %Y"), Side.center,
                                       left_color, left_text_color,
                                       right_color, right_text_color,
                                       sent_date_font_size, sent_date_text_color,
                                       day_color, day_text_color, day_font_size,
                                       bg_color, font_size,
                                       border_radius,
                                       draw_bubble_triangle, bubble_triangle_pos)

                    new_side = Side.right
                    if str(message['from']) in right_id:
                        new_side = Side.left

                    if bubble_triangle_pos == Side.top:
                        new_draw_bubble_triangle = (new_side != side) and draw_bubble_triangle
                    else:
                        new_draw_bubble_triangle = draw_bubble_triangle # If it's the last message and at the bottom, draw the triangle
                        if i+1 <= len(messages_list)-1:
                            next_side = Side.right
                            if str(messages_list[i+1]['from']) in right_id:
                                next_side = Side.left
                            new_draw_bubble_triangle = (next_side != new_side) and draw_bubble_triangle
                    side = new_side

                    self.addBubble(message, side,
                                   left_color, left_text_color,
                                   right_color, right_text_color,
                                   sent_date_font_size, sent_date_text_color,
                                   day_color, day_text_color, day_font_size,
                                   bg_color, font_size,
                                   border_radius,
                                   new_draw_bubble_triangle, bubble_triangle_pos)

            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

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

    def get_final_value(self, overriding_value, original_value):
        if overriding_value is None:
            return original_value
        return overriding_value
    
    def setControls(self):
        self.radius_slider_label = QLabel("Radius")
        self.radius_slider = QSlider(Qt.Horizontal)
        self.radius_slider.setRange(0, 100)
        self.radius_slider.valueChanged.connect(self.update_chat)

        self.font_size_slider_label = QLabel("Size")
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(5, 30)
        self.font_size_slider.valueChanged.connect(self.update_chat)

        self.content_margins_slider_label = QLabel("Padding")
        self.content_margins_slider = QSlider(Qt.Horizontal)
        self.content_margins_slider.setRange(0, 30)
        self.content_margins_slider.valueChanged.connect(self.update_chat)

        # self.left_color_selector_label = QLabel()
        # self.left_color_selector_label.setAutoFillBackground(True)
        # self.left_color_selector_label.setFixedSize(100, 100)

        self.left_color_selector_button = QPushButton("Left")
        self.left_color_selector_button.clicked.connect(self.pick_left_color)

        # self.right_color_selector_label = QLabel()
        # self.right_color_selector_label.setAutoFillBackground(True)
        # self.right_color_selector_label.setFixedSize(100, 100)

        self.right_color_selector_button = QPushButton("Right")
        self.right_color_selector_button.clicked.connect(self.pick_right_color)

        self.bg_color_selector_button = QPushButton("Background")
        self.bg_color_selector_button.clicked.connect(self.pick_bg_color)

        self.sliders_layout = QHBoxLayout()
        self.sliders_layout.addWidget(self.radius_slider_label)
        self.sliders_layout.addWidget(self.radius_slider)
        self.sliders_layout.addWidget(self.font_size_slider_label)
        self.sliders_layout.addWidget(self.font_size_slider)
        self.sliders_layout.addWidget(self.content_margins_slider_label)
        self.sliders_layout.addWidget(self.content_margins_slider)

        self.colors_layout = QHBoxLayout()
        # self.colors_layout.addWidget(self.left_color_selector_label)
        self.colors_layout.addWidget(self.left_color_selector_button)
        # self.colors_layout.addWidget(self.right_color_selector_label)
        self.colors_layout.addWidget(self.right_color_selector_button)
        # self.colors_layout.addWidget(self.bg_color_selector_button_label)
        self.colors_layout.addWidget(self.bg_color_selector_button)

        self.controls_layout = QVBoxLayout()
        self.controls_layout.addLayout(self.sliders_layout)
        self.controls_layout.addLayout(self.colors_layout)

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
            self.left_color = color.name()
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
            self.right_color = color.name()
            self.update_chat()

    def pick_bg_color(self):
        self.color_chooser = QColorDialog()
        self.color_chooser.currentColorChanged.connect(self.bg_color_picked)
        self.color_chooser.show()

    def bg_color_picked(self, color):
        if color.isValid():
            self.bg_color = color.name()
            self.update_chat()

    def update_chat(self):
        self.font_size = str(self.font_size_slider.value())+"pt"
        self.font_size_slider_label.setText("Size " + str(self.font_size_slider.value()) +"pt")
        self.border_radius = int(self.radius_slider.value())
        self.radius_slider_label.setText("Radius " + str(self.border_radius) +"px")
        self.content_margins = int(self.content_margins_slider.value())
        self.content_margins_slider_label.setText("Padding " + str(self.content_margins) +"px")
        self.chat_widget.setStyleSheet("background-color: %s;" % (self.bg_color))
        self.scroll_area.setStyleSheet("background-color: transparent;")
        items = (self.chat_layout.itemAt(i) for i in range(self.chat_layout.count()))
        for w in items:
            if type(w.widget()) == MessageWidget:
                if w.widget().side == Side.left:
                    w.widget().updateBubble(color=self.left_color, font_size=self.font_size, border_radius=self.border_radius, content_margins=self.content_margins)
                else:
                    w.widget().updateBubble(color=self.right_color, font_size=self.font_size,  border_radius=self.border_radius, content_margins=self.content_margins)
        self.repaint()

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
        self.addBubble(text, side=Side.left)
        self.chat_box.setText("")