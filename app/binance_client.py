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
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

load_dotenv()

class BinanceThailandClient:
    """
    Direct REST API client for Binance Thailand v1.0.0
    Base URL: https://api.binance.th
    API Version: v1
    """
    
    def __init__(self, api_key: str | None = None, api_secret: str | None = None):
        # Prefer explicitly provided user keys; fallback to environment (legacy)
        self.api_key = api_key or os.getenv('BINANCE_API_KEY')
        self.api_secret = api_secret or os.getenv('BINANCE_SECRET')
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
            logger.error(f"Binance TH API Error: {e}", exc_info=True)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    logger.error(f"Response: {e.response.text}")
                except Exception:
                    pass
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

    # Convenience wrappers to match internal bot usage
    def create_market_buy_order(self, symbol: str, amount: float):
        """Create a MARKET BUY order using the unified signature expected by the bot."""
        # Binance TH expects symbols without slash, convert if needed
        sym = symbol.replace('/', '')
        return self.create_order(
            symbol=sym,
            side='BUY',
            order_type='MARKET',
            quantity=amount
        )

    def create_market_sell_order(self, symbol: str, amount: float):
        """Create a MARKET SELL order using the unified signature expected by the bot."""
        sym = symbol.replace('/', '')
        return self.create_order(
            symbol=sym,
            side='SELL',
            order_type='MARKET',
            quantity=amount
        )
    
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


# ==================== MARKET DATA CLIENT (NATIVE BINANCE TH) ====================

from time import time as now_ts

# Cache for market data to reduce API calls
_MARKET_DATA_CACHE = {}
_COOLDOWN_UNTIL = 0


class BinanceThMarketData:
    """
    Market data client using native Binance TH API v1.
    Implements ccxt-compatible interface (fetch_ticker, fetch_ohlcv, fetch_order_book)
    with in-memory caching and rate-limit protection.
    
    Replaces ccxt.binance which doesn't support Binance TH's /api/v1/* endpoints.
    """
    
    def __init__(self):
        self.client = BinanceThailandClient()  # Public endpoints don't need API keys
        self._cache = {}
        self._cooldown_until = 0
    
    def _get_cached(self, key):
        """Get cached value if not expired"""
        if key in self._cache:
            cached_at, ttl, value = self._cache[key]
            if now_ts() - cached_at < ttl:
                return value
        return None
    
    def _set_cache(self, key, ttl, value):
        """Cache a value with TTL in seconds"""
        self._cache[key] = (now_ts(), ttl, value)
    
    def _respect_cooldown(self):
        """Wait if we're in rate-limit cooldown"""
        global _COOLDOWN_UNTIL
        remaining = _COOLDOWN_UNTIL - now_ts()
        if remaining > 0:
            logger.warning(f"Rate limit cooldown active, waiting {remaining:.1f}s")
            time.sleep(min(remaining, 5))
    
    def _handle_rate_limit(self, error):
        """Set cooldown on rate limit errors"""
        global _COOLDOWN_UNTIL
        _COOLDOWN_UNTIL = now_ts() + 60  # 1 minute cooldown
        logger.error(f"Rate limit hit, cooldown for 60s: {error}")
        raise
    
    def fetch_ticker(self, symbol: str):
        """
        Fetch 24h ticker data for a symbol.
        Returns ccxt-compatible dict with keys: symbol, last, bid, ask, high, low, volume, etc.
        """
        # Convert ccxt format (BTC/USDT) to Binance format (BTCUSDT)
        binance_symbol = symbol.replace('/', '')
        
        key = f"ticker:{binance_symbol}"
        cached = self._get_cached(key)
        if cached is not None:
            return cached
        
        self._respect_cooldown()
        
        try:
            ticker_data = self.client.get_ticker_24h(symbol=binance_symbol)
            
            # Convert Binance TH format to ccxt format
            result = {
                'symbol': symbol,
                'timestamp': ticker_data.get('closeTime'),
                'datetime': None,
                'high': float(ticker_data.get('highPrice', 0)),
                'low': float(ticker_data.get('lowPrice', 0)),
                'bid': float(ticker_data.get('bidPrice', 0)),
                'ask': float(ticker_data.get('askPrice', 0)),
                'last': float(ticker_data.get('lastPrice', 0)),
                'close': float(ticker_data.get('lastPrice', 0)),
                'baseVolume': float(ticker_data.get('volume', 0)),
                'quoteVolume': float(ticker_data.get('quoteVolume', 0)),
                'info': ticker_data
            }
            
            self._set_cache(key, 5, result)  # Cache for 5 seconds
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code in [418, 429]:
                self._handle_rate_limit(e)
            raise
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        """
        Fetch OHLCV (candlestick) data.
        Returns list of [timestamp, open, high, low, close, volume]
        """
        # Convert ccxt format (BTC/USDT) to Binance format (BTCUSDT)
        binance_symbol = symbol.replace('/', '')
        
        # Map ccxt timeframes to Binance intervals
        interval_map = {
            '1m': '1m', '3m': '3m', '5m': '5m', '15m': '15m', '30m': '30m',
            '1h': '1h', '2h': '2h', '4h': '4h', '6h': '6h', '8h': '8h', '12h': '12h',
            '1d': '1d', '3d': '3d', '1w': '1w', '1M': '1M'
        }
        interval = interval_map.get(timeframe, '1h')
        
        key = f"ohlcv:{binance_symbol}:{interval}:{limit}"
        
        # Cache duration based on timeframe
        cache_ttl = {'1m': 10, '5m': 30, '15m': 60, '1h': 300, '1d': 3600}.get(timeframe, 60)
        
        cached = self._get_cached(key)
        if cached is not None:
            return cached
        
        self._respect_cooldown()
        
        try:
            klines = self.client.get_klines(symbol=binance_symbol, interval=interval, limit=limit)
            
            # Convert Binance format to ccxt format
            # Binance: [openTime, open, high, low, close, volume, closeTime, quoteVolume, ...]
            result = [
                [
                    int(k[0]),  # timestamp
                    float(k[1]),  # open
                    float(k[2]),  # high
                    float(k[3]),  # low
                    float(k[4]),  # close
                    float(k[5])   # volume
                ]
                for k in klines
            ]
            
            self._set_cache(key, cache_ttl, result)
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code in [418, 429]:
                self._handle_rate_limit(e)
            raise
    
    def fetch_order_book(self, symbol: str, limit: int = 100):
        """
        Fetch order book (market depth).
        Returns dict with 'bids' and 'asks' arrays.
        """
        # Convert ccxt format (BTC/USDT) to Binance format (BTCUSDT)
        binance_symbol = symbol.replace('/', '')
        
        key = f"orderbook:{binance_symbol}:{limit}"
        cached = self._get_cached(key)
        if cached is not None:
            return cached
        
        self._respect_cooldown()
        
        try:
            depth = self.client.get_order_book(symbol=binance_symbol, limit=limit)
            
            # Convert to ccxt format
            result = {
                'symbol': symbol,
                'bids': [[float(p), float(q)] for p, q in depth.get('bids', [])],
                'asks': [[float(p), float(q)] for p, q in depth.get('asks', [])],
                'timestamp': depth.get('lastUpdateId'),
                'datetime': None,
                'nonce': depth.get('lastUpdateId')
            }
            
            self._set_cache(key, 2, result)  # Cache for 2 seconds
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code in [418, 429]:
                self._handle_rate_limit(e)
            raise
    
    def load_markets(self):
        """
        Load market metadata (optional, for ccxt compatibility).
        Returns dict of market info.
        """
        try:
            exchange_info = self.client.get_exchange_info()
            # Cache and return - not critical for operation
            return exchange_info
        except Exception as e:
            logger.warning(f"Could not load markets: {e}")
            return {}


# ==================== CONVENIENCE FUNCTIONS ====================

# Global singleton for market data client
_MARKET_DATA_CLIENT = None

def get_binance_th_client(api_key: str | None = None, api_secret: str | None = None):
    """Get Binance Thailand API client. Accepts optional per-user API credentials."""
    return BinanceThailandClient(api_key=api_key, api_secret=api_secret)

def get_market_data_client():
    """
    Get cached market data client using native Binance TH API v1.
    This replaces ccxt.binance which doesn't support Binance TH endpoints.
    """
    global _MARKET_DATA_CLIENT
    if _MARKET_DATA_CLIENT is None:
        _MARKET_DATA_CLIENT = BinanceThMarketData()
        logger.info("Initialized native Binance TH market data client")
    return _MARKET_DATA_CLIENT
