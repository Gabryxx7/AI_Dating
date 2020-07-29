from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import utils
from GUI.log import log

class AvatarLabel(QLabel):
    def __init__(self, image_path, size, antialiasing=True):
        super(AvatarLabel, self).__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMaximumSize(size)
        self.setMinimumSize(size)
        self.antialiasing = antialiasing
        self.image_path = image_path

        self.target = None
        self.pixmap = None

        # self.setPicture(self.image_path, size)

        # log.d("AVATAR", "Image used: " +str(self.image_path))

    def resizeEvent(self, e):
        # self.update_avatar_size(self.size())
        super(AvatarLabel, self).resizeEvent(e)  # Do the default action on the parent class QLineEdit

    def setPicturePath(self, image_path, size=None):
        image = QImage(image_path)
        self.setPicturePixmap(QPixmap.fromImage(image))

    def setPicturePixmap(self, pixmap):
        self.pixmap = pixmap
        self.target = QPixmap(self.size())
        self.target.fill(Qt.transparent)
        self.update_avatar_size(self.size())

    def update_avatar_size(self, size):
        painter = QPainter(self.target)
        if self.antialiasing:
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # So the picture is always on the top-left corner
        # If it's vertical and we clip a circle, the right side might end up straight since the pic is too small and does not fill the square
        # So we zoom in the picture by a 1.25x factor to make sure it fills the square box
        p_scaled = self.pixmap.scaledToHeight(size.height()*1.3, Qt.SmoothTransformation)
        path = QPainterPath()
        self.radius = min(size.width(), size.height())*0.5
        # And then we crop it as a circle shape.
        # The radius has to be half the largest side, so we'll take the maximum of the height and width
        # And halve it to get the proper radius!
        # Instead of starting from 0,0 at the top-left I am starting at a 0.05xsize so a bit offset
        # This is to center the circle in the middle of the square
        path.addRoundedRect(size.width()*0.05, size.height()*0.05, size.width()*0.9, size.height()*0.9, self.radius, self.radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, p_scaled)
        self.setPixmap(self.target)
        self.repaint()
        # log.d("Avatar", "Resized! " +str(size.width()) + " " + str(size.height()))