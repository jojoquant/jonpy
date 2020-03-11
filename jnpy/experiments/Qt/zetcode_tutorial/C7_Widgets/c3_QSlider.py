# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2019/11/13 上午11:49
# @Author   : Fangyang
# @Software : PyCharm


from PyQt5.QtWidgets import QWidget, QSlider, QLabel, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        sld = QSlider(Qt.Horizontal, self)
        sld.setFocusPolicy(Qt.NoFocus)
        sld.setGeometry(30, 40, 100, 30)
        sld.valueChanged[int].connect(self.changeValue)

        self.label = QLabel(self)
        self.label.setPixmap(QPixmap('../web.png'))
        self.label.setGeometry(160, 40, 580, 530)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('QSlider')
        self.show()

    def changeValue(self, value):
        if value == 0:
            self.label.setPixmap(QPixmap('../web.png'))
        elif 0 < value <= 30:
            self.label.setPixmap(QPixmap('../python.png'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
