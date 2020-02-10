#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/1 下午3:23
@Author   :   Fangyang
"""

import random
import pandas as pd
import numpy as np
import gym

DEFAULT_BARS_COUNT = 10
DEFAULT_COMMISSION_RATE = 2.5 / 10000
DEFAULT_TIME_COST = 0.1 / 10000
DEFAULT_SECURITY_RATE = 9 / 100  # 保证金比例 螺纹暂时按9%
DEFAULT_CONTRACT_PROD = 10  # 合约乘数
BALANCE = 1.0e6


class FutureEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(
            self, prices_df: pd.DataFrame,
            bars_count: int = DEFAULT_BARS_COUNT,
            commission_rate: float = DEFAULT_COMMISSION_RATE,
            time_cost: float = DEFAULT_TIME_COST,
            balance: float = BALANCE,
            security_rate: float = DEFAULT_SECURITY_RATE,
            contract_prod: int = DEFAULT_CONTRACT_PROD
    ):

        assert commission_rate >= 0.0, "佣金比例 should >= 0.0"
        assert contract_prod > 0, "合约乘数 should > 0"
        assert security_rate > 0.0, "保证金比率 should > 0.0"
        assert time_cost >= 0.0, "Time cost should >= 0.0"
        assert balance >= 0.0, "Balance should >= 0.0"
        assert len(prices_df) > 0, "DataFrame length should > 0"

        self.ix = 0  # 每次游戏开始数据的起始的索引
        self.step_len = bars_count  # 每个step的长度
        self.step_n = 1  # 连续obs 相邻 steps 之间的跨度, 为了简化计算, 这里默认为1步, 如果想改周期, 请修改输入的KBar周期
        self.have_long_position = False  # 是否持多仓
        self.have_short_position = False  # 是否持空仓
        self.new_df_first_bar_open_price = 0.0  # 开仓价格
        self.buy_condition = False
        self.sell_condition = False
        self.short_condition = False
        self.cover_condition = False

        self.commission_rate = commission_rate  # 手续费率
        self.contract_prod = contract_prod  # 合约乘数
        self.security_rate = security_rate  # 保证金比例
        self.time_cost = time_cost

        self.start_balance = balance
        self.hold_money_value = self.start_balance
        self.hold_share_value = 0.0
        self.net_position = 0  # 带正负号
        self.long_position = 0  # 不带正负号
        self.short_position = 0  # 不带正负号
        # self.long_profit_df = pd.DataFrame()
        # self.short_profit_df = pd.DataFrame()

        self.prices_df_columns_list = list(prices_df.columns)
        self.account_position_columns_list = [
            'net_position', 'long_position', 'short_position'  # , 'trade_num'
        ]
        self.account_value_columns_list = [
            'balance', 'hold_share_value', 'hold_money_value'  # , 'profit'
        ]
        for col in self.account_position_columns_list + self.account_value_columns_list:
            prices_df[col] = self.start_balance if (col == 'balance' or col == 'hold_money_value') else 0.0

        self.prices_df = prices_df
        self.prices_df_length = len(prices_df)
        self.cur_state_df = pd.DataFrame()
        self.trade_record_df = pd.DataFrame()

        self.action_space = gym.spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32)
        # shape 为 df columns (包含时间, 去掉日期) + position + reward
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf,
                                                shape=(self.prices_df.shape[1] * self.step_len,),
                                                dtype=np.float32)

    def reset(self):
        """ 初始化第一个state, 默认上面没有任何操作"""
        self.ix = random.choice(range(len(self.prices_df) - self.step_len))
        self.cur_state_df = self.prices_df.iloc[self.ix: self.ix + self.step_len, :]

        # 初始化起始状态时, 可能在某个bar上有多空仓位, 此处排除 Sell Cover 平仓动作
        # start_position_index = random.choice(range(self.step_len))
        # start_position = random.choice([i for i in Actions if (i != Actions.Cover and i != Actions.Sell)])
        # start_position_index += self.ix
        # self.cur_state_df['position'][start_position_index] = start_position
        # if start_position != Actions.Skip:
        #     pass

        # self.total_position = start_position
        # self.offset_total_price = self.cur_state_df['open_price'][start_position_index] * self.total_position

        return self.cur_state_df

    def reset_from_start(self):
        """ 初始化第一个state, 用于回测"""
        self.ix = 0
        self.cur_state_df = self.prices_df.iloc[self.ix: self.ix + self.step_len, :].reset_index(drop=True)

        return self.cur_state_df

    def update_new_df(self, action: float, new_df: pd.DataFrame, commission: float, trade_num: int):
        """
        记录 开平仓价格 和 位置,
        给出step_reward均摊更新到new step的每个bar上
        更新持仓信息
        """
        new_df = self.update_new_df_position_info(trade_num, new_df)

        # 本次step买进 trade_num手 share 的 真金白银 钱
        trade_share_on_first_bar_open_value = trade_num \
                                              * self.contract_prod \
                                              * self.new_df_first_bar_open_price \
                                              * self.security_rate
        # 花掉这么多价值的钱+手续费
        if self.buy_condition or self.sell_condition:
            self.hold_money_value -= (trade_share_on_first_bar_open_value + commission)
        elif self.short_condition or self.cover_condition:
            self.hold_money_value += (trade_share_on_first_bar_open_value - commission)

        # 账户余额
        new_df.loc[:, 'hold_money_value'] = self.hold_money_value

        # 更新交易记录表
        if self.trade_record_df.empty:
            self.trade_record_df = new_df.iloc[[0]]
        self.trade_record_df = self.trade_record_df.append(new_df.iloc[0])

        # 实时净值
        if self.buy_condition or self.sell_condition:
            # 持仓share的实时价值
            new_df.loc[:, 'hold_share_value'] = new_df.apply(
                lambda x: x['close_price'] * self.contract_prod * self.security_rate * x['long_position'],
                axis=1
            )
            new_df.loc[:, 'balance'] = new_df.loc[:, 'hold_share_value'] + self.hold_money_value
            # new_df['profit'] = new_df['balance'] - self.start_balance

        elif self.short_condition or self.cover_condition:

            new_df.loc[:, 'hold_share_value'] = new_df.apply(
                lambda x: x['close_price'] * self.contract_prod * self.security_rate * abs(x['short_position']), axis=1)

            new_df.loc[:, 'balance'] = 2 * (self.start_balance - commission) - abs(
                new_df.loc[:, 'hold_share_value']) - self.hold_money_value
            # new_df['profit'] = new_df['balance'] - self.start_balance

        # 在上面条件判断后, 更新多空持仓逻辑
        self.have_long_position = True if self.long_position > 0 else False
        self.have_short_position = True if self.short_position > 0 else False

        return new_df, new_df['balance'].iloc[-1] - self.start_balance

    def get_cur_state_trade_num_by_money(self, action: float, current_price: float):
        """通过多空仓位资金使用比例, 计算当前状态下最后一根bar收盘价可交易的数量"""
        # (买入比例 * 账户金额) / (当前价格 * 合约乘数 * (保证金比例 + 手续费率)) = 交易手数
        return round(
            (action[0] * self.hold_money_value) /
            (current_price * self.contract_prod * (self.security_rate + self.commission_rate))
        )

    def get_cur_state_trade_num_by_share(self, action: float, current_price: float):
        """通过持仓可使用比例, 计算当前状态下最后一根bar收盘价可交易的数量"""
        # (买入比例 * 账户金额) / (当前价格 * 合约乘数 * 保证金比例) = 交易手数
        return round(action[0] * abs(self.net_position))

    def get_next_state_commission(self, trade_num):
        """ float: = 交易手数 * 合约乘数 * 成交价格(open) * 交易费率 """
        return abs(trade_num) * self.contract_prod * self.new_df_first_bar_open_price * self.commission_rate

    def step(self, action: float):
        # 给出下一个状态
        # obs中含有全局reward, Agent设计的时候需要进行记忆
        obs = self.cur_state_df.iloc[self.step_n:, :]
        obs_last_index = self.cur_state_df.index.to_list()[-1]
        reward = 0
        done = False

        # 更新action条件
        self.buy_condition = action > 0.0 and not self.have_short_position
        self.sell_condition = action < 0.0 and self.have_long_position
        self.short_condition = action < 0.0 and not self.have_long_position
        self.cover_condition = action > 0.0 and self.have_short_position

        if obs_last_index + 1 + self.step_n > self.prices_df_length:
            done = True
            info = {}
            return obs, reward, done, info

        new_df = self.prices_df.iloc[obs_last_index + 1: obs_last_index + 1 + self.step_n]
        # 获取当前状态的最后收盘价, 用于计算开仓数量
        self.new_df_first_bar_open_price = new_df.loc[:, 'open_price'].iloc[0]
        # buy, sell 通过hold_money来计算比例
        if self.buy_condition or self.short_condition:
            # 有正负, 和action一致
            trade_num = self.get_cur_state_trade_num_by_money(action, self.new_df_first_bar_open_price)
        else:
            trade_num = self.get_cur_state_trade_num_by_share(action, self.new_df_first_bar_open_price)
        commission = self.get_next_state_commission(trade_num)  # no sign >= 0

        # 给出下一个状态的 reward 和 done flag
        # TODO 这里环境预设不会双向持仓, 保证训练出来的模型不会有相同行为
        # 开仓 Buy
        if self.buy_condition:
            self.long_position += trade_num
            new_df, reward = self.update_new_df(action, new_df, commission, trade_num)
        # 平仓 sell
        elif self.sell_condition:
            # 减持多仓数目不能大于持仓量, 大于的部分按照全平处理
            trade_num, done = (trade_num, False) if abs(trade_num) < self.long_position else (-self.long_position, True)
            self.long_position += trade_num
            new_df, reward = self.update_new_df(action, new_df, commission, trade_num)
        # 开仓 short
        elif self.short_condition:
            self.short_position += abs(trade_num)  # self.short_position不带正负号, trade_num带正负号
            new_df, reward = self.update_new_df(action, new_df, commission, trade_num)
        # 平仓 cover
        elif self.cover_condition:
            trade_num, done = (trade_num, False) if trade_num < self.short_position else (self.short_position, True)
            self.short_position -= trade_num  # 注意这里是减持
            new_df, reward = self.update_new_df(action, new_df, commission, trade_num)

        # skip 或者 手有多仓 还收到 buy action
        else:
            reward -= self.time_cost
            trade_num = 0
            new_df = self.update_new_df_position_info(trade_num, new_df)
            new_df.loc[:, 'hold_money_value'] = self.hold_money_value

            new_df.loc[:, 'hold_share_value'] = new_df.apply(
                lambda x: x['close_price'] * self.contract_prod * self.security_rate * abs(x['net_position']), axis=1)

            if self.have_long_position:
                new_df.loc[:, 'balance'] = new_df.loc[:, 'hold_share_value'] + self.hold_money_value
                # new_df['profit'] = new_df['balance'] - self.start_balance
            elif self.have_short_position:
                new_df.loc[:, 'balance'] = 2 * self.start_balance - abs(
                    new_df.loc[:, 'hold_share_value']) - self.hold_money_value
                # new_df['profit'] = new_df['balance'] - self.start_balance

        obs = obs.append(new_df)
        self.cur_state_df = obs
        obs_last_index = obs.index.to_list()[-1]
        if obs_last_index + 1 + self.step_n >= self.prices_df_length:
            done = True
        info = {}

        return obs, reward, done, info

    def update_new_df_position_info(self, trade_num: int, new_df: pd.DataFrame):

        # new_df['trade_num'] = trade_num
        new_df.loc[:, 'long_position'] = self.long_position
        new_df.loc[:, 'short_position'] = self.short_position
        self.net_position = self.long_position - self.short_position
        new_df.loc[:, 'net_position'] = self.net_position

        return new_df

    def render(self, mode='human', close=False):
        pass

    def close(self):
        pass


if __name__ == "__main__":
    df = pd.read_csv("./data/RBL8.csv")
    columns_list = [
        'open_price', 'high_price', 'low_price', 'close_price',
        'open_interest', 'volume'
    ]
    df = df[columns_list]

    env = FutureEnv(prices_df=df)
    action = env.action_space.sample()
    initial_state_df = env.reset()

    # 将起始状态送入model, 给出output action
    reward_list = []
    done_list = []

    obs0, reward, done, info = env.step(action)
    reward_list.append(reward)
    done_list.append(done)
    for _ in range(100):
        # action_key = random.choice(list(action_ratio_dict.keys()))
        # action = action_ratio_dict[action_key]

        action = env.action_space.sample()
        print(action)
        obs, reward, done, info = env.step(action)
        obs0 = obs0.append(obs.iloc[[-1]])
        reward_list.append(reward)
        done_list.append(done)

    print(1)
