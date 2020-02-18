"""
Author: Zehua Wei (nanoric)
"""

from vnpy.event import EventEngine
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtCore, QtWidgets

from ..engine import APP_NAME
# from ..engine import APP_NAME

from jnpy.DataSource.pytdx.contracts import read_contracts_json_dict


class PytdxLoaderWidget(QtWidgets.QWidget):
    """"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__()

        self.engine = main_engine.get_engine(APP_NAME)

        self.progress_bar_dict = {}
        self.init_ui()

    def init_ui(self):
        """"""
        self.setWindowTitle("pytdx载入")
        # self.setFixedWidth(600)

        self.setWindowFlags(
            (self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
            & ~QtCore.Qt.WindowMaximizeButtonHint)

        hbox_layout = QtWidgets.QHBoxLayout()

        load_button = QtWidgets.QPushButton("载入数据.to_db")
        load_button.clicked.connect(self.load_data)

        to_csv_button = QtWidgets.QPushButton("载入数据.to_csv")
        to_csv_button.clicked.connect(self.load_data)

        self.symbol_type = QtWidgets.QLineEdit("L8")

        self.symbol_combo = QtWidgets.QComboBox()
        self.exchange_combo = QtWidgets.QComboBox()
        for i in Exchange:
            self.exchange_combo.addItem(str(i.name), i)
        self.exchange_combo.activated[str].connect(self.onExchangeActivated)

        self.interval_combo = QtWidgets.QComboBox()
        for i in Interval:
            self.interval_combo.addItem(str(i.name), i)

        self.datetime_edit = QtWidgets.QLineEdit("Datetime")
        self.open_edit = QtWidgets.QLineEdit("Open")
        self.high_edit = QtWidgets.QLineEdit("High")
        self.low_edit = QtWidgets.QLineEdit("Low")
        self.close_edit = QtWidgets.QLineEdit("Close")
        self.volume_edit = QtWidgets.QLineEdit("Volume")
        self.open_interest_edit = QtWidgets.QLineEdit("OpenInterest")

        self.format_edit = QtWidgets.QLineEdit("%Y-%m-%d %H:%M:%S")

        info_label = QtWidgets.QLabel("合约信息")
        info_label.setAlignment(QtCore.Qt.AlignCenter)

        head_label = QtWidgets.QLabel("表头信息")
        head_label.setAlignment(QtCore.Qt.AlignCenter)

        format_label = QtWidgets.QLabel("格式信息")
        format_label.setAlignment(QtCore.Qt.AlignCenter)

        save_progress_label = QtWidgets.QLabel("保存进度信息")
        save_progress_label.setAlignment(QtCore.Qt.AlignCenter)

        save_progress_bar = QtWidgets.QProgressBar()
        save_progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar_dict['save_progress_bar'] = save_progress_bar

        form_left = QtWidgets.QFormLayout()
        form_left.addRow(QtWidgets.QLabel())
        form_left.addRow(info_label)
        form_left.addRow("交易所", self.exchange_combo)
        form_left.addRow("代码", self.symbol_combo)
        form_left.addRow("类型\n(L8主连/L9指数/2006)", self.symbol_type)
        form_left.addRow("周期", self.interval_combo)
        form_left.addRow(QtWidgets.QLabel())
        form_left.addRow(head_label)
        form_left.addRow("时间戳", self.datetime_edit)
        form_left.addRow("开盘价", self.open_edit)
        form_left.addRow("最高价", self.high_edit)
        form_left.addRow("最低价", self.low_edit)
        form_left.addRow("收盘价", self.close_edit)
        form_left.addRow("成交量", self.volume_edit)
        form_left.addRow("持仓量", self.open_interest_edit)
        form_left.addRow(QtWidgets.QLabel())
        form_left.addRow(format_label)
        form_left.addRow("时间格式", self.format_edit)
        form_left.addRow(QtWidgets.QLabel())
        form_left.addRow(save_progress_label)
        form_left.addRow(save_progress_bar)
        form_left.addRow(load_button)
        form_left.addRow(to_csv_button)
        form_left_widget = QtWidgets.QWidget()
        form_left_widget.setLayout(form_left)

        form_right_layout = QtWidgets.QFormLayout()
        # form_right_layout.addRow(QtWidgets.QLabel())
        # form_right_layout.addRow(info_label)
        # form_right_layout.addRow("交易所", self.exchange_combo)
        # form_right_layout.addRow("代码", self.symbol_combo)
        # form_right_layout.addRow("类型\n(L8主连/L9指数/2006)", self.symbol_type)
        # form_right_layout.addRow("周期", self.interval_combo)
        # form_right_layout.addRow(QtWidgets.QLabel())
        # form_right_layout.addRow(head_label)
        # form_right_layout.addRow("时间戳", self.datetime_edit)
        # form_right_layout.addRow("开盘价", self.open_edit)
        # form_right_layout.addRow("最高价", self.high_edit)
        # form_right_layout.addRow("最低价", self.low_edit)
        # form_right_layout.addRow("收盘价", self.close_edit)
        # form_right_layout.addRow("成交量", self.volume_edit)
        # form_right_layout.addRow("持仓量", self.open_interest_edit)
        form_right_widget = QtWidgets.QWidget()
        form_right_widget.setLayout(form_right_layout)

        hbox_layout.addStretch(1)
        hbox_layout.addWidget(form_left_widget)
        hbox_layout.addWidget(form_right_widget)

        self.setLayout(hbox_layout)

        # self.setLayout(form)

    def onExchangeActivated(self, exchange_str):
        self.symbol_combo.clear()
        contracts_dict = read_contracts_json_dict()

        # 提取 contracts_dict 中信息变为 symbols_dict
        symbols_dict = {}
        for key, value in contracts_dict.items():
            if value["exchange"] in symbols_dict:
                symbols_dict[value["exchange"]].append(f"{key}.{value['name']}")
            else:
                symbols_dict[value["exchange"]] = [f"{key}.{value['name']}"]

        if exchange_str in symbols_dict:
            for symbol in symbols_dict[exchange_str]:
                self.symbol_combo.addItem(symbol, symbol)
        else:
            err_msg = f"{exchange_str} is not in pytdx market_code_info.json file!"
            QtWidgets.QMessageBox.information(self, "载入失败！", err_msg)
            print(err_msg)



    def load_data(self):
        """"""
        symbol_code = self.symbol_combo.currentData().split(".")[0]
        symbol_type = self.symbol_type.text()
        exchange = self.exchange_combo.currentData()
        interval = self.interval_combo.currentData()
        datetime_head = self.datetime_edit.text()
        open_head = self.open_edit.text()
        low_head = self.low_edit.text()
        high_head = self.high_edit.text()
        close_head = self.close_edit.text()
        volume_head = self.volume_edit.text()
        open_interest_head = self.open_interest_edit.text()
        datetime_format = self.format_edit.text()

        # to_db / to_csv
        click_button_text = self.sender().text().split('.')[1]

        symbol = symbol_code + symbol_type
        start, end, count = self.engine.load(
            symbol,
            exchange,
            interval,
            datetime_head,
            open_head,
            high_head,
            low_head,
            close_head,
            volume_head,
            open_interest_head,
            datetime_format,
            progress_bar_dict=self.progress_bar_dict,
            opt_str=click_button_text
        )

        msg = f"\
        执行成功\n\
        代码：{symbol}\n\
        交易所：{exchange.value}\n\
        周期：{interval.value}\n\
        起始：{start}\n\
        结束：{end}\n\
        总数量：{count}\n\
        "
        QtWidgets.QMessageBox.information(self, "载入成功！", msg)
