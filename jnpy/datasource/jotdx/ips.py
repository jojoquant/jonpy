# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Datetime : 2020/1/15 1:02
# @Author   : Fangyang
# @Software : PyCharm


from jotdx.exhq import TdxExHq_API
from jotdx.hq import TdxHq_API
import time
from jnpy.utils.utils_log import LogModule


class IPsSource:

    def __init__(self):

        self.hq_ips_dict = {
            "深圳双线主站1": ("120.79.60.82", 7709),
            "深圳双线主站2": ("8.129.13.54", 7709),
            "深圳双线主站3": ("120.24.149.49", 7709),
            "深圳双线主站4": ("47.113.94.204", 7709),
            "深圳双线主站5": ("8.129.174.169", 7709),
            "深圳双线主站6": ("47.113.123.248", 7709),
            "上海双线主站1": ("47.103.48.45", 7709),
            "上海双线主站2": ("47.100.236.28", 7709),
            "上海双线主站3": ("101.133.214.242", 7709),
            "上海双线主站4": ("47.116.21.80", 7709),
            "上海双线主站5": ("47.116.105.28", 7709),
            "上海双线主站6": ("47.116.10.29", 7709),
            "北京双线主站1": ("39.98.234.173", 7709),
            "北京双线主站2": ("39.98.198.249", 7709),
            "北京双线主站3": ("39.100.68.59", 7709),
            "东莞电信主站": ("113.105.142.162", 7721),
            "广州双线主站1": ("106.53.96.220", 7709),
            "广州双线主站2": ("106.53.99.72", 7709),
            "广州双线主站3": ("106.55.12.89", 7709)
        }
        self.exhq_ips_dict = {
            "扩展市场深圳双线": ("112.74.214.43", 7727),
            # "扩展市场北京双线": ("47.92.127.181", 7727),
            "扩展市场深圳双线3": ("47.107.75.159", 7727),
            "扩展市场武汉主站1": ("119.97.185.5", 7727),
            "扩展市场武汉主站2": ("59.175.238.38", 7727),
            "扩展市场上海双线1": ("106.14.95.149", 7727),
            "扩展市场上海双线2": ("47.102.108.214", 7727),
        }
        self.log = LogModule(name="IPsSource", level="info")

    def get_fast_exhq_ip(self) -> (str, int):

        fast_exhq_ip_dict = {}
        exhq_api = TdxExHq_API()

        for name, (ip, exhq_port) in self.exhq_ips_dict.items():
            try:
                with exhq_api.connect(ip, exhq_port):
                    start_time = time.time()
                    instrument_count = exhq_api.get_instrument_count()
                    cost_time = time.time() - start_time
                    self.log.write_log(f"{name}({ip}), time: {cost_time:.3f}s, response: {instrument_count}")
                    fast_exhq_ip_dict[f"{ip}:{exhq_port}"] = cost_time
            except:
                print(f"高能预警 ! 扩展行情异常捕获: {ip}:{exhq_port}可能宕机了报错了!")

        ip_str, port_str = min(fast_exhq_ip_dict, key=fast_exhq_ip_dict.get).split(":")
        self.log.write_log(f"-" * 50)
        self.log.write_log(f"Select ({ip_str} : {port_str})")
        self.log.write_log(f"-" * 50)

        return ip_str, int(port_str)

    def get_fast_hq_ip(self) -> (str, int):

        fast_hq_ip_dict = {}
        hq_api = TdxHq_API()

        for name, (ip, hq_port) in self.hq_ips_dict.items():
            try:
                with hq_api.connect(ip, hq_port):
                    start_time = time.time()
                    instrument_count = hq_api.get_security_count(0)
                    cost_time = time.time() - start_time
                    self.log.write_log(f"{name}({ip}), time: {cost_time:.3f}s, response: {instrument_count}")
                    fast_hq_ip_dict[f"{ip}:{hq_port}"] = cost_time
            except:
                print(f"高能预警 ! 标准行情异常捕获: {ip}:{hq_port}可能宕机了报错了!")

        ip_str, port_str = min(fast_hq_ip_dict, key=fast_hq_ip_dict.get).split(":")
        self.log.write_log(f"-" * 50)
        self.log.write_log(f"Select ({ip_str} : {port_str})")
        self.log.write_log(f"-" * 50)
        return ip_str, int(port_str)


if __name__ == '__main__':
    ips_pool = IPsSource()
    # exhq_ip, exhq_port = ips_pool.get_fast_exhq_ip()
    hq_ip, hq_port = ips_pool.get_fast_hq_ip()
    print(1)
