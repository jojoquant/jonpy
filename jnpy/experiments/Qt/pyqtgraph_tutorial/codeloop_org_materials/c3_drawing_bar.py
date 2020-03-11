# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2019/11/14 上午2:26
# @Author   : Fangyang
# @Software : PyCharm

import sys
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg
import numpy as np

app = QApplication(sys.argv)
x = np.arange(10)
y1 = np.sin(x)
y2 = 1.1*np.sin(x+1)
y3 = 1.2*np.sin(x+2)
win = pg.plot(x=x, y=y1)

bg1 = pg.BarGraphItem(x=x, height=y1, width=0.3, brush='r')
bg2 = pg.BarGraphItem(x=x+0.33, height=y2, width=0.3, brush='g')
bg3 = pg.BarGraphItem(x=x+0.66, height=y3, width=0.3, brush='b')


win.addItem(bg1)
win.addItem(bg2)
win.addItem(bg3)

class BarGraph(pg.BarGraphItem):
    def mouseClickEvent(self, event):
        print('clicked')

bg = BarGraph(x=x, y=y1*0.3+2, height=0.4+y1*0.2, width=0.8)
win.addItem(bg)

status = app.exec_()
sys.exit(status)


if __name__ == '__main__':
    pass


