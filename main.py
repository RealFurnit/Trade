import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import  MarketOrderRequest,TakeProfitRequest, StopLossRequest
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
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

def getLastQuote(symb):
    req=StockLatestQuoteRequest(symbol_or_symbols=[symb])
    result = data_client.get_stock_latest_quote(req)
    return result



def getCandles(n,symb):
    candles=data_client.get_stock_bars(StockBarsRequest(symbol_or_symbols=[symb],timeframe=TimeFrame.Day,start=start_time,limit=n,sort="desc"))
    return candles


def getOpenedTrades(symb):
    positions = trading_client.get_all_positions()
    return len(positions)

def get_candles_frame(n, symb):
    candles = getCandles(n,symb)
    dfstream = pd.DataFrame(columns=["Open","Close","High","Low"])

    for x in range(n):
        dfstream.loc[x, ["Date"]] = str(candles.data[symb][x].timestamp)
        dfstream.loc[x, ['Open']] = float(str(candles.data[symb][x].open))
        dfstream.loc[x, ["Close"]] = float(str(candles.data[symb][x].close))
        dfstream.loc[x, ["High"]] = float(str(candles.data[symb][x].high))
        dfstream.loc[x, ["Low"]] = float(str(candles.data[symb][x].low))
        
    #dfstream["Date"]=pd.to_datetime(df["Date"], format='')

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

def ema_signal(df, current_candle, backcandles):
    df_slice = df.reset_index().copy()
    # Get the range of candles to consider
    start = max(0, current_candle - backcandles)
    end = current_candle
    relevant_rows = df_slice.iloc[start:end]

    # Check if all EMA_fast values are below EMA_slow values
    if all(relevant_rows["EMA_fast"] < relevant_rows["EMA_slow"]):
        return 1
    elif all(relevant_rows["EMA_fast"] > relevant_rows["EMA_slow"]):
        return 2
    else:
        return 0   

def total_signal(df, current_candle, backcandles):
    if (ema_signal(df, current_candle, backcandles)==2
        and df.Close[current_candle]<=df['BBL_15_1.5'][current_candle]
        #and df.RSI[current_candle]<60
        ):
            return 2
    if (ema_signal(df, current_candle, backcandles)==1
        and df.Close[current_candle]>=df['BBU_15_1.5'][current_candle]
        #and df.RSI[current_candle]>40
        ):
    
            return 1
    return 0

def SIGNAL():
    return daframe.TotalSignal

# Trading job
from datetime import datetime

def trading_job(symb):
    dfstream = get_candles_frame(2000,symb)
    signal = total_signal(dfstream, len(dfstream)-1, 7)

    slatr = 1.1*dfstream.ATR.iloc[-1]
    TPSLRatio=1.5
    max_spread=16e-5

    candle = getLastQuote(symb)
    candle_open_bid = float(str(candle[symb].bid_price))
    candle_open_ask = float(str(candle[symb].ask_price))
    spread = candle_open_ask - candle_open_bid

    SLBuy = candle_open_ask+slatr*TPSLRatio+spread
    SLSell = candle_open_ask+slatr+spread

    TPBuy = candle_open_ask+slatr*TPSLRatio+spread
    TPSell = candle_open_bid-slatr*TPSLRatio-spread

    #SELL
    if signal == 1 and getOpenedTrades() == 0 and spread<max_spread:
        print("Sell Signal Found...")
        mor = MarketOrderRequest(
            symbol=symb,
            qty=1,
            side=OrderSide.SELL,
            take_profit=TakeProfitRequest(
                TPSell
            ),
            stop_loss=StopLossRequest(
                SLSell
            )
        )
        mo = trading_client.submit_order(order_data=mor)
        


trading_job("SPY")
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
