import csv
import subprocess
from datetime import datetime, timedelta
import copy
from enum import Enum
from typing import Dict

import numpy as np
import pyqtgraph as pg
import pandas as pd
import webbrowser

from vnpy.chart.item import ChartItem, LineItem, BalanceLineItem
from vnpy.trader.constant import Direction, Interval, Exchange
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtCore, QtWidgets, QtGui
from vnpy.trader.ui.widget import BaseMonitor, BaseCell, DirectionCell, EnumCell

from vnpy.event import Event, EventEngine
from vnpy.chart import ChartWidget, CandleItem, VolumeItem
from vnpy.trader.utility import load_json, save_json
from vnpy.trader.database import DB_TZ

from jnpy.datasource.jotdx.contracts import read_contracts_json_dict
# from .KLine_pro_pyecharts import draw_chart
from ..engine import (
    APP_NAME,
    EVENT_JNPY_BACKTESTER_LOG,
    EVENT_JNPY_BACKTESTER_BACKTESTING_FINISHED,
    EVENT_JNPY_BACKTESTER_OPTIMIZATION_FINISHED,
    OptimizationSetting
)

from vnpy_ctabacktester.engine import (
    APP_NAME as vnpy_app_name,
    EVENT_BACKTESTER_LOG,
    EVENT_BACKTESTER_BACKTESTING_FINISHED,
    EVENT_BACKTESTER_OPTIMIZATION_FINISHED)

from dateutil import parser


class BacktesterEngineType(Enum):
    vnpy = "vnpy"
    jnpy = "jnpy"


class JnpyBacktesterManager(QtWidgets.QWidget):
    """"""

    setting_filename = "cta_backtester_setting.json"

    signal_log = QtCore.Signal(Event)
    signal_backtesting_finished = QtCore.Signal(Event)
    signal_optimization_finished = QtCore.Signal(Event)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine

        self.jnpy_backtester_engine = main_engine.get_engine(APP_NAME)
        self.vnpy_backtester_engine = main_engine.get_engine(vnpy_app_name)
        self.last_backtester_engine_type: BacktesterEngineType = None

        self.class_names = []
        self.settings = {}
        self.db_instance = self.jnpy_backtester_engine.database
        self.dbbardata_groupby_df = pd.DataFrame()
        self.pytdx_contracts_dict = read_contracts_json_dict()

        self.target_display = ""

        self.init_ui()
        self.register_event()
        self.jnpy_backtester_engine.init_engine()
        self.vnpy_backtester_engine.init_engine()
        self.init_strategy_settings()
        self.load_backtesting_setting()

    def init_strategy_settings(self):
        """"""
        self.class_names = self.jnpy_backtester_engine.get_strategy_class_names()

        for class_name in self.class_names:
            setting = self.jnpy_backtester_engine.get_default_setting(class_name)
            self.settings[class_name] = setting

        self.class_combo.addItems(self.class_names)

    def init_ui(self):
        """"""
        self.setWindowTitle("CTA回测")

        # Setting Part
        self.class_combo = QtWidgets.QComboBox()

        self.symbol_line = QtWidgets.QLineEdit("")
        self.symbol_label = QtWidgets.QLabel()
        self.data_counts_label = QtWidgets.QLabel()

        #############################################
        # fangyang add, 根据数据库内容进行选项显示
        self.exchange_combo = QtWidgets.QComboBox()
        self.exchange_combo.textActivated.connect(self.onExchangeActivated)

        self.dbbardata_groupby_df = self.db_instance.get_groupby_df()
        if not self.dbbardata_groupby_df.empty:
            self.exchange_combo.addItems(self.dbbardata_groupby_df['exchange'].drop_duplicates().to_list())

        self.symbol_combo = QtWidgets.QComboBox()
        self.symbol_combo.currentIndexChanged.connect(self.onSymbolActivated)

        self.interval_combo = QtWidgets.QComboBox()
        self.interval_combo.currentIndexChanged.connect(self.onIntervalActivated)
        ##########################################

        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=3 * 365)

        self.start_date_edit = QtWidgets.QDateEdit(
            QtCore.QDate(
                start_dt.year,
                start_dt.month,
                start_dt.day
            )
        )
        self.end_date_edit = QtWidgets.QDateEdit(
            QtCore.QDate.currentDate()
        )

        self.rate_line = QtWidgets.QLineEdit("0.000025")
        self.slippage_line = QtWidgets.QLineEdit("0.2")
        self.size_line = QtWidgets.QLineEdit("300")
        self.pricetick_line = QtWidgets.QLineEdit("0.2")
        self.capital_line = QtWidgets.QLineEdit("1000000")

        self.inverse_combo = QtWidgets.QComboBox()
        self.inverse_combo.addItems(["正向", "反向"])

        vnpy_backtesting_button = QtWidgets.QPushButton("开始_vnpy_回测")
        vnpy_backtesting_button.clicked.connect(lambda: self.start_backtesting(BacktesterEngineType.vnpy))

        jnpy_backtesting_button = QtWidgets.QPushButton("开始_jnpy_回测")
        jnpy_backtesting_button.clicked.connect(lambda: self.start_backtesting(BacktesterEngineType.jnpy))

        rl_train_button = QtWidgets.QPushButton("开始RL训练")
        rl_train_button.clicked.connect(self.start_rl_train)

        optimization_button = QtWidgets.QPushButton("参数优化")
        optimization_button.clicked.connect(self.start_optimization)

        self.result_button = QtWidgets.QPushButton("优化结果")
        self.result_button.clicked.connect(self.show_optimization_result)
        self.result_button.setEnabled(False)

        downloading_button = QtWidgets.QPushButton("下载数据")
        downloading_button.clicked.connect(self.start_downloading)

        self.order_button = QtWidgets.QPushButton("委托记录")
        self.order_button.clicked.connect(self.show_backtesting_orders)
        self.order_button.setEnabled(False)

        self.trade_button = QtWidgets.QPushButton("成交记录")
        self.trade_button.clicked.connect(self.show_backtesting_trades)
        self.trade_button.setEnabled(False)

        self.daily_button = QtWidgets.QPushButton("每日盈亏")
        self.daily_button.clicked.connect(self.show_daily_results)
        self.daily_button.setEnabled(False)

        self.candle_button = QtWidgets.QPushButton("K线图表")
        self.candle_button.clicked.connect(self.show_candle_chart)
        self.candle_button.setEnabled(False)

        self.candle_button_web = QtWidgets.QPushButton("K线图表web")
        self.candle_button_web.clicked.connect(self.show_candle_chart_web)

        edit_button = QtWidgets.QPushButton("代码编辑")
        edit_button.clicked.connect(self.edit_strategy_code)

        reload_button = QtWidgets.QPushButton("策略重载")
        reload_button.clicked.connect(self.reload_strategy_class)

        form = QtWidgets.QFormLayout()
        form.addRow("交易策略", self.class_combo)
        form.addRow("交易所代码", self.exchange_combo)
        form.addRow("本地代码", self.symbol_combo)
        form.addRow("合约名称", self.symbol_label)
        form.addRow("K线周期", self.interval_combo)
        form.addRow("开始日期", self.start_date_edit)
        form.addRow("结束日期\n(+1天才能回测到最后这天)", self.end_date_edit)
        form.addRow("DB内总数据量", self.data_counts_label)
        form.addRow("手续费率", self.rate_line)
        form.addRow("交易滑点", self.slippage_line)
        form.addRow("合约乘数", self.size_line)
        form.addRow("价格跳动", self.pricetick_line)
        form.addRow("回测资金", self.capital_line)
        form.addRow("合约模式\n(数字货币用反向)", self.inverse_combo)

        result_grid = QtWidgets.QGridLayout()
        result_grid.addWidget(self.trade_button, 0, 0)
        result_grid.addWidget(self.order_button, 0, 1)
        result_grid.addWidget(self.daily_button, 1, 0)
        result_grid.addWidget(self.candle_button, 1, 1)
        result_grid.addWidget(self.candle_button_web, 2, 1)

        left_vbox = QtWidgets.QVBoxLayout()
        left_vbox.addLayout(form)
        left_vbox.addWidget(vnpy_backtesting_button)
        left_vbox.addWidget(jnpy_backtesting_button)
        left_vbox.addWidget(rl_train_button)
        left_vbox.addWidget(downloading_button)
        left_vbox.addStretch()
        left_vbox.addLayout(result_grid)
        left_vbox.addStretch()
        left_vbox.addWidget(optimization_button)
        left_vbox.addWidget(self.result_button)
        left_vbox.addStretch()
        left_vbox.addWidget(edit_button)
        left_vbox.addWidget(reload_button)

        # Result part
        self.statistics_monitor = StatisticsMonitor()

        self.log_monitor = QtWidgets.QTextEdit()
        self.log_monitor.setMaximumHeight(400)

        self.chart = BacktesterChart()
        self.chart.setMinimumWidth(1000)

        self.trade_dialog = BacktestingResultDialog(
            self.main_engine,
            self.event_engine,
            "回测成交记录",
            BacktestingTradeMonitor
        )
        self.order_dialog = BacktestingResultDialog(
            self.main_engine,
            self.event_engine,
            "回测委托记录",
            BacktestingOrderMonitor
        )
        self.daily_dialog = BacktestingResultDialog(
            self.main_engine,
            self.event_engine,
            "回测每日盈亏",
            DailyResultMonitor
        )

        # Candle Chart
        self.candle_dialog = CandleChartDialog()

        # Layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.statistics_monitor)
        vbox.addWidget(self.log_monitor)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(left_vbox)
        hbox.addLayout(vbox)
        hbox.addWidget(self.chart)
        self.setLayout(hbox)

    def load_backtesting_setting(self):
        """"""
        setting = load_json(self.setting_filename)
        if not setting:
            return

        self.class_combo.setCurrentIndex(
            self.class_combo.findText(setting["class_name"])
        )

        self.symbol_line.setText(setting["vt_symbol"])

        self.interval_combo.setCurrentIndex(
            self.interval_combo.findText(setting["interval"])
        )

        self.rate_line.setText(str(setting["rate"]))
        self.slippage_line.setText(str(setting["slippage"]))
        self.size_line.setText(str(setting["size"]))
        self.pricetick_line.setText(str(setting["pricetick"]))
        self.capital_line.setText(str(setting["capital"]))

        if not setting["inverse"]:
            self.inverse_combo.setCurrentIndex(0)
        else:
            self.inverse_combo.setCurrentIndex(1)

    def onExchangeActivated(self, current_exchange_text):

        '''
        exchange变化触发, 重置symbol QCombox
        '''

        self.symbol_combo.clear()

        self.symbol_combo.addItems(
            self.dbbardata_groupby_df[
                self.dbbardata_groupby_df['exchange'] == current_exchange_text
                ]['symbol'].drop_duplicates().sort_values().to_list()
        )

    def onSymbolActivated(self):

        '''
        symbol变化触发, 重置interval QCombox
        '''

        self.interval_combo.clear()
        current_symbol = self.symbol_combo.currentText()
        current_exchange = self.exchange_combo.currentText()

        self.interval_combo.addItems(
            self.dbbardata_groupby_df[
                (self.dbbardata_groupby_df['symbol'] == current_symbol)
                & (self.dbbardata_groupby_df['exchange'] == current_exchange)
                ]['interval'].to_list()
        )

    def onIntervalActivated(self):

        current_symbol = self.symbol_combo.currentText()
        current_exchange = self.exchange_combo.currentText()
        current_interval = self.interval_combo.currentText()

        count_series = self.dbbardata_groupby_df[
            (self.dbbardata_groupby_df['symbol'] == current_symbol)
            & (self.dbbardata_groupby_df['exchange'] == current_exchange)
            & (self.dbbardata_groupby_df['interval'] == current_interval)
            ]['count(1)']

        if count_series.empty:
            self.data_counts_label.setText("0")
        else:
            self.data_counts_label.setText(f'''{count_series.values[0]}''')

        if current_exchange and current_symbol and current_interval:
            symbol_de_L8_str = current_symbol[:-2]
            if symbol_de_L8_str in self.pytdx_contracts_dict:
                self.symbol_label.setText(f"{self.pytdx_contracts_dict[symbol_de_L8_str]['name']}")
                self.size_line.setText(f"{self.pytdx_contracts_dict[symbol_de_L8_str]['size']}")
                self.pricetick_line.setText(f"{self.pytdx_contracts_dict[symbol_de_L8_str]['pricetick']}")
            # elif current_exchange.lower() in self.pyccxt_exchange.exchange_list:
            #     self.symbol_label.setText(f"{current_symbol}")
            #     cur_exchange_market_info_dict = self.pyccxt_exchange.read_local_market_info_json_file(
            #         current_exchange.lower()
            #     )
            #     if cur_exchange_market_info_dict \
            #             and (current_symbol.replace("_", "/").upper() in cur_exchange_market_info_dict):
            #         market_info = cur_exchange_market_info_dict[current_symbol.replace("_", "/").upper()]
            #         self.pricetick_line.setText(f"{market_info['limits']['price']['min']}")
            #     else:
            #         self.pricetick_line.setText(f"999")
            #     self.size_line.setText(f"{1}")

            # TODO 增加重置日期后统计数据数目
            # 重置日期
            db_end_dt = self.db_instance.get_end_date(
                symbol=current_symbol,
                exchange=Exchange(current_exchange),
                interval=Interval(current_interval)
            )
            db_end_dt = parser.parse(str(db_end_dt))
            db_start_dt = self.db_instance.get_start_date(
                symbol=current_symbol,
                exchange=Exchange(current_exchange),
                interval=Interval(current_interval)
            )
            db_start_dt = parser.parse(str(db_start_dt))
            self.start_date_edit.setDate(
                QtCore.QDate(
                    db_start_dt.year,
                    db_start_dt.month,
                    db_start_dt.day
                )
            )
            self.end_date_edit.setDate(
                QtCore.QDate(
                    db_end_dt.year,
                    db_end_dt.month,
                    db_end_dt.day
                )
            )

    def register_event(self):
        """"""
        self.signal_log.connect(self.process_log_event)
        self.signal_backtesting_finished.connect(
            self.process_backtesting_finished_event)
        self.signal_optimization_finished.connect(
            self.process_optimization_finished_event)

        self.event_engine.register(EVENT_JNPY_BACKTESTER_LOG, self.signal_log.emit)
        self.event_engine.register(EVENT_BACKTESTER_LOG, self.signal_log.emit)

        self.event_engine.register(
            EVENT_JNPY_BACKTESTER_BACKTESTING_FINISHED, self.signal_backtesting_finished.emit)
        self.event_engine.register(
            EVENT_BACKTESTER_BACKTESTING_FINISHED, self.signal_backtesting_finished.emit)

        self.event_engine.register(
            EVENT_JNPY_BACKTESTER_OPTIMIZATION_FINISHED, self.signal_optimization_finished.emit)
        self.event_engine.register(
            EVENT_BACKTESTER_OPTIMIZATION_FINISHED, self.signal_optimization_finished.emit)

    def process_log_event(self, event: Event):
        """"""
        msg = event.data
        self.write_log(msg)

    def write_log(self, msg):
        """"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"{timestamp}\t{msg}"
        self.log_monitor.append(msg)

    def process_backtesting_finished_event(self, event: Event):
        """"""
        engine = self.get_current_backtester_engine()

        # 这里statistics是个dict
        statistics = engine.get_result_statistics()
        statistics_deep_copy = copy.deepcopy(statistics)

        df = engine.get_result_df()

        # 将上面的dict直接传入set_data, 然后再里面对其进行修改,
        # 所以数据类型从float变成了str
        # 正确做法这里应该使用一次深拷贝
        self.statistics_monitor.set_data(statistics_deep_copy)
        self.chart.set_data(df)

        self.trade_button.setEnabled(True)
        self.order_button.setEnabled(True)
        self.daily_button.setEnabled(True)

        # Tick data can not be displayed using candle chart
        interval = self.interval_combo.currentText()
        if interval != Interval.TICK.value:
            self.candle_button.setEnabled(True)

    def process_optimization_finished_event(self, event: Event):
        """"""
        self.write_log("请点击[优化结果]按钮查看")
        self.result_button.setEnabled(True)

    def start_rl_train(self):

        print("start RL !!!")
        class_name = self.class_combo.currentText()
        vt_symbol = f"{self.symbol_combo.currentText()}.{self.exchange_combo.currentText()}"
        interval = self.interval_combo.currentText()
        start = self.start_date_edit.date().toPyDate()
        end = self.end_date_edit.date().toPyDate()
        rate = float(self.rate_line.text())
        slippage = float(self.slippage_line.text())
        size = float(self.size_line.text())
        pricetick = float(self.pricetick_line.text())
        capital = float(self.capital_line.text())

        if self.inverse_combo.currentText() == "正向":
            inverse = False
        else:
            inverse = True

        # backtesting_debug_mode = True
        # Get strategy setting
        old_setting = self.settings[class_name]
        dialog = BacktestingSettingEditor(class_name, old_setting)
        i = dialog.exec()
        if i != dialog.Accepted:
            return

        new_setting = dialog.get_setting()
        self.settings[class_name] = new_setting

        result = self.jnpy_backtester_engine.rl_training(
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
            new_setting
        )

    def start_backtesting(self, engine_type: BacktesterEngineType):
        """"""
        class_name = self.class_combo.currentText()
        vt_symbol = f"{self.symbol_combo.currentText()}.{self.exchange_combo.currentText()}"
        interval = self.interval_combo.currentText()
        start = self.start_date_edit.dateTime().toPython()
        end = self.end_date_edit.dateTime().toPython()
        rate = float(self.rate_line.text())
        slippage = float(self.slippage_line.text())
        size = float(self.size_line.text())
        pricetick = float(self.pricetick_line.text())
        capital = float(self.capital_line.text())

        if self.inverse_combo.currentText() == "正向":
            inverse = False
        else:
            inverse = True

        # Check validity of vt_symbol
        if "." not in vt_symbol:
            self.write_log("本地代码缺失交易所后缀，请检查")
            return

        _, exchange_str = vt_symbol.split(".")
        if exchange_str not in Exchange.__members__:
            self.write_log("本地代码的交易所后缀不正确，请检查")
            return

        # Save backtesting parameters
        backtesting_setting = {
            "class_name": class_name,
            "vt_symbol": vt_symbol,
            "interval": interval,
            "start": start.isoformat(),
            "rate": rate,
            "slippage": slippage,
            "size": size,
            "pricetick": pricetick,
            "capital": capital,
            "inverse": inverse,
        }
        save_json(self.setting_filename, backtesting_setting)

        # Get strategy setting
        old_setting = self.settings[class_name]
        dialog = BacktestingSettingEditor(class_name, old_setting)
        i = dialog.exec()
        if i != dialog.Accepted:
            return

        new_setting = dialog.get_setting()
        self.settings[class_name] = new_setting

        if engine_type == BacktesterEngineType.vnpy:
            result = self.vnpy_backtester_engine.start_backtesting(
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
                new_setting
            )
            self.last_backtester_engine_type = engine_type

        elif engine_type == BacktesterEngineType.jnpy:
            result = self.jnpy_backtester_engine.start_backtesting(
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
                new_setting
            )
            self.last_backtester_engine_type = engine_type

        if result:
            self.statistics_monitor.clear_data()
            self.chart.clear_data()

            self.trade_button.setEnabled(False)
            self.order_button.setEnabled(False)
            self.daily_button.setEnabled(False)
            self.candle_button.setEnabled(False)

            self.trade_dialog.clear_data()
            self.order_dialog.clear_data()
            self.daily_dialog.clear_data()
            self.candle_dialog.clear_data()

    def start_optimization(self):
        """"""
        class_name = self.class_combo.currentText()
        vt_symbol = f"{self.symbol_combo.currentText()}.{self.exchange_combo.currentText()}"
        interval = self.interval_combo.currentText()
        start = self.start_date_edit.dateTime().toPyDateTime()
        end = self.end_date_edit.dateTime().toPyDateTime()
        rate = float(self.rate_line.text())
        slippage = float(self.slippage_line.text())
        size = float(self.size_line.text())
        pricetick = float(self.pricetick_line.text())
        capital = float(self.capital_line.text())

        if self.inverse_combo.currentText() == "正向":
            inverse = False
        else:
            inverse = True

        parameters = self.settings[class_name]
        dialog = OptimizationSettingEditor(class_name, parameters)
        i = dialog.exec()
        if i != dialog.Accepted:
            return

        optimization_setting, use_ga = dialog.get_setting()
        self.target_display = dialog.target_display

        engine = self.get_current_backtester_engine()
        engine.start_optimization(
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
            optimization_setting,
            use_ga
        )

        self.result_button.setEnabled(False)

    def start_downloading(self):
        """"""
        vt_symbol = self.symbol_line.text()
        interval = self.interval_combo.currentText()
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()

        start = datetime(
            start_date.year(),
            start_date.month(),
            start_date.day(),
        )
        start = DB_TZ.localize(start)

        end = datetime(
            end_date.year(),
            end_date.month(),
            end_date.day(),
            23,
            59,
            59,
        )
        end = DB_TZ.localize(end)

        engine = self.get_current_backtester_engine()
        engine.start_downloading(
            vt_symbol,
            interval,
            start,
            end
        )

    def show_optimization_result(self):
        """"""
        engine = self.get_current_backtester_engine()

        result_values = engine.get_result_values()

        dialog = OptimizationResultMonitor(
            result_values,
            self.target_display
        )
        dialog.exec_()

    def show_backtesting_trades(self):
        """"""
        engine = self.get_current_backtester_engine()

        if not self.trade_dialog.is_updated():
            trades = engine.get_all_trades()
            self.trade_dialog.update_data(trades)

        self.trade_dialog.exec_()

    def show_backtesting_orders(self):
        """"""
        engine = self.get_current_backtester_engine()

        if not self.order_dialog.is_updated():
            orders = engine.get_all_orders()
            self.order_dialog.update_data(orders)

        self.order_dialog.exec_()

    def show_daily_results(self):
        """"""
        engine = self.get_current_backtester_engine()

        if not self.daily_dialog.is_updated():
            results = engine.get_all_daily_results()
            self.daily_dialog.update_data(results)

        self.daily_dialog.exec_()

    def show_candle_chart_web(self):

        engine = self.get_current_backtester_engine()

        # 所有的 BarData
        history = engine.get_history_data()
        # 比history少了初始化用掉的那些bars, 多了pnl信息
        results = engine.get_all_daily_results()
        # 真实发生交易的结果, 都是成交的订单
        # trades = self.backtester_engine.get_all_trades()
        # 策略实际产生的订单, 包括未成交订单
        orders = engine.get_all_orders()

        # statistics = engine.get_result_statistics()
        result_df = engine.get_result_df()

        # TODO 从策略中获取使用的ta-lib技术指标信息
        strategy_tech_visual_list = engine.backtesting_engine.strategy.variables
        strategy_tech_visual_list = ["am.sma(n=5, array=True)", "am.sma(10, True)"]
        file_path = draw_chart(history, results, orders, strategy_tech_visual_list, result_df)

        webbrowser.open(file_path)

    def show_candle_chart(self):
        """"""
        engine = self.get_current_backtester_engine()

        if not self.candle_dialog.is_updated():
            history = engine.get_history_data()
            self.candle_dialog.update_history(history)

            trades = engine.get_all_trades()
            self.candle_dialog.update_trades(trades)

        self.candle_dialog.exec_()

    def edit_strategy_code(self):
        """"""
        class_name = self.class_combo.currentText()

        if not class_name:
            return

        file_path = self.backtester_engine.get_strategy_class_file(class_name)
        cmd = ["code", file_path]

        p: subprocess.CompletedProcess = subprocess.run(cmd, shell=True)
        if p.returncode:
            QtWidgets.QMessageBox.warning(
                self,
                "启动代码编辑器失败",
                "请检查是否安装了Visual Studio Code，并将其路径添加到了系统全局变量中！"
            )

    def reload_strategy_class(self):
        """"""
        engine = self.get_current_backtester_engine()

        engine.reload_strategy_class()

        current_strategy_name = self.class_combo.currentText()

        self.class_combo.clear()
        self.init_strategy_settings()

        ix = self.class_combo.findText(current_strategy_name)
        self.class_combo.setCurrentIndex(ix)

    def show(self):
        """"""
        self.showMaximized()

    def get_current_backtester_engine(self):

        if self.last_backtester_engine_type == BacktesterEngineType.vnpy:
            return self.vnpy_backtester_engine
        elif self.last_backtester_engine_type == BacktesterEngineType.jnpy:
            return self.jnpy_backtester_engine

        return None


class StatisticsMonitor(QtWidgets.QTableWidget):
    """"""
    KEY_NAME_MAP = {
        "start_date": "首个交易日",
        "end_date": "最后交易日",

        "total_days": "总交易日",
        "profit_days": "盈利交易日",
        "loss_days": "亏损交易日",

        "capital": "起始资金",
        "end_balance": "结束资金",

        "total_return": "总收益率",
        "annual_return": "年化收益",
        "max_drawdown": "最大回撤",
        "max_ddpercent": "百分比最大回撤",

        "total_net_pnl": "总盈亏",
        "total_commission": "总手续费",
        "total_slippage": "总滑点",
        "total_turnover": "总成交额",
        "total_trade_count": "总成交笔数",

        "daily_net_pnl": "日均盈亏",
        "daily_commission": "日均手续费",
        "daily_slippage": "日均滑点",
        "daily_turnover": "日均成交额",
        "daily_trade_count": "日均成交笔数",

        "daily_return": "日均收益率",
        "return_std": "收益标准差",
        "sharpe_ratio": "夏普比率",
        "return_drawdown_ratio": "收益回撤比"
    }

    def __init__(self):
        """"""
        super().__init__()

        self.cells = {}

        self.init_ui()

    def init_ui(self):
        """"""
        self.setRowCount(len(self.KEY_NAME_MAP))
        self.setVerticalHeaderLabels(list(self.KEY_NAME_MAP.values()))

        self.setColumnCount(1)
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.setEditTriggers(self.NoEditTriggers)

        for row, key in enumerate(self.KEY_NAME_MAP.keys()):
            cell = QtWidgets.QTableWidgetItem()
            self.setItem(row, 0, cell)
            self.cells[key] = cell

    def clear_data(self):
        """"""
        for cell in self.cells.values():
            cell.setText("")

    def set_data(self, data: dict):
        """"""
        data["capital"] = f"{data['capital']:.2f}"
        data["end_balance"] = f"{data['end_balance']:,.2f}"
        data["total_return"] = f"{data['total_return']:,.2f}%"
        data["annual_return"] = f"{data['annual_return']:,.2f}%"
        data["max_drawdown"] = f"{data['max_drawdown']:,.2f}"
        data["max_ddpercent"] = f"{data['max_ddpercent']:,.2f}%"
        data["total_net_pnl"] = f"{data['total_net_pnl']:,.2f}"
        data["total_commission"] = f"{data['total_commission']:,.2f}"
        data["total_slippage"] = f"{data['total_slippage']:,.2f}"
        data["total_turnover"] = f"{data['total_turnover']:,.2f}"
        data["daily_net_pnl"] = f"{data['daily_net_pnl']:,.2f}"
        data["daily_commission"] = f"{data['daily_commission']:,.2f}"
        data["daily_slippage"] = f"{data['daily_slippage']:,.2f}"
        data["daily_turnover"] = f"{data['daily_turnover']:,.2f}"
        data["daily_trade_count"] = f"{data['daily_trade_count']:,.2f}"
        data["daily_return"] = f"{data['daily_return']:,.2f}%"
        data["return_std"] = f"{data['return_std']:,.2f}%"
        data["sharpe_ratio"] = f"{data['sharpe_ratio']:,.2f}"
        data["return_drawdown_ratio"] = f"{data['return_drawdown_ratio']:,.2f}"

        for key, cell in self.cells.items():
            value = data.get(key, "")
            cell.setText(str(value))


class BacktestingSettingEditor(QtWidgets.QDialog):
    """
    For creating new strategy and editing strategy parameters.
    """

    def __init__(
            self, class_name: str, parameters: dict
    ):
        """"""
        super(BacktestingSettingEditor, self).__init__()

        self.class_name = class_name
        self.parameters = parameters
        self.edits = {}

        self.init_ui()

    def init_ui(self):
        """"""
        form = QtWidgets.QFormLayout()

        # Add vt_symbol and name edit if add new strategy
        self.setWindowTitle(f"策略参数配置：{self.class_name}")
        button_text = "确定"
        parameters = self.parameters

        for name, value in parameters.items():
            type_ = type(value)

            edit = QtWidgets.QLineEdit(str(value))
            if type_ is int:
                validator = QtGui.QIntValidator()
                edit.setValidator(validator)
            elif type_ is float:
                validator = QtGui.QDoubleValidator()
                edit.setValidator(validator)

            form.addRow(f"{name} {type_}", edit)

            self.edits[name] = (edit, type_)

        button = QtWidgets.QPushButton(button_text)
        button.clicked.connect(self.accept)
        form.addRow(button)

        widget = QtWidgets.QWidget()
        widget.setLayout(form)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(scroll)
        self.setLayout(vbox)

    def get_setting(self):
        """"""
        setting = {}

        for name, tp in self.edits.items():
            edit, type_ = tp
            value_text = edit.text()

            if type_ == bool:
                if value_text == "True":
                    value = True
                else:
                    value = False
            else:
                value = type_(value_text)

            setting[name] = value

        return setting


class BacktesterChart(pg.GraphicsWindow):
    """"""

    def __init__(self):
        """"""
        super().__init__(title="Backtester Chart")

        self.dates = {}

        self.init_ui()

    def init_ui(self):
        """"""
        pg.setConfigOptions(antialias=True)

        # Create plot widgets
        self.balance_plot = self.addPlot(
            title="账户净值",
            axisItems={"bottom": DateAxis(self.dates, orientation="bottom")}
        )
        self.nextRow()

        self.drawdown_plot = self.addPlot(
            title="净值回撤",
            axisItems={"bottom": DateAxis(self.dates, orientation="bottom")}
        )
        self.nextRow()

        self.pnl_plot = self.addPlot(
            title="每日盈亏",
            axisItems={"bottom": DateAxis(self.dates, orientation="bottom")}
        )
        self.nextRow()

        self.distribution_plot = self.addPlot(title="盈亏分布")

        # Add curves and bars on plot widgets
        self.balance_curve = self.balance_plot.plot(
            pen=pg.mkPen("#ffc107", width=3)
        )

        dd_color = "#303f9f"
        self.drawdown_curve = self.drawdown_plot.plot(
            fillLevel=-0.3, brush=dd_color, pen=dd_color
        )

        profit_color = 'r'
        loss_color = 'g'
        self.profit_pnl_bar = pg.BarGraphItem(
            x=[], height=[], width=0.3, brush=profit_color, pen=profit_color
        )
        self.loss_pnl_bar = pg.BarGraphItem(
            x=[], height=[], width=0.3, brush=loss_color, pen=loss_color
        )
        self.pnl_plot.addItem(self.profit_pnl_bar)
        self.pnl_plot.addItem(self.loss_pnl_bar)

        distribution_color = "#6d4c41"
        self.distribution_curve = self.distribution_plot.plot(
            fillLevel=-0.3, brush=distribution_color, pen=distribution_color
        )

    def clear_data(self):
        """"""
        self.balance_curve.setData([], [])
        self.drawdown_curve.setData([], [])
        self.profit_pnl_bar.setOpts(x=[], height=[])
        self.loss_pnl_bar.setOpts(x=[], height=[])
        self.distribution_curve.setData([], [])

    def set_data(self, df):
        """"""
        if df is None:
            return

        count = len(df)

        self.dates.clear()
        for n, date in enumerate(df.index):
            self.dates[n] = date

        # Set data for curve of balance and drawdown
        self.balance_curve.setData(df["balance"])
        self.drawdown_curve.setData(df["drawdown"])

        # Set data for daily pnl bar
        profit_pnl_x = []
        profit_pnl_height = []
        loss_pnl_x = []
        loss_pnl_height = []

        for count, pnl in enumerate(df["net_pnl"]):
            if pnl >= 0:
                profit_pnl_height.append(pnl)
                profit_pnl_x.append(count)
            else:
                loss_pnl_height.append(pnl)
                loss_pnl_x.append(count)

        self.profit_pnl_bar.setOpts(x=profit_pnl_x, height=profit_pnl_height)
        self.loss_pnl_bar.setOpts(x=loss_pnl_x, height=loss_pnl_height)

        # Set data for pnl distribution
        hist, x = np.histogram(df["net_pnl"], bins="auto")
        x = x[:-1]
        self.distribution_curve.setData(x, hist)


class DateAxis(pg.AxisItem):
    """Axis for showing date data"""

    def __init__(self, dates: dict, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.dates = dates

    def tickStrings(self, values, scale, spacing):
        """"""
        strings = []
        for v in values:
            dt = self.dates.get(v, "")
            strings.append(str(dt))
        return strings


class OptimizationSettingEditor(QtWidgets.QDialog):
    """
    For setting up parameters for optimization.
    """
    DISPLAY_NAME_MAP = {
        "总收益率": "total_return",
        "夏普比率": "sharpe_ratio",
        "收益回撤比": "return_drawdown_ratio",
        "日均盈亏": "daily_net_pnl"
    }

    def __init__(
            self, class_name: str, parameters: dict
    ):
        """"""
        super().__init__()

        self.class_name = class_name
        self.parameters = parameters
        self.edits = {}

        self.optimization_setting = None
        self.use_ga = False

        self.init_ui()

    def init_ui(self):
        """"""
        QLabel = QtWidgets.QLabel

        self.target_combo = QtWidgets.QComboBox()
        self.target_combo.addItems(list(self.DISPLAY_NAME_MAP.keys()))

        grid = QtWidgets.QGridLayout()
        grid.addWidget(QLabel("目标"), 0, 0)
        grid.addWidget(self.target_combo, 0, 1, 1, 3)
        grid.addWidget(QLabel("参数"), 1, 0)
        grid.addWidget(QLabel("开始"), 1, 1)
        grid.addWidget(QLabel("步进"), 1, 2)
        grid.addWidget(QLabel("结束"), 1, 3)

        # Add vt_symbol and name edit if add new strategy
        self.setWindowTitle(f"优化参数配置：{self.class_name}")

        validator = QtGui.QDoubleValidator()
        row = 2

        for name, value in self.parameters.items():
            type_ = type(value)
            if type_ not in [int, float]:
                continue

            start_edit = QtWidgets.QLineEdit(str(value))
            step_edit = QtWidgets.QLineEdit(str(1))
            end_edit = QtWidgets.QLineEdit(str(value))

            for edit in [start_edit, step_edit, end_edit]:
                edit.setValidator(validator)

            grid.addWidget(QLabel(name), row, 0)
            grid.addWidget(start_edit, row, 1)
            grid.addWidget(step_edit, row, 2)
            grid.addWidget(end_edit, row, 3)

            self.edits[name] = {
                "type": type_,
                "start": start_edit,
                "step": step_edit,
                "end": end_edit
            }

            row += 1

        parallel_button = QtWidgets.QPushButton("多进程优化")
        parallel_button.clicked.connect(self.generate_parallel_setting)
        grid.addWidget(parallel_button, row, 0, 1, 4)

        row += 1
        ga_button = QtWidgets.QPushButton("遗传算法优化")
        ga_button.clicked.connect(self.generate_ga_setting)
        grid.addWidget(ga_button, row, 0, 1, 4)

        widget = QtWidgets.QWidget()
        widget.setLayout(grid)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(scroll)
        self.setLayout(vbox)

    def generate_ga_setting(self):
        """"""
        self.use_ga = True
        self.generate_setting()

    def generate_parallel_setting(self):
        """"""
        self.use_ga = False
        self.generate_setting()

    def generate_setting(self):
        """"""
        self.optimization_setting = OptimizationSetting()

        self.target_display = self.target_combo.currentText()
        target_name = self.DISPLAY_NAME_MAP[self.target_display]
        self.optimization_setting.set_target(target_name)

        for name, d in self.edits.items():
            type_ = d["type"]
            start_value = type_(d["start"].text())
            step_value = type_(d["step"].text())
            end_value = type_(d["end"].text())

            if start_value == end_value:
                self.optimization_setting.add_parameter(name, start_value)
            else:
                self.optimization_setting.add_parameter(
                    name,
                    start_value,
                    end_value,
                    step_value
                )

        self.accept()

    def get_setting(self):
        """"""
        return self.optimization_setting, self.use_ga


class OptimizationResultMonitor(QtWidgets.QDialog):
    """
    For viewing optimization result.
    """

    def __init__(
            self, result_values: list, target_display: str
    ):
        """"""
        super().__init__()

        self.result_values = result_values
        self.target_display = target_display

        self.init_ui()

    def init_ui(self):
        """"""
        self.setWindowTitle("参数优化结果")
        self.resize(1100, 500)

        # Creat table to show result
        table = QtWidgets.QTableWidget()

        table.setColumnCount(2)
        table.setRowCount(len(self.result_values))
        table.setHorizontalHeaderLabels(["参数", self.target_display])
        table.setEditTriggers(table.NoEditTriggers)
        table.verticalHeader().setVisible(False)

        table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch
        )

        for n, tp in enumerate(self.result_values):
            setting, target_value, _ = tp
            setting_cell = QtWidgets.QTableWidgetItem(str(setting))
            target_cell = QtWidgets.QTableWidgetItem(f"{target_value:.2f}")

            setting_cell.setTextAlignment(QtCore.Qt.AlignCenter)
            target_cell.setTextAlignment(QtCore.Qt.AlignCenter)

            table.setItem(n, 0, setting_cell)
            table.setItem(n, 1, target_cell)

        # Create layout
        button = QtWidgets.QPushButton("保存")
        button.clicked.connect(self.save_csv)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(button)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(table)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def save_csv(self) -> None:
        """
        Save table data into a csv file
        """
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "保存数据", "", "CSV(*.csv)")

        if not path:
            return

        with open(path, "w") as f:
            writer = csv.writer(f, lineterminator="\n")

            writer.writerow(["参数", self.target_display])

            for tp in self.result_values:
                setting, target_value, _ = tp
                row_data = [str(setting), str(target_value)]
                writer.writerow(row_data)


class BacktestingTradeMonitor(BaseMonitor):
    """
    Monitor for backtesting trade data.
    """

    headers = {
        "tradeid": {"display": "成交号 ", "cell": BaseCell, "update": False},
        "orderid": {"display": "委托号", "cell": BaseCell, "update": False},
        "symbol": {"display": "代码", "cell": BaseCell, "update": False},
        "exchange": {"display": "交易所", "cell": EnumCell, "update": False},
        "direction": {"display": "方向", "cell": DirectionCell, "update": False},
        "offset": {"display": "开平", "cell": EnumCell, "update": False},
        "price": {"display": "价格", "cell": BaseCell, "update": False},
        "volume": {"display": "数量", "cell": BaseCell, "update": False},
        "datetime": {"display": "时间", "cell": BaseCell, "update": False},
        "gateway_name": {"display": "接口", "cell": BaseCell, "update": False},
    }


class BacktestingOrderMonitor(BaseMonitor):
    """
    Monitor for backtesting order data.
    """

    headers = {
        "orderid": {"display": "委托号", "cell": BaseCell, "update": False},
        "symbol": {"display": "代码", "cell": BaseCell, "update": False},
        "exchange": {"display": "交易所", "cell": EnumCell, "update": False},
        "type": {"display": "类型", "cell": EnumCell, "update": False},
        "direction": {"display": "方向", "cell": DirectionCell, "update": False},
        "offset": {"display": "开平", "cell": EnumCell, "update": False},
        "price": {"display": "价格", "cell": BaseCell, "update": False},
        "volume": {"display": "总数量", "cell": BaseCell, "update": False},
        "traded": {"display": "已成交", "cell": BaseCell, "update": False},
        "status": {"display": "状态", "cell": EnumCell, "update": False},
        "datetime": {"display": "时间", "cell": BaseCell, "update": False},
        "gateway_name": {"display": "接口", "cell": BaseCell, "update": False},
    }


class FloatCell(BaseCell):
    """
    Cell used for showing pnl data.
    """

    def __init__(self, content, data):
        """"""
        content = f"{content:.2f}"
        super().__init__(content, data)


class DailyResultMonitor(BaseMonitor):
    """
    Monitor for backtesting daily result.
    """

    headers = {
        "date": {"display": "日期", "cell": BaseCell, "update": False},
        "trade_count": {"display": "成交笔数", "cell": BaseCell, "update": False},
        "start_pos": {"display": "开盘持仓", "cell": BaseCell, "update": False},
        "end_pos": {"display": "收盘持仓", "cell": BaseCell, "update": False},
        "turnover": {"display": "成交额", "cell": FloatCell, "update": False},
        "commission": {"display": "手续费", "cell": FloatCell, "update": False},
        "slippage": {"display": "滑点", "cell": FloatCell, "update": False},
        "trading_pnl": {"display": "交易盈亏", "cell": FloatCell, "update": False},
        "holding_pnl": {"display": "持仓盈亏", "cell": FloatCell, "update": False},
        "total_pnl": {"display": "总盈亏", "cell": FloatCell, "update": False},
        "net_pnl": {"display": "净盈亏", "cell": FloatCell, "update": False},
    }


class BacktestingResultDialog(QtWidgets.QDialog):
    """
    """

    def __init__(
            self,
            main_engine: MainEngine,
            event_engine: EventEngine,
            title: str,
            table_class: QtWidgets.QTableWidget
    ):
        """"""
        super().__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine
        self.title = title
        self.table_class = table_class

        self.updated = False

        self.init_ui()

    def init_ui(self):
        """"""
        self.setWindowTitle(self.title)
        self.resize(1100, 600)

        self.table = self.table_class(self.main_engine, self.event_engine)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.table)

        self.setLayout(vbox)

    def clear_data(self):
        """"""
        self.updated = False
        self.table.setRowCount(0)

    def update_data(self, data: list):
        """"""
        self.updated = True

        data.reverse()
        for obj in data:
            self.table.insert_new_row(obj)

    def is_updated(self):
        """"""
        return self.updated


class CandleChartDialog(QtWidgets.QDialog):
    """
    """

    def __init__(self):
        """"""
        super().__init__()

        self.updated = False

        self.dt_ix_map = {}
        self.ix_bar_map = {}

        self.high_price = 0
        self.low_price = 0
        self.price_range = 0

        self.items = []

        self.init_ui()

    def init_ui(self):
        """"""
        self.setWindowTitle("回测K线图表")
        self.resize(1400, 800)

        # Create chart widget
        self.chart = ChartWidget()
        self.chart.add_plot("candle", hide_x_axis=True)
        self.chart.add_plot("volume", maximum_height=200)
        self.chart.add_plot("others", maximum_height=200)
        self.chart.add_plot("balance", maximum_height=200)
        self.chart.add_item(CandleItem, "candle", "candle")
        self.chart.add_item(VolumeItem, "volume", "volume")
        self.chart.add_item(LineItem, "others", "others")
        self.chart.add_item(BalanceLineItem, "balance", "balance")
        self.chart.add_cursor()

        # Create help widget
        text1 = "红色虚线 —— 盈利交易"
        label1 = QtWidgets.QLabel(text1)
        label1.setStyleSheet("color:red")

        text2 = "绿色虚线 —— 亏损交易"
        label2 = QtWidgets.QLabel(text2)
        label2.setStyleSheet("color:#00FF00")

        text3 = "黄色向上箭头 —— 买入开仓 Buy"
        label3 = QtWidgets.QLabel(text3)
        label3.setStyleSheet("color:yellow")

        text4 = "黄色向下箭头 —— 卖出平仓 Sell"
        label4 = QtWidgets.QLabel(text4)
        label4.setStyleSheet("color:yellow")

        text5 = "紫红向下箭头 —— 卖出开仓 Short"
        label5 = QtWidgets.QLabel(text5)
        label5.setStyleSheet("color:magenta")

        text6 = "紫红向上箭头 —— 买入平仓 Cover"
        label6 = QtWidgets.QLabel(text6)
        label6.setStyleSheet("color:magenta")

        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch()
        hbox1.addWidget(label1)
        hbox1.addStretch()
        hbox1.addWidget(label2)
        hbox1.addStretch()

        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addStretch()
        hbox2.addWidget(label3)
        hbox2.addStretch()
        hbox2.addWidget(label4)
        hbox2.addStretch()

        hbox3 = QtWidgets.QHBoxLayout()
        hbox3.addStretch()
        hbox3.addWidget(label5)
        hbox3.addStretch()
        hbox3.addWidget(label6)
        hbox3.addStretch()

        # Set layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.chart)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        self.setLayout(vbox)

    def update_history(self, history: list):
        """"""
        self.updated = True
        self.chart.update_history(history)

        for ix, bar in enumerate(history):
            self.ix_bar_map[ix] = bar
            self.dt_ix_map[bar.datetime] = ix

            if not self.high_price:
                self.high_price = bar.high_price
                self.low_price = bar.low_price
            else:
                self.high_price = max(self.high_price, bar.high_price)
                self.low_price = min(self.low_price, bar.low_price)

        self.price_range = self.high_price - self.low_price

    def update_trades(self, trades: list):
        """"""
        trade_pairs = generate_trade_pairs(trades)

        candle_plot = self.chart.get_plot("candle")

        scatter_data = []

        y_adjustment = self.price_range * 0.001

        for d in trade_pairs:
            open_ix = self.dt_ix_map[d["open_dt"]]
            close_ix = self.dt_ix_map[d["close_dt"]]
            open_price = d["open_price"]
            close_price = d["close_price"]

            # Trade Line
            x = [open_ix, close_ix]
            y = [open_price, close_price]

            if d["direction"] == Direction.LONG and close_price >= open_price:
                color = "r"
            elif d["direction"] == Direction.SHORT and close_price <= open_price:
                color = "r"
            else:
                color = "g"

            pen = pg.mkPen(color, width=1.5, style=QtCore.Qt.DashLine)
            item = pg.PlotCurveItem(x, y, pen=pen)

            self.items.append(item)
            candle_plot.addItem(item)

            # Trade Scatter
            open_bar = self.ix_bar_map[open_ix]
            close_bar = self.ix_bar_map[close_ix]

            if d["direction"] == Direction.LONG:
                scatter_color = "yellow"
                open_symbol = "t1"
                close_symbol = "t"
                open_side = 1
                close_side = -1
                open_y = open_bar.low_price
                close_y = close_bar.high_price
            else:
                scatter_color = "magenta"
                open_symbol = "t"
                close_symbol = "t1"
                open_side = -1
                close_side = 1
                open_y = open_bar.high_price
                close_y = close_bar.low_price

            pen = pg.mkPen(QtGui.QColor(scatter_color))
            brush = pg.mkBrush(QtGui.QColor(scatter_color))
            size = 10

            open_scatter = {
                "pos": (open_ix, open_y - open_side * y_adjustment),
                "size": size,
                "pen": pen,
                "brush": brush,
                "symbol": open_symbol
            }

            close_scatter = {
                "pos": (close_ix, close_y - close_side * y_adjustment),
                "size": size,
                "pen": pen,
                "brush": brush,
                "symbol": close_symbol
            }

            scatter_data.append(open_scatter)
            scatter_data.append(close_scatter)

            # Trade text
            volume = d["volume"]
            text_color = QtGui.QColor(scatter_color)
            open_text = pg.TextItem(f"[{volume}]", color=text_color, anchor=(0.5, 0.5))
            close_text = pg.TextItem(f"[{volume}]", color=text_color, anchor=(0.5, 0.5))

            open_text.setPos(open_ix, open_y - open_side * y_adjustment * 3)
            close_text.setPos(close_ix, close_y - close_side * y_adjustment * 3)

            self.items.append(open_text)
            self.items.append(close_text)

            candle_plot.addItem(open_text)
            candle_plot.addItem(close_text)

        trade_scatter = pg.ScatterPlotItem(scatter_data)
        self.items.append(trade_scatter)
        candle_plot.addItem(trade_scatter)

    def update_indicates(self, indicates: Dict[str, Dict[str, list]], plot_name: str = "candle"):
        ''' 在策略中记录技术指标, 使用该方法更新到 k线图表中 '''
        candle_plot = self.chart.get_plot(plot_name)

        # if candle_plot is None:
        #     self.chart.add_plot(plot_name=plot_name, maximum_height=200)
        #     candle_plot = self.chart.get_plot(plot_name)
        #     self.chart.add_item(LineItem, plot_name, plot_name)
        #
        #     # Update limit for y-axis
        #     y_min, y_max = 0, 0
        #     for key, indicate_dict in indicates.items():
        #         if key == 'dt':
        #             continue
        #         y_min = min(min(indicate_dict['value']), y_min)
        #         y_max = max(max(indicate_dict['value']), y_max)
        #
        #     candle_plot.setYRange(y_min, y_max)

        x = [self.dt_ix_map[key] for key in indicates['dt']]

        for key, indicate_dict in indicates.items():

            if key == 'dt':
                continue

            pen = indicate_dict.get('pen', pg.mkPen('y', width=1, style=QtCore.Qt.DashLine))
            item = pg.PlotCurveItem(x, indicate_dict['value'], pen=pen, name=key)
            self.items.append(item)
            candle_plot.addItem(item)
            # if plot_name== "others":
            #     pass

    def clear_data(self):
        """"""
        self.updated = False

        candle_plot = self.chart.get_plot("candle")
        for item in self.items:
            candle_plot.removeItem(item)
        self.items.clear()

        self.chart.clear_all()

        self.dt_ix_map.clear()
        self.ix_bar_map.clear()

    def is_updated(self):
        """"""
        return self.updated


def generate_trade_pairs(trades: list) -> list:
    """"""
    long_trades = []
    short_trades = []
    trade_pairs = []

    for trade in trades:
        trade = copy.deepcopy(trade)

        if trade.direction == Direction.LONG:
            same_direction = long_trades
            opposite_direction = short_trades
        else:
            same_direction = short_trades
            opposite_direction = long_trades

        while trade.volume and opposite_direction:
            open_trade = opposite_direction[0]

            close_volume = min(open_trade.volume, trade.volume)
            d = {
                "open_dt": open_trade.datetime,
                "open_price": open_trade.price,
                "close_dt": trade.datetime,
                "close_price": trade.price,
                "direction": open_trade.direction,
                "volume": close_volume,
            }
            trade_pairs.append(d)

            open_trade.volume -= close_volume
            if not open_trade.volume:
                opposite_direction.pop(0)

            trade.volume -= close_volume

        if trade.volume:
            same_direction.append(trade)

    return trade_pairs
