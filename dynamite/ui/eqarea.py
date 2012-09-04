# encoding: utf-8

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *


class EquationArea(QWidget):

# <script type="text/x-mathjax-config">
#   MathJax.Hub.Config({
#     "HTML-CSS": { availableFonts: ["Times"] }
#   });
# </script>

    PREVIEW_HTML = """
<html>
<head>
<script type="text/x-mathjax-config">
</script>
<script type="text/javascript" src="MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
</head>
<body>
    $$ <eqarea:formula> $$
</body>
</html>    
    """

    equationDone = Signal(object)

    def __init__(self, *args, **kwargs):
        super(EquationArea, self).__init__(*args, **kwargs)

        self._formula = QTextEdit()
        self._formula.setMinimumWidth(400)
        self._formula.textChanged.connect(self._processFormula)

        self._preview = QWebView()
        self._preview.show()

        self._ok = QPushButton(u'OK') 
        self._ok.released.connect(self._okClicked)       

        self._system = {'dx': None, 'dy': None, 'x0': None, 'y0': None}

        hbox = QHBoxLayout(self)
        hbox.addWidget(self._formula)
        hbox.addWidget(self._preview)
        hbox.addWidget(self._ok)

    def _okClicked(self):
        self.equationDone.emit(self._system)

    def setFormula(self, text):
        self._formula.setPlainText(text)

    def _processFormula(self):
        from sympy import latex

        formula = self.sender().toPlainText()

        try:
            expression = self._parseFormula(formula)
            
            html = self.PREVIEW_HTML
            html = html.replace(u'<eqarea:formula>', latex(expression))
            
            # m_pMyWidget = new QWidget(this);
            # m_pMyWidget->setGeometry(0,0,300,100);
            # m_pMyWidget->setStyleSheet("background-color:black;");
            # m_pMyWidget->show();

            self._formula.setStyleSheet('background-color: white;')
            self._preview.setHtml(html, QUrl('http://cdn.mathjax.org/mathjax/latest/'))

            #self._formula.setTextColor(Qt.black)
        except Exception, e:
            self._formula.setStyleSheet('background-color: red;')
            self._preview.setHtml('')
            print repr(e)
            #self._formula.setTextColor(Qt.red)

    def _parseFormula(self, text):
        from sympy.parsing.sympy_parser import parse_expr

        text = text.replace(u'^', u'**')
        text = text.replace(u'x\'', u'dx')
        text = text.replace(u'y\'', u'dy')

        if 'dx' not in text or 'dy' not in text or 'x0' not in text or 'y0'not in text:
            raise Exception('missing parts')

        parts = text.split(',')

        dx, dy, x0, y0 = (None,) * 4
        if parts is not None:

            for part in parts:
                _part = part.strip()

                if _part.startswith('dx'):
                    dx = parse_expr(_part.lstrip('dx='))
                elif _part.startswith('dy'):
                    dy = parse_expr(_part.lstrip('dy='))
                elif _part.startswith('x0'):
                    x0 = parse_expr(_part.lstrip('x0='))
                elif _part.startswith('y0'):
                    y0 = parse_expr(_part.lstrip('y0='))   

        if None not in (dx, dy, x0, y0):
            self._system['dx'] = dx
            self._system['dy'] = dy
            self._system['x0'] = x0
            self._system['y0'] = y0
            return parse_expr(u'[%s,%s,[%s,%s]]' % (dx, dy, x0, y0))

        return None