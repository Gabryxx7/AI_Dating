from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import dateutil.parser

from GUI.rounded_poly import RoundedPolygon

class Side:
    left = "left"
    right = "right"
    center = "center"


"""
The message widget is a wrapper made of an hbox that adds a stretch to either left or right (or both) to position the bubble
"""
class MessageWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(MessageWidget,self).__init__()
        self.setContentsMargins(0,0,0,0)
        self.side = kwargs['side']

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
    def __init__(self, message=None, side=Side.left, color=None, text_color=None, font_size=10, border_radius=10, draw_triangle=True, triangle_pos=1):
        super(MessageBubble, self).__init__()

        self.side = side
        self.color = color
        self.text_color = text_color
        self.font_size = font_size
        self.border_radius = border_radius
        self.content_margins = border_radius * 0.3
        self.draw_triangle = draw_triangle
        self.triangle_pos = triangle_pos  # 0 Bottom, 1 Top
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
        self.text_label.setContentsMargins(0,0,0,0)
        self.text_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.text_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.text_label.setWordWrap(True)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.text_label)

        if self.sent_date:
            self.date_label = QLabel(self.sent_date.strftime("%H:%M"))
            newfont = QFont("Times", self.font_size*0.6)
            self.date_label.setFont(newfont)
            self.date_label.setStyleSheet("color: %s;" % (self.text_color))
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
        if self.side == Side.left or self.side == Side.center:
            p.drawRoundedRect(self.bubble_triangle_width, 0, self.width()-self.bubble_triangle_width-1, self.height()-1, self.border_radius, self.border_radius)
            width = 0+self.bubble_triangle_width+min_width
            self.setContentsMargins(self.content_margins + self.border_radius*0.4 + self.bubble_triangle_width,
                                self.content_margins + self.border_radius*0.5,
                                self.content_margins + self.border_radius*0.4,
                                self.content_margins + self.border_radius*0.5)
            if self.draw_triangle:
                if self.triangle_pos == 0: # bottom left
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
                # p.drawPolygon(points)
                p.drawPath(points.GetPath())
        elif self.side == Side.right:
            p.drawRoundedRect(0, 0, self.width()-self.bubble_triangle_width-1, self.height()-1, self.border_radius, self.border_radius)
            width = self.width()-self.bubble_triangle_width-min_width
            self.setContentsMargins(self.content_margins + self.border_radius*0.4,
                                    self.content_margins + self.border_radius*0.5,
                                    self.content_margins + self.border_radius*0.4 + self.bubble_triangle_width,
                                    self.content_margins + self.border_radius*0.5)
            if self.draw_triangle:
                if self.triangle_pos == 0: # bottom right
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
        super(MessageBubble, self).paintEvent(e)

    def updateBubble(self, side=None, color=None, text_color=None, font_size=None, border_radius=None, content_margins=None):
        if color:
            self.color = color
        if text_color:
            self.text_color = text_color
        if border_radius:
            self.border_radius = border_radius
        if font_size:
            self.font_size = font_size
        self.content_margins = border_radius * 0.3
        if content_margins is not None:
            self.content_margins = content_margins
        newfont = QFont("Times", self.font_size)
        self.text_label.setFont(newfont)
        self.repaint()
