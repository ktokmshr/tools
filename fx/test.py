import pandas as pd
import numpy as np
import time
import seaborn as sns
import matplotlib.pyplot as plt
import datetime

import consts
import db_access
import bollinger_bands

def get_raw_data(limit=None):
	engine = db_access.get_engine()
	query = "select * from usd_jpy"
	if (limit is not None and type(limit) is int):
		query = query + "limit " + str(limit)
	return pd.read_sql("SELECT * FROM usd_jpy", engine)

if __name__ == "__main__":
	df_raw = get_raw_data()
	df_bband_2 = bollinger_bands.get_bollinger_bands(
		df_raw,
		consts.BBand.BB_BAND_WINDOW,
		consts.BBand.SIGMA_2
	)
	df_extends = pd.merge(df_raw, df_bband_2, on='datetime')
	print(df_extends.head(20))
