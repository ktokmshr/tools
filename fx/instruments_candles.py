from oandapyV20.endpoints.instruments import InstrumentsCandles
import oandapyV20
import oanda_access_key as oak
import consts

from dateutil.relativedelta import relativedelta
import datetime
import json
import pandas as pd

account_id = oak.ACCOUNT_ID
access_token = oak.PERSONAL_ACCESS_TOKEN

api = oandapyV20.API(access_token = access_token, environment = "practice")

datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"
base_datetime = datetime.datetime(year=2017, month=1, day=1)

ic = InstrumentsCandles(
		instrument="USD_JPY",
		params={
			"granularity": consts.Granularity.H4,
			"alignmentTimezone": "Japan",
			"from":base_datetime.strftime(datetime_format),
			"to": (base_datetime + relativedelta(years=1) - relativedelta(seconds=1)).strftime(datetime_format)
			}
	)

api.request(ic)

# with open("./" + base_datetime.strftime(%Y-%m-%d) + "_H4.json", "w") as f:
# 	f.write(json.dumps(ic.response, indent=4))

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
df.columns = ['time', 'volume', 'open', 'high', 'low', 'close']
df = df.set_index('time')
df.index = pd.to_datetime(df.index)
print(df.head())
print(df.tail())
