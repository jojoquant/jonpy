# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2019/11/13 上午11:49
# @Author   : Fangyang
# @Software : PyCharm


from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QApplication
import sys


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.lbl = QLabel(self)
        qle = QLineEdit(self)

        qle.move(60, 100)
        self.lbl.move(60, 40)

        qle.textChanged[str].connect(self.onChanged)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('QLineEdit')
        self.show()

    def onChanged(self, text):
        self.lbl.setText(text)
        self.lbl.adjustSize()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
