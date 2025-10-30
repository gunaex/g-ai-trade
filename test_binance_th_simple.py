import requests

# Test Binance TH public API (no authentication needed)
print("Testing Binance Thailand public API...")
print("=" * 50)

try:
    # Test 1: Server time
    response = requests.get('https://api.binance.th/api/v3/time')
    if response.status_code == 200:
        print("✅ Server time:", response.json())
    else:
        print("❌ Server time failed:", response.status_code)
    
    # Test 2: BTC price
    response = requests.get('https://api.binance.th/api/v3/ticker/price?symbol=BTCUSDT')
    if response.status_code == 200:
        data = response.json()
        print(f"✅ BTC Price: {data['price']} USDT")
    else:
        print("❌ Price check failed:", response.text)
    
    # Test 3: Exchange info
    response = requests.get('https://api.binance.th/api/v3/exchangeInfo?symbol=BTCUSDT')
    if response.status_code == 200:
        print("✅ Exchange info retrieved successfully")
    else:
        print("❌ Exchange info failed:", response.status_code)
        
    print("\n✅ Binance Thailand API is accessible!")
    print("Your API keys should work with this endpoint.")
    
except Exception as e:
    print(f"❌ Connection error: {e}")
    print("\nPossible issues:")
    print("1. No internet connection")
    print("2. Binance TH is blocked in your region")
    print("3. Firewall blocking the connection")