"""
Global setting of VN Trader.
"""
import json
from logging import CRITICAL
from typing import Dict, Any
from tzlocal import get_localzone

from .utility import load_json, TEMP_DIR


SETTINGS: Dict[str, Any] = {
    "font.family": "微软雅黑",
    "font.size": 12,

    "log.active": True,
    "log.level": CRITICAL,
    "log.console": True,
    "log.file": True,

    "email.server": "smtp.qq.com",
    "email.port": 465,
    "email.username": "",
    "email.password": "",
    "email.sender": "",
    "email.receiver": "",

    "datafeed.name": "",
    "datafeed.username": "",
    "datafeed.password": "",

    "database.timezone": get_localzone().zone,
    "database.name": "sqlite",
    "database.database": "database.db",         # for sqlite, use this as filepath
    "database.host": "localhost",
    "database.port": 3306,
    "database.user": "root",
    "database.password": "",
    "database.authentication_source": "admin",  # for mongodb

    "genus.parent_host": "",
    "genus.parent_port": "",
    "genus.parent_sender": "",
    "genus.parent_target": "",
    "genus.child_host": "",
    "genus.child_port": "",
    "genus.child_sender": "",
    "genus.child_target": "",
}

# Load global setting from json file.
SETTING_FILENAME: str = "vt_setting.json"
SETTINGS.update(load_json(SETTING_FILENAME))

################################################################
# .vntrader/vt_setting.json 的 database的配置只写一个driver就行,
# 其他配置如果写在database目录下相应的json内, 会覆盖更新全局database配置
database_dir = TEMP_DIR.joinpath("database")
# 判断 .vntrader/database 是否存在
if database_dir.exists():
    # 如果存在读取相应driver的json配置, 重新更新配置
    # with open(database_dir.joinpath(f"{SETTINGS['database.driver']}.json"), mode="r", encoding="UTF-8") as f:
    with open(database_dir.joinpath(f"mongodb.json"), mode="r", encoding="UTF-8") as f:
        data = json.load(f)
    SETTINGS.update(data)
    print(f"[来自vnpy.trader.setting消息] SETTINGS database 内容"
          f"从 database 目录下 {SETTINGS['database.driver']}.json 文件进行更新")
###################################################################


def get_settings(prefix: str = "") -> Dict[str, Any]:
    prefix_length = len(prefix)
    return {k[prefix_length:]: v for k, v in SETTINGS.items() if k.startswith(prefix)}
