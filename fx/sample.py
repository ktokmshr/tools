import datetime
import pandas as pd

import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc

import db_access

UNIT = 10000
ASSET = 300000
DIFF_PRICE = 0.10

def get_datas():
	engine = db_access.get_engine()
	return pd.read_sql("SELECT * FROM usd_jpy", engine)

def convert_datas(datas):
	datas['open'] = datas['open'].astype(float)
	datas['high'] = datas['high'].astype(float)
	datas['low'] = datas['low'].astype(float)
	datas['close'] = datas['close'].astype(float)

	quotes_arr = []
	tmp_open_price = 0
	tmp_high_price = []
	tmp_low_price = []
	tmp_close_price = 0
	count = 0

	for loop, cDate in enumerate(datas['time']):
		isNext = False
		cDatetime = datetime.datetime.strptime(str(cDate), "%Y-%m-%d %H:%M:%S")

		if cDatetime.minute % 5 == 0:
			isNext = True

		if tmp_open_price == 0:
			tmp_open_price = datas['open'][loop]

		if isNext == True and loop != 0:
			data = []
			data.append(cDate)
			data.append(tmp_open_price)
			data.append(max(tmp_high_price))
			data.append(min(tmp_low_price))
			data.append(tmp_close_price)

			pddata = pd.DataFrame([data])
			pddata.columns = ["time", "open", "high", "low", "close"]
			pddata.index = [count]
			quotes_arr.append(pddata)

			tmp_open_price = datas['open'][loop]
			tmp_high_price = []
			tmp_low_price = []
			count += 1

		tmp_high_price.append(datas['high'][loop])
		tmp_low_price.append(datas['low'][loop])
		tmp_close_price = datas['close'][loop]

	for idx, value in enumerate(quotes_arr):
		if idx == 0:
			quotes = quotes_arr[idx]
		else:
			quotes = pd.concat([quotes, value],axis=0)

	quotes['time'] = quotes['time']
	quotes['open'] = quotes['open'].astype(float)
	quotes['high'] = quotes['high'].astype(float)
	quotes['low'] = quotes['low'].astype(float)
	quotes['close'] = quotes['close'].astype(float)

	return quotes

def check_price(datas):
	#移動平均線
	s = pd.Series(datas['close'])
	sma25 = s.rolling(window=25).mean()
	#sma5 = s.rolling(window=5).mean()
	#plt.plot(datas['datetime'], sma5)
	deviation = 2
	sigma = s.rolling(window=25).std(ddof=0) #σの計算
	upper2_siguma = sma25 + sigma * deviation
	lower2_siguma = sma25 - sigma * deviation
	
	asset = ASSET
	have_position = 0	#ポジションを持っているか　0持っていない　1買を持っている　2売を持っている
	order_price = 0
	cnt_win = 0
	cnt_loose = 0
	
	result = []

	for idx, high in enumerate(datas['high']):
		low = datas['low'][idx]
		if have_position == 0:   #ポジションを持っていない場合
			if high >= upper2_siguma[idx]:
				#売り注文
				print("売り注文 価格　2σ", high, upper2_siguma[idx])
				have_position, order_price = open_order(have_position, order_price, 2, datas['high'][idx])
			elif low <= lower2_siguma[idx]:
				#買い注文
				print("買い注文　価格　2σ", low, lower2_siguma[idx])
				have_position, order_price = open_order(have_position, order_price, 1, datas['low'][idx])
 
		else:
			#print("価格チェック　order_price　price", order_price, datas['close'][idx])
			#print("abs", abs(order_price - datas['close'][idx]))
			if abs(order_price - datas['close'][idx]) > DIFF_PRICE:
				print("order close", order_price, datas['close'][idx])
				asset, have_position, order_price, cnt_win, cnt_loose = close_order(asset, have_position, order_price, cnt_win, cnt_loose, datas['close'][idx])
 
		result.append(asset)
 
	return result, asset, cnt_win, cnt_loose

def open_order(have_position, order_price, order_type, price):
	have_position = order_type
	order_price = price
	return have_position, order_price
 
def close_order(asset, have_position, order_price, cnt_win, cnt_loose, price):
	if have_position == 1:   #買いポジションの場合
		diff_price = price - order_price
	elif have_position == 2: #売りポジションの場合
		diff_price = order_price - price
 
	if diff_price > 0:  #勝った場合
		cnt_win += 1
	else:
		cnt_loose += 1
		
	asset = asset + diff_price * UNIT
	have_position = 0
	return asset, have_position, order_price, cnt_win, cnt_loose
	
if __name__ == '__main__':
	datas = get_datas()
	datas = convert_datas(datas)

	#print(datas.info())
	
	result, asset, cnt_win, cnt_loose = check_price(datas)
	
	print("asset=", asset)
	print("cnt_win=", cnt_win)
	print("cnt_loose=", cnt_loose)

	
	additional_col = pd.DataFrame([result]).T
	additional_col.columns = ["asset"]
	additional_col.index = range(len(datas))
	datas = pd.concat([datas, additional_col], axis=1)
	
	print(datas.info())

	plt.grid()
	ax = plt.subplot()

	plt.plot(datas['time'], datas['asset'])

	plt.xlabel('Date')
	plt.ylabel('Price')
	plt.title('USD-JPY')
	plt.show()
