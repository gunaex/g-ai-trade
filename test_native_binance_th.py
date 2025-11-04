"""
Test native Binance TH market data client
"""
from app.binance_client import get_market_data_client

def test_market_data():
    print("Testing native Binance TH market data client...")
    
    client = get_market_data_client()
    
    # Test 1: Fetch ticker
    print("\n1. Fetching BTC/USDT ticker...")
    try:
        ticker = client.fetch_ticker('BTC/USDT')
        print(f"   ✅ Last price: {ticker['last']}")
        print(f"   ✅ 24h Volume: {ticker['baseVolume']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Fetch OHLCV
    print("\n2. Fetching BTC/USDT 1h candlesticks...")
    try:
        ohlcv = client.fetch_ohlcv('BTC/USDT', '1h', limit=5)
        print(f"   ✅ Got {len(ohlcv)} candles")
        if ohlcv:
            latest = ohlcv[-1]
            print(f"   ✅ Latest: O:{latest[1]} H:{latest[2]} L:{latest[3]} C:{latest[4]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Fetch order book
    print("\n3. Fetching BTC/USDT order book...")
    try:
        orderbook = client.fetch_order_book('BTC/USDT', limit=5)
        print(f"   ✅ Top bid: {orderbook['bids'][0] if orderbook['bids'] else 'N/A'}")
        print(f"   ✅ Top ask: {orderbook['asks'][0] if orderbook['asks'] else 'N/A'}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Load markets (optional)
    print("\n4. Loading exchange info...")
    try:
        markets = client.load_markets()
        if markets:
            print(f"   ✅ Loaded exchange info")
        else:
            print(f"   ⚠️  No market data returned")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_market_data()
