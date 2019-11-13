# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2019/11/13 上午11:49
# @Author   : Fangyang
# @Software : PyCharm


from PyQt5.QtWidgets import (
    QWidget, QLabel, QComboBox, QVBoxLayout, QApplication
)
import sys


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.lbl = QLabel('Manjaro', self)
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.lbl)

        combo = QComboBox(self)
        combo.addItem('Ubuntu')
        combo.addItem('Mandriva')
        combo.addItem('Fedora')
        combo.addItem('Arch')
        combo.addItem('Gentoo')

        vbox.addWidget(combo)
        # combo.move(50, 50)
        # self.lbl.move(50, 150)

        combo.activated[str].connect(self.onActivated)

        self.setLayout(vbox)
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('QComboBox')
        self.show()

    def onActivated(self, text):
        self.lbl.setText(text)
        self.lbl.adjustSize()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
