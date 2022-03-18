# flake8: noqa
from vnpy.event import EventEngine

from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

from vnpy_ctp import CtpGateway
# from vnpy_ctptest import CtptestGateway
# from vnpy_mini import MiniGateway
# from vnpy.gateway.minitest import MinitestGateway
# from vnpy.gateway.futu import FutuGateway
# from vnpy.gateway.ib import IbGateway
# from vnpy.gateway.tiger import TigerGateway

from jnpy.gateway.acestock.acestock.gateway import AcestockGateway
# from acestock import AcestockGateway

from vnpy_ctastrategy import CtaStrategyApp
from vnpy_ctabacktester import CtaBacktesterApp
# from vnpy_spreadtrading import SpreadTradingApp
# from vnpy.app.algo_trading import AlgoTradingApp
# from vnpy.app.option_master import OptionMasterApp
from vnpy_portfoliostrategy import PortfolioStrategyApp
from vnpy_scripttrader import ScriptTraderApp
# from vnpy.app.market_radar import MarketRadarApp
from vnpy_chartwizard import ChartWizardApp
# from vnpy.app.rpc_service import RpcServiceApp
# from vnpy.app.excel_rtd import ExcelRtdApp
from vnpy_datamanager import DataManagerApp
from vnpy_datarecorder import DataRecorderApp
from vnpy_riskmanager import RiskManagerApp
# from vnpy_webtrader import WebTraderApp
# from vnpy.app.portfolio_manager import PortfolioManagerApp
# from vnpy_paperaccount import PaperAccountApp

from jnpy.app.csv_loader import CsvLoaderApp
from jnpy.app.pytdx_loader import PytdxLoaderApp
from jnpy.app.cta_backtester import CtaBacktesterJnpyApp as CtaBacktesterApp_jnpy
from jnpy.app.vnpy_webtrader import WebTraderApp

# from pandarallel import pandarallel
# pandarallel.initialize()


def main():
    """"""
    qapp = create_qapp()

    event_engine = EventEngine()

    main_engine = MainEngine(event_engine)

    main_engine.add_gateway(AcestockGateway)
    main_engine.add_gateway(CtpGateway)

    main_engine.add_app(CtaBacktesterApp_jnpy)
    main_engine.add_app(CsvLoaderApp)
    main_engine.add_app(PytdxLoaderApp)
    main_engine.add_app(WebTraderApp)

    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(CtaBacktesterApp)
    # main_engine.add_app(AlgoTradingApp)
    main_engine.add_app(DataRecorderApp)
    main_engine.add_app(RiskManagerApp)
    main_engine.add_app(ScriptTraderApp)
    # main_engine.add_app(RpcServiceApp)
    # main_engine.add_app(SpreadTradingApp)
    # main_engine.add_app(PortfolioManagerApp)
    main_engine.add_app(PortfolioStrategyApp)
    # main_engine.add_app(OptionMasterApp)
    main_engine.add_app(ChartWizardApp)
    # main_engine.add_app(MarketRadarApp)
    # main_engine.add_app(ExcelRtdApp)
    # main_engine.add_app(PaperAccountApp)
    main_engine.add_app(DataManagerApp)
    # main_engine.add_app(WebTraderApp)

    # main_engine.query_history()

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()


if __name__ == "__main__":
    main()
