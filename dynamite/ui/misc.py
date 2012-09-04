# encoding: utf-8

from PySide.QtCore import *
from PySide.QtGui import *


class ColorButton(QWidget):

    class ColorRepresentation(QWidget):
        def __init__(self, *args, **kwargs):
            super(ColorButton.ColorRepresentation, self).__init__(*args, **kwargs)
            self.color = None

            self.setMinimumWidth(20)
            self.setMinimumHeight(20)

        def paintEvent(self, event):
            if self.color is None:
                return

            p = QPainter(self)
            p.fillRect(QRectF(0, 0, self.width(), self.height()), self.color)

    colorChanged = Signal(QColor)

    def __init__(self, parent=None):
        super(ColorButton, self).__init__(parent)
        self._color = None

        # setup UI
        hbox = QHBoxLayout(self)
        
        self._colorEx = ColorButton.ColorRepresentation(self)
        hbox.addWidget(self._colorEx)
        
        button = QPushButton(self.tr('Change Color'), self)
        button.clicked.connect(self._showColorDialog)
        hbox.addWidget(button)

    def setColor(self, color):
        self._color = color
        self._colorEx.color = color

        self.colorChanged.emit(color)

        self.repaint()

    def getColor(self):
        return self._color

    # on OS X we suffer from QTBUG-11188
    def _showColorDialog(self):
        dialog = QColorDialog(self)
        dialog.setCurrentColor(self._color)

        if dialog.exec_():
            self.setColor(dialog.selectedColor())
