# encoding: utf-8

from PySide.QtCore import *
from PySide.QtGui import *

from dynamite.view import DynamiteView
from dynamite.ui.treemodel import PlotTreeModel
from dynamite.core import Pendulum2D
from dynamite.plots import *


class DynamiteWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(DynamiteWindow, self).__init__(*args, **kwargs)

        self._initUI()
        self.setMinimumWidth(1000)


    def _initUI(self):
        self._menuBar = self.menuBar()
        self._helpMenu = self._menuBar.addMenu("Whatever")

        self._aboutAction = QAction("nenen", self, statusTip="nana", triggered=self.close)
        self._helpMenu.addAction(self._aboutAction)
        self.setMenuBar(self._menuBar)


        self._initToolBar() # toolbar

        # statusbar
        self._statusBar = QStatusBar(self)
        self._statusBar.setAutoFillBackground(False)
        self.setStatusBar(self._statusBar)

        # widget
        centralwidget = QWidget(self)

        hbox = QHBoxLayout(centralwidget)

        self._view = DynamiteView(self)
        self._plotListView = QTreeView(self)
        self._plotListView.setModel(PlotTreeModel(self._view))

        # textedit.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        hbox.addWidget(self._plotListView)

        #self._view.view_changed.connect(self._updateTextArea)
        hbox.addWidget(self._view)

        self.setCentralWidget(centralwidget)

    def _initToolBar(self):
        toolbar = QToolBar(self)
        toolbar.setFloatable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(u'Test', self._testAction)

    # Actions
    def _testAction(self):
        for i in xrange(0, 10):
            self._view.addPlot(OrbitPlot(Pendulum2D(), QPointF(0.5 * i, 0.0)))
        # self._view.addPlot(OrbitPlot(Pendulum2D(), QPointF(0.0, 0.0)))
        # self._view.addPlot(OrbitPlot(Pendulum2D(), QPointF(0.5, 0.0)))
        # self._view.addPlot(OrbitPlot(Pendulum2D(), QPointF(1.0, 0.0)))
        self._view.addPlot(SlopeField(Pendulum2D()))
