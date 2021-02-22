
import platform

from abc import ABC, abstractmethod
from sqlalchemy import create_engine

from vnpy.trader.utility import get_file_path


class PdBase(ABC):

    def __init__(self, DBOCls_init_dict):
        self.settings_dict = DBOCls_init_dict["settings_dict"]
        self.file_path_str = DBOCls_init_dict["file_path_str"]
        self.sqlite_os = ""
        self.os_str = platform.system()

        self.check_system()

    def check_system(self):
        if self.os_str == "Windows":
            self.sqlite_os = "/"
        elif self.os_str == "Linux":
            self.sqlite_os = "//"
        else:
            print(f"OS is {self.os_str}. DBoperation may meet problem.")

    @abstractmethod
    def new_engine(self):
        pass

    @abstractmethod
    def get_groupby_data(self):
        pass

    @abstractmethod
    def get_end_date(self, symbol, exchange, interval):
        pass

    @abstractmethod
    def get_start_date(self, symbol, exchange, interval):
        pass

    @abstractmethod
    def get_bar_data_df(self, symbol, exchange, interval, start=None, end=None):
        pass

    @abstractmethod
    def get_bar_data(self, symbol, exchange, interval, start=None, end=None):
        ''' 速度没有本来的列表推导式快 '''
        pass


if __name__ == "__main__":
    pass
