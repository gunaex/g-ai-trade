"""
Binance Thailand API v1.0.0 Client
Official docs: https://www.binance.th/api-docs/en/
"""
import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
import os
from dotenv import load_dotenv

load_dotenv()

class BinanceThailandClient:
    """
    Direct REST API client for Binance Thailand v1.0.0
    Base URL: https://api.binance.th
    API Version: v1
    """
    
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_SECRET')
        self.base_url = 'https://api.binance.th'
        self.recv_window = 5000
        
    def _get_timestamp(self):
        """Get current timestamp in milliseconds"""
        return int(time.time() * 1000)
    
    def _sign(self, params):
        """Generate signature for authenticated endpoints"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method, endpoint, params=None, signed=False):
        """Make HTTP request to Binance TH API"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if params is None:
            params = {}
        
        if signed:
            # Add timestamp and recvWindow for signed requests
            params['timestamp'] = self._get_timestamp()
            params['recvWindow'] = self.recv_window
            # Generate signature
            params['signature'] = self._sign(params)
            headers['X-MBX-APIKEY'] = self.api_key
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, params=params, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, params=params, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Binance TH API Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    # ==================== PUBLIC ENDPOINTS ====================
    
    def get_server_time(self):
        """Test connectivity and get server time"""
        return self._request('GET', '/api/v1/time')
    
    def get_ticker_price(self, symbol=None):
        """Get latest price for a symbol or all symbols"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self._request('GET', '/api/v1/ticker/price', params)
    
    def get_ticker_24h(self, symbol=None):
        """Get 24hr ticker price change statistics"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self._request('GET', '/api/v1/ticker/24hr', params)
    
    def get_klines(self, symbol, interval='1h', limit=500):
        """
        Get Kline/candlestick data
        Intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
        """
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        return self._request('GET', '/api/v1/klines', params)
    
    def get_order_book(self, symbol, limit=100):
        """Get order book depth"""
        params = {
            'symbol': symbol,
            'limit': limit
        }
        return self._request('GET', '/api/v1/depth', params)
    
    def get_recent_trades(self, symbol, limit=500):
        """Get recent trades"""
        params = {
            'symbol': symbol,
            'limit': limit
        }
        return self._request('GET', '/api/v1/trades', params)
    
    def get_exchange_info(self):
        """Get current exchange trading rules and symbol information"""
        return self._request('GET', '/api/v1/exchangeInfo')
    
    # ==================== AUTHENTICATED ENDPOINTS ====================
    
    def get_account(self):
        """Get current account information"""
        return self._request('GET', '/api/v1/account', signed=True)
    
    def get_balance(self):
        """Get account balances"""
        account = self.get_account()
        return account.get('balances', [])
    
    def create_order(self, symbol, side, order_type, quantity, price=None, time_in_force='GTC'):
        """
        Create a new order
        side: BUY or SELL
        order_type: LIMIT, MARKET
        time_in_force: GTC, IOC, FOK
        """
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': order_type.upper(),
            'quantity': quantity,
        }
        
        if order_type.upper() == 'LIMIT':
            if price is None:
                raise ValueError("Price is required for LIMIT orders")
            params['price'] = price
            params['timeInForce'] = time_in_force
        
        return self._request('POST', '/api/v1/order', params, signed=True)
    
    def get_order(self, symbol, order_id):
        """Query order status"""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._request('GET', '/api/v1/order', params, signed=True)
    
    def cancel_order(self, symbol, order_id):
        """Cancel an active order"""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._request('DELETE', '/api/v1/order', params, signed=True)
    
    def get_open_orders(self, symbol=None):
        """Get all open orders"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self._request('GET', '/api/v1/openOrders', params, signed=True)
    
    def get_all_orders(self, symbol, limit=500):
        """Get all account orders (active, canceled, or filled)"""
        params = {
            'symbol': symbol,
            'limit': limit
        }
        return self._request('GET', '/api/v1/allOrders', params, signed=True)
    
    def get_my_trades(self, symbol, limit=500):
        """Get trades for a specific account and symbol"""
        params = {
            'symbol': symbol,
            'limit': limit
        }
        return self._request('GET', '/api/v1/myTrades', params, signed=True)


# ==================== GLOBAL BINANCE FOR MARKET DATA ====================

import ccxt

def get_global_exchange():
    """
    Get global Binance exchange for reliable market data
    Uses ccxt for convenience
    """
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',
        }
    })
    return exchange


# ==================== CONVENIENCE FUNCTIONS ====================

def get_binance_th_client():
    """Get Binance Thailand API client"""
    return BinanceThailandClient()

def get_market_data_client():
    """Get client for market data (uses global Binance)"""
    return get_global_exchange()
