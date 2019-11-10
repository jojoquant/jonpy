# !/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
created by Fangyang on Time:2019/11/10
'''
__author__ = 'Fangyang'


import sys
from PyQt5.QtWidgets import QApplication, QWidget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w= QWidget()
    w.resize(250,150)
    w.move(300,300)
    w.setWindowTitle('Simple')
    w.show()

    sys.exit(app.exec_())


