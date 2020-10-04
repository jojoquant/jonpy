#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   03/07/2020 00:09
@Author   :   Fangyang
"""
import json

import pika

from jnpy.app.pub_sub.base import base_ps
from jnpy.app.pub_sub.setting import (
    qapubsub_ip, qapubsub_password, qapubsub_port, qapubsub_user
)


class Publisher(base_ps):
    def __init__(
            self, host=qapubsub_ip, port=qapubsub_port,
            user=qapubsub_user, password=qapubsub_password,
            channel_number=1, queue_name='', routing_key='default',
            exchange='', exchange_type='fanout', vhost='/',
            durable=False
    ):
        """
        exchange_type: ["fanout", "direct", "topic"], default "fanout"
        """
        super().__init__(host, port, user, password, channel_number,
                         queue_name, routing_key, exchange, vhost)
        self.exchange_type = exchange_type
        self.channel.queue_declare(
            self.queue_name, auto_delete=True, exclusive=True)
        self.channel.exchange_declare(exchange=exchange,
                                      exchange_type=self.exchange_type,
                                      passive=False,
                                      durable=durable,
                                      auto_delete=True)
        self.routing_key = routing_key

    def pub(self, text):
        # channel.basic_publish向队列中发送信息
        # exchange -- 它使我们能够确切地指定消息应该到哪个队列去。
        # routing_key 指定向哪个队列中发送消息
        # body是要插入的内容, 字符串格式

        if isinstance(text, dict):
            content_type = 'application/json'
            text = json.dumps(text)
        else:
            content_type = 'text/plain'
        try:
            self.channel.basic_publish(exchange=self.exchange,
                                       routing_key=self.routing_key,
                                       body=text,
                                       properties=pika.BasicProperties(content_type=content_type,
                                                                       delivery_mode=1))
        except Exception as e:
            print(e)
            self.reconnect().channel.basic_publish(exchange=self.exchange,
                                                   routing_key=self.routing_key,
                                                   body=text,
                                                   properties=pika.BasicProperties(content_type=content_type,
                                                                                   delivery_mode=1))

    def exit(self):
        self.connection.close()


if __name__ == '__main__':
    import datetime
    import time

    p = Publisher(exchange='z3', exchange_type="direct", routing_key="hh")
    while True:
        print(1)
        # p.pub('{}'.format(datetime.datetime.now()))
        p.pub({"dd": 1, "aa": 123, "cc": "cccc"})
        time.sleep(1)
