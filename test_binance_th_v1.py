from app.binance_client import get_binance_th_client, get_market_data_client

print("=" * 70)
print("  Testing Binance Thailand REST API v1.0.0 Integration")
print("=" * 70)

# Test 1: Public Endpoints (No Auth)
print("\n[TEST 1] Public Market Data (Global Binance)...")
try:
    market_client = get_market_data_client()
    ticker = market_client.fetch_ticker('BTC/USDT')
    print(f"✅ Market Data Works!")
    print(f"   BTC Price: ${ticker['last']:,.2f}")
    print(f"   24h Volume: ${ticker['quoteVolume']:,.0f}")
except Exception as e:
    print(f"❌ Market Data Failed: {e}")

# Test 2: Binance TH Public Endpoints
print("\n[TEST 2] Binance TH Public Endpoints...")
try:
    th_client = get_binance_th_client()
    
    # Test server time
    server_time = th_client.get_server_time()
    print(f"✅ Server Time: {server_time}")
    
    # Test ticker price
    ticker = th_client.get_ticker_price('BTCUSDT')
    print(f"✅ BTC Price (TH): {ticker['price']} USDT")
    
    # Test 24h ticker
    ticker_24h = th_client.get_ticker_24h('BTCUSDT')
    print(f"✅ 24h Change: {ticker_24h['priceChangePercent']}%")
    
except Exception as e:
    print(f"❌ Binance TH Public API Failed: {e}")

# Test 3: Binance TH Authenticated Endpoints
print("\n[TEST 3] Binance TH Authenticated API...")
try:
    th_client = get_binance_th_client()
    
    # Test account endpoint
    account = th_client.get_account()
    print(f"✅ Account Connected!")
    print(f"   Can Trade: {account.get('canTrade', False)}")
    print(f"   Can Withdraw: {account.get('canWithdraw', False)}")
    
    # Get balances
    balances = th_client.get_balance()
    usdt_balance = next((b for b in balances if b['asset'] == 'USDT'), None)
    if usdt_balance:
        print(f"   USDT Balance: {usdt_balance['free']}")
    
    print(f"\n✅ ALL TESTS PASSED!")
    print(f"   Your Binance TH API keys are working correctly!")
    
except Exception as e:
    print(f"❌ Binance TH Auth Failed: {e}")
    print(f"   Please check your API keys in .env file")
    print(f"   Make sure they are from Binance Thailand (not global Binance)")

print("\n" + "=" * 70)
print("Integration Summary:")
print("- Market data: https://api.binance.com (via ccxt)")
print("- Trading: https://api.binance.th/api/v1 (direct REST)")
print("=" * 70)
