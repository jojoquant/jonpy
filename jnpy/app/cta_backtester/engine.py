from datetime import datetime
from threading import Thread

from vnpy.event import Event, EventEngine
from vnpy.trader.engine import MainEngine
from jnpy.app.cta_backtester.DRL.main import accept_bars_data_list

from vnpy.app.cta_backtester.engine import BacktesterEngine
from vnpy.app.cta_strategy.backtesting import OptimizationSetting

APP_NAME = "CtaBacktester_jnpy"

EVENT_BACKTESTER_LOG = "eBacktesterLog_jnpy"
EVENT_BACKTESTER_BACKTESTING_FINISHED = "eBacktesterBacktestingFinished_jnpy"
EVENT_BACKTESTER_OPTIMIZATION_FINISHED = "eBacktesterOptimizationFinished_jnpy"


class BacktesterEngineJnpy(BacktesterEngine):
    """
    For running CTA strategy backtesting.
    """

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__(main_engine, event_engine)
        self.engine_name = APP_NAME

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

        engine.run_backtesting()
        self.result_df = engine.calculate_result()
        self.result_statistics = engine.calculate_statistics(output=False)

        # Clear thread object handler.
        self.thread = None

        # Put backtesting done event
        event = Event(EVENT_BACKTESTER_BACKTESTING_FINISHED)
        self.event_engine.put(event)

    def start_backtesting(
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
            backtesting_debug_mode: bool,
            setting: dict
    ):
        if self.thread:
            self.write_log("已有任务在运行中，请等待完成")
            return False

        self.write_log("-" * 40)
        if backtesting_debug_mode:
            self.backtesting_engine.output = self.backtesting_engine.output_for_backtester
            self.run_backtesting(
                class_name,
                vt_symbol,
                interval,
                start,
                end,
                rate,
                slippage,
                size,
                pricetick,
                capital,
                inverse,
                setting
            )
        else:
            self.thread = Thread(
                target=self.run_backtesting,
                args=(
                    class_name,
                    vt_symbol,
                    interval,
                    start,
                    end,
                    rate,
                    slippage,
                    size,
                    pricetick,
                    capital,
                    inverse,
                    setting
                )
            )
            self.thread.start()

        return True
