from pathlib import Path

from vnpy.trader.app import BaseApp
from .fengchen_engine import APP_NAME, PytdxLoaderEngine
# from .engine import APP_NAME, CsvLoaderEngine


class PytdxLoaderApp(BaseApp):
    """
    把CsvLoaderEngine替换成fengchen_engine
    """

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "通达信API载入"
    engine_class = PytdxLoaderEngine
    widget_name = "PytdxLoaderWidget"
    icon_name = "Bulbasaur.svg"
