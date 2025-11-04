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


# ==================== GLOBAL BINANCE FOR MARKET DATA ====================

import ccxt
from ccxt.base.errors import DDoSProtection, RateLimitExceeded
from time import time as now_ts

# cache global exchange to avoid repeated, slow initializations
_GLOBAL_EXCHANGE = None
_GLOBAL_MARKETS_LOADED = False


class MarketDataProxy:
    """
    Thin proxy around ccxt.binance with:
    - enableRateLimit already set on underlying exchange
    - small in-memory caches to avoid hammering Binance
    - graceful handling of 418/429 (DDoSProtection / RateLimitExceeded) with cooldown
    - drop-in replacement: implements fetch_ticker, fetch_ohlcv, fetch_order_book
    """

    def __init__(self, exchange: ccxt.binance):
        self.exchange = exchange
        # caches: key -> (expires_at, value)
        self._cache: dict[str, tuple[float, Any]] = {}
        # cooldown until timestamp if rate-limited/banned
        self._cooldown_until: float = 0.0

    def _cache_key(self, name: str, *parts) -> str:
        return f"{name}|{'|'.join(map(str, parts))}"

    def _get_cached(self, key: str) -> Optional[Any]:
        item = self._cache.get(key)
        if not item:
            return None
        expires, value = item
        if now_ts() < expires:
            return value
        # expired
        self._cache.pop(key, None)
        return None

    def _set_cache(self, key: str, ttl_sec: float, value: Any):
        self._cache[key] = (now_ts() + ttl_sec, value)

    def _handle_rate_limit(self, err: Exception):
        # Exponential-ish backoff; keep a short cooldown to avoid repeated hammering
        cooldown = 30  # seconds
        self._cooldown_until = max(self._cooldown_until, now_ts() + cooldown)
        raise

    def _respect_cooldown(self):
        if now_ts() < self._cooldown_until:
            # During cooldown return cached data if any; else raise a friendly error
            raise DDoSProtection(f"Cooling down until {self._cooldown_until}")

    # Drop-in wrappers
    def fetch_ticker(self, symbol: str):
        key = self._cache_key('ticker', symbol)
        try:
            # small TTL cache (5s)
            cached = self._get_cached(key)
            if cached is not None:
                return cached
            self._respect_cooldown()
            data = self.exchange.fetch_ticker(symbol)
            self._set_cache(key, 5, data)
            return data
        except (DDoSProtection, RateLimitExceeded) as e:
            # return stale if present
            cached = self._get_cached(key)
            if cached is not None:
                return cached
            self._handle_rate_limit(e)

    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        key = self._cache_key('ohlcv', symbol, timeframe, limit)
        try:
            # OHLCV can be cached longer (i.e., one candle for timeframe)
            ttl = {
                '1m': 30, '3m': 45, '5m': 60, '15m': 180, '30m': 300,
                '1h': 600, '2h': 1200, '4h': 1800, '1d': 3600
            }.get(timeframe, 120)
            cached = self._get_cached(key)
            if cached is not None:
                return cached
            self._respect_cooldown()
            data = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            self._set_cache(key, ttl, data)
            return data
        except (DDoSProtection, RateLimitExceeded) as e:
            cached = self._get_cached(key)
            if cached is not None:
                return cached
            self._handle_rate_limit(e)

    def fetch_order_book(self, symbol: str, limit: Optional[int] = None):
        key = self._cache_key('order_book', symbol, limit or 0)
        try:
            # order book can be cached very briefly (2s)
            cached = self._get_cached(key)
            if cached is not None:
                return cached
            self._respect_cooldown()
            data = self.exchange.fetch_order_book(symbol, limit=limit)
            self._set_cache(key, 2, data)
            return data
        except (DDoSProtection, RateLimitExceeded) as e:
            cached = self._get_cached(key)
            if cached is not None:
                return cached
            self._handle_rate_limit(e)

def get_global_exchange():
    """
    Get (and cache) a global Binance exchange for reliable market data.
    Attempts to load markets once in a best-effort manner without blocking future requests.
    
    IMPORTANT: Uses Binance TH (api.binance.th) to avoid geo-restrictions on international endpoints.
    """
    global _GLOBAL_EXCHANGE, _GLOBAL_MARKETS_LOADED
    if _GLOBAL_EXCHANGE is None:
        _GLOBAL_EXCHANGE = ccxt.binance({
            'enableRateLimit': True,
            'rateLimit': 1000,  # ms between requests (conservative)
            'hostname': 'binance.th',  # Force Thailand endpoint to avoid 451 geo-blocks (best-effort; we also patch urls below)
            'options': {
                'defaultType': 'spot',
            }
        })
        # Force all relevant URLs to use api.binance.th to avoid geo-blocks
        # CRITICAL: ccxt builds URLs from exchange.urls dict; patching it forces TH endpoints
        try:
            urls = _GLOBAL_EXCHANGE.urls
            # Spot endpoints (primary)
            urls['api'] = 'https://api.binance.th'
            urls['public'] = 'https://api.binance.th'
            urls['private'] = 'https://api.binance.th'
            # Service-specific endpoints
            urls['sapi'] = 'https://api.binance.th/sapi'
            urls['wapi'] = 'https://api.binance.th/wapi'
            urls['eapi'] = 'https://api.binance.th/eapi'
            urls['vapi'] = 'https://api.binance.th/vapi'
            # Futures/Delivery not used but patch anyway to be safe
            urls['fapi'] = 'https://api.binance.th/fapi'
            urls['dapi'] = 'https://api.binance.th/dapi'
            logger.info(f"Patched ccxt Binance URLs to api.binance.th: {urls.get('api')}")
        except Exception as e:
            logger.error(f"Failed to patch ccxt URLs: {e}")
        # Best-effort market load in a short-lived background thread to avoid blocking
        try:
            import threading
            def _load():
                global _GLOBAL_MARKETS_LOADED
                try:
                    _GLOBAL_EXCHANGE.load_markets()
                    _GLOBAL_MARKETS_LOADED = True
                except Exception:
                    _GLOBAL_MARKETS_LOADED = False
            t = threading.Thread(target=_load, daemon=True)
            t.start()
            t.join(timeout=3)
        except Exception:
            pass
    return _GLOBAL_EXCHANGE


# ==================== CONVENIENCE FUNCTIONS ====================

def get_binance_th_client(api_key: str | None = None, api_secret: str | None = None):
    """Get Binance Thailand API client. Accepts optional per-user API credentials."""
    return BinanceThailandClient(api_key=api_key, api_secret=api_secret)

def get_market_data_client():
    """Get client for market data with caching and cooldown handling."""
    try:
        exchange = get_global_exchange()
        return MarketDataProxy(exchange)
    except Exception as e:
        logger.error(f"Error getting market data client: {e}", exc_info=True)
        # Fallback to a fresh, minimal proxied exchange if cache failed
        fallback = ccxt.binance({
            'enableRateLimit': True,
            'rateLimit': 1200,
            'hostname': 'binance.th',  # Force Thailand endpoint (best-effort; also patch urls)
            'options': {
                'defaultType': 'spot',
            },
        })
        try:
            urls = fallback.urls
            urls['api'] = 'https://api.binance.th'
            urls['public'] = 'https://api.binance.th'
            urls['private'] = 'https://api.binance.th'
            urls['sapi'] = 'https://api.binance.th/sapi'
            urls['wapi'] = 'https://api.binance.th/wapi'
            urls['eapi'] = 'https://api.binance.th/eapi'
            urls['vapi'] = 'https://api.binance.th/vapi'
            urls['fapi'] = 'https://api.binance.th/fapi'
            urls['dapi'] = 'https://api.binance.th/dapi'
            logger.info(f"Patched fallback ccxt Binance URLs to api.binance.th: {urls.get('api')}")
        except Exception as e:
            logger.error(f"Failed to patch fallback URLs: {e}")
        return MarketDataProxy(fallback)
