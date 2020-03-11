#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/1 下午3:23
@Author   :   Fangyang
"""

import random
import enum

import pandas as pd
import numpy as np
import gym

DEFAULT_BARS_COUNT = 10
DEFAULT_COMMISSION_RATE = 2.5 / 10000
DEFAULT_TIME_COST = 0.1 / 10000
DEFAULT_SECURITY_RATE = 9 / 100  # 保证金比例 螺纹暂时按9%
DEFAULT_CONTRACT_PROD = 10  # 合约乘数
BALANCE = 1.0e6


class Actions(enum.Enum):
    # 这里和FutureEnv中声明的类型和结构保持一致
    # TODO 做测试先设置为0.2, 以后由神经网络给出
    Buy = np.array([0.3], dtype=np.float32)
    Sell = np.array([0.5], dtype=np.float32)

    Short = np.array([0.4], dtype=np.float32)
    Cover = np.array([0.0], dtype=np.float32)


class FutureEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(
            self, prices_df: pd.DataFrame, bars_count: int = DEFAULT_BARS_COUNT,
            commission_rate: float = DEFAULT_COMMISSION_RATE, time_cost: float = DEFAULT_TIME_COST,
            balance: float = BALANCE, security_rate: float = DEFAULT_SECURITY_RATE,
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
        self.step_n = 5  # 连续obs 相邻 steps 之间的跨度
        self.have_long_position = False  # 是否持多仓
        self.have_short_position = False  # 是否持空仓
        self.new_df_first_bar_open_price = 0.0  # 开仓价格
        self.new_df_last_bar_close_price = 0.0  # 用于记录单步收益
        self.next_position = 0  # 持仓手数, 正代表多, 负代表空

        self.commission_rate = commission_rate
        self.contract_prod = contract_prod
        self.security_rate = security_rate
        self.time_cost = time_cost

        self.start_balance = balance
        self.hold_money_value = self.start_balance
        self.hold_share_value = 0.0
        self.position = 0
        # self.cum_profit = pd.Series([0.0 for i in range(self.step_n)])
        self.cum_profit = np.empty(self.step_n)

        prices_df['position'] = 0
        prices_df['profit'] = 0.0
        prices_df['balance'] = self.start_balance
        prices_df['trade_num'] = 0
        prices_df['hold_share_value'] = 0.0
        prices_df['hold_money_value'] = 0.0

        self.prices_df = prices_df
        self.prices_df_length = len(prices_df)
        self.cur_state_df = pd.DataFrame()

        self.action_space = gym.spaces.Tuple(
            spaces=(
                gym.spaces.Discrete(n=len(Actions)),
                gym.spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)
            )
        )
        # shape 为 df columns (包含时间, 去掉日期) + position + reward
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf,
                                                shape=(self.prices_df.shape[1],),
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
        # self.offset_total_price = self.cur_state_df['<OPEN>'][start_position_index] * self.total_position

        return self.cur_state_df

    def update_new_df(self, new_df: pd.DataFrame, action: Actions, commission: float, trade_num: int):
        """
        记录 开平仓价格 和 位置,
        给出step_reward均摊更新到new step的每个bar上
        更新持仓信息
        """
        if action == Actions.Buy:

            new_df['trade_num'] = trade_num
            self.position += trade_num
            new_df['position'] = self.position

            # 本次step买进 trade_num手 share 的 真金白银 钱
            trade_share_on_first_bar_open_value = trade_num * self.contract_prod * self.new_df_first_bar_open_price * self.security_rate
            # 花掉这么多价值的钱+手续费
            self.hold_money_value -= (trade_share_on_first_bar_open_value + commission)
            # 账户余额
            new_df['hold_money_value'] = self.hold_money_value
            # 实时净值
            new_df['balance'] = new_df.apply(
                lambda x: x['<CLOSE>'] * self.contract_prod * self.security_rate * x['position'], axis=1
            ) + self.hold_money_value
            # 持仓share的实时价值
            new_df['hold_share_value'] = new_df.apply(
                lambda x: x['<CLOSE>'] * self.contract_prod * self.security_rate * x['position'], axis=1)

            # 将单次profit进行累加
            # self.cum_profit += new_df['hold_share_value'].values - trade_share_on_first_bar_open_value
            # new_df['profit'] = self.cum_profit
            new_df['profit'] = new_df['balance'] - self.start_balance

        elif action == Actions.Sell:
            # 减持多仓数目不能大于持仓量, 大于的部分按照全平处理
            trade_num = -trade_num if trade_num < self.position else -self.position

            new_df['trade_num'] = trade_num
            self.position += trade_num
            new_df['position'] = self.position

            # 本次step卖出 trade_num手 share 的 真金白银 钱
            trade_share_on_first_bar_open_value = trade_num * self.contract_prod * self.new_df_first_bar_open_price * self.security_rate
            # 增加这么多价值的钱+手续费
            self.hold_money_value -= (trade_share_on_first_bar_open_value + commission)
            # 账户余额
            new_df['hold_money_value'] = self.hold_money_value
            # 实时净值
            new_df['balance'] = new_df.apply(
                lambda x: x['<CLOSE>'] * self.contract_prod * self.security_rate * x['position'], axis=1
            ) + self.hold_money_value
            # 持仓share的实时价值
            new_df['hold_share_value'] = new_df.apply(
                lambda x: x['<CLOSE>'] * self.contract_prod * self.security_rate * x['position'], axis=1)

            # 将单次profit进行累加
            # self.cum_profit += new_df['hold_share_value'].values - trade_share_on_first_bar_open_value
            # new_df['profit'] = self.cum_profit
            new_df['profit'] = new_df['balance'] - self.start_balance

        elif action == Actions.Short:
            trade_num = -trade_num

            new_df['trade_num'] = trade_num
            self.position += trade_num
            new_df['position'] = self.position

            # 本次step卖出 trade_num手 share 的 真金白银 钱
            trade_share_on_first_bar_open_value = trade_num * self.contract_prod * self.new_df_first_bar_open_price * self.security_rate
            # 增加这么多价值的钱+手续费
            self.hold_money_value -= (trade_share_on_first_bar_open_value + commission)
            # 账户余额
            new_df['hold_money_value'] = self.hold_money_value
            # 实时净值
            new_df['balance'] = new_df.apply(
                lambda x: x['<CLOSE>'] * self.contract_prod * self.security_rate * x['position'], axis=1
            ) + self.hold_money_value
            # 持仓share的实时价值
            new_df['hold_share_value'] = new_df.apply(
                lambda x: x['<CLOSE>'] * self.contract_prod * self.security_rate * x['position'], axis=1)

            # 将单次profit进行累加
            # self.cum_profit += new_df['hold_share_value'].values - trade_share_on_first_bar_open_value
            # new_df['profit'] = self.cum_profit
            new_df['profit'] = new_df['balance'] - self.start_balance
        elif action == Actions.Cover:
            step_reward = -(new_df['<CLOSE>'].iloc[
                                0] - self.new_df_first_bar_open_price) / self.new_df_first_bar_open_price + reward
            new_df['position'] = trade_num
            self.have_short_position = False

        # 将reward均摊到每个新增bar上
        # new_df['profit'] = step_reward / self.step_n

        return new_df, new_df['balance'].iloc[-1]

    def get_cur_state_trade_num(self, action, current_price):
        """通过多空仓位资金使用比例, 计算当前状态下最后一根bar收盘价可交易的数量"""
        # (买入比例 * 账户金额) / (当前价格 * 合约乘数 * 保证金比例) = 交易手数
        return int(
            (action.value[0] * self.hold_money_value) / (current_price * self.contract_prod * self.security_rate))

    def get_next_state_commission(self, trade_num):
        """ float: = 交易手数 * 合约乘数 * 成交价格(open) * 交易费率 """
        return trade_num * self.contract_prod * self.new_df_first_bar_open_price * self.commission_rate

    def step(self, action):
        # 给出下一个状态
        # obs中含有全局reward, Agent设计的时候需要进行记忆
        obs = self.cur_state_df.iloc[self.step_n:, :]
        obs_last_index = self.cur_state_df.index.to_list()[-1]
        reward = 0
        done = False

        if obs_last_index + 1 + self.step_n > self.prices_df_length:
            done = True
            info = {}
            return obs, reward, done, info

        new_df = self.prices_df.iloc[obs_last_index + 1: obs_last_index + 1 + self.step_n]
        # 获取当前状态的最后收盘价, 用于计算开仓数量
        current_price = obs['<CLOSE>'].iloc[-1]
        trade_num = self.get_cur_state_trade_num(action, current_price)
        self.new_df_first_bar_open_price = new_df['<OPEN>'].iloc[0]
        self.new_df_last_bar_close_price = new_df['<CLOSE>'].iloc[-1]

        commission = self.get_next_state_commission(trade_num)
        reward -= commission

        # 给出下一个状态的 reward 和 done flag
        # 开仓
        if action == Actions.Buy:
            new_df, reward = self.update_new_df(new_df, action, commission, trade_num)

        elif action == Actions.Short:
            new_df, reward = self.update_new_df(new_df, action, commission, trade_num)

        # 平仓
        elif action == Actions.Sell:
            new_df, reward = self.update_new_df(new_df, action, commission, trade_num)
            if not self.have_short_position:
                done = True

        elif action == Actions.Cover and self.have_short_position:
            new_df, reward = self.update_new_df(new_df, action, reward)
            if not self.have_long_position:
                done = True

        # skip 或者 手有多仓 还收到 buy action
        else:
            reward -= self.time_cost

        obs = obs.append(new_df)
        self.cur_state_df = obs
        obs_last_index = obs.index.to_list()[-1]
        if obs_last_index + 1 + self.step_n >= self.prices_df_length:
            done = True
        info = {}

        return obs, reward, done, info

    def render(self, mode='human', close=False):
        pass

    def close(self):
        pass


if __name__ == "__main__":
    df = pd.read_csv("./data/YNDX_150101_151231.csv")
    env = FutureEnv(prices_df=df.iloc[:, 1:])

    # xx = env.action_space.sample()
    # Tuple的第一个为action, 后面为对应的数值
    # (0, array([0.6831512], dtype=float32))
    initial_state_df = env.reset()

    # 将起始状态送入model, 给出output action
    reward_list = []
    done_list = []

    action = Actions.Buy
    obs0, reward, done, info = env.step(action)
    reward_list.append(reward)
    done_list.append(done)
    for _ in range(10):
        action = Actions.Sell
        obs, reward, done, info = env.step(action)
        obs0 = obs0.append(obs)
        reward_list.append(reward)
        done_list.append(done)

    action = Actions.Sell
    obs, reward, done, info = env.step(action)
    obs0 = obs0.append(obs)
    reward_list.append(reward)
    done_list.append(done)
    print(1)
