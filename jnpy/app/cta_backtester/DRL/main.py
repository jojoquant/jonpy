#!/usr/bin/env python
# _*_coding:utf-8_*_

"""
@Datetime :   2020/2/7 下午7:19
@Author   :   Fangyang
"""

import pandas as pd
import numpy as np
from dataclasses import fields

from jnpy.app.cta_backtester.DRL.environ_future import FutureEnv
from jnpy.app.cta_backtester.DRL.model import *


def accept_bars_data_list(all_bar_list: list):
    if all_bar_list:
        df = pd.DataFrame(all_bar_list, columns=['all_bars'])
        for field in fields(all_bar_list[0]):
            attr = field.name
            df[attr] = df['all_bars'].apply(lambda x: getattr(x, attr))
        df.drop(labels=['all_bars'], axis=1, inplace=True)
    else:
        df = None

    df.to_csv("/home/fangyang/桌面/python_project/vnpy/vnpy/app/cta_backtester_jnpy/DRL/data/RBL8.csv", index=False)
    print(1)



if __name__ == "__main__":
    action_ratio_dict = {
        "Buy": np.array([0.3], dtype=np.float32),
        "Sell": np.array([0.3], dtype=np.float32),
        "Short": np.array([0.4], dtype=np.float32),
        "Cover": np.array([0.3], dtype=np.float32),
    }

    df = pd.read_csv('./data/RBL8.csv')
    columns_list = [
        'open_price', 'high_price', 'low_price', 'close_price',
        'open_interest', 'volume'
    ]
    df = df[columns_list]
    env = FutureEnv(prices_df=df, action_ratio_dict=action_ratio_dict)

    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space[0].n
    max_action = env.action_space[1].high[0]

    action, value = env.action_space_sample()
    # Tuple的第一个为action, 后面为对应的数值
    # (0, array([0.6831512], dtype=float32))
    initial_state_df = env.reset()

    # 将起始状态送入model, 给出output action
    reward_list = []
    done_list = []

    obs0, reward, done, info = env.step('Buy')
    reward_list.append(reward)
    done_list.append(done)
    for _ in range(10):
        # action_key = random.choice(list(action_ratio_dict.keys()))
        # action = action_ratio_dict[action_key]

        action, value = env.action_space_sample()
        obs, reward, done, info = env.step(action)
        obs0 = obs0.append(obs)
        reward_list.append(reward)
        done_list.append(done)
    print(1)
