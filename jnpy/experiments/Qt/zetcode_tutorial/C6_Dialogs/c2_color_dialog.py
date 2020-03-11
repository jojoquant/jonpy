# !/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
created by Fangyang on Time:2019/11/10
'''
__author__ = 'Fangyang'

from PyQt5.QtWidgets import (
    QWidget, QPushButton, QFrame,
    QColorDialog, QApplication
)
from PyQt5.QtGui import QColor
import sys


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        col = QColor(0, 0, 0)

        self.btn = QPushButton('Dialog', self)
        self.btn.move(60, 60)
        self.btn.clicked.connect(self.showDialog)

        self.frm = QFrame(self)
        self.frm.move(20, 20)
        print(col.name())
        self.frm.setStyleSheet(f"QWidget {{background-color:{col.name()}}}")

        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('input dialog')
        self.show()

    def showDialog(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.frm.setStyleSheet(f"QWidget {{background-color:{col.name()}}}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
