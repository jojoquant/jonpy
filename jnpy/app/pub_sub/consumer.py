#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   03/07/2020 00:13
@Author   :   Fangyang
"""
import json

from jnpy.app.pub_sub.base import base_ps
from jnpy.app.pub_sub.setting import qapubsub_ip, qapubsub_port, qapubsub_user, qapubsub_password
import random


class Subscriber(base_ps):

    def __init__(
            self, host=qapubsub_ip, port=qapubsub_port,
            user=qapubsub_user, password=qapubsub_password,
            exchange='', exchange_type='fanout',
            vhost='/', queue='qa_sub.{}'.format(random.randint(0, 1000000)),
            routing_key='default'
    ):
        """
        exchange_type: ["fanout", "direct", "topic"], default "fanout"
        """
        super().__init__(host=host, port=port, user=user, vhost=vhost,
                         password=password, exchange=exchange)
        self.queue = queue
        self.exchange_type = exchange_type
        self.channel.exchange_declare(exchange=exchange,
                                      exchange_type=self.exchange_type,
                                      passive=False,
                                      durable=False,
                                      auto_delete=True)
        self.routing_key = routing_key
        self.queue = self.channel.queue_declare(
            queue='', auto_delete=True, exclusive=True).method.queue
        self.channel.queue_bind(queue=self.queue, exchange=exchange,
                                routing_key=self.routing_key)  # 队列名采用服务端分配的临时队列
        # self.channel.basic_qos(prefetch_count=1)

    def add_sub(self, exchange, routing_key):

        self.channel.queue_bind(queue=self.queue, exchange=exchange,
                                routing_key=routing_key)

    def callback(self, chan, method_frame, _header_frame, body, userdata=None):
        if _header_frame.content_type == 'application/json':
            xxx = json.loads(body)
        print(1)
        print(" [x] %r" % body)

    def subscribe(self):
        self.channel.basic_consume(self.queue, self.callback, auto_ack=True)
        self.channel.start_consuming()

    def start(self):
        try:
            self.subscribe()
        except Exception as e:
            print(e)
            self.start()


if __name__ == "__main__":
    s1 = Subscriber(exchange='z3', exchange_type='direct', routing_key="hh")
    s1.subscribe()
