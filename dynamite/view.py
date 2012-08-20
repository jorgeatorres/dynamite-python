# encoding: utf-8

from PySide.QtCore import *
from PySide.QtGui import *

from dynamite.plots import DynamitePlot


class DynamiteView(QWidget):

    DEFAULT_SETTINGS = {'show-grid': True,
                        'show-axes': True,
                        'axes-width': 1.1,
                        'axes-color': Qt.black,
                        'axes-tick-length': 2.0,
                        'axes-tick-spacing': 5.0}

    # signals
    view_changed = Signal()
    plot_added = Signal(DynamitePlot)
    plot_changed = Signal(DynamitePlot)
    plot_removed = Signal(DynamitePlot)


    def __init__(self, *args, **kwargs):
        super(DynamiteView, self).__init__(*args, **kwargs)

        self._settings = self.DEFAULT_SETTINGS

        self._width = 0.0
        self._height = 0.0
        self._dx = 0.5
        self._dy = 0.5

        self._transform = CoordinateTransform()

        self._view = [QPointF(-5.5, -3.0), QPointF(5.5, 3.0)] # [(x0,y0), (x1,y1)]
        self._origin = QPoint(0.0, 0.0)

        self.setMinimumWidth(800)
        self.setMinimumHeight(500)

        self._plots = []

    # handle resize events
    def resizeEvent(self, event):
        self._width = event.size().width()
        self._height = event.size().height()
        self._transform.setView(self._view, self._width, self._height)
        super(DynamiteView, self).resizeEvent(event)

    # paint event
    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(QRectF(0, 0, self._width, self._height), Qt.white)
        p.setRenderHint(QPainter.Antialiasing, True)

        p.save()
        self._paintAxes(p)
        p.restore()

        # plot everything else
        for plot in self._plots:
            if plot.enabled:
                p.save()
                plot.paint(p, self._transform)
                p.restore()

        # paint coordinate axes 
        #self._paintAxes()

    def _paintAxes(self, p):
        if not self._settings['show-axes']:
            return

        pen = QPen()
        pen.setWidthF(self._settings['axes-width'])
        pen.setColor(self._settings['axes-color'])
        p.setPen(pen)

        p.drawLine(self._transform.pointToPixel(0.0, 0.0), self._transform.pointToPixel(0.0, self._view[1].y()))
        p.drawLine(self._transform.pointToPixel(0.0, 0.0), self._transform.pointToPixel(self._view[1].x(), 0.0))

        # ticks

    def addPlot(self, plot):
        if plot not in self._plots:
            #plot.setView(self._view)
            self._plots.append(plot)
            plot.plotChanged.connect(self.repaint)
            self.plot_added.emit(plot)

        self.view_changed.emit()
        self.repaint()

    def getPlots(self):
        return self._plots


class CoordinateTransform(object):
    
    def setView(self, view, screenWidth, screenHeight):
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