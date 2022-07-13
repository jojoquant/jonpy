# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2022/7/11 16:34
# @Author   : Fangyang
# @Software : PyCharm


from pathlib import Path
from vnpy.trader.app import BaseApp
from .engine import APP_NAME, RobotEngine


class DingdingRobotApp(BaseApp):
    """"""
    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "钉钉机器人"
    engine_class = RobotEngine
    widget_name = "RobotWidget"
    icon_name = str(app_path.joinpath("ui", "logo.svg"))
