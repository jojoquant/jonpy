#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/9 下午1:32
@Author   :   Fangyang
"""

# 导入模块
from wxpy import *
# 初始化机器人，扫码登陆
bot = Bot()
# 搜索名称含有 "游否" 的男性深圳好友
my_friend = bot.friends().search('Nina 娇娇', sex=FEMALE)[0]
# 发送文本给好友
my_friend.send('忙啥呢?')

# group = bot.groups().search('量化投资小项目发家致富道路多')[0]
# group.send('Hello 哎喂宝呆!!!! 有人在吗?')

# 回复 my_friend 的消息 (优先匹配后注册的函数!)
@bot.register(my_friend)
def reply_my_friend(msg):
    return f'为什么{msg.text}? '

# @bot.register(group)
# def reply_my_friend(msg):
#     return f'为什么{msg.text}? 啊?'


if __name__ == "__main__":
    embed()