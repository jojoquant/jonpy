# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2019/11/14 上午2:23
# @Author   : Fangyang
# @Software : PyCharm

import sys
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg

app = QApplication(sys.argv)
pg.plot(x=[0, 1, 2, 4], y=[4, 5, 9, 6])
status = app.exec_()
sys.exit(status)

if __name__ == '__main__':
    pass
