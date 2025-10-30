from app.binance_client import get_binance_client

try:
    client = get_binance_client()
    ticker = client.get_symbol_ticker(symbol="BTCUSDT")
    print(f"✅ Connected to Binance TH!")
    print(f"BTC Price: {ticker['price']} USDT")
except Exception as e:
    print(f"❌ Error: {e}")

