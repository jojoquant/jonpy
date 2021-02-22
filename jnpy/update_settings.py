import json
from typing import Dict, Any

from vnpy.trader.utility import TEMP_DIR
from vnpy.trader.setting import SETTINGS


def update_settings(settings):
    '''

    '''
    if settings == None:
        return SETTINGS

    # .vntrader/vt_setting.json 的 database的配置只写一个driver就行,
    # 其他配置如果写在database目录下相应的json内, 会覆盖更新全局database配置
    database_dir = TEMP_DIR.joinpath("database")
    # 判断 .vntrader/database 是否存在
    if database_dir.exists():
        # 如果存在读取相应driver的json配置, 重新更新配置
        # with open(database_dir.joinpath(f"{SETTINGS['database.driver']}.json"), mode="r", encoding="UTF-8") as f:
        with open(database_dir.joinpath(f"mongodb.json"), mode="r", encoding="UTF-8") as f:
            data = json.load(f)
        settings.update(get_settings_with_param(data, "database."))
        print(f"[来自vnpy.trader.setting消息] SETTINGS database 内容"
              f"从 database 目录下 {settings['driver']}.json 文件进行更新")
    return settings

def get_settings_with_param(settings: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    prefix_length = len(prefix)
    return {k[prefix_length:]: v for k, v in settings.items() if k.startswith(prefix)}
