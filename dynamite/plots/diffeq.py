# encoding: utf-8

import math

from PySide.QtCore import *
from PySide.QtGui import *

from dynamite.plots import DynamitePlot
from dynamite.core.integrators import RungeKutta4


class OrbitPlot(DynamitePlot):
    
    def __init__(self, system, point):
        super(OrbitPlot, self).__init__()
        self._system = system
        self._initialPoint = point
        self._data = []

        self.priority = 10

        self._solve()

    def _solve(self):
        # solve the PVI
        self._data = RungeKutta4.solve(self._system, self._initialPoint.x(), self._initialPoint.y(), 0.0, 400)

    def paint(self, painter, transform):
        path = QPainterPath()

        ppixel = transform.pointToPixel(self._data[0])
        for point in self._data:
            pixel = transform.pointToPixel(point)

            path.moveTo(ppixel)
            path.lineTo(pixel)

            ppixel = pixel

        painter.drawPath(path)

    def initialPoint(self):
        return self._initialPoint

    def __str__(self):
        return '(x,y) = (%0.2lf, %0.2lf)' % (self._initialPoint.x(), self._initialPoint.y())

    # def formula(self):
    #     return u'{dx/dt = %s, dy/dt = %s, x0 = %s, y0 = %s}' % (self._system.formula(), )


class SlopeField(DynamitePlot):

    def __init__(self, system):
        super(SlopeField, self).__init__()
        self._system = system

        self.settings['color'] = Qt.green
        self.settings['density'] = 15.0
        self.settings['line-width'] = 0.9

        self.priority = 5

    def paint(self, painter, transform):
        xstep = transform.width / self.settings['density']
        ystep = transform.height / self.settings['density']

        p1 = transform.pixelToPoint(xstep, ystep)
        p2 = transform.pixelToPoint(2 * xstep, 2 * ystep)
        a = p2.x() - p1.x()
        b = p2.y() - p1.y()

        N = math.sqrt(a*a + b*b)

        x = xstep
        while (x <= transform.width):
            y = ystep # reset y

            while (y <= transform.height):
                point = transform.pixelToPoint(x, y)
                L, M = self._system.evaluate(point.x(), point.y(), 0.0)
                Mod = 4.0 * math.sqrt(L*L + M*M)

                q1 = transform.pointToPixel(point.x() + L * N/Mod, point.y() + M * N / Mod)
                q2 = transform.pointToPixel(point.x(), point.y())

                painter.drawLine(q2.x(), q2.y(), q1.x(), q1.y())
                painter.drawPoint(q2)

                y = y + ystep
            x = x + xstep
        
    def getName(self):
        return '%s slope field' % self._system.getName()
