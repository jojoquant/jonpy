
import time
from typing import Dict

import uvicorn

from jnpy.app.vnpy_webtrader import WebTraderApp
from jnpy.app.vnpy_webtrader.web import app
from vnpy.event import EventEngine, Event
from vnpy.trader.engine import MainEngine
from vnpy.trader.event import EVENT_LOG
from vnpy.gateway.ctp import CtpGateway
from vnpy.trader.utility import load_json


def gen_ctp_setting(conn_name: str = "7_24") -> Dict[str, str]:
    """
    dx1：Trade Front：180.168.146.187:10201，Market Front：180.168.146.187:10211；【电信】（看穿式前置，使用监控中心生产秘钥）
    dx2：Trade Front：180.168.146.187:10202，Market Front：180.168.146.187:10212；【电信】（看穿式前置，使用监控中心生产秘钥）
    yd3：Trade Front：218.202.237.33:10203，Market Front：218.202.237.33:10213；【移动】（看穿式前置，使用监控中心生产秘钥）
    用户注册后，默认的APPID为simnow_client_test，认证码为0000000000000000（16个0），默认不开终端认证，程序化用户可以选择不开终端认证接入。
    交易品种：五所所有期货品种以及上期所所有期权品种。
    账户资金：初始资金两千万，支持入金，每日最多三次。
    交易阶段(服务时间)：与实际生产环境保持一致。

    7_24: 交易前置：180.168.146.187:10130，行情前置：180.168.146.187:10131；【7x24】（看穿式前置，使用监控中心生产秘钥）
    仅服务于CTP API开发爱好者，仅为用户提供CTP API测试需求，不提供结算等其它服务。
    交易阶段(服务时间)：交易日，16：00～次日09：00；非交易日，16：00～次日15：00。

    @param conn_name: string - "dx1", "dx2", "yd3", "7_24"
    @return:
    """
    setting = load_json("connect_ctp.json")

    if len(setting) != 7:
        setting = {
            "用户名": "",
            "密码": "",
            "经纪商代码": "9999",
            "交易服务器": "180.168.146.187:10130",
            "行情服务器": "180.168.146.187:10131",
            "产品名称": "simnow_client_test",
            "授权编码": "0000 0000 0000 0000".replace(" ", ''),
            "产品信息": ""
        }

    if conn_name == "dx1":
        setting["交易服务器"] = "180.168.146.187:10201"
        setting["行情服务器"] = "180.168.146.187:10211"
    elif conn_name == "dx2":
        setting["交易服务器"] = "180.168.146.187:10202"
        setting["行情服务器"] = "180.168.146.187:10212"
    elif conn_name == "yd3":
        setting["交易服务器"] = "218.202.237.33:10203"
        setting["行情服务器"] = "218.202.237.33:10213"
    elif conn_name == "7_24":
        setting["交易服务器"] = "180.168.146.187:10130"
        setting["行情服务器"] = "180.168.146.187:10131"

    return setting


def process_log_event(event: Event):
    """"""
    log = event.data
    msg = f"{log.time}\t{log.msg}"
    print(msg)


if __name__ == '__main__':
    event_engine = EventEngine()
    event_engine.register(EVENT_LOG, process_log_event)
    main_engine = MainEngine(event_engine)

    # add gateway
    main_engine.add_gateway(CtpGateway)
    ctp_setting = gen_ctp_setting()

    main_engine.connect(ctp_setting, "CTP")
    time.sleep(10)

    # add web_trader engine
    web_engine = main_engine.add_app(WebTraderApp)

    web_trader_setting = load_json("web_trader_setting.json")
    username = web_trader_setting.get("username", "vnpy")
    password = web_trader_setting.get("password", "vnpy")
    req_address = web_trader_setting.get("req_address", "tcp://127.0.0.1:2014")
    sub_address = web_trader_setting.get("sub_address", "tcp://127.0.0.1:4102")
    web_address = web_trader_setting.get("web_address", "0.0.0.0")
    web_port = web_trader_setting.get("web_port", "8000")

    web_engine.start_server(req_address, sub_address)
    uvicorn.run(app, host="0.0.0.0", port=8000)
