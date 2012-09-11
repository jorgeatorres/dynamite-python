# encoding: utf-8

from PySide.QtCore import *
from PySide.QtGui import *

from dynamite.core import ParsedSystem

from dynamite.view import DynamiteView

from dynamite.ui.dialogs import ViewLimitsDialog, PlotSettingsDialog
from dynamite.ui.treeview import *
from dynamite.ui.eqarea import EquationArea


class DynamiteWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(DynamiteWindow, self).__init__(*args, **kwargs)
        
        self._setupActions()

        self._initUI()
        self.setMinimumWidth(1000)

    def _setupActions(self):
        self._actions = {}

        a = QAction('New', self)
        #a.setShortcut(QKeySequence.New)
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
        a = QAction('New Equation', self)
        a.setShortcut(QKeySequence.New)
        a.triggered.connect(self._newEquation)
        self._actions['new-equation'] = a

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
        self._treeView = PlotTreeView(self._view)
        self._treeView.selectionModel().selectionChanged.connect(self._treeViewSelectionChanged)
        self._model = self._treeView.model()
        hbox.addWidget(self._treeView)

        vboxWidget = QWidget()

        vbox = QVBoxLayout(vboxWidget)
        self._equationArea = EquationArea()
        self._equationArea.formulaDone.connect(self._formulaDone)
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
        plotMenu.addAction(self._actions['new-equation'])
        plotMenu.addSeparator()
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
        toolbar.addSeparator()

    def _selectionChanged(self, selected, notSelected):
        self._inspector.setPlots(selected)

    def _formulaDone(self, formula, expression, obj):
        data = self._treeView.selectionModel().currentIndex().internalPointer()

        if data._kind == TreeNodeKind.OBJECT:
            self._view.remove(data._data)

        if obj is None:
            data._data = formula
        else:
            # a plot
            #search = self._treeView.model().search(obj._system)

            # if search is None:
            #     node = TreeNode(obj, TreeNodeKind.OBJECT)
            #     data.add(node)
            #     data._data = obj._system
            #     data._kind = TreeNodeKind.OBJECT
            #     self._treeView.model().reset()
            # else:
            #     pass

            data._kind = TreeNodeKind.OBJECT
            data._data = obj
            self._view.add(obj)

        self._treeView.update()

    def _treeViewSelectionChanged(self, selected, deselected):
        indexes = self._treeView.selectionModel().selectedIndexes()
        
        if len(indexes) == 0:
            self._equationArea.setFormula(u'')
            return

        if len(indexes) > 1:
            self._equationArea.state = EquationArea.State.MULTIPLE
            return

        data = indexes[0].internalPointer()
        
        if data._kind == u'invalid-formula':
            self._equationArea.state = EquationArea.State.SINGLE
            self._equationArea.setFormula(data.data())
        elif data._kind == u'object':
            self._equationArea.state = EquationArea.State.SINGLE
            self._equationArea.setFormula(data.data()._formula)

        #self._equationArea.setFormula()

    def showEvent(self, *args, **kwargs):
        self._newEquation()

        #self._equationArea.setFocus(Qt.OtherFocusReason)
        return super(DynamiteWindow, self).showEvent(*args, **kwargs)

    #
    # Action callbacks
    #
    def _newEquation(self):
        self._model.addFormula(u'{dx/dt = ?, dy/dt = ?, x_0 = ?, y_0 = ?}')

    def _changeCursorMode(self):
        print 'cursor mode'

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
