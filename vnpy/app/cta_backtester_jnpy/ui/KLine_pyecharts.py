#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/15 下午6:49
@Author   :   Fangyang
"""
from typing import List, Union

from pyecharts.charts import Grid, Bar, Kline, Line
from pyecharts import options as opts
from vnpy.trader.utility import get_folder_path


def draw_charts(x_axis_list, oclh_data_list, volume_list, tech_line_dict):
    upColor = '#ec0000'
    downColor = '#00da3c'
    upBorderColor = '#8A0000'
    downBorderColor = '#008F2'

    kline = (
        Kline()
            .add_xaxis(x_axis_list)
            .add_yaxis("kline", oclh_data_list)
            .set_series_opts(
            itemstyle_opts=opts.ItemStyleOpts(
                color=upColor,
                color0=downColor,
                border_color=upBorderColor,
                border_color0=downBorderColor
            ),
        )
            .set_global_opts(
            legend_opts=opts.LegendOpts(
                pos_bottom=10, pos_left="center"
            ),
            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger='axis',
                axis_pointer_type='cross',
                background_color='rgba(245,245,245,0.8)',
                border_width=1,
                border_color='#ccc',
                textstyle_opts=opts.TextStyleOpts(color='#000')
            ),
            visualmap_opts=opts.VisualMapOpts(
                is_show=False,
                dimension=2,
                series_index=5,
                is_piecewise=True,
                pieces=[
                    {"value": 1, "color": downColor},
                    {"value": -1, "color": upColor},
                ],
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    type_="inside",
                    xaxis_index=[0, 1],
                    range_start=98,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    type_="slider",
                    xaxis_index=[0, 1],
                    range_start=98,
                    range_end=100,
                    pos_top='85%',
                )
            ],
            axispointer_opts=opts.AxisPointerOpts(
                is_show=True,
                link=[{"xAxisIndex": "all"}],
                label=opts.LabelOpts(background_color="#777"),
            ),
            brush_opts=opts.BrushOpts(
                x_axis_index="all",
                brush_link="all",
                out_of_brush={"colorAlpha": 0.1},
                brush_type="lineX",
            ),
            title_opts=opts.TitleOpts(title="Kline")
        )
    )

    if tech_line_dict:
        line = (
            Line()
                .add_xaxis(xaxis_data=x_axis_list)
                .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        )
        [
            line.add_yaxis(
                series_name=name,
                y_axis=value_list,
                is_smooth=True,
                is_hover_animation=False,
                linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False), ) for name, value_list in tech_line_dict.items()
        ]
        kline = kline.overlap(line)

    bar = (
        Bar()
            .add_xaxis(x_axis_list)
            .add_yaxis(
            series_name="成交量",
            yaxis_data=volume_list,
            xaxis_index=1,
            yaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False)
        )
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                is_scale=True,
                grid_index=1,
                boundary_gap=False,
                axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
                axislabel_opts=opts.LabelOpts(is_show=False),
                split_number=20,
                min_="dataMin",
                max_="dataMax",
            ),
            yaxis_opts=opts.AxisOpts(
                grid_index=1,
                is_scale=True,
                split_number=2,
                axislabel_opts=opts.LabelOpts(is_show=False),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=False),
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    grid_chart = Grid(
        init_opts=opts.InitOpts(
            width="1000px",
            height="800px",
            animation_opts=opts.AnimationOpts(animation=False),
        )
    )

    grid_chart.add(kline, grid_opts=opts.GridOpts(pos_left="10%", pos_right="8%", height="50%"))
    grid_chart.add(bar, grid_opts=opts.GridOpts(pos_left="10%", pos_right="8%", pos_top="63%", height="16%"))

    folder_path = get_folder_path("backtesting_result_pyecharts")
    file_path = f"{folder_path}/render.html"
    grid_chart.render(path=file_path)

    return file_path


if __name__ == "__main__":
    pass
