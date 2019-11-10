# !/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
created by Fangyang on Time:2019/11/10
'''
__author__ = 'Fangyang'

import sys
from PyQt5.QtWidgets import QAction, QMainWindow, QApplication, QMenu
from PyQt5.QtGui import QIcon

class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')

        impMenu = QMenu('Import', self)
        impAct = QAction('Import mail', self)
        impMenu.addAction(impAct)

        newAct = QAction('New', self)
        fileMenu.addAction(newAct)

        fileMenu.addMenu(impMenu)

        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('Sub menu')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
