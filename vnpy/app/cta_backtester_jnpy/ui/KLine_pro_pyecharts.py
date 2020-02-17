#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/16 下午1:36
@Author   :   Fangyang
"""

import numpy as np
import pandas as pd

from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Kline, Line, Bar, Grid

from jnpy.utils.DataManager import ArrayManagerWithDatetime
from vnpy.trader.utility import get_folder_path
from vnpy.trader.constant import Status, Offset, Direction


def gen_kline(xaxis_data_list, oclh_data_list, order_list):
    kline = Kline()
    kline.add_xaxis(xaxis_data=xaxis_data_list)
    kline.add_yaxis(
        series_name="",
        y_axis=oclh_data_list,
        itemstyle_opts=opts.ItemStyleOpts(
            color="#ef232a",
            color0="#14b143",
            border_color="#ef232a",
            border_color0="#14b143",
        ),
        markpoint_opts=opts.MarkPointOpts(
            data=[
                opts.MarkPointItem(type_="max", name="最大值"),
                opts.MarkPointItem(type_="min", name="最小值"),
                *order_list
            ]
        ),
        # markline_opts=opts.MarkLineOpts(
        #     label_opts=opts.LabelOpts(
        #         position="middle", color="blue", font_size=15
        #     ),
        #     data=split_data_part(),
        #     symbol=["circle", "none"],
        # ),
    )
    # 这部分是画箱体的, 上面是画箱体对角线连线的
    # kline.set_series_opts(
    #     markarea_opts=opts.MarkAreaOpts(is_silent=True, data=split_data_part())
    # )
    kline.set_global_opts(
        title_opts=opts.TitleOpts(title="K线周期图表", pos_left="0"),
        xaxis_opts=opts.AxisOpts(
            type_="category",
            is_scale=True,
            boundary_gap=False,
            axisline_opts=opts.AxisLineOpts(is_on_zero=False),
            splitline_opts=opts.SplitLineOpts(is_show=False),
            split_number=20,
            min_="dataMin",
            max_="dataMax",
            axislabel_opts=opts.LabelOpts(is_show=True, rotate=-30),  # 旋转x轴标签一定角度
        ),
        yaxis_opts=opts.AxisOpts(
            is_scale=True, splitline_opts=opts.SplitLineOpts(is_show=True)
        ),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line"),
        datazoom_opts=[
            opts.DataZoomOpts(
                is_show=False, type_="inside", xaxis_index=[0, 0], range_end=100
            ),
            opts.DataZoomOpts(
                is_show=True, xaxis_index=[0, 1], pos_top="97%", range_end=100
            ),
            opts.DataZoomOpts(is_show=False, xaxis_index=[0, 2], range_end=100),
            opts.DataZoomOpts(is_show=False, xaxis_index=[0, 3], range_end=100),  # 连动第三个资金曲线轴
        ],

        # 三个图的 axis 连在一块
        # axispointer_opts=opts.AxisPointerOpts(
        #     is_show=True,
        #     link=[{"xAxisIndex": "all"}],
        #     label=opts.LabelOpts(background_color="#777"),
        # ),
    )
    return kline


def gen_tech_line(xaxis_data_list):
    tech_line = Line()

    tech_line.add_xaxis(xaxis_data=xaxis_data_list)
    tech_line.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            type_="category",
            grid_index=1,
            axislabel_opts=opts.LabelOpts(is_show=False),
        ),
        yaxis_opts=opts.AxisOpts(
            grid_index=1,
            split_number=3,
            axisline_opts=opts.AxisLineOpts(is_on_zero=False),
            axistick_opts=opts.AxisTickOpts(is_show=False),
            splitline_opts=opts.SplitLineOpts(is_show=False),
            axislabel_opts=opts.LabelOpts(is_show=True),
        ),
    )

    return tech_line


def gen_volume_bar(xaxis_data_list, volume_list):
    # Bar-1
    volume_bar = Bar()

    volume_bar.add_xaxis(xaxis_data=xaxis_data_list)
    volume_bar.add_yaxis(
        series_name="Volumn",
        yaxis_data=volume_list,
        xaxis_index=1,
        yaxis_index=1,
        label_opts=opts.LabelOpts(is_show=False),
        # 根据 echarts demo 的原版是这么写的
        # itemstyle_opts=opts.ItemStyleOpts(
        #     color=JsCode("""
        #     function(params) {
        #         var colorList;
        #         if (data.datas[params.dataIndex][1]>data.datas[params.dataIndex][0]) {
        #           colorList = '#ef232a';
        #         } else {
        #           colorList = '#14b143';
        #         }
        #         return colorList;
        #     }
        #     """)
        # )
        # 改进后在 grid 中 add_js_funcs 后变成如下
        itemstyle_opts=opts.ItemStyleOpts(
            color=JsCode(
                """
            function(params) {
                var colorList;
                if (barData[params.dataIndex][1] > barData[params.dataIndex][0]) {
                    colorList = '#ef232a';
                } else {
                    colorList = '#14b143';
                }
                return colorList;
            }
            """
            )
        ),
    )
    volume_bar.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            type_="category",
            grid_index=1,
            axislabel_opts=opts.LabelOpts(is_show=False),
        ),
        legend_opts=opts.LegendOpts(is_show=False),
    )

    return volume_bar


def gen_macd_bar_line(xaxis_data_list, macd_list, dif_list, deas_list):
    # Bar-2 (Overlap Bar + Line)
    bar_2 = (
        Bar()
            .add_xaxis(xaxis_data=xaxis_data_list)
            .add_yaxis(
            series_name="MACD",
            yaxis_data=macd_list,
            xaxis_index=2,
            yaxis_index=2,
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(
                color=JsCode(
                    """
                        function(params) {
                            var colorList;
                            if (params.data >= 0) {
                              colorList = '#ef232a';
                            } else {
                              colorList = '#14b143';
                            }
                            return colorList;
                        }
                        """
                )
            ),
        )
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                grid_index=2,
                axislabel_opts=opts.LabelOpts(is_show=False),
            ),
            yaxis_opts=opts.AxisOpts(
                grid_index=2,
                split_number=4,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                axislabel_opts=opts.LabelOpts(is_show=True),
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    line_2 = (
        Line()
            .add_xaxis(xaxis_data=xaxis_data_list)
            .add_yaxis(
            series_name="DIF",
            y_axis=dif_list,
            xaxis_index=2,
            yaxis_index=2,
            label_opts=opts.LabelOpts(is_show=False),
        )
            .add_yaxis(
            series_name="DEAS",
            y_axis=deas_list,
            xaxis_index=2,
            yaxis_index=2,
            label_opts=opts.LabelOpts(is_show=False),
        )
            .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
    )

    # 最下面的柱状图和折线图
    overlap_bar_line = bar_2.overlap(line_2)
    return overlap_bar_line


def gen_order_list(orders):
    order_list = []
    if orders:
        for order_data in orders:

            if order_data.direction == Direction.LONG and order_data.offset == Offset.OPEN:
                symbol = 'arrow'
                symbol_size = 20
                if order_data.status == Status.ALLTRADED:
                    item_style = opts.ItemStyleOpts(color='rgb(0,0,255)')
                else:
                    item_style = opts.ItemStyleOpts(color='rgb(255,100,0)')  # orange

            elif order_data.direction == Direction.LONG and (
                    order_data.offset == Offset.CLOSE
                    or order_data.offset == Offset.CLOSETODAY
                    or order_data.offset == Offset.CLOSEYESTERDAY):
                symbol = 'arrow'
                symbol_size = 20
                if order_data.status == Status.ALLTRADED:
                    item_style = opts.ItemStyleOpts(color='rgb(0,0,0)')
                else:
                    item_style = opts.ItemStyleOpts(color='rgb(255,100,0)')  # orange

            elif order_data.direction == Direction.SHORT and order_data.offset == Offset.OPEN:
                symbol = 'pin'
                symbol_size = 40
                if order_data.status == Status.ALLTRADED:
                    item_style = opts.ItemStyleOpts(color='rgb(0,0,255)')
                else:
                    item_style = opts.ItemStyleOpts(color='rgb(255,100,0)')  # orange

            elif order_data.direction == Direction.SHORT and (
                    order_data.offset == Offset.CLOSE
                    or order_data.offset == Offset.CLOSETODAY
                    or order_data.offset == Offset.CLOSEYESTERDAY):
                symbol = 'pin'
                symbol_size = 40
                if order_data.status == Status.ALLTRADED:
                    item_style = opts.ItemStyleOpts(color='rgb(0,0,0)')
                else:
                    item_style = opts.ItemStyleOpts(color='rgb(255,100,0)')  # orange

            order_item = opts.MarkPointItem(
                name=f"orderid_{order_data.orderid}",
                coord=[str(order_data.datetime), order_data.price],
                value=f"{order_data.price}\n{order_data.offset.value}\n{order_data.status.value}",
                symbol=symbol,
                symbol_size=symbol_size,
                itemstyle_opts=item_style,
            )

            order_list.append(order_item)

    return order_list


def gen_balance_line(x_axis_list, result_df):
    head_df = pd.DataFrame()
    for _ in range(len(x_axis_list) - result_df.shape[0]):
        head_df = head_df.append(result_df.iloc[0, :])
    result_df = head_df.append(result_df)
    yaxis_data_list = result_df['balance'].tolist()

    balance_line = Line()
    balance_line.add_xaxis(x_axis_list)
    balance_line.add_yaxis(
        "balance",
        y_axis=yaxis_data_list,
        xaxis_index=3,
        yaxis_index=3,
        label_opts=opts.LabelOpts(is_show=False),
    )
    balance_line.set_global_opts(
        xaxis_opts=opts.AxisOpts(
            grid_index=3,
            name_rotate=60,
        ),
        yaxis_opts=opts.AxisOpts(
            grid_index=3,
            split_number=4,
            is_scale=True,
        ),
        legend_opts=opts.LegendOpts(is_show=False)
    )

    return balance_line


def draw_chart(history, results, orders, strategy_tech_visual_list, result_df):
    order_list = gen_order_list(orders)

    if history:
        am = ArrayManagerWithDatetime(size=len(history))
        [am.update_bar(bar) for bar in history]
        oclh_data_list = np.vstack((am.open, am.close, am.low, am.high)).T.tolist()
        volume_list = am.volume.tolist()
        x_axis_list = am.datetime_list

        kline = gen_kline(xaxis_data_list=x_axis_list, oclh_data_list=oclh_data_list, order_list=order_list)
    else:
        kline = Kline()

    if strategy_tech_visual_list:
        tech_line = gen_tech_line(xaxis_data_list=x_axis_list)
        for tech_str in strategy_tech_visual_list:
            df = pd.DataFrame().fillna(method='bfill')
            df[tech_str] = eval(tech_str)
            df[tech_str].fillna(method='bfill', inplace=True)
            y_axis_list = df[tech_str].tolist()
            tech_line.add_yaxis(
                series_name=tech_str,
                y_axis=y_axis_list,
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
            )

        # Overlap Kline + Line
        kline = kline.overlap(tech_line)

    volumne_bar = gen_volume_bar(xaxis_data_list=x_axis_list, volume_list=volume_list)

    macd, signal, hist = am.macd(12, 26, 9, True)
    macd[np.isnan(macd)] = 0
    signal[np.isnan(signal)] = 0
    hist[np.isnan(hist)] = 0

    macd_bar_line = gen_macd_bar_line(
        xaxis_data_list=x_axis_list,
        macd_list=macd.tolist(),
        dif_list=signal.tolist(),
        deas_list=hist.tolist()
    )

    balance_line = gen_balance_line(x_axis_list, result_df)

    # 最后的 Grid
    grid_chart = Grid(init_opts=opts.InitOpts(width="1400px", height="800px"))

    # 这个是为了把 data.datas 这个数据写入到 html 中,还没想到怎么跨 series 传值
    # demo 中的代码也是用全局变量传的
    grid_chart.add_js_funcs("var barData = {}".format(y_axis_list))

    pos_left = '5%'
    pos_right = '1%'
    height = 10
    interval = 3
    kline_height = 40
    # K线图和 MA5 的折线图
    grid_chart.add(
        kline,
        grid_opts=opts.GridOpts(pos_left=pos_left, pos_right=pos_right, height=f"{kline_height}%"),
    )
    # Volumn 柱状图
    volume_pos_top = kline_height + 6*interval
    grid_chart.add(
        volumne_bar,
        grid_opts=opts.GridOpts(
            pos_left=pos_left, pos_right=pos_right, pos_top=f"{volume_pos_top}%", height=f"{height}%"
        ),
    )
    macd_pos_top = volume_pos_top + interval + height
    # MACD DIFS DEAS
    grid_chart.add(
        macd_bar_line,
        grid_opts=opts.GridOpts(
            pos_left=pos_left, pos_right=pos_right, pos_top=f"{macd_pos_top}%", height=f"{height}%"
        ),
    )

    balance_pos_top = macd_pos_top + interval + height
    grid_chart.add(
        balance_line,
        grid_opts=opts.GridOpts(
            pos_left=pos_left, pos_right=pos_right, pos_top=f"{balance_pos_top}%", height=f"{height}%"
        ),
    )

    folder_path = get_folder_path("backtesting_result_pyecharts")
    file_path = f"{folder_path}/render.html"
    grid_chart.render(path=file_path)

    return file_path


if __name__ == "__main__":
    pass
