from functools import partial
from typing import List, Dict, Type

import pyqtgraph as pg
from PyQt5.QtWidgets import QMenu, QAction

from vnpy.trader.ui import QtGui, QtWidgets, QtCore
from vnpy.trader.object import BarData

from .manager import BarManager
from .base import (
    GREY_COLOR, WHITE_COLOR, CURSOR_COLOR, BLACK_COLOR,
    to_int, NORMAL_FONT
)
from .axis import DatetimeAxis
from .item import ChartItem
from ..app.cta_backtester.ui.widget_jnpy import TechIndexSettingEditor

pg.setConfigOptions(antialias=True)


class ChartWidget(pg.PlotWidget):
    """"""
    MIN_BAR_COUNT = 100

    def __init__(self, parent: QtWidgets.QWidget = None):
        """"""
        super().__init__(parent)

        self._manager: BarManager = BarManager()

        self._plots: Dict[str, pg.PlotItem] = {}
        self._items: Dict[str, ChartItem] = {}
        self._item_plot_map: Dict[ChartItem, pg.PlotItem] = {}

        self._first_plot: pg.PlotItem = None
        self._cursor: ChartCursor = None

        self._right_ix: int = 0  # Index of most right data
        self._bar_count: int = self.MIN_BAR_COUNT  # Total bar visible in chart

        # 右键菜单栏 self.tech_dict
        # key: plot_name, 用于区分在那个图区, 目前分为 candle 和 volume 上下两个图区
        # value:{key: 技术指标名(str), value: QAction(checkable)}
        self.tech_dict: dict = {}

        # 右键菜单栏 self.tech_curve_dict
        # key: plot_name, 用于区分在那个图区, 目前分为 candle 和 volume 上下两个图区
        # value:{key: 技术指标名(str), value: TechIndexPlotCurveItem(pg.PlotCurveItem())}
        self.tech_curve_dict: dict = {}

        self._init_ui()

    def _init_ui(self) -> None:
        """"""
        self.setWindowTitle("ChartWidget of vn.py")

        self._layout = pg.GraphicsLayout()
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(0)
        self._layout.setBorder(color=GREY_COLOR, width=0.8)
        self._layout.setZValue(0)
        self.setCentralItem(self._layout)

        self._x_axis = DatetimeAxis(self._manager, orientation='bottom')

    def add_cursor(self) -> None:
        """"""
        if not self._cursor:
            self._cursor = ChartCursor(
                self, self._manager, self._plots, self._item_plot_map)

    def add_plot(
            self,
            plot_name: str,
            minimum_height: int = 80,
            maximum_height: int = None,
            hide_x_axis: bool = False
    ) -> None:
        """
        Add plot area.
        """
        # Create plot object
        plot = pg.PlotItem(axisItems={'bottom': self._x_axis})
        plot.setMenuEnabled(False)
        plot.setClipToView(True)
        plot.hideAxis('left')
        plot.showAxis('right')
        plot.setDownsampling(mode='peak')
        plot.setRange(xRange=(0, 1), yRange=(0, 1))
        plot.hideButtons()
        plot.setMinimumHeight(minimum_height)

        if maximum_height:
            plot.setMaximumHeight(maximum_height)

        if hide_x_axis:
            plot.hideAxis("bottom")

        if not self._first_plot:
            self._first_plot = plot

        # Connect view change signal to update y range function
        view = plot.getViewBox()
        view.sigXRangeChanged.connect(self._update_y_range)
        view.setMouseEnabled(x=True, y=False)

        # Set right axis
        right_axis = plot.getAxis('right')
        right_axis.setWidth(60)
        right_axis.tickFont = NORMAL_FONT

        # Connect x-axis link
        if self._plots:
            first_plot = list(self._plots.values())[0]
            plot.setXLink(first_plot)

        # Store plot object in dict
        self._plots[plot_name] = plot

        # Add plot onto the layout
        self._layout.nextRow()
        self._layout.addItem(plot)

    def add_item(
            self,
            item_class: Type[ChartItem],
            item_name: str,
            plot_name: str
    ):
        """
        Add chart item.
        """
        item = item_class(self._manager)
        self._items[item_name] = item

        plot = self._plots.get(plot_name)
        plot.addItem(item)

        self._item_plot_map[item] = plot

    def get_plot(self, plot_name: str) -> pg.PlotItem:
        """
        Get specific plot with its name.
        """
        return self._plots.get(plot_name, None)

    def get_all_plots(self) -> List[pg.PlotItem]:
        """
        Get all plot objects.
        """
        return self._plots.values()

    def clear_all(self) -> None:
        """
        Clear all data.
        """
        self._manager.clear_all()

        for item in self._items.values():
            item.clear_all()

        if self._cursor:
            self._cursor.clear_all()

    def update_history(self, history: List[BarData]) -> None:
        """
        Update a list of bar data.
        """
        self._manager.update_history(history)

        for item in self._items.values():
            item.update_history(history)

        self._update_plot_limits()

        self.move_to_right()

    def update_bar(self, bar: BarData) -> None:
        """
        Update single bar data.
        """
        self._manager.update_bar(bar)

        for item in self._items.values():
            item.update_bar(bar)

        self._update_plot_limits()

        if self._right_ix >= (self._manager.get_count() - self._bar_count / 2):
            self.move_to_right()

    def _update_plot_limits(self) -> None:
        """
        Update the limit of plots.
        """
        for item, plot in self._item_plot_map.items():
            min_value, max_value = item.get_y_range()

            plot.setLimits(
                xMin=-1,
                xMax=self._manager.get_count(),
                yMin=min_value,
                yMax=max_value
            )

    def _update_x_range(self) -> None:
        """
        Update the x-axis range of plots.
        """
        max_ix = self._right_ix
        min_ix = self._right_ix - self._bar_count

        for plot in self._plots.values():
            plot.setRange(xRange=(min_ix, max_ix), padding=0)

    def _update_y_range(self) -> None:
        """
        Update the y-axis range of plots.
        """
        view = self._first_plot.getViewBox()
        view_range = view.viewRange()

        min_ix = max(0, int(view_range[0][0]))
        max_ix = min(self._manager.get_count(), int(view_range[0][1]))

        # Update limit for y-axis
        for item, plot in self._item_plot_map.items():
            y_range = item.get_y_range(min_ix, max_ix)
            plot.setRange(yRange=y_range)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """
        Reimplement this method of parent to update current max_ix value.
        """
        view = self._first_plot.getViewBox()
        view_range = view.viewRange()
        self._right_ix = max(0, view_range[0][1])

        super().paintEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """
        Reimplement this method of parent to move chart horizontally and zoom in/out.
        """
        if event.key() == QtCore.Qt.Key_Left:
            self._on_key_left()
        elif event.key() == QtCore.Qt.Key_Right:
            self._on_key_right()
        elif event.key() == QtCore.Qt.Key_Up:
            self._on_key_up()
        elif event.key() == QtCore.Qt.Key_Down:
            self._on_key_down()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """
        Reimplement this method of parent to zoom in/out.
        """
        delta = event.angleDelta()

        if delta.y() > 0:
            self._on_key_up()
        elif delta.y() < 0:
            self._on_key_down()

    def _on_key_left(self) -> None:
        """
        Move chart to left.
        """
        self._right_ix -= 1
        self._right_ix = max(self._right_ix, self._bar_count)

        self._update_x_range()
        self._cursor.move_left()
        self._cursor.update_info()

    def _on_key_right(self) -> None:
        """
        Move chart to right.
        """
        self._right_ix += 1
        self._right_ix = min(self._right_ix, self._manager.get_count())

        self._update_x_range()
        self._cursor.move_right()
        self._cursor.update_info()

    def _on_key_down(self) -> None:
        """
        Zoom out the chart.
        """
        self._bar_count *= 1.2
        self._bar_count = min(int(self._bar_count), self._manager.get_count())

        self._update_x_range()
        self._cursor.update_info()

    def _on_key_up(self) -> None:
        """
        Zoom in the chart.
        """
        self._bar_count /= 1.2
        self._bar_count = max(int(self._bar_count), self.MIN_BAR_COUNT)

        self._update_x_range()
        self._cursor.update_info()

    def move_to_right(self) -> None:
        """
        Move chart to the most right.
        """
        self._right_ix = self._manager.get_count()
        self._update_x_range()
        self._cursor.update_info()

    def call_dialog(self, cursor_pos_plot_name, tech_name_str):

        dialog = TechIndexSettingEditor('TechIndex_Dialog', {'a': 1, 'b': 'aa'})  # 这里传入技术指标的默认参数值
        i = dialog.exec_()
        if i != dialog.Accepted:
            self.tech_dict[cursor_pos_plot_name][tech_name_str].setChecked(False)
            return
        new_setting = dialog.get_setting()  # 这里获得用户修改后的技术指标参数值

        # TODO draw curve
        df = self._manager.get_df()

        plot = self.get_plot(cursor_pos_plot_name)  # 确定在哪张图上画技术指标, candle or volume
        print(f"plot {tech_name_str} on {plot}")

        if cursor_pos_plot_name not in self.tech_curve_dict:
            self.tech_curve_dict[cursor_pos_plot_name] = {}

        self.tech_curve_dict[cursor_pos_plot_name][tech_name_str] = pg.PlotCurveItem()
        close_ma_series_10 = df['close_price'].rolling(window=10).mean().fillna(method='bfill')
        x = close_ma_series_10.index.values
        y = close_ma_series_10.to_numpy()
        self.tech_curve_dict[cursor_pos_plot_name][tech_name_str].setData(x, y)
        pen_10 = pg.mkPen(width=3, color='y')
        self.tech_curve_dict[cursor_pos_plot_name][tech_name_str].setPen(pen_10)

        plot.addItem(self.tech_curve_dict[cursor_pos_plot_name][tech_name_str])

        self.tech_dict[cursor_pos_plot_name][tech_name_str].setChecked(True)

    def is_call_dialog(self, cursor_pos_plot_name, tech_name_str):
        origin_bool = self.tech_dict[cursor_pos_plot_name][tech_name_str].isChecked()
        print(origin_bool)
        if self.tech_dict[cursor_pos_plot_name][tech_name_str].isChecked():
            self.call_dialog(cursor_pos_plot_name, tech_name_str)
        else:
            self.tech_dict[cursor_pos_plot_name][tech_name_str].setChecked(False)
            plot = self.get_plot(cursor_pos_plot_name)
            plot.removeItem(self.tech_curve_dict[cursor_pos_plot_name][tech_name_str])
            print(f'抹除{tech_name_str}plot线')

    def contextMenuEvent(self, QContextMenuEvent):
        '''右键单击鼠标出现该菜单'''
        cmenu = QMenu(self)
        cursor_pos_plot_name = self._cursor.get_current_plot_name()
        menu0 = QMenu('技术指标', self)
        tech_name_str_list = ['MA', 'boll', 'kdj', 'cci']

        # if not self.tech_dict:
        if not self.tech_dict.get(cursor_pos_plot_name, {}):
            self.tech_dict[cursor_pos_plot_name] = {}
            for tech_name_str in tech_name_str_list:
                qAction = QAction(tech_name_str, self, checkable=True)
                qAction.setChecked(False)
                self.tech_dict[cursor_pos_plot_name][tech_name_str] = qAction
                qAction.triggered.connect(partial(self.is_call_dialog, cursor_pos_plot_name, tech_name_str))
                menu0.addAction(self.tech_dict[cursor_pos_plot_name][tech_name_str])
        else:
            for tech_name_str, qAction in self.tech_dict[cursor_pos_plot_name].items():
                menu0.addAction(qAction)

        cmenu.addMenu(menu0)
        cmenu.exec_(self.mapToGlobal(QContextMenuEvent.pos()))


class ChartCursor(QtCore.QObject):
    """"""

    def __init__(
            self,
            widget: ChartWidget,
            manager: BarManager,
            plots: Dict[str, pg.GraphicsObject],
            item_plot_map: Dict[ChartItem, pg.GraphicsObject]
    ):
        """"""
        super().__init__()

        self._widget: ChartWidget = widget
        self._manager: BarManager = manager
        self._plots: Dict[str, pg.GraphicsObject] = plots
        self._item_plot_map: Dict[ChartItem, pg.GraphicsObject] = item_plot_map

        self._x: int = 0
        self._y: int = 0
        self._plot_name: str = ""

        self._init_ui()
        self._connect_signal()

    def _init_ui(self):
        """"""
        self._init_line()
        self._init_label()
        self._init_info()

    def _init_line(self) -> None:
        """
        Create line objects.
        """
        self._v_lines: Dict[str, pg.InfiniteLine] = {}
        self._h_lines: Dict[str, pg.InfiniteLine] = {}
        self._views: Dict[str, pg.ViewBox] = {}

        pen = pg.mkPen(WHITE_COLOR)

        for plot_name, plot in self._plots.items():
            v_line = pg.InfiniteLine(angle=90, movable=False, pen=pen)
            h_line = pg.InfiniteLine(angle=0, movable=False, pen=pen)
            view = plot.getViewBox()

            for line in [v_line, h_line]:
                line.setZValue(0)
                line.hide()
                view.addItem(line)

            self._v_lines[plot_name] = v_line
            self._h_lines[plot_name] = h_line
            self._views[plot_name] = view

    def _init_label(self) -> None:
        """
        Create label objects on axis.
        """
        self._y_labels: Dict[str, pg.TextItem] = {}
        for plot_name, plot in self._plots.items():
            label = pg.TextItem(
                plot_name, fill=CURSOR_COLOR, color=BLACK_COLOR)
            label.hide()
            label.setZValue(2)
            label.setFont(NORMAL_FONT)
            plot.addItem(label, ignoreBounds=True)
            self._y_labels[plot_name] = label

        self._x_label: pg.TextItem = pg.TextItem(
            "datetime", fill=CURSOR_COLOR, color=BLACK_COLOR)
        self._x_label.hide()
        self._x_label.setZValue(2)
        self._x_label.setFont(NORMAL_FONT)
        plot.addItem(self._x_label, ignoreBounds=True)

    def _init_info(self) -> None:
        """
        """
        self._infos: Dict[str, pg.TextItem] = {}
        for plot_name, plot in self._plots.items():
            info = pg.TextItem(
                "info",
                color=CURSOR_COLOR,
                border=CURSOR_COLOR,
                fill=BLACK_COLOR
            )
            info.hide()
            info.setZValue(2)
            info.setFont(NORMAL_FONT)
            plot.addItem(info)  # , ignoreBounds=True)
            self._infos[plot_name] = info

    def _connect_signal(self) -> None:
        """
        Connect mouse move signal to update function.
        """
        self._widget.scene().sigMouseMoved.connect(self._mouse_moved)

    def _mouse_moved(self, evt: tuple) -> None:
        """
        Callback function when mouse is moved.
        """
        if not self._manager.get_count():
            return

        # First get current mouse point
        pos = evt

        for plot_name, view in self._views.items():
            rect = view.sceneBoundingRect()

            if rect.contains(pos):
                mouse_point = view.mapSceneToView(pos)
                self._x = to_int(mouse_point.x())
                self._y = mouse_point.y()
                self._plot_name = plot_name
                break

        # Then update cursor component
        self._update_line()
        self._update_label()
        self.update_info()

    def _update_line(self) -> None:
        """"""
        for v_line in self._v_lines.values():
            v_line.setPos(self._x)
            v_line.show()

        for plot_name, h_line in self._h_lines.items():
            if plot_name == self._plot_name:
                h_line.setPos(self._y)
                h_line.show()
            else:
                h_line.hide()

    def _update_label(self) -> None:
        """"""
        bottom_plot = list(self._plots.values())[-1]
        axis_width = bottom_plot.getAxis("right").width()
        axis_height = bottom_plot.getAxis("bottom").height()
        axis_offset = QtCore.QPointF(axis_width, axis_height)

        bottom_view = list(self._views.values())[-1]
        bottom_right = bottom_view.mapSceneToView(
            bottom_view.sceneBoundingRect().bottomRight() - axis_offset
        )

        for plot_name, label in self._y_labels.items():
            if plot_name == self._plot_name:
                label.setText(str(self._y))
                label.show()
                label.setPos(bottom_right.x(), self._y)
            else:
                label.hide()

        dt = self._manager.get_datetime(self._x)
        if dt:
            self._x_label.setText(dt.strftime("%Y-%m-%d %H:%M:%S"))
            self._x_label.show()
            self._x_label.setPos(self._x, bottom_right.y())
            self._x_label.setAnchor((0, 0))

    def update_info(self) -> None:
        """"""
        buf = {}

        for item, plot in self._item_plot_map.items():
            item_info_text = item.get_info_text(self._x)

            if plot not in buf:
                buf[plot] = item_info_text
            else:
                if item_info_text:
                    buf[plot] += ("\n\n" + item_info_text)

        for plot_name, plot in self._plots.items():
            plot_info_text = buf[plot]
            info = self._infos[plot_name]
            info.setText(plot_info_text)
            info.show()

            view = self._views[plot_name]
            top_left = view.mapSceneToView(view.sceneBoundingRect().topLeft())
            info.setPos(top_left)

    def move_right(self) -> None:
        """
        Move cursor index to right by 1.
        """
        if self._x == self._manager.get_count() - 1:
            return
        self._x += 1

        self._update_after_move()

    def move_left(self) -> None:
        """
        Move cursor index to left by 1.
        """
        if self._x == 0:
            return
        self._x -= 1

        self._update_after_move()

    def _update_after_move(self) -> None:
        """
        Update cursor after moved by left/right.
        """
        bar = self._manager.get_bar(self._x)
        self._y = bar.close_price

        self._update_line()
        self._update_label()

    def get_current_plot_name(self) -> str:
        return self._plot_name

    def clear_all(self) -> None:
        """
        Clear all data.
        """
        self._x = 0
        self._y = 0
        self._plot_name = ""

        for line in list(self._v_lines.values()) + list(self._h_lines.values()):
            line.hide()

        for label in list(self._y_labels.values()) + [self._x_label]:
            label.hide()
