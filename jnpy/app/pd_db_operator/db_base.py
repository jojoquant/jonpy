
import platform
from abc import ABC, abstractmethod


class PdBase(ABC):

    def __init__(self, settings_dict):
        self.settings_dict = settings_dict
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

    @abstractmethod
    def write_df_to_db(self, df, table, append, callback=None):
        pass


if __name__ == "__main__":
    pass
