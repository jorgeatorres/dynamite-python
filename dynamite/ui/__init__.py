# encoding: utf-8

from PySide.QtCore import *
from PySide.QtGui import *

from dynamite.core import ParsedSystem

from dynamite.view import DynamiteView

from dynamite.ui.dialogs import ViewLimitsDialog, PlotSettingsDialog
from dynamite.ui.treeview import PlotTreeView
from dynamite.ui.eqarea import EquationArea


class DynamiteWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(DynamiteWindow, self).__init__(*args, **kwargs)
        
        self._setupActions()

        self._initUI()
        self.setMinimumWidth(1000)

    def _setupActions(self):
        self._actions = {}

        a = QAction('Test', self)
        a.triggered.connect(self._testAction)
        self._actions['test'] = a

        a = QAction('New', self)
        a.setShortcut(QKeySequence.New)
        self._actions['new'] = a

        a = QAction('Open', self)
        a.setShortcut(QKeySequence.Open)
        self._actions['open'] = a

        a = QAction('Close', self)
        a.setShortcut(QKeySequence.Close)
        self._actions['close'] = a

        a = QAction('Save', self)
        a.setShortcut(QKeySequence.Save)
        self._actions['save'] = a

        a = QAction('Export', self)
        self._actions['export'] = a

        a = QAction('Print', self)
        a.setShortcut(QKeySequence.Print)
        self._actions['print'] = a

        # Plot-related
        a = QAction('Axes && Grid Settings...', self)
        a.triggered.connect(self._changeAxesSettings)
        self._actions['change-axes-settings'] = a

        a = QAction('Show Inspector', self)
        a.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_I))
        a.setCheckable(True)
        a.setChecked(False)
        a.triggered.connect(self._showInspector)
        self._actions['show-inspector'] = a

        # View-related

        a = QAction(u'View Limits...', self)
        a.triggered.connect(self._setViewLimits)
        self._actions['set-view-limits'] = a

        zoomin = QAction('Zoom In', self)
        zoomin.setShortcut(QKeySequence.ZoomIn)
        zoomin.triggered.connect(self._zoomIn)
        self._actions['zoom-in'] = zoomin

        zoomout = QAction('Zoom Out', self)
        zoomout.triggered.connect(self._zoomOut)
        zoomout.setShortcut(QKeySequence.ZoomOut)
        self._actions['zoom-out'] = zoomout

        a = QAction(u'Select tool', self)
        a.setCheckable(True)
        a.setChecked(True)      
        a.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_1))
        a.triggered.connect(self._changeCursorMode)
        self._actions['set-select-tool'] = a

        a = QAction(u'Move tool', self)
        a.setCheckable(True)
        a.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_2))
        a.triggered.connect(self._changeCursorMode)
        self._actions['set-move-tool'] = a

        a = QAction(u'Zoom tool', self)
        a.setCheckable(True)
        a.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_3))
        a.triggered.connect(self._changeCursorMode)
        self._actions['set-zoom-tool'] = a

        a = QAction('Show toolbar', self)
        a.setCheckable(True)
        a.setChecked(True)
        a.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_T))
        self._actions['show-hide-toolbar'] = a

        a = QAction('Center origin', self)
        self._actions['center-origin'] = a


    def _initUI(self):
        self._initMenuBar()
        self._initToolBar() # toolbar

        # statusbar
        self._statusBar = QStatusBar(self)
        self._statusBar.setAutoFillBackground(False)
        self.setStatusBar(self._statusBar)

        # widget
        centralwidget = QWidget(self)

        hbox = QHBoxLayout(centralwidget)

        self._view = DynamiteView(self)
        self._view.selectionChanged.connect(self._selectionChanged)
        hbox.addWidget(PlotTreeView(self._view))

        vboxWidget = QWidget()

        vbox = QVBoxLayout(vboxWidget)
        self._equationArea = EquationArea()
        self._equationArea.equationDone.connect(self._equationDone)
        vbox.addWidget(self._equationArea)
        vbox.addWidget(self._view)

        hbox.addWidget(vboxWidget)

        self.setCentralWidget(centralwidget)

        # inspector window
        self._inspector = PlotSettingsDialog(self)
        self._inspector.accepted.connect(self._actions['show-inspector'].toggle)
        self._inspector.rejected.connect(self._actions['show-inspector'].toggle)

    def _initMenuBar(self):
        self._menuBar = self.menuBar()
        #self._helpMenu = self._menuBar.addMenu("Whatever")

        # self._aboutAction = QAction("nenen", self, statusTip="nana", triggered=self.close)
        # self._helpMenu.addAction(self._aboutAction)
        # self.setMenuBar(self._menuBar)

        fileMenu = self._menuBar.addMenu(u'&File')
        fileMenu.addAction(self._actions['new'])
        fileMenu.addAction(self._actions['open'])
        fileMenu.addAction(self._actions['close'])
        fileMenu.addAction(self._actions['save'])
        fileMenu.addSeparator()
        fileMenu.addAction(self._actions['export'])
        fileMenu.addSeparator()
        fileMenu.addAction(self._actions['print'])

        plotMenu = self._menuBar.addMenu(u'&Plots')
        plotMenu.addAction(self._actions['show-inspector'])
        plotMenu.addSeparator()
        plotMenu.addAction(self._actions['change-axes-settings'])

        viewMenu = self._menuBar.addMenu(u'&View')
        viewMenu.addAction(self._actions['set-view-limits'])
        viewMenu.addSeparator()
        viewMenu.addAction(self._actions['zoom-in'])
        viewMenu.addAction(self._actions['zoom-out'])
        viewMenu.addSeparator()
        viewMenu.addAction(self._actions['set-select-tool'])
        viewMenu.addAction(self._actions['set-move-tool'])
        viewMenu.addAction(self._actions['set-zoom-tool'])
        viewMenu.addSeparator()
        viewMenu.addAction(self._actions['show-hide-toolbar'])
        viewMenu.addSeparator()
        viewMenu.addAction(self._actions['center-origin'])


    def _initToolBar(self):
        toolbar = QToolBar(self)
        toolbar.setFloatable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self._actions['test'])
        toolbar.addSeparator()

    def _equationDone(self, eq):
        system = ParsedSystem(eq['dx'], eq['dy'])
        self._view.add(OrbitPlot(system, QPointF(eq['x0'], eq['y0'])))

    def _selectionChanged(self, selected, notSelected):
        self._inspector.setPlots(selected)

    # Action callbacks
    def _changeCursorMode(self):
        print 'cursor mode'

    def _testAction(self):
        from dynamite.core.examples import Pendulum2D
        from dynamite.plots.diffeq import OrbitPlot, SlopeField
        
        p2d = Pendulum2D()
        for i in xrange(0, 5):
            self._view.add(OrbitPlot(p2d, QPointF(0.5 * i, 0.0)))
        self._view.add(SlopeField(p2d))

    def _showInspector(self):
        inspector = self._inspector

        if not self._actions['show-inspector'].isChecked():
            inspector.close()
        else:
            inspector.move(self.x() + self.width() - inspector.width() - 20, self.y() + 80)
            inspector.show()
            inspector.raise_()
            inspector.activateWindow()

    def _changeAxesSettings(self):
        inspector = self._inspector
        self._actions['show-inspector'].setChecked(True)
        self._view.setSelectedPlot(self._view.getAxesPlot())
        inspector.setPlot(self._view.getAxesPlot())
        inspector.show()
        inspector.raise_()
        inspector.activateWindow()

    def _zoomIn(self):
        self._view.zoomIn()

    def _zoomOut(self):
        self._view.zoomOut()

    def _setViewLimits(self):
        dlg = ViewLimitsDialog(self)
        dlg.setView(self._view.view)

        if dlg.exec_():
            self._view.view = dlg.getView()
