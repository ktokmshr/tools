from oandapyV20.endpoints.instruments import InstrumentsCandles
import oandapyV20
import oanda_access_key as oak
import consts
import db_access

from dateutil.relativedelta import relativedelta
import datetime
import json
import pandas as pd
from sqlalchemy import create_engine
import time
from tqdm import tqdm

account_id = oak.ACCOUNT_ID
access_token = oak.PERSONAL_ACCESS_TOKEN

api = oandapyV20.API(access_token = access_token, environment = "practice")

datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"
start_datetime = datetime.datetime(year=2019, month=1, day=1)
end_datetime = datetime.datetime(year=2020, month=3, day=6)
date_window = 2

while (start_datetime + relativedelta(days=date_window)) <= end_datetime:
	try:
		ic = InstrumentsCandles(
				instrument="USD_JPY",
				params={
					"granularity": consts.Granularity.D,
					"alignmentTimezone": "Japan",
					# "count": 5000
					"from": start_datetime.strftime(datetime_format),
					"to": (start_datetime + relativedelta(days=date_window) - relativedelta(seconds=1)).strftime(datetime_format)
				}
			)
		start_datetime = start_datetime + relativedelta(days=date_window)
		api.request(ic)
		data = []
		for candle in ic.response["candles"]:
			data.append(
				[
					candle['time'],
					candle['volume'],
					candle['mid']['o'],
					candle['mid']['h'],
					candle['mid']['l'],
					candle['mid']['c']
				]
			)
		time.sleep(1)
		df = pd.DataFrame(data)
		if(df.empty):
			continue
		df.columns = ['datetime', 'volume', 'open', 'high', 'low', 'close']
		df = df.set_index('datetime')
		df.index = pd.to_datetime(df.index)
		# print(df.head())
		# print(df.isna().all())
		engine = db_access.get_engine()
		df.to_sql('usd_jpy_d', con=engine, if_exists='append')
	except Exception as e:
		print(e)
