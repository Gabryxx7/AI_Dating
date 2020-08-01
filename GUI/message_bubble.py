from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import dateutil.parser

from GUI.rounded_poly import RoundedPolygon

class Side:
    left = "left"
    right = "right"
    center = "center"
    top = "top"
    bottom = "bottom"

default_theme = {
    'left_color': "#2e7690",
    'left_text_color': "#FFFFFF",
    'right_color': "#1a323d",
    'right_text_color': "#FFFFFF",
    'sent_date_font_size': "5pt",
    'sent_date_text_color': "#CCCCCC",
    'font_size': "10pt",
    'day_color': "#AAAAAA",
    'day_text_color': "#FFFFFF",
    'day_font_size': "8pt",
    'border_radius': 10,
    'bg_color': "transparent",
    'draw_bubble_triangle': True,
    'bubble_triangle_pos': Side.top
}

"""
The message widget is a wrapper made of an hbox that adds a stretch to either left or right (or both) to position the bubble
"""
class MessageWidget(QWidget):
    # signal_shown = Signal(object)

    def copyBubble(self, otherBubble):
        self.bubble.message = otherBubble.message
        self.bubble.side = otherBubble.side
        self.bubble.text_color = otherBubble.text_color
        self.bubble.font_size = otherBubble.font_size
        self.bubble.sent_date_font_size = otherBubble.sent_date_font_size
        self.bubble.sent_date_text_color = otherBubble.sent_date_text_color
        self.bubble.border_radius = otherBubble.border_radius
        self.bubble.draw_bubble_triangle = otherBubble.draw_bubble_triangle
        self.bubble.bubble_triangle_pos = otherBubble.bubble_triangle_pos

    @staticmethod
    def fromMessageBubble(otherBubble):
        kwargs = {}
        kwargs['message'] = otherBubble.message
        kwargs['side'] = otherBubble.side
        kwargs['text_color'] = otherBubble.text_color
        kwargs['font_size'] = otherBubble.font_size
        kwargs['sent_date_font_size'] = otherBubble.sent_date_font_size
        kwargs['sent_date_text_color'] = otherBubble.sent_date_text_color
        kwargs['border_radius'] = otherBubble.border_radius
        kwargs['draw_bubble_triangle'] = otherBubble.draw_bubble_triangle
        kwargs['bubble_triangle_pos'] = otherBubble.bubble_triangle_pos
        return MessageWidget(**kwargs)

    # def showEvent(self, event):
    #     super(MessageWidget, self).showEvent(event)
    #     self.signal_shown.emit(self)

    def __init__(self, *args, **kwargs):
        super(MessageWidget,self).__init__()
        self.setContentsMargins(0,0,0,0)
        if 'side' in kwargs:
            self.side = kwargs['side']
        else:
            self.side = Side.center

        self.bubble = MessageBubble(*args, **kwargs)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)
        if self.side == Side.right or self.side == Side.center:
            hbox.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding))
        hbox.addWidget(self.bubble)
        if self.side == Side.left or self.side == Side.center:
            hbox.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setStyleSheet("background-color: transparent;")

        self.setLayout(hbox)

    def updateBubble(self, *args, **kwargs):
        self.bubble.updateBubble(*args, **kwargs)

"""
The bubble is the atualy widget which can hae multiple labels and stuff inside it but it's all painted with a bubble background
And the margins are set so that the content is never outside the bubble
"""
class MessageBubble(QWidget):
    def __init__(self, message=" ", side=Side.left,
                 color=default_theme['left_color'], text_color=default_theme['left_text_color'], font_size=default_theme['font_size'],
                 sent_date_font_size=default_theme['sent_date_font_size'], sent_date_text_color=default_theme['sent_date_text_color'],
                 border_radius=default_theme['border_radius'],
                 draw_bubble_triangle=default_theme['draw_bubble_triangle'], bubble_triangle_pos=default_theme['bubble_triangle_pos']):
        super(MessageBubble, self).__init__()

        self.side = side
        self.color = color
        self.text_color =text_color
        self.font_size = font_size
        self.sent_date_text_color = sent_date_text_color
        self.sent_date_font_size = sent_date_font_size
        self.border_radius = border_radius
        self.draw_bubble_triangle = draw_bubble_triangle
        self.bubble_triangle_pos = bubble_triangle_pos

        self.content_margins = border_radius * 0.3
        self.bubble_triangle_width = 20
        self.bubble_triangle_height = 20
        self.message = message
        if isinstance(message, dict):
            self.text = message['message']
            self.sent_date = dateutil.parser.isoparse(self.message['sent_date'])
        else:
            self.text = message
            self.sent_date = None

        self.text_label = QLabel(self.text)
        self.text_label.setStyleSheet("color: %s; font-size: %s;" % (self.text_label, self.font_size))
        self.text_label.setContentsMargins(0,0,0,0)
        self.text_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        if self.side != Side.center:
            self.text_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        else:
            self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.text_label)

        self.date_label = None
        if self.sent_date:
            self.date_label = QLabel(self.sent_date.strftime("%H:%M"))
            self.date_label.setStyleSheet("color: %s; font-size: %s;" % (self.sent_date_text_color, self.sent_date_font_size))
            self.date_label_layout = QHBoxLayout()
            self.date_label_layout.addStretch(1)
            self.date_label_layout.addWidget(self.date_label)
            self.layout.addLayout(self.date_label_layout)

        self.setLayout(self.layout)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing,True)
        p.setBackground(Qt.transparent)
        if self.color is not None:
            color = QColor(self.color)
            brush = QBrush(color)
            p.setBrush(brush)
            p.setPen(QPen(color, 0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        min_height = min(self.border_radius*0.6, self.height()*0.25) # This is how wide the side attached to the bubble should be
        min_width = min(self.border_radius, self.width()*0.5) # This is how long the side from the edge to teh bubble should be

        if self.side == Side.left:
            p.drawRoundedRect(self.bubble_triangle_width, 0, self.width()-self.bubble_triangle_width-1, self.height()-1, self.border_radius, self.border_radius)
            width = 0+self.bubble_triangle_width+min_width
            self.setContentsMargins(self.content_margins + self.border_radius*0.4 + self.bubble_triangle_width,
                                self.content_margins + self.border_radius*0.5,
                                self.content_margins + self.border_radius*0.4,
                                self.content_margins + self.border_radius*0.5)
            if self.draw_bubble_triangle and self.side != Side.center:
                if self.bubble_triangle_pos == Side.bottom: # bottom left
                    height = self.height() - self.bubble_triangle_height - min_height
                    points = RoundedPolygon([
                        QPoint(0, self.height()-self.border_radius*0.1),
                        QPoint(width, self.height()-self.border_radius*0.1),
                        QPoint(width, height)
                    ], radius=10)
                else: # top left
                    height = self.bubble_triangle_height + min_height
                    points = RoundedPolygon([
                        QPoint(0, 0),
                        QPoint(width, 0),
                        QPoint(width, height)
                    ], radius=10)
                # p.drawPolygon(points)  # Draw non-rounded corners polygon
                p.drawPath(points.GetPath())
        elif self.side == Side.right:
            p.drawRoundedRect(0, 0, self.width()-self.bubble_triangle_width-1, self.height()-1, self.border_radius, self.border_radius)
            width = self.width()-self.bubble_triangle_width-min_width
            self.setContentsMargins(self.content_margins + self.border_radius*0.4,
                                    self.content_margins + self.border_radius*0.5,
                                    self.content_margins + self.border_radius*0.4 + self.bubble_triangle_width,
                                    self.content_margins + self.border_radius*0.5)
            if self.draw_bubble_triangle and self.side != Side.center:
                if self.bubble_triangle_pos == Side.bottom: # bottom right
                    height = self.height()-self.bubble_triangle_height-min_height
                    points = RoundedPolygon([
                        QPoint(self.width(), self.height()-self.border_radius*0.1),
                        QPoint(width, self.height()-self.border_radius*0.1),
                        QPoint(width, height)
                    ], radius=10)
                else: # top right
                    height = self.bubble_triangle_height+min_height
                    points = RoundedPolygon([
                        QPoint(self.width(), 0),
                        QPoint(width, 0),
                        QPoint(width, height)
                    ], radius=10)
                # p.drawPolygon(points)
                p.drawPath(points.GetPath())
        else:
            p.drawRoundedRect(0, 0, self.width()-1, self.height()-1, self.border_radius*0.5, self.border_radius*0.5)
            self.setContentsMargins(self.content_margins*0.7,
                                    self.content_margins*0.9,
                                    self.content_margins*0.7,
                                    self.content_margins*0.9)
        super(MessageBubble, self).paintEvent(e)

    def updateBubble(self, color=None, text_color=None, font_size=None, border_radius=None, content_margins=None):
        if color is not None:
            self.color = color
        if text_color is not None:
            self.text_color = text_color
        if border_radius is not None:
            self.border_radius = border_radius
        if font_size is not None:
            self.font_size = font_size
        self.content_margins = border_radius * 0.3
        if content_margins is not None:
            self.content_margins = content_margins
        if self.date_label is not None:
            self.date_label.setStyleSheet("color: %s; font-size: %s;" % (self.sent_date_text_color, self.sent_date_font_size))
        self.text_label.setStyleSheet("color: %s; font-size: %s;" % (self.text_color, self.font_size))
        self.repaint()