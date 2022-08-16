# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2022/7/11 16:36
# @Author   : Fangyang
# @Software : PyCharm
import json
from typing import List

import requests

from vnpy.trader.engine import BaseEngine, MainEngine, EventEngine
from vnpy.trader.utility import load_json

APP_NAME = "DingdingRobot"
WEBHOOK = "webhook"
TEST_CONTENT = "test_content"


class RobotEngine(BaseEngine):
    """"""

    def __init__(
            self,
            main_engine: MainEngine,
            event_engine: EventEngine,
    ):
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)

        self.headers = {
            "Content-Type": "application/json;charset=utf-8 "
        }

        self.robot_setting_filename = "dingding_robot_setting.json"

        self.robot_setting_dict = load_json(self.robot_setting_filename)

        self.webhooks: str = self.robot_setting_dict[WEBHOOK] if WEBHOOK in self.robot_setting_dict else ''
        self.webhook_list: List[str] = [
            i for i in self.webhooks.split('\n') if i
        ]
        self.test_content: str = self.robot_setting_dict[TEST_CONTENT] \
            if TEST_CONTENT in self.robot_setting_dict else ""

    def update_webhooks(self, webhooks):
        self.webhooks = webhooks
        self.webhook_list: List[str] = [
            i for i in self.webhooks.split('\n') if i
        ]

    def send_message(self, message=None):
        for webhook in self.webhook_list:
            try:
                res = requests.post(webhook, data=json.dumps(message), headers=self.headers)
                print(res.text)
            except Exception as e:
                print("Dingding send message error: ", e)

    def send_text(self, content, is_at_all=True):
        msg = {
            "msgtype": "text",
            "text": {
                "content": content
            },
            "at": {
                # "atDingtalkIds": [post_userid],
                "is_at_all": is_at_all
            }
        }
        self.send_message(message=msg)

    def send_markdown(self, title, content, is_at_all=True):
        """
            标题
            # 一级标题
            ## 二级标题
            ### 三级标题
            #### 四级标题
            ##### 五级标题
            ###### 六级标题

            引用
            > A man who stands for nothing will fall for anything.

            文字加粗、斜体
            **bold**
            *italic*

            链接
            [this is a link](https://www.dingtalk.com/)

            图片
            ![](http://name.com/pic.jpg)

            无序列表
            - item1
            - item2

            有序列表
            1. item1
            2. item2
        """
        msg = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": content
            },
            "at": {
                # "atDingtalkIds": [],
                "is_at_all": is_at_all
            }
        }
        self.send_message(message=msg)
