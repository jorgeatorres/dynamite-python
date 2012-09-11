# encoding: utf-8

from PySide.QtCore import *
from PySide.QtGui import *

from dynamite.parser import convert, parse


class EquationArea(QTextEdit):

    class State(object):
        SINGLE = 1
        MULTIPLE = 2


    formulaDone = Signal(unicode, object, object)


    def __init__(self, *args, **kwargs):
        super(EquationArea, self).__init__(*args, **kwargs)
        self.setMinimumWidth(400)

        # default style
        font = QFont('Times', 15)
        font.setStyleHint(QFont.Serif)
        self.setFont(font)

        self._expression = None
        self._formula = None
        self._state = EquationArea.State.SINGLE

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self._validateFormula()
            return
        return super(EquationArea, self).keyPressEvent(event)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if state == 1 or state == 2:
            self._state = state

            if state == self.State.MULTIPLE:
                self._formula = None
                self._expression = None
                self.setReadOnly(True)
                self.setFormula(u'(Multiple Equations Selected)')
            else:
                self.setReadOnly(False)
                self.setFormula(u'')
        else:
            raise Exception('Invalid EquationArea state')

    def setFormula(self, text):
        self.setPlainText(text)

    def _validateFormula(self):
        if self.state == EquationArea.State.MULTIPLE:
            return

        text = self.toPlainText()
        expression = obj = None

        try:
            expression = parse(text)
            obj = convert(expression)
            obj._formula = text
        except Exception as e:
            print 'ParseError:', e

        self.formulaDone.emit(text, expression, obj)



    def _processFormula(self):
        pass
        # from sympy import latex

        # formula = self.sender().toPlainText()

        # try:
        #     expression = self._parseFormula(formula)
            
        #     html = self.PREVIEW_HTML
        #     html = html.replace(u'<eqarea:formula>', latex(expression))
            
        #     self._formula.setStyleSheet('background-color: white;')
        #     self._preview.setHtml(html, QUrl('http://cdn.mathjax.org/mathjax/latest/'))

        #     #self._formula.setTextColor(Qt.black)
        # except Exception, e:
        #     self._formula.setStyleSheet('background-color: red;')
        #     self._preview.setHtml('')
        #     print repr(e)
        #     #self._formula.setTextColor(Qt.red)

    def _parseFormula(self, text):
        pass
        # from sympy.parsing.sympy_parser import parse_expr

        # text = text.replace(u'^', u'**')
        # text = text.replace(u'x\'', u'dx')
        # text = text.replace(u'y\'', u'dy')

        # if 'dx' not in text or 'dy' not in text or 'x0' not in text or 'y0'not in text:
        #     raise Exception('missing parts')

        # parts = text.split(',')

        # dx, dy, x0, y0 = (None,) * 4
        # if parts is not None:

        #     for part in parts:
        #         _part = part.strip()

        #         if _part.startswith('dx'):
        #             dx = parse_expr(_part.lstrip('dx='))
        #         elif _part.startswith('dy'):
        #             dy = parse_expr(_part.lstrip('dy='))
        #         elif _part.startswith('x0'):
        #             x0 = parse_expr(_part.lstrip('x0='))
        #         elif _part.startswith('y0'):
        #             y0 = parse_expr(_part.lstrip('y0='))   

        # if None not in (dx, dy, x0, y0):
        #     self._system['dx'] = dx
        #     self._system['dy'] = dy
        #     self._system['x0'] = x0
        #     self._system['y0'] = y0
        #     return parse_expr(u'[%s,%s,[%s,%s]]' % (dx, dy, x0, y0))

        # return None