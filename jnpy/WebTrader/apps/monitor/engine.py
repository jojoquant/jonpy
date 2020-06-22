#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   07/06/2020 23:31
@Author   :   Fangyang
"""

from vnpy.app.cta_strategy import CtaTemplate
from vnpy.app.cta_strategy.base import EVENT_CTA_LOG

from vnpy.trader.engine import MainEngine
from vnpy.trader.event import EVENT_LOG
from vnpy.event import Event, EventEngine
from vnpy.app.cta_strategy.engine import CtaEngine
from vnpy.trader.object import LogData
import threading


class MonitorMainEngine(MainEngine):
    def __init__(self, event_engine: EventEngine):
        """"""
        super(MonitorMainEngine, self).__init__(event_engine)

        self.tornado_client = ""

    def update_tornado_client(self, tornado_client):
        self.tornado_client = tornado_client

    def write_log(self, msg: str, source: str = "") -> None:
        """
        Put log event with specific message.
        """
        log = LogData(msg=msg, gateway_name=source)
        event = Event(EVENT_LOG, log)
        self.event_engine.put(event)
        print("MonitorMainEngine", threading.current_thread().getName())
        if self.tornado_client and (threading.current_thread().getName() == "MainThread"):
            self.tornado_client.write_message({"dialog": {"msg": msg, "type": "info"}})


class MonitorCtaEngine(CtaEngine):

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super(MonitorCtaEngine, self).__init__(main_engine, event_engine)

    def write_log(self, msg: str, strategy: CtaTemplate = None):
        """
        Create cta engine log event.
        """
        if strategy:
            msg = f"{strategy.strategy_name}: {msg}"

        log = LogData(msg=msg, gateway_name="CtaStrategy")
        event = Event(type=EVENT_CTA_LOG, data=log)
        self.event_engine.put(event)
        print("MonitorCtaEngine", threading.current_thread().getName())

        if self.main_engine.tornado_client and (threading.current_thread().getName() == "MainThread"):
            self.main_engine.tornado_client.write_message({"dialog": {"msg": msg, "type": "info"}})


if __name__ == "__main__":
    pass
