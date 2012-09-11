#!/usr/bin/python
# encoding: utf-8

import sys
from PySide.QtGui import QApplication
from dynamite.ui import DynamiteWindow


if __name__  == '__main__':
    app = QApplication(sys.argv)

    mainWindow = DynamiteWindow()
    mainWindow.show()

    sys.exit(app.exec_())