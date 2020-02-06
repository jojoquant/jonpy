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
DEFAULT_COMMISSION_PERC = 2.5 / 10000
DEFAULT_TIME_COST = 0.1 / 10000
BALANCE = 1.0e6


class Actions(enum.Enum):
    Skip = 0

    Buy = 1
    Sell = 2

    Short = 3
    Cover = 4


class StocksEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(
            self, prices_df: pd.DataFrame, bars_count: int = DEFAULT_BARS_COUNT,
            commission: float = DEFAULT_COMMISSION_PERC, time_cost: float = DEFAULT_TIME_COST,
            balance: float = BALANCE
    ):

        assert commission >= 0.0, "Commission should >= 0.0"
        assert balance >= 0.0, "Balance should >= 0.0"
        assert time_cost >= 0.0, "Time cost should >= 0.0"
        assert len(prices_df) > 0, "DataFrame length should > 0"
        assert len(Actions) > 1, "Actions length should > 1"

        self.commission_perc = commission
        self.balance = balance
        self.time_cost = time_cost

        prices_df['position'] = 0
        prices_df['profit'] = 0
        self.prices_df = prices_df
        self.prices_df_length = len(prices_df)
        self.cur_state_df = pd.DataFrame()

        self.action_space = gym.spaces.Discrete(n=len(Actions))
        # shape 为 df columns (包含时间, 去掉日期) + position + reward
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf,
                                                shape=(self.prices_df.shape[1],),
                                                dtype=np.float32)

        self.ix = 0  # 每次游戏开始数据的起始的索引
        self.step_len = bars_count  # 每个step的长度
        self.step_n = 5  # 连续obs 相邻 steps 之间的跨度
        # self.offset_total_price = 0.0  # 持仓总价 = 按open价开仓的价格 * 仓位(带正负号表示方向)
        # self.total_position = 0  # 持仓总量, 带正负号表示方向
        self.have_long_position = False  # 是否持多仓
        self.have_short_position = False  # 是否持空仓
        self.open_price = 0.0  # 开仓价格

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

    def update_new_df(self, new_df: pd.DataFrame, action: Actions, reward: float):
        """
        记录 开平仓价格 和 位置,
        给出step_reward均摊更新到new step的每个bar上
        更新持仓信息
        """
        new_df['position'].iloc[0] = action
        # 新增n根 k线上的 reward 平均, 即每个k线算 E((c-o)/o), 非常小
        # step_reward = new_df.apply(lambda x: (x['<CLOSE>'] - x['<OPEN>'])/x['<OPEN>'], axis=1).sum()
        self.open_price = new_df['<OPEN>'].iloc[0]

        if action == Actions.Buy:
            # 最后1根bar的C
            step_reward = (new_df['<CLOSE>'].iloc[-1] - self.open_price) / self.open_price + reward
            self.have_long_position = True
        elif action == Actions.Sell:
            # 第1根bar的C
            step_reward = (new_df['<CLOSE>'].iloc[0] - self.open_price) / self.open_price + reward
            self.have_long_position = False
        elif action == Actions.Short:
            step_reward = -(new_df['<CLOSE>'].iloc[-1] - self.open_price) / self.open_price + reward
            self.have_short_position = True
        elif action == Actions.Cover:
            step_reward = -(new_df['<CLOSE>'].iloc[0] - self.open_price) / self.open_price + reward
            self.have_short_position = False

        # 将reward均摊到每个新增bar上
        new_df['profit'] = step_reward / self.step_n

        return new_df, step_reward

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

        # 给出下一个状态的 reward 和 done flag
        # 开仓
        if action == Actions.Buy and not self.have_long_position:
            reward -= self.commission_perc
            new_df, reward = self.update_new_df(new_df, action, reward)

        elif action == Actions.Short and not self.have_short_position:
            reward -= self.commission_perc
            new_df, reward = self.update_new_df(new_df, action, reward)

        # 平仓
        elif action == Actions.Sell and self.have_long_position:
            reward -= self.commission_perc
            new_df, reward = self.update_new_df(new_df, action, reward)
            if not self.have_short_position:
                done = True

        elif action == Actions.Cover and self.have_short_position:
            reward -= self.commission_perc
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
    env = StocksEnv(prices_df=df.iloc[:, 1:])
    initial_state_df = env.reset()

    # 将起始状态送入model, 给出output action
    reward_list = []
    done_list = []

    action = Actions.Buy
    obs0, reward, done, info = env.step(action)
    reward_list.append(reward)
    done_list.append(done)
    for _ in range(10):
        action = Actions.Skip
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
