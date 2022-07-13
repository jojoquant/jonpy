# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2022/7/10 20:29
# @Author   : Fangyang
# @Software : PyCharm
import json
from datetime import datetime
import requests


class DingRobot:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url
        self.headers = {
            "Content-Type": "application/json;charset=utf-8 "
        }

    def send_message(self, message=None):
        try:
            res = requests.post(self.webhook_url, data=json.dumps(message), headers=self.headers)
            print(res.text)
            return res
        except Exception as e:
            print("Dingding send message error: ", e)
            return None

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


if __name__ == '__main__':
    from vnpy.trader.utility import load_json

    setting = load_json("dingding_robot_setting.json")

    ding_msg = [
        f'### [股票] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f' 你好漂亮!',
        "![美景](http://www.sinaimg.cn/dy/slidenews/5_img/2013_28/453_28488_469248.jpg)\n\n",
        "![美女](https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fimg.jj20.com%2Fup%2Fallimg%2F1114%2F062021132H5%2F210620132H5-1-1200.jpg&refer=http%3A%2F%2Fimg.jj20.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=auto?sec=1660053926&t=89a13ed380c8de8a7fe8142ce1586d16)\n\n",
    ]
    ding = "\n\n".join(ding_msg)

    robot = DingRobot(
        webhook_url=setting['webhook']
    )
    robot.send_markdown(title="股票消息提示", content=ding)
