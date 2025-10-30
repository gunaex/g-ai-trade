from app.binance_client import get_market_exchange, get_trading_exchange

print("=" * 60)
print("Testing Binance Thailand Dual-Endpoint Setup")
print("=" * 60)

# Test 1: Market Data (Global API)
print("\n1. Testing Market Data (Global Binance API)...")
try:
    market_exchange = get_market_exchange()
    ticker = market_exchange.fetch_ticker('BTC/USDT')
    print(f"✅ Market Data Works!")
    print(f"   BTC Price: ${ticker['last']:,.2f}")
    print(f"   24h Change: {ticker['percentage']:.2f}%")
except Exception as e:
    print(f"❌ Market Data Failed: {e}")

# Test 2: Trading Exchange Connection (Binance TH API)
print("\n2. Testing Trading Exchange (Binance TH API)...")
try:
    trading_exchange = get_trading_exchange()
    balance = trading_exchange.fetch_balance()
    print(f"✅ Trading API Connected!")
    print(f"   Account connected to Binance TH")
    print(f"   Free USDT: {balance.get('USDT', {}).get('free', 0)}")
except Exception as e:
    print(f"❌ Trading API Failed: {e}")
    print("   Check your BINANCE_API_KEY and BINANCE_SECRET in .env")

print("\n" + "=" * 60)
print("Setup Summary:")
print("- Market data uses: https://api.binance.com (reliable)")
print("- Trading uses: https://api.binance.th (your TH account)")
print("=" * 60)
