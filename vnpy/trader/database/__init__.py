import os
from typing import TYPE_CHECKING

from jnpy.update_settings import update_settings

if TYPE_CHECKING:
    from vnpy.trader.database.database import BaseDatabaseManager

if "VNPY_TESTING" not in os.environ:
    from vnpy.trader.setting import get_settings
    from .initialize import init

    updated_settings = update_settings(get_settings("database."))
    database_manager: "BaseDatabaseManager" = init(settings=updated_settings)
