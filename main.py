from alpaca.trading.client import TradingClient

trading_client = TradingClient("PKNUQZ0GZBVJO93DIJX0", "4Y3AHu81cUoklfaG8dCJey5d0fC0RbHwwPjWFxTy", paper=True)

account = trading_client.get_account()

search_params = GetAssetsRequest(asset_class=AssetClass.CRYPTO)
assets = trading_client.get_all_assets(search_params)

print(assets)