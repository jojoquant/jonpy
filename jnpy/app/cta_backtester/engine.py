import traceback
from datetime import datetime
from threading import Thread

from vnpy_ctastrategy import CtaTemplate
from vnpy_ctastrategy.base import BacktestingMode

from vnpy.event import Event, EventEngine
from vnpy.trader.constant import Interval
from vnpy.trader.engine import MainEngine

from vnpy_ctabacktester import BacktesterEngine
from vnpy_ctastrategy.backtesting import OptimizationSetting  # 给widget使用, 和vnpy widget尽量一致, 这里不要删除

# from jnpy.app.cta_backtester.DRL.main import accept_bars_data_list
from jnpy.app.cta_backtester.backtesting import BacktestingEngineJnpy

APP_NAME = "CtaBacktester_jnpy"

EVENT_JNPY_BACKTESTER_LOG = "eBacktesterLog_jnpy"
EVENT_JNPY_BACKTESTER_BACKTESTING_FINISHED = "eBacktesterBacktestingFinished_jnpy"
EVENT_JNPY_BACKTESTER_OPTIMIZATION_FINISHED = "eBacktesterOptimizationFinished_jnpy"


class BacktesterEngineJnpy(BacktesterEngine):
    """
    For running CTA strategy backtesting.
    """

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__(main_engine, event_engine)
        self.engine_name = APP_NAME

    def init_engine(self):
        """"""
        self.write_log("初始化 jnpy 魔改 CTA 回测引擎")

        self.backtesting_engine = BacktestingEngineJnpy(self.database)
        # Redirect log from backtesting engine outside.
        self.backtesting_engine.write_log = self.write_log
        self.backtesting_engine.output = self.write_log

        self.load_strategy_class()
        self.write_log("策略文件加载完成")

        self.init_datafeed()

    def write_log(self, msg: str, strategy: CtaTemplate = None):
        """"""
        event = Event(EVENT_JNPY_BACKTESTER_LOG)
        event.data = msg if strategy is None else f"{strategy.strategy_name} log: {msg}"
        self.event_engine.put(event)

    def rl_training(
            self, class_name: str,
            vt_symbol: str,
            interval: str,
            start: datetime,
            end: datetime,
            rate: float,
            slippage: float,
            size: int,
            pricetick: float,
            capital: int,
            inverse: bool,
            setting: dict):

        engine = self.backtesting_engine
        engine.clear_data()
        engine.set_parameters(
            vt_symbol=vt_symbol,
            interval=interval,
            start=start,
            end=end,
            rate=rate,
            slippage=slippage,
            size=size,
            pricetick=pricetick,
            capital=capital,
            inverse=inverse
        )
        engine.load_data()

        all_bars_list = engine.history_data
        accept_bars_data_list(all_bars_list)

    def run_backtesting(
            self,
            class_name: str,
            vt_symbol: str,
            interval: str,
            start: datetime,
            end: datetime,
            rate: float,
            slippage: float,
            size: int,
            pricetick: float,
            capital: int,
            inverse: bool,
            setting: dict
    ):
        """"""
        self.result_df = None
        self.result_statistics = None

        engine = self.backtesting_engine
        engine.clear_data()

        if interval == Interval.TICK.value:
            mode = BacktestingMode.TICK
        else:
            mode = BacktestingMode.BAR

        engine.set_parameters(
            vt_symbol=vt_symbol,
            interval=interval,
            start=start,
            end=end,
            rate=rate,
            slippage=slippage,
            size=size,
            pricetick=pricetick,
            capital=capital,
            inverse=inverse,
            mode=mode
        )

        strategy_class = self.classes[class_name]
        engine.add_strategy(
            strategy_class,
            setting
        )

        engine.load_data()  # fangyang, 从数据库中查询结果， 放入engine这个类实例的self.history_data中

        # fangyang 如果engine有这个属性, 即为 BacktestingEngine 类型的实例,
        # 将本 BacktesterEngine 传入, 用于接收 BacktestingEngine 实例产生的信息, 即回测进度信息
        if hasattr(engine, "backtester_engine"):
            engine.backtester_engine = self

        try:
            engine.run_backtesting()
        except Exception:
            msg = f"策略回测失效, 触发异常: \n{traceback.format_exc()}"
            self.write_log(msg)
            self.thread = None
            return

        self.result_df = engine.calculate_result()
        self.result_statistics = engine.calculate_statistics(output=False)

        # Clear thread object handler.
        self.thread = None

        # Put backtesting done event
        event = Event(EVENT_JNPY_BACKTESTER_BACKTESTING_FINISHED)
        self.event_engine.put(event)
