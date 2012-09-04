# encoding: utf-8

from PySide.QtCore import *
from PySide.QtGui import *

from dynamite.ui.misc import ColorButton


class ViewLimitsDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super(ViewLimitsDialog, self).__init__(*args, **kwargs)
        self._setupDialog()

    def _setupDialog(self):
        self.setWindowTitle(self.tr('View Limits'))

        # buttons
        buttons = QDialogButtonBox(self)
        buttons.setOrientation(Qt.Horizontal)
        buttons.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)        

        form = QWidget(self)

        # TODO: align/size things correctly

        self._x0 = QDoubleSpinBox()
        self._x0.setDecimals(2)
        self._x0.setSingleStep(0.1)
        self._x0.setRange(-999999999.99, 999999999.99)
        self._x0.valueChanged.connect(self._updateRanges)

        self._x1 = QDoubleSpinBox()
        self._x1.setDecimals(2)
        self._x1.setSingleStep(0.1)
        self._x1.setRange(-999999999.99, 999999999.99)
        self._x1.valueChanged.connect(self._updateRanges)

        self._y0 = QDoubleSpinBox()
        self._y0.setDecimals(2)
        self._y0.setSingleStep(0.1)
        self._y0.setRange(-999999999.99, 999999999.99)
        self._y0.valueChanged.connect(self._updateRanges)

        self._y1 = QDoubleSpinBox()
        self._y1.setDecimals(2)
        self._y1.setSingleStep(0.1)
        self._y1.setRange(-999999999.99, 999999999.99)
        self._y1.valueChanged.connect(self._updateRanges)        
        
        grid = QGridLayout(form)
        grid.addWidget(QLabel('x:'), 0, 0)
        grid.addWidget(self._x0, 0, 1)
        grid.addWidget(QLabel('...'), 0, 2)
        grid.addWidget(self._x1, 0, 3)
        grid.addWidget(QLabel('y:'), 1, 0)
        grid.addWidget(self._y0, 1, 1)
        grid.addWidget(QLabel('...'), 1, 2)
        grid.addWidget(self._y1, 1, 3)

        vbox = QVBoxLayout()
        vbox.addWidget(form)
        vbox.addWidget(buttons)
        self.setLayout(vbox)

    def _updateRanges(self, d):
        x0 = self._x0.value()
        x1 = self._x1.value()
        y0 = self._y0.value()
        y1 = self._y1.value()

        self._x0.setMaximum(x1)
        self._x1.setMinimum(x0 + 0.1)
        self._y0.setMaximum(y1)
        self._y1.setMinimum(y0 + 0.1)


    def setView(self, view):
        self._x0.setValue(view[0].x())
        self._x1.setValue(view[1].x())
        self._y0.setValue(view[0].y())
        self._y1.setValue(view[1].y())

    def getView(self):
        return [QPointF(self._x0.value(), self._y0.value()), QPointF(self._x1.value(), self._y1.value())]


class PlotSettingsDialog(QDialog):

    class AutoSetter(object):

        def __init__(self, plots, setting):
            self.setting = setting
            self.plots = plots

        def __call__(self, arg0):
            import types

            for p in self.plots:
                value = arg0

                settingType = type(self.plots[0].settings[self.setting])

                if settingType == types.BooleanType:
                    if arg0 == Qt.CheckState.Checked:
                        value = True
                    else:
                        value = False

                p.settings[self.setting] = value
                p.plotChanged.emit()


    def __init__(self, *args, **kwargs):
        super(PlotSettingsDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle(self.tr('Inspector'))

        self.setWindowFlags(Qt.Tool)
        self.setModal(False)
        self.setMinimumWidth(250)

        self._vbox = QVBoxLayout(self)
        self._plots = []

    def setPlot(self, plot):
        self.setPlots([plot])

    def setPlots(self, plots=[]):
        child = self._vbox.takeAt(0)
        while (child is not None):
            widget = child.widget()
            widget.deleteLater()
            widget.setParent(None)
            del widget
            del child
            child = self._vbox.takeAt(0)
        self.layout().activate()
        self.resize(self.sizeHint())
 
        self._plots = plots

        if not plots:
            return

        if len(plots) == 1 and plots[0].__class__.__name__ == 'CoordinateAxesPlot':
            self._axesPlotSettings()
        else:
            self._vbox.addWidget(self._lineSettings())

        # settings = {}

        # for plot in plots:
        #     if type(plot) not in settings:
        #         settings[type(plot)] = {}
        #     settings[type(plot)].update(plot.settings)

    def _lineSettings(self, show_lines=None, color='color'):
        group = QGroupBox(self.tr('Line Settings'), self)
        vbox = QVBoxLayout(group)

        if show_lines is not None:
            checkbox = QCheckBox(self.tr('Show lines'))
            checkbox.setCheckState(Qt.CheckState.Checked if self._plots[0].settings[show_lines] else Qt.CheckState.Unchecked)
            checkbox.stateChanged.connect(self.AutoSetter(self._plots, 'show-lines'))
            vbox.addWidget(checkbox)

        if color is not None:
            colorbutton = ColorButton(parent=self)
            colorbutton.setColor(self._plots[0].settings[color])
            colorbutton.colorChanged.connect(self.AutoSetter(self._plots, 'color'))
            vbox.addWidget(colorbutton)

        return group

    def _axesPlotSettings(self):
        self._vbox.addWidget(self._lineSettings(show_lines='show-lines'))

        # Axes
        group = QGroupBox(self.tr('Axes'), self)
        vbox = QVBoxLayout(group)

        checkbox = QCheckBox(self.tr('Show grid'))
        checkbox.setCheckState(Qt.CheckState.Checked if self._plots[0].settings['show-grid'] else Qt.CheckState.Unchecked)
        checkbox.stateChanged.connect(self.AutoSetter(self._plots, 'show-grid'))
        vbox.addWidget(checkbox) 

        checkbox = QCheckBox(self.tr('Show axes labels'))
        checkbox.setCheckState(Qt.CheckState.Checked if self._plots[0].settings['show-labels'] else Qt.CheckState.Unchecked)
        checkbox.stateChanged.connect(self.AutoSetter(self._plots, 'show-labels'))
        vbox.addWidget(checkbox)               

        hbox = QHBoxLayout()
        checkbox = QCheckBox(self.tr('Major ticks'))
        checkbox.setCheckState(Qt.CheckState.Checked if self._plots[0].settings['major-ticks'] else Qt.CheckState.Unchecked)
        checkbox.stateChanged.connect(self.AutoSetter(self._plots, 'major-ticks'))
        hbox.addWidget(checkbox)
        checkbox = QCheckBox(self.tr('Numbered'))
        checkbox.setCheckState(Qt.CheckState.Checked if self._plots[0].settings['major-ticks-numbered'] else Qt.CheckState.Unchecked)
        checkbox.stateChanged.connect(self.AutoSetter(self._plots, 'major-ticks-numbered'))
        hbox.addWidget(checkbox)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        checkbox = QCheckBox(self.tr('Minor ticks'))
        checkbox.setCheckState(Qt.CheckState.Checked if self._plots[0].settings['minor-ticks'] else Qt.CheckState.Unchecked)
        checkbox.stateChanged.connect(self.AutoSetter(self._plots, 'minor-ticks'))
        hbox.addWidget(checkbox)
        checkbox = QCheckBox(self.tr('Numbered'))
        checkbox.setCheckState(Qt.CheckState.Checked if self._plots[0].settings['minor-ticks-numbered'] else Qt.CheckState.Unchecked)
        checkbox.stateChanged.connect(self.AutoSetter(self._plots, 'minor-ticks-numbered'))
        hbox.addWidget(checkbox)
        vbox.addLayout(hbox)

        self._vbox.addWidget(group)

        # Ticks
        group = QGroupBox(self.tr('Ticks'), self)
        grid = QGridLayout(group)

        grid.addWidget(QLabel(self.tr('Spacing')), 0, 0)
        slider = QSlider(Qt.Horizontal, self)
        slider.setMinimum(1)
        slider.setMaximum(10)
        grid.addWidget(slider, 0, 1)

        grid.addWidget(QLabel(self.tr('Major ticks width')), 1, 0)
        spinbox = QDoubleSpinBox()
        spinbox.setDecimals(1)
        spinbox.setRange(0.0, 16.0)
        spinbox.setValue(self._plots[0].settings['major-tick-length'])
        spinbox.valueChanged.connect(self.AutoSetter(self._plots, 'major-tick-length'))
        grid.addWidget(spinbox, 1, 1)

        grid.addWidget(QLabel(self.tr('Minor ticks width')), 2, 0)
        spinbox = QDoubleSpinBox()
        spinbox.setDecimals(1)
        spinbox.setRange(0.0, 16.0) 
        spinbox.setValue(self._plots[0].settings['minor-tick-length'])
        spinbox.valueChanged.connect(self.AutoSetter(self._plots, 'minor-tick-length'))
        grid.addWidget(spinbox, 2, 1)


        self._vbox.addWidget(group)

