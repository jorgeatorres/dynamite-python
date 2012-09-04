# encoding: utf-8

import math

from PySide.QtCore import *
from PySide.QtGui import *


def drawArrow(painter, x, y, incl=0.0, dx=10, dy=8, color=Qt.black, lineWidth=1.0):
    incl = -incl

    painter.save()

    pen = QPen(color)
    pen.setWidth(lineWidth)
    painter.setPen(pen)
    painter.setBrush(QBrush(color, Qt.SolidPattern))
    
    # (x1,y1) *
    #         |
    # (x,y)   |-----* (x3,y3)
    #         |
    # (x2,y2) *

    x1, y1 = x - (dy/2.0)*math.cos(math.pi/2.0 - incl), y - (dy/2.0)*math.sin(math.pi/2.0 - incl)
    x2, y2 = x + (dy/2.0)*math.cos(math.pi/2.0 - incl), y + (dy/2.0)*math.sin(math.pi/2.0 - incl)
    x3, y3 = x + math.cos(incl)*dx, y + math.sin(incl)*dx

    # painter.drawLine(x, y, x1, y1)
    # painter.drawLine(x, y, x2, y2)
    # painter.drawLine(x, y, x3, y3)

    polygon = QPolygonF()
    polygon.append(QPointF(x, y))
    polygon.append(QPointF(x1, y1))
    polygon.append(QPointF(x3,y3))
    polygon.append(QPointF(x2,y2))
    painter.drawPolygon(polygon)

    painter.restore()