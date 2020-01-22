# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2020/1/15 1:02
# @Author   : Fangyang
# @Software : PyCharm


from pytdx.exhq import TdxExHq_API
from pytdx.hq import TdxHq_API
import time
from jnpy.DataSource.pytdx.log import LogModule


class IPsSource:

    def __init__(self):

        self.hq_ips_dict = {
            "深圳双线主站1": "120.79.60.82",
            "深圳双线主站2": "47.112.129.66",
            "上海双线主站1": "47.103.48.45",
            "上海双线主站2": "47.103.86.229",
            "上海双线主站3": "47.103.88.146",
            "北京双线主站1": "39.98.234.173",
            "北京双线主站2": "39.98.198.249",
            "北京双线主站3": "39.100.68.59",
            "东莞电信主站": "113.105.142.162"
        }
        self.exhq_ips_dict = {
            "扩展市场深圳双线": "112.74.214.43",
            "扩展市场北京双线": "47.92.127.181",
            "扩展市场深圳双线3": "47.107.75.159",
            "扩展市场武汉主站1": "119.97.185.5",
            "扩展市场武汉主站2": "59.175.238.38",
            "扩展市场上海双线1": "106.14.95.149",
            "扩展市场上海双线2": "47.102.108.214",
        }
        self.hq_port = 7709
        self.exhq_port = 7727
        self.log = LogModule(name="IPsSource", level="info")

    def get_fast_exhq_ip(self) -> (str, int):

        fast_exhq_ip_dict = {}
        exhq_api = TdxExHq_API()

        for name, ip in self.exhq_ips_dict.items():
            with exhq_api.connect(ip, self.exhq_port):
                start_time = time.time()
                instrument_count = exhq_api.get_instrument_count()
                cost_time = time.time() - start_time
                self.log.write_log(f"{name}({ip}), time: {cost_time:.3f}s, response: {instrument_count}")
                fast_exhq_ip_dict[f"{ip}:{self.exhq_port}"] = cost_time

        ip_str, port_str = min(fast_exhq_ip_dict, key=fast_exhq_ip_dict.get).split(":")
        self.log.write_log(f"-"*50)
        self.log.write_log(f"Select ({ip_str} : {port_str})")
        self.log.write_log(f"-"*50)

        return ip_str, int(port_str)

    def get_fast_hq_ip(self) -> (str, int):

        fast_hq_ip_dict = {}
        hq_api = TdxHq_API()

        for name, ip in self.hq_ips_dict.items():
            # 东莞电信主站的port和别的不一样
            if name == "东莞电信主站":
                hq_port = 7721
            else:
                hq_port = self.hq_port
            with hq_api.connect(ip, hq_port):
                start_time = time.time()
                instrument_count = hq_api.get_security_count(0)
                cost_time = time.time() - start_time
                self.log.write_log(f"{name}({ip}), time: {cost_time:.3f}s, response: {instrument_count}")
                fast_hq_ip_dict[f"{ip}:{hq_port}"] = cost_time

        ip_str, port_str = min(fast_hq_ip_dict, key=fast_hq_ip_dict.get).split(":")
        self.log.write_log(f"-" * 50)
        self.log.write_log(f"Select ({ip_str} : {port_str})")
        self.log.write_log(f"-" * 50)
        return ip_str, int(port_str)


if __name__ == '__main__':
    ips_pool = IPsSource()
    exhq_ip, exhq_port = ips_pool.get_fast_exhq_ip()
    hq_ip, hq_port = ips_pool.get_fast_hq_ip()

