from pathlib import Path

from vnpy.trader.app import BaseApp
from .fengchen_engine import APP_NAME, PdCsvLoaderEngine


class CsvLoaderApp(BaseApp):
    """
    把CsvLoaderEngine替换成fengchen_engine
    """

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "CSV载入"
    engine_class = PdCsvLoaderEngine
    widget_name = "CsvLoaderWidget"
    icon_name = "csv.ico"
