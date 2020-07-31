from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from GUI.rounded_poly import RoundedPolygon

class Side:
    left = "left"
    right = "right"
    center = "center"

class MessageWidget(QWidget):
    def __init__(self,text, side=Side.left, color=None, text_color=None, font_size=10, border_radius=10, draw_triangle=True):
        super(MessageWidget,self).__init__()

        self.setContentsMargins(0,0,0,0)
        self.side = side
        self.color = color
        self.text_color = text_color
        self.font_size = font_size
        self.border_radius = border_radius
        self.draw_triangle = draw_triangle

        hbox = QHBoxLayout()
        self.bubble = MessageBubble(text, side, color=self.color, text_color=self.text_color,
                                    font_size=self.font_size, border_radius=self.border_radius, draw_triangle=self.draw_triangle)
        self.setStyleSheet("background-color: transparent;")

        if self.side == Side.right or self.side == Side.center:
            hbox.addSpacerItem(QSpacerItem(1,1,QSizePolicy.Expanding,QSizePolicy.Expanding))
        hbox.addWidget(self.bubble)
        if self.side == Side.left or self.side == Side.center:
            hbox.addSpacerItem(QSpacerItem(1,1,QSizePolicy.Expanding,QSizePolicy.Expanding))

        hbox.setContentsMargins(0,0,0,0)
        self.setLayout(hbox)

    def updateBubble(self, side=None, color=None, text_color=None, font_size=None, border_radius=None, content_margins=None):
        self.bubble.updateBubble(color, text_color, font_size, border_radius, content_margins)

class MessageBubble(QLabel):
    def __init__(self, text, side=Side.left, color=None, text_color=None, font_size=10, border_radius=10, draw_triangle=True, triangle_pos=1):
        super(MessageBubble,self).__init__(text)
        self.side = side
        self.color = color
        self.text_color = text_color
        self.font_size = font_size
        self.border_radius = border_radius
        self.content_margins = border_radius*0.3
        self.draw_triangle = draw_triangle
        self.triangle_pos = triangle_pos # 0 Bottom, 1 Top
        self.bubble_triangle_width = 20
        self.bubble_triangle_height = 20

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.setWordWrap(True)
        newfont = QFont("Times", self.font_size)
        self.setFont(newfont)
        self.setStyleSheet("color: %s;" % (self.text_color))

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

    def updateBubble(self, color=None, text_color=None, font_size=None, border_radius=None, content_margins=None):
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
        self.setFont(newfont)
        self.repaint()