# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2019/11/17 上午12:13
# @Author   : Fangyang
# @Software : PyCharm

from vnpy.trader.ui import QtCore, QtWidgets, QtGui


class TechIndexSettingEditor(QtWidgets.QDialog):
    """
    For creating new strategy and editing strategy parameters.
    """

    def __init__(
            self, class_name: str, parameters: dict, combox_list: list
    ):
        """"""
        super(TechIndexSettingEditor, self).__init__()

        self.class_name = class_name
        self.parameters = parameters
        self.edits = {}
        self.column_name_combo_dict = {
            '数据源': combox_list,
            # '数据源2': ['high', 'low', 'volume']
        }

        self.init_ui()

    def init_ui(self):
        """"""
        form = QtWidgets.QFormLayout()

        for key, column_name_list in self.column_name_combo_dict.items():
            column_name_combo = QtWidgets.QComboBox()
            for column_name in column_name_list:
                column_name_combo.addItem(f'{column_name}', column_name)
            self.column_name_combo_dict[key] = column_name_combo
            form.addRow(key, column_name_combo)

        # Add vt_symbol and name edit if add new strategy
        self.setWindowTitle(f"技术指标参数配置：{self.class_name}")
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

        self.setLayout(form)

    def get_setting(self):
        """"""
        setting = {}
        for key, combox in self.column_name_combo_dict.items():
            setting[key] = combox.currentData()

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


class TechIndexPlotCurveItem(object):
    def __init__(self):
        pass


if __name__ == '__main__':
    pass
