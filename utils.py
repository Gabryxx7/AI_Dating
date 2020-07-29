"""
https://www.geeksforgeeks.org/pyqt5-how-to-create-circular-image-from-any-image/
"""

# importing libraries
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from GUI.log import log
import os
import oyaml as yaml

# function to alter image
def mask_image(imgdata, imgtype='png', size=64):
    # Load image
    image = QImage.fromData(imgdata, imgtype)

    # convert image to 32-bit ARGB (adds an alpha
    # channel ie transparency factor):
    image.convertToFormat(QImage.Format_ARGB32)

    # Crop image to a square:
    imgsize = min(image.width(), image.height())
    rect = QRect(
        (image.width() - imgsize) / 2,
        (image.height() - imgsize) / 2,
        imgsize,
        imgsize,
    )

    image = image.copy(rect)

    # Create the output image with the same dimensions
    # and an alpha channel and make it completely transparent:
    out_img = QImage(imgsize, imgsize, QImage.Format_ARGB32)
    out_img.fill(Qt.transparent)

    # Create a texture brush and paint a circle
    # with the original image onto the output image:
    brush = QBrush(image)

    # Paint the output image
    painter = QPainter(out_img)
    painter.setBrush(brush)

    # Don't draw an outline
    painter.setPen(Qt.NoPen)

    # drawing circle
    painter.drawEllipse(0, 0, imgsize, imgsize)

    # closing painter event
    painter.end()

    # Convert the image to a pixmap and rescale it.
    pr = QWindow().devicePixelRatio()
    pm = QPixmap.fromImage(out_img)
    pm.setDevicePixelRatio(pr)
    size *= pr
    pm = pm.scaled(size, size, Qt.KeepAspectRatio,
                   Qt.SmoothTransformation)

    # return back the pixmap data
    return pm


error_code_to_message = dict([(200, "Everything went okay, and returned a result (if any)."),
                              (301, "The server is redirecting you to a different endpoint. This can happen when a company switches domain names, or an endpoint's name has changed."),
                              (400, "The server thinks you made a bad request. This can happen when you don't send the information the API requires to process your request, among other things."),
                              (401,"The server thinks you're not authenticated. This happens when you don't send the right credentials to access an API"),
                              (404, "The server didn't find the resource you tried to access."),
                              (503, "	Back-end server is at capacity.")
                              ])