# encoding: utf-8

from PySide.QtCore import *
from PySide.QtGui import *

from dynamite.plots import DynamitePlot
from dynamite.plots.basic import CoordinateAxesPlot


class DynamiteView(QWidget):

    DEFAULT_SETTINGS = {'show-grid': True,
                        'show-axes': True,
                        'axes-width': 1.1,
                        'axes-color': Qt.black,
                        'axes-tick-length': 2.0,
                        'axes-tick-spacing': 5.0}

    # signals
    viewChanged = Signal()
    plotAdded = Signal(DynamitePlot)
    plotChanged = Signal(DynamitePlot)
    plotRemoved = Signal(DynamitePlot)

    selectionChanged = Signal(list, list)


    def __init__(self, *args, **kwargs):
        super(DynamiteView, self).__init__(*args, **kwargs)

        self._settings = dict(self.DEFAULT_SETTINGS)

        self._width = 0.0
        self._height = 0.0

        self._view = [QPointF(-5.0, -3.0), QPointF(5.0, 3.0)] # [(x0,y0), (x1,y1)]
        self._origin = QPoint(0.0, 0.0)

        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        self.setAttribute(Qt.WA_OpaquePaintEvent)
        #self.setAttribute(Qt.WA_NoSystemBackground)

        self.setFocusPolicy(Qt.ClickFocus)


        self._plots = []
        self.add(CoordinateAxesPlot())

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, view):
        self._view = list(view)
        self.viewChanged.emit()
        self.repaint()

    def focusInEvent(self, event):
        super(DynamiteView, self).focusInEvent(event)
        self.setSelectedPlot(None)

    # handle resize events
    def resizeEvent(self, event):
        self._width = event.size().width()
        self._height = event.size().height()
        super(DynamiteView, self).resizeEvent(event)

    # paint event
    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(QRectF(0, 0, self._width, self._height), Qt.white)

        p.setRenderHint(QPainter.Antialiasing, True)            

        selectedPlots = self.selectedPlots()

        # plots are painted according to their priority
        coordTransform = CoordinateTransform(self._view, self._width, self._height)
        for i, plot in enumerate(sorted(self._plots, key=lambda x : x.priority)):
            if plot.enabled:
                    p.save()

                    pen = QPen()
                    color = QColor(plot.settings['color'])
                    
                    if selectedPlots and plot not in selectedPlots and i != 0:
                        color.setAlphaF(0.5)

                    pen.setColor(color)
                    pen.setWidth(plot.settings['line-width'])
                    p.setPen(pen)

                    plot.paint(p, coordTransform)
                    p.restore()


        if self.hasFocus():
            pass
            # p.setRenderHint(QPainter.Antialiasing, False)
            # p.drawRect(0, 0, self._width - 1, self._height - 1)
        else:
            pass

    def plots(self):
        return self._plots

    def selectedPlots(self):
        return [x for x in self._plots if x.selected]

    def setSelectedPlot(self, selectedPlot):
        for plot in self._plots:
            if selectedPlot is None or plot != selectedPlot:
                plot.selected = False
            else:
                plot.selected = True

    def getAxesPlot(self):
        return self._plots[0]

    def add(self, plot):
        if plot not in self._plots:
            self._plots.append(plot)
            plot.plotSelectionChanged.connect(self._selectionChanged)
            plot.plotChanged.connect(self.repaint)
            
            self.plotAdded.emit(plot)

        self.viewChanged.emit()
        self.repaint()

    def _selectionChanged(self):
        if self.sender() != self._plots[0]:
            self.selectionChanged.emit([x for x in self._plots if x.selected], [x for x in self._plots if not x.selected])
        else:
            self.selectionChanged.emit([], [x for x in self._plots if not x.selected and x != self._plots[0]])
        
        self.viewChanged.emit()
        self.repaint()

    def remove(self, plot):
        if plot in self._plots:
            self._plots.remove(plot)
            self.plotRemoved.emit(plot)

            self.viewChanged.emit()
            self.repaint()

            return plot
        return None

    def zoomIn(self, factor=1.1):
        return self.zoom(1.0 / factor)

    def zoomOut(self, factor=1.1):
        return self.zoom(factor)

    def zoom(self, factor=1.0, position=None):
        viewWidth = self._view[1].x() - self._view[0].x()
        viewHeight = self._view[1].y() - self._view[0].y()
        viewCenterX = self._view[0].x() + viewWidth / 2.0
        viewCenterY = self._view[0].y() + viewHeight / 2.0

        viewWidth *= factor
        viewHeight *= factor

        self._view[0].setX(viewCenterX - viewWidth / 2.0)
        self._view[1].setX(viewCenterX + (viewWidth / 2.0))
        self._view[0].setY(viewCenterY - viewHeight / 2.0)
        self._view[1].setY(viewCenterY + (viewHeight / 2.0))

        self.repaint()


class CoordinateTransform(object):
    
    def __init__(self, view, screenWidth, screenHeight):
        self.view = view
        self.width = screenWidth
        self.height = screenHeight

    def pointToPixel(self, *args):
        if (len(args) >= 2):
            return self.pointToPixel(QPointF(args[0], args[1]))

        qpoint = args[0]

        x = (qpoint.x() - self.view[0].x()) * ( self.width / (self.view[1].x() - self.view[0].x()) )
        y = self.height - ((qpoint.y() - self.view[0].y()) * (self.height / (self.view[1].y() - self.view[0].y()) ))
        return QPointF(x, y)

    def pixelToPoint(self, *args):
        if len(args) >= 2:
            return self.pixelToPoint(QPointF(args[0], args[1]))

        point = args[0]

        originPixel = self.pointToPixel(0.0, 0.0)
        # Point2D originPixel = pointToPixel(origin);

        #print repr(point)

        x = (point.x() - originPixel.x()) * ( (self.view[1].x() - self.view[0].x()) / self.width )
        y = (self.height - point.y() - originPixel.y()) * ( (self.view[1].y() - self.view[0].y()) / self.height )

        # Point2D.Double res = new Point2D.Double();
        # res.x = (src.getX() - originPixel.getX()) * (this.view.width / this.width);
        # res.y = (this.height - src.getY() - originPixel.getY()) * (this.view.height / this.height);
        
        # return res;        

        return QPointF(x, y)

    # private void paintCursorPosition(Graphics2D g) {
    #     if (cursorPosition == null)
    #         return;
        
    #     Point2D cursorCoords = pixelToPoint(cursorPosition);        
        
    #     g.setColor(Color.GRAY);
    #     g.drawString(String.format("(%.2f, %.2f)", cursorCoords.getX(), cursorCoords.getY()),
    #                  (int) cursorPosition.getX(), (int) cursorPosition.getY());
        
    # }
    
  
    # private void paintGrid(Graphics2D g) {
    #     int startY = (int) Math.floor(this.view.y / this.gridDY);
    #     int endY = (int) Math.floor((this.view.y + this.view.height) / this.gridDY);
        
    #     // Horizontal lines
    #     g.setColor(Color.LIGHT_GRAY);
        
    #     GeneralPath gp = new GeneralPath();
        
    #     for (int k = startY; k <= endY; k++) {
    #         Point2D pos = pointToPixel(0.0, k * this.gridDY);
            
    #         gp.moveTo(0.0, pos.getY());
    #         gp.lineTo(this.width, pos.getY());
    #         gp.closePath();
    #     }
    #     g.draw(gp);
        
    #     int startX = (int) (Math.floor(this.view.x / this.gridDX));
    #     int endX = (int) (Math.floor( (this.view.x + this.view.width) / this.gridDX));
        
    #     GeneralPath gp2 = new GeneralPath();
    #     for (int k = startX; k <= endX; k++) {
    #         Point2D pos = pointToPixel(k * this.gridDX, 0.0);
            
    #         gp2.moveTo(pos.getX(), 0.0);
    #         gp2.lineTo(pos.getX(), this.height);
    #         gp2.closePath();   
    #     }
    #     g.draw(gp2);
    # }