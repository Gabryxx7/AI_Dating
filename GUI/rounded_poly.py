# https://www.toptal.com/c-plus-plus/rounded-corners-bezier-curves-qpainter

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

class RoundedPolygon(QPolygon):
    def __init__(self, *args, radius=10):
        super(RoundedPolygon, self).__init__(*args)
        self.radius = radius

    def setRadius(self, radius):
        self.radius = radius

    def GetLineStart(self, i):
        pt = QPointF()
        pt1 = self.at(i)
        pt2 = self.at((i+1) % self.count())
        fRat = self.radius / self.GetDistance(pt1, pt2);
        if fRat > 0.5:
            fRat = 0.5

        pt.setX((1.0-fRat) * pt1.x() + fRat * pt2.x())
        pt.setY((1.0-fRat) * pt1.y() + fRat * pt2.y())
        return pt

    def GetLineEnd(self, i):
        pt = QPointF()
        pt1 = self.at(i)
        pt2 = self.at((i + 1) % self.count())
        fRat = self.radius / self.GetDistance(pt1, pt2);
        if fRat > 0.5:
            fRat = 0.5

        pt.setX(fRat * pt1.x() + (1.0 - fRat) * pt2.x());
        pt.setY(fRat * pt1.y() + (1.0 - fRat) * pt2.y());
        return pt

    def GetDistance(self, pt1, pt2):
        fD = (pt1.x() - pt2.x())*(pt1.x() - pt2.x()) + (pt1.y() - pt2.y()) * (pt1.y() - pt2.y())
        return fD**0.5

    def GetPath(self):
        path = QPainterPath()

        if self.count() < 3:
            print("Polygon should have at least 3 points!")
            return
        pt1 = QPointF()
        pt2 = QPointF()

        for i in range(self.count()):
            pt1 = self.GetLineStart(i)
            if i == 0:
                path.moveTo(pt1)
            else:
                path.quadTo(self.at(i), pt1)
            pt2 = self.GetLineEnd(i)
            path.lineTo(pt2)
        pt1 = self.GetLineStart(0)
        path.quadTo(self.at(0), pt1)
        return path
