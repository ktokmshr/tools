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

account_id = oak.ACCOUNT_ID
access_token = oak.PERSONAL_ACCESS_TOKEN

api = oandapyV20.API(access_token = access_token, environment = "practice")

datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"
base_datetime = datetime.datetime(year=2019, month=11, day=1)

ic = InstrumentsCandles(
		instrument="USD_JPY",
		params={
			"granularity": consts.Granularity.M5,
			"alignmentTimezone": "Japan",
			"count": 5000
			# "from": base_datetime.strftime(datetime_format),
			# "to": (base_datetime + relativedelta(months=1) - relativedelta(seconds=1)).strftime(datetime_format)
		}
	)

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

df = pd.DataFrame(data)
df.columns = ['datetime', 'volume', 'open', 'high', 'low', 'close']
df = df.set_index('datetime')
df.index = pd.to_datetime(df.index)
# print(df.head())
# print(df.isna().all())

engine = db_access.get_engine()
df.to_sql('usd_jpy', con=engine, if_exists='append')
