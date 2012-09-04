# encoding: utf-8

import math

from PySide.QtCore import *
from PySide.QtGui import *

from dynamite.plots import DynamitePlot
from dynamite.plots import misc


class CoordinateAxesPlot(DynamitePlot):

    def __init__(self, *args, **kwargs):
        super(CoordinateAxesPlot, self).__init__(*args, **kwargs)
        self.settings = {'color': Qt.black,
                         'grid-color': QColor('#eeeeee'),
                         'show-lines': True,
                         'show-grid': True,
                         'show-labels': True,
                         'major-ticks': True,
                         'major-tick-length': 4.0,
                         'major-ticks-numbered': True,
                         'minor-ticks-per-major-tick': 3,
                         'minor-ticks': True,
                         'minor-tick-length': 2.0,
                         'minor-ticks-numbered': False,                    
                         'line-width': 1.0}
        self.priority = -1

    # TODO: make this more logical, follow Grapher's automatic axis handling
    def _calculateTickStep(self, transform):
        h = round((transform.view[1].x() - transform.view[0].x()) / 10.0, 5)
        i, d = divmod(h, 1)

        realStep = h

        if i > 0.0:
            realStep = round(h, 0)
        else:
            pass

        #realStep = realStep / (self.settings['minor-ticks-per-major-tick'] + 1.0)
        
        step = transform.pointToPixel(realStep, 0.0).x() - transform.pointToPixel(0.0, 0.0).x()
        step = step / (self.settings['minor-ticks-per-major-tick'] + 1.0)

        return step    

    def _paintTicks(self, p, transform, startX, startY, stepX, stepY):
        x = startX
        y = startY

        if not self.settings['major-ticks'] and not self.settings['minor-ticks']:
            return

        i = 0
        while (x >= 0.0 and x <= transform.width and y >= 0.0 and y <= transform.height):
            real_p = transform.pixelToPoint(x, y)
            tickWidth, tickHeight = 0, 0
            isMajor = (i % (self.settings['minor-ticks-per-major-tick'] + 1) == 0)

            if stepX != 0.0:
                tickWidth = 0.0
                tickHeight = self.settings['major-tick-length'] if isMajor else self.settings['minor-tick-length']
            else:
                tickWidth = self.settings['major-tick-length'] if isMajor else self.settings['minor-tick-length']
                tickHeight = 0.0

            if (isMajor and self.settings['major-ticks']) or (not isMajor and self.settings['minor-ticks']):
                if self.settings['show-grid']:
                    p.save()
                    p.setPen(QPen(self.settings['grid-color']))

                    if stepX != 0.0:
                        p.drawLine(x, 0.0, x, transform.height)
                    else:
                        p.drawLine(0.0, y, transform.width, y)

                    p.restore() 

                p.drawLine(QPointF(x - tickWidth / 2.0, y - tickHeight / 2.0), QPointF(x + tickWidth, y + tickHeight))

            if (isMajor and self.settings['major-ticks'] and self.settings['major-ticks-numbered']) or (not isMajor and self.settings['minor-ticks'] and self.settings['minor-ticks-numbered']):
                p.drawText(QPointF(x, y), u'%0.1lf' % (real_p.x() if stepX != 0.0 else real_p.y()))
            
            x += stepX
            y += stepY

            i += 1

    def paint(self, p, transform):
        orig = transform.pointToPixel(0.0, 0.0)

        step = self._calculateTickStep(transform)

        # TODO: y axis does not look as well as x axis (spacing does not coincide with expected values)
        # TODO: do not repaint origin 4 times
        self._paintTicks(p, transform, 0.0, orig.y(), step, 0.0) # x axis
        #self._paintTicks(p, transform, orig.x(), orig.y(), -step, 0.0) # x- axis
        self._paintTicks(p, transform, orig.x(), orig.y(), 0.0, -step) # y+ axis
        self._paintTicks(p, transform, orig.x(), orig.y(), 0.0, step) # y- axis

        if self.settings['show-lines']:
            p.drawLine(QPointF(orig.x(), 0.0), QPointF(orig.x(), transform.height))
            p.drawLine(QPointF(0.0, orig.y()), QPointF(transform.width, orig.y()))

            misc.drawArrow(p, transform.width - 10, orig.y(), color=self.settings['color'], lineWidth=self.settings['line-width']) # x axis arrow
            misc.drawArrow(p, orig.x(), 8, incl=math.pi/2.0, color=self.settings['color'], lineWidth=self.settings['line-width']) # y axis arrow        

