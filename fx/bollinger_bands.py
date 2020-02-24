import pandas as pd
import numpy as np
import time
import datetime
import consts


def get_bollinger_bands(df, window:int, sigma:int):
	bband = pd.DataFrame()

	bband['datetime'] = df['datetime']
	# bband['close'] = df['close']
	bband['mean'] = df['close'].rolling(window=window).mean()
	# bband['std'] = df['close'].rolling(window=window).std()
	bband['upper'] = bband['mean'] + (bband['std'] * sigma)
	bband['lower'] = bband['mean'] - (bband['std'] * sigma)

	return bband
