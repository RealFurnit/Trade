from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import StockBarsRequest
from datetime import datetime
import pandas as pd
# Fetch real time market data

data_client = StockHistoricalDataClient("PKNUQZ0GZBVJO93DIJX0", "4Y3AHu81cUoklfaG8dCJey5d0fC0RbHwwPjWFxTy")

def getCandles(n):
    candles=data_client.get_stock_bars(StockBarsRequest(symbol_or_symbols=["AAPL"],timeframe=TimeFrame(5,TimeFrameUnit("Min")),limit=n,sort="desc"))
    return candles

candles = getCandles(3)
for x in range(3):
    print(float(str(candles.data["AAPL"][x].open))>1)

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
