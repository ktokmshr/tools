import pandas as pd
import numpy as np
import time
import seaborn as sns
import matplotlib.pyplot as plt
import datetime

import consts
import db_access

from backtesting import Strategy
from backtesting import Backtest

import talib as ta

def bb3(array, timeperiod):
    gain = pd.DataFrame(array)
    gain.columns = ['close']
    upper, middle, lower = ta.BBANDS(
        gain.close,
        timeperiod=timeperiod,
        nbdevup=3,
        nbdevdn=3,
        matype=0
    )
    gain['bb_upper'] = upper
    gain['bb_lower'] = lower
    return gain['bb_upper'], gain['bb_lower']

def bb2(array, timeperiod):
    gain = pd.DataFrame(array)
    gain.columns = ['close']
    upper, middle, lower = ta.BBANDS(
        gain.close,
        timeperiod=timeperiod,
        nbdevup=2,
        nbdevdn=2,
        matype=0
    )
    gain['bb_upper'] = upper
    gain['bb_lower'] = lower
    return gain['bb_upper'], gain['bb_lower']

def get_raw_data(limit=None):
    engine = db_access.get_engine()
    query = "select * from usd_jpy"
    if (limit is not None and type(limit) is int):
        query = query + "limit " + str(limit)
    return pd.read_sql("SELECT * FROM usd_jpy", engine)

class bb_band(Strategy):
    def init(self):
        self.bb_timeperiod = 9
        self.trade_range = 0.05 # 損切りライン 7pips
        self.bb_upper2, self.bb_lower2 = self.I(bb2, self.data.Close, self.bb_timeperiod)
        self.bb_upper3, self.bb_lower3 = self.I(bb3, self.data.Close, self.bb_timeperiod)

    def next(self):
        if (self.position):
            # 買いポジションを持っている場合
            if (self.position.is_long):
                if (self.data.Close[-1] > self.bb_lower2):
                    # 利確
                    self.position.close()
            # 売りポジションを持っている場合
            elif (self.position.is_short):
                if (self.data.Close[-1] < self.bb_upper2:
                    # 利確
                    self.position.close()
            else:
                print("Unexpected Status")
        else:
            # ポジションを持っていない場合
            if (self.data.High[-1] > self.bb_upper3):
                self.sell(price=self.data.High[-1], sl=self.data.High[-1] + self.trade_range)
            elif (self.data.Low[-1] < self.bb_lower3):
                self.buy(price=self.data.Low[-1], sl=self.data.Low[-1] - self.trade_range)

if __name__ == "__main__":
    df = get_raw_data()
    df = df[["datetime","open","high","low","close","volume"]].copy()
    df.columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df = df.reset_index().set_index('Datetime')
    print(df.head())

    bt = Backtest(df, bb_band, cash=100000, commission=.00004, trade_on_close=True)
    output = bt.run()
    print(output)
    bt.plot()
