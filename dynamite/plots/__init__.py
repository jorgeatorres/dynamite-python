# encoding: utf-8

from PySide.QtCore import *
from PySide.QtGui import *

from dynamite.utils import WithSettings


class DynamitePlot(QObject):

    DEFAULT_SETTINGS = {'line-width': 2.0,
                        'color': Qt.black}

    plotChanged = Signal()
    plotSelectionChanged = Signal()


    def __init__(self, *args, **kwargs):
        super(DynamitePlot, self).__init__(*args, **kwargs)
        self._selected = False
        self._priority = 0
        self.enabled = True
        self.settings = dict(self.DEFAULT_SETTINGS)
        self._formula = None

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        if self._selected != value:
            self._selected = value
        self.plotSelectionChanged.emit()

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value=0):
        self._priority = value

    def paint(self, painter, transform):
        raise NotImplementedError('paint()')

    def setEnabled(self, value=True):
        self.enabled = value
        self.plotChanged.emit()

    def formula(self):
        return u'(Formula Unavailable)'
