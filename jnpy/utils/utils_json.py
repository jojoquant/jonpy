import datetime
import json
from dataclasses import asdict
from typing import Union

from vnpy.trader.object import TickData, BarData, LogData, AccountData, PositionData
from vnpy.trader.constant import Exchange, Interval


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            # return obj.strftime("%Y-%m-%d %H:%M:%S")
            return obj.isoformat()

        elif isinstance(obj, Exchange):
            return obj.value

        elif isinstance(obj, Interval):
            return obj.value

        else:
            return json.JSONEncoder.default(self, obj)


def convert_object_to_json(obj: TickData | BarData | LogData | AccountData | PositionData) -> str:
    tick_dict = asdict(obj)
    return json.dumps(tick_dict, cls=DateEncoder)


def convert_json_to_TickData(json_str: str):
    tick_dict = json.loads(json_str)
    tick_dict['exchange'] = Exchange(tick_dict['exchange'])
    tick_dict['datetime'] = datetime.datetime.fromisoformat(tick_dict['datetime'])
    return TickData(**tick_dict)


def convert_json_to_BarData(json_str: str):
    bar_dict = json.loads(json_str)
    bar_dict['exchange'] = Exchange(bar_dict['exchange'])
    bar_dict['datetime'] = datetime.datetime.fromisoformat(bar_dict['datetime'])
    bar_dict['interval'] = Interval(bar_dict['interval'])
    return BarData(**bar_dict)


if __name__ == '__main__':
    tt = TickData(gateway_name="CTP", symbol='rb2205', exchange=Exchange.SHFE, datetime=datetime.datetime(2022, 2, 20))
    bb = BarData(gateway_name="CTP", symbol='rb2205', exchange=Exchange.SHFE,
                 interval=Interval.MINUTE, datetime=datetime.datetime(2022, 2, 20))
    print(isinstance(tt, TickData))

    tt1 = convert_object_to_json(tt)
    tt2 = convert_json_to_TickData(tt1)

    bb1 = convert_object_to_json(bb)
    bb2 = convert_json_to_BarData(bb1)
    print(1)

    t2 = asdict(tt)
    t3 = json.dumps(t2)
    print(1)
