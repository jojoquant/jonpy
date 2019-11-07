# !/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
created by Fangyang on Time:2019/10/29
'''
__author__ = 'Fangyang'

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from Qt.untitled import Ui_MainWindow


class Mwindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Mwindow()
    w.show()
    sys.exit(app.exec_())
