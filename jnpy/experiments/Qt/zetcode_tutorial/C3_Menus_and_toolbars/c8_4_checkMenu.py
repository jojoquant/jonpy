# !/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
created by Fangyang on Time:2019/11/10
'''
__author__ = 'Fangyang'

import sys
from PyQt5.QtWidgets import QAction, QMainWindow, QApplication


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.statusBar = self.statusBar()
        self.statusBar.showMessage('ready')

        menuBar = self.menuBar()
        viewMenu = menuBar.addMenu('View')

        viewStatAct = QAction('View status bar', self, checkable=True)
        viewStatAct.setStatusTip('View status bar RRRRRRRR')
        viewStatAct.setChecked(True)
        viewStatAct.triggered.connect(self.toggleMenu)
        viewMenu.addAction(viewStatAct)

        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('Sub menu')
        self.show()

    def toggleMenu(self, state):
        if state:
            self.statusBar.show()
        else:
            self.statusBar.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
