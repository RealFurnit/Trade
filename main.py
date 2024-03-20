import os
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import StockBarsRequest
from datetime import datetime
import pandas as pd
import talib as tae
import pandas_ta as ta
from dotenv import load_dotenv

# Load the stored environment variables
load_dotenv()

api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")

# Initilaize clients
data_client = StockHistoricalDataClient(api_key,secret_key)
trading_client = TradingClient(api_key, secret_key, paper=True)

# Get market data
start_time = pd.to_datetime("2010-01-19").tz_localize('America/New_York')

def getCandles(n):
    candles=data_client.get_stock_bars(StockBarsRequest(symbol_or_symbols=["AAPL"],timeframe=TimeFrame.Day,start=start_time,limit=n,sort="desc"))
    return candles


def getOpenedTrades():
    positions = trading_client.get_all_positions()
    return len(positions)

def get_candles_frame(n):
    candles = getCandles(n)
    dfstream = pd.DataFrame(columns=["Open","Close","High","Low"])

    for x in range(n):
        dfstream.loc[x, ['Open']] = float(str(candles.data["AAPL"][x].open))
        dfstream.loc[x, ["Close"]] = float(str(candles.data["AAPL"][x].close))
        dfstream.loc[x, ["High"]] = float(str(candles.data["AAPL"][x].high))
        dfstream.loc[x, ["Low"]] = float(str(candles.data["AAPL"][x].low))
        

    dfstream["Open"] = dfstream["Open"].astype(float)
    dfstream["Close"] = dfstream["Close"].astype(float)
    dfstream["High"] = dfstream["High"].astype(float)
    dfstream["Low"] = dfstream["Low"].astype(float)

    dfstream["ATR"] = ta.atr(dfstream.High,dfstream.Low,dfstream.Close,length=7)
    dfstream["EMA_fast"]= ta.ema(dfstream.Close, 30)
    dfstream["EMA_slow"]= ta.sma(dfstream.Close, 50)
    dfstream["RSI"]= ta.rsi(dfstream.Close, length=10)
    my_bbands = ta.bbands(dfstream.Close, length=15, std=1.5)
    dfstream=dfstream.join(my_bbands)
    return dfstream

def ema_signal(df,current_candle,backcandles):
    df_slice = df.reset_index().copy()
    start = max(0,current_candle- backcandles)
    end = current_candle
    relevant_rows = df_slice.iloc[start:end]

    if all(relevant_rows["EMA_fast"] < relevant_rows["EMA_slow"]):
        return 1
    elif all(relevant_rows["EMA_fast"] > relevant_rows["EMA_slow"]):
        return 2
    else:
        return 0

def total_signal(df,current_candle,backcandles):
    if(ema_signal(df,current_candle,backcandles)==2
       and df.Close[current_candle]<=df["BBL_15_1.5"][current_candle]
      ): return 2
    if (ema_signal(df,current_candle,backcandles)==1
        and df.Close[current_candle]>=df['BBU_15_1.5'][current_candle]

        ): return 1
    return 0


daframe=get_candles_frame(2000)
daframe=daframe[-2000:-1]
from tqdm import tqdm
tqdm.pandas()
daframe.reset_index(inplace=True)
daframe["EMASignal"] = daframe.progress_apply(lambda row: ema_signal(daframe,row.name,7) if row.name >= 20 else 0, axis=1)
daframe["TotalSignal"]= daframe.progress_apply(lambda row: total_signal(daframe, row.name, 7), axis=1)
print(daframe["TotalSignal"],daframe["EMASignal"])
daframe.to_csv("Daframe.csv",index=False)







# Make BUY and SELL orders using data

"""market_order_data = MarketOrderRequest(
    symbol="SPY",
    qty=1,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.DAY
)

# Market order
market_order = trading_client.submit_order(
    order_data=market_order_data
)

trading_stream = TradingStream("PKNUQZ0GZBVJO93DIJX0", "4Y3AHu81cUoklfaG8dCJey5d0fC0RbHwwPjWFxTy", paper=True)

async def update_handler(data):
    # trade updates will arrive in our async handler
    print(data)

# subscribe to trade updates and supply the handler as a parameter
trading_stream.subscribe_trade_updates(update_handler)

# start our websocket streaming
trading_stream.run()

positions = trading_client.get_all_positions()

print(positions)"""
