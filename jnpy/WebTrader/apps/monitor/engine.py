#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   07/06/2020 23:31
@Author   :   Fangyang
"""
from typing import Any

from vnpy.trader.engine import MainEngine
from vnpy.trader.event import EVENT_LOG
from vnpy.event import Event, EventEngine
from vnpy.app.cta_strategy.engine import CtaEngine
from vnpy.trader.object import LogData


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
        if self.tornado_client:
            self.tornado_client.write_message({"dialog": {"msg": msg, "type": "info"}})


class MonitorCtaEngine(CtaEngine):

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super(MonitorCtaEngine, self).__init__(main_engine, event_engine)


if __name__ == "__main__":
    pass
