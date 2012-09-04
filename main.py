#!/usr/bin/python
# encoding: utf-8

import sys
from PySide.QtGui import QApplication
from dynamite.ui import DynamiteWindow


if __name__  == '__main__':
    # Parser testing
    from dynamite.core.parser import ExpressionParser

    # #print repr(parser.parse('x+1'))
    # parser = ExpressionParser()

    # # text = raw_input("Expression:\n")
    # # print repr(parser.parse(text))
    # print repr(parser.parse('1+2*3'))

    # sys.exit(0)
    # End of parser testing

    app = QApplication(sys.argv)

    mainWindow = DynamiteWindow()
    mainWindow.show()

    sys.exit(app.exec_())