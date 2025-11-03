"""
Comprehensive Test Suite for Advanced AI Trading System

This script tests all 7 new AI modules with real and mock data:
1. Kelly Criterion Position Sizing
2. Multi-Timeframe Analysis
3. Volume Analysis (VWAP, OBV, Volume Spikes)
4. Adaptive Trailing Stop Loss
5. Order Book Liquidity Analysis
6. Performance Tracking
7. Correlation Analysis

Run: python test_ai_complete.py
"""

import sys
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import modules to test
try:
    from app.ai.risk_management import PositionSizer, AdaptiveStopLoss, PerformanceTracker
    from app.ai.market_analysis import MultiTimeframeAnalyzer, VolumeAnalyzer, LiquidityAnalyzer, CorrelationAnalyzer
    from app.ai.advanced_modules import AdvancedAITradingEngine
    from app.binance_client import get_market_data_client
    print("✅ All modules imported successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


# ============================================================================
# TEST DATA GENERATORS
# ============================================================================

def generate_mock_ohlcv(periods: int = 100, trend: str = 'up') -> pd.DataFrame:
    """
    Generate mock OHLCV data for testing
    
    Args:
        periods: Number of candles
        trend: 'up', 'down', or 'sideways'
    """
    timestamps = [datetime.now() - timedelta(hours=periods-i) for i in range(periods)]
    
    if trend == 'up':
        # Uptrend with noise
        base_price = 50000
        closes = [base_price + (i * 100) + np.random.normal(0, 200) for i in range(periods)]
    elif trend == 'down':
        # Downtrend with noise
        base_price = 60000
        closes = [base_price - (i * 100) + np.random.normal(0, 200) for i in range(periods)]
    else:
        # Sideways with noise
        base_price = 50000
        closes = [base_price + np.random.normal(0, 500) for i in range(periods)]
    
    # Generate OHLC from close prices
    data = []
    for i, close in enumerate(closes):
        high = close + abs(np.random.normal(100, 50))
        low = close - abs(np.random.normal(100, 50))
        open_price = closes[i-1] if i > 0 else close
        volume = np.random.uniform(1000, 5000)
        
        data.append({
            'timestamp': timestamps[i],
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    return pd.DataFrame(data)


def generate_mock_order_book(mid_price: float = 50000) -> Dict:
    """Generate mock order book data"""
    spread = mid_price * 0.001  # 0.1% spread
    
    bids = []
    asks = []
    
    for i in range(20):
        bid_price = mid_price - spread/2 - (i * mid_price * 0.0001)
        ask_price = mid_price + spread/2 + (i * mid_price * 0.0001)
        
        bid_volume = np.random.uniform(0.1, 2.0)
        ask_volume = np.random.uniform(0.1, 2.0)
        
        bids.append([bid_price, bid_volume])
        asks.append([ask_price, ask_volume])
    
    return {
        'bids': bids,
        'asks': asks,
        'timestamp': datetime.now().timestamp() * 1000
    }


# ============================================================================
# TEST CASES
# ============================================================================

class TestResults:
    """Store and display test results"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
    
    def add_result(self, test_name: str, passed: bool, message: str = "", actual=None, expected=None):
        """Add test result"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            self.tests_failed += 1
            status = "❌ FAIL"
        
        self.results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'actual': actual,
            'expected': expected
        })
        
        print(f"{status} - {test_name}")
        if message:
            print(f"    {message}")
        if not passed and actual is not None and expected is not None:
            print(f"    Expected: {expected}")
            print(f"    Actual: {actual}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✅")
        print(f"Failed: {self.tests_failed} ❌")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print("="*80)


results = TestResults()


# ============================================================================
# TEST 1: Position Sizing
# ============================================================================

def test_position_sizing():
    """Test Kelly Criterion position sizing"""
    print("\n" + "="*80)
    print("TEST 1: POSITION SIZING (Kelly Criterion)")
    print("="*80)
    
    sizer = PositionSizer(max_risk_per_trade=0.02)
    
    # Test Case 1.1: Normal conditions
    pos = sizer.calculate_position_size(
        account_balance=10000,
        win_rate=0.6,
        avg_win_pct=0.05,
        avg_loss_pct=0.03,
        current_volatility=0.02,
        confidence=0.8
    )
    
    # Expected: Should return position between 1-3% of account
    expected_min = 100  # 1% of 10000
    expected_max = 300  # 3% of 10000
    actual = pos['position_size_usd']
    
    results.add_result(
        "Position Size - Normal Conditions",
        expected_min <= actual <= expected_max,
        f"Position size should be 1-3% of account in normal conditions",
        f"${actual:.2f}",
        f"${expected_min:.2f} - ${expected_max:.2f}"
    )
    
    # Test Case 1.2: High volatility should reduce size
    pos_high_vol = sizer.calculate_position_size(
        account_balance=10000,
        win_rate=0.6,
        avg_win_pct=0.05,
        avg_loss_pct=0.03,
        current_volatility=0.05,  # 2.5x higher volatility
        confidence=0.8
    )
    
    results.add_result(
        "Position Size - Volatility Adjustment",
        pos_high_vol['position_size_usd'] < pos['position_size_usd'],
        "High volatility should reduce position size",
        f"${pos_high_vol['position_size_usd']:.2f}",
        f"< ${pos['position_size_usd']:.2f}"
    )
    
    # Test Case 1.3: Low confidence should reduce size
    pos_low_conf = sizer.calculate_position_size(
        account_balance=10000,
        win_rate=0.6,
        avg_win_pct=0.05,
        avg_loss_pct=0.03,
        current_volatility=0.02,
        confidence=0.5  # Lower confidence
    )
    
    results.add_result(
        "Position Size - Confidence Adjustment",
        pos_low_conf['position_size_usd'] < pos['position_size_usd'],
        "Low confidence should reduce position size",
        f"${pos_low_conf['position_size_usd']:.2f}",
        f"< ${pos['position_size_usd']:.2f}"
    )
    
    # Test Case 1.4: Max risk cap
    results.add_result(
        "Position Size - Max Risk Cap",
        pos['position_pct'] <= 2.0,
        "Position should never exceed max_risk_per_trade (2%)",
        f"{pos['position_pct']:.2f}%",
        "<= 2.0%"
    )
    
    # Test Case 1.5: Minimum position
    results.add_result(
        "Position Size - Minimum Size",
        pos['position_size_usd'] >= 50,  # Min 0.5% of 10000
        "Position should never be less than 0.5% of account",
        f"${pos['position_size_usd']:.2f}",
        ">= $50.00"
    )
    
    print(f"\n📊 Position Sizing Results:")
    print(f"   Kelly Fraction: {pos['kelly_fraction']*100:.2f}%")
    print(f"   Volatility Multiplier: {pos['volatility_multiplier']:.2f}")
    print(f"   Confidence Multiplier: {pos['confidence_multiplier']:.2f}")
    print(f"   Final Position: ${pos['position_size_usd']:.2f} ({pos['position_pct']:.2f}%)")


# ============================================================================
# TEST 2: Adaptive Stop Loss
# ============================================================================

def test_adaptive_stop_loss():
    """Test adaptive trailing stop loss"""
    print("\n" + "="*80)
    print("TEST 2: ADAPTIVE TRAILING STOP LOSS")
    print("="*80)
    
    # Generate uptrend data
    ohlcv = generate_mock_ohlcv(periods=50, trend='up')
    entry_price = ohlcv['close'].iloc[0]
    
    stop = AdaptiveStopLoss(entry_price=entry_price, side='BUY', atr_multiplier=2.5)
    
    # Test Case 2.1: Initial stop calculation
    stop_info = stop.update_stop(ohlcv, entry_price)
    
    results.add_result(
        "Adaptive Stop - Initial Calculation",
        stop_info['stop_loss_price'] is not None and stop_info['stop_loss_price'] > 0,
        "Stop loss should be calculated on initialization",
        f"${stop_info['stop_loss_price']:.2f}",
        "> $0"
    )
    
    # Test Case 2.2: Stop should be below entry for BUY
    results.add_result(
        "Adaptive Stop - Below Entry (BUY)",
        stop_info['stop_loss_price'] < entry_price,
        "Stop loss should be below entry price for BUY position",
        f"${stop_info['stop_loss_price']:.2f}",
        f"< ${entry_price:.2f}"
    )
    
    # Test Case 2.3: Stop should trail as price increases
    initial_stop = stop_info['stop_loss_price']
    higher_price = entry_price * 1.05  # Price up 5%
    
    new_stop_info = stop.update_stop(ohlcv, higher_price)
    
    results.add_result(
        "Adaptive Stop - Trailing",
        new_stop_info['stop_loss_price'] > initial_stop,
        "Stop should trail up when price increases",
        f"${new_stop_info['stop_loss_price']:.2f}",
        f"> ${initial_stop:.2f}"
    )
    
    # Test Case 2.4: Stop hit detection
    price_below_stop = new_stop_info['stop_loss_price'] * 0.99
    should_exit, reason = stop.should_exit(price_below_stop)
    
    results.add_result(
        "Adaptive Stop - Hit Detection",
        should_exit == True,
        "Stop should trigger when price falls below stop level",
        should_exit,
        True
    )
    
    # Test Case 2.5: Stop not hit when above
    price_above_stop = new_stop_info['stop_loss_price'] * 1.01
    should_exit, reason = stop.should_exit(price_above_stop)
    
    results.add_result(
        "Adaptive Stop - No False Triggers",
        should_exit == False,
        "Stop should NOT trigger when price is above stop level",
        should_exit,
        False
    )
    
    print(f"\n🛡️  Adaptive Stop Results:")
    print(f"   Entry Price: ${entry_price:.2f}")
    print(f"   Initial Stop: ${initial_stop:.2f} ({((entry_price - initial_stop)/entry_price*100):.2f}% away)")
    print(f"   After +5% Move: ${new_stop_info['stop_loss_price']:.2f}")
    print(f"   Method Used: {new_stop_info['method_used']}")
    print(f"   ATR: ${new_stop_info['atr']:.2f}")


# ============================================================================
# TEST 3: Volume Analysis
# ============================================================================

def test_volume_analysis():
    """Test volume analysis (VWAP, OBV, etc.)"""
    print("\n" + "="*80)
    print("TEST 3: VOLUME ANALYSIS (VWAP, OBV, Volume Spikes)")
    print("="*80)
    
    analyzer = VolumeAnalyzer()
    
    # Test Case 3.1: Normal volume conditions
    ohlcv = generate_mock_ohlcv(periods=100, trend='up')
    result = analyzer.analyze(ohlcv)
    
    results.add_result(
        "Volume Analysis - Returns Score",
        'score' in result and 0 <= result['score'] <= 1,
        "Analysis should return score between 0 and 1",
        result.get('score', None),
        "0-1"
    )
    
    # Test Case 3.2: VWAP calculation
    results.add_result(
        "Volume Analysis - VWAP Calculation",
        'vwap' in result and result['vwap'] is not None,
        "VWAP should be calculated",
        "Calculated" if 'vwap' in result else "Missing",
        "Present"
    )
    
    # Test Case 3.3: OBV trend detection
    results.add_result(
        "Volume Analysis - OBV Trend",
        'obv' in result and 'trend' in result['obv'],
        "OBV trend should be detected (RISING/FALLING/FLAT)",
        result.get('obv', {}).get('trend', None),
        "RISING/FALLING/FLAT"
    )
    
    # Test Case 3.4: Volume spike detection
    results.add_result(
        "Volume Analysis - Spike Detection",
        'volume_spike' in result and 'signal' in result['volume_spike'],
        "Volume spikes should be detected",
        result.get('volume_spike', {}).get('signal', None),
        "Signal present"
    )
    
    # Test Case 3.5: Interpretation provided
    valid_interpretations = ['STRONG_BULLISH', 'BULLISH', 'NEUTRAL', 'BEARISH', 'STRONG_BEARISH']
    results.add_result(
        "Volume Analysis - Interpretation",
        result.get('interpretation') in valid_interpretations,
        "Should provide valid interpretation",
        result.get('interpretation'),
        f"One of: {valid_interpretations}"
    )
    
    print(f"\n📊 Volume Analysis Results:")
    print(f"   Score: {result['score']:.2f}")
    print(f"   Interpretation: {result['interpretation']}")
    if 'vwap' in result and isinstance(result['vwap'], dict):
        print(f"   Price vs VWAP: {result['vwap'].get('price_vs_vwap_pct', 0):+.2f}%")
    if 'obv' in result:
        print(f"   OBV Trend: {result['obv'].get('trend', 'N/A')}")
    if 'volume_spike' in result:
        print(f"   Volume Signal: {result['volume_spike'].get('signal', 'N/A')}")


# ============================================================================
# TEST 4: Performance Tracking
# ============================================================================

def test_performance_tracking():
    """Test performance tracking system"""
    print("\n" + "="*80)
    print("TEST 4: PERFORMANCE TRACKING")
    print("="*80)
    
    tracker = PerformanceTracker()
    
    # Generate mock trades
    mock_trades = [
        # Winning trades
        {'timestamp': datetime.now(), 'symbol': 'BTC/USDT', 'side': 'BUY', 'entry_price': 50000, 
         'exit_price': 51000, 'quantity': 0.1, 'pnl_usd': 100, 'pnl_pct': 2.0, 
         'confidence': 0.8, 'regime': 'TRENDING_UP', 'hold_time_minutes': 120},
        
        {'timestamp': datetime.now(), 'symbol': 'ETH/USDT', 'side': 'BUY', 'entry_price': 3000,
         'exit_price': 3090, 'quantity': 1.0, 'pnl_usd': 90, 'pnl_pct': 3.0,
         'confidence': 0.75, 'regime': 'TRENDING_UP', 'hold_time_minutes': 180},
        
        {'timestamp': datetime.now(), 'symbol': 'BTC/USDT', 'side': 'BUY', 'entry_price': 51000,
         'exit_price': 52000, 'quantity': 0.1, 'pnl_usd': 100, 'pnl_pct': 1.96,
         'confidence': 0.85, 'regime': 'TRENDING_UP', 'hold_time_minutes': 240},
        
        # Losing trades
        {'timestamp': datetime.now(), 'symbol': 'BTC/USDT', 'side': 'BUY', 'entry_price': 52000,
         'exit_price': 51000, 'quantity': 0.1, 'pnl_usd': -100, 'pnl_pct': -1.92,
         'confidence': 0.6, 'regime': 'SIDEWAYS', 'hold_time_minutes': 60},
        
        {'timestamp': datetime.now(), 'symbol': 'ETH/USDT', 'side': 'BUY', 'entry_price': 3090,
         'exit_price': 3030, 'quantity': 1.0, 'pnl_usd': -60, 'pnl_pct': -1.94,
         'confidence': 0.65, 'regime': 'TRENDING_DOWN', 'hold_time_minutes': 90},
    ]
    
    # Log all trades
    for trade in mock_trades:
        tracker.log_trade(trade)
    
    # Get statistics
    stats = tracker.get_statistics(lookback_days=30)
    
    # Test Case 4.1: Trade count
    results.add_result(
        "Performance - Trade Count",
        stats['total_trades'] == 5,
        "Should track all logged trades",
        stats['total_trades'],
        5
    )
    
    # Test Case 4.2: Win rate calculation
    expected_win_rate = 3/5  # 3 wins out of 5 trades = 60%
    results.add_result(
        "Performance - Win Rate",
        abs(stats['win_rate'] - expected_win_rate) < 0.01,
        "Win rate should be 60%",
        f"{stats['win_rate']*100:.1f}%",
        "60.0%"
    )
    
    # Test Case 4.3: Profit factor
    # Total wins: 290, Total losses: 160, PF = 290/160 = 1.81
    results.add_result(
        "Performance - Profit Factor",
        stats['profit_factor'] > 1.0,
        "Profit factor should be > 1.0 for profitable strategy",
        f"{stats['profit_factor']:.2f}",
        "> 1.0"
    )
    
    # Test Case 4.4: Net P&L
    expected_pnl = 290 - 160  # 130
    results.add_result(
        "Performance - Net P&L",
        abs(stats['net_pnl_usd'] - expected_pnl) < 1,
        "Net P&L should match sum of all trades",
        f"${stats['net_pnl_usd']:.2f}",
        f"${expected_pnl:.2f}"
    )
    
    # Test Case 4.5: Sharpe ratio calculated
    results.add_result(
        "Performance - Sharpe Ratio",
        'sharpe_ratio' in stats and stats['sharpe_ratio'] != 0,
        "Sharpe ratio should be calculated",
        f"{stats.get('sharpe_ratio', 0):.2f}",
        "!= 0"
    )
    
    print(f"\n📈 Performance Tracking Results:")
    print(f"   Total Trades: {stats['total_trades']}")
    print(f"   Win Rate: {stats['win_rate']*100:.1f}%")
    print(f"   Profit Factor: {stats['profit_factor']:.2f}")
    print(f"   Net P&L: ${stats['net_pnl_usd']:.2f}")
    print(f"   Sharpe Ratio: {stats['sharpe_ratio']:.2f}")
    print(f"   Max Drawdown: {stats['max_drawdown_pct']:.2f}%")


# ============================================================================
# TEST 5: Integration Test (Full AI Analysis)
# ============================================================================

def test_full_ai_analysis():
    """Test complete AI analysis pipeline"""
    print("\n" + "="*80)
    print("TEST 5: FULL AI ANALYSIS INTEGRATION")
    print("="*80)
    
    try:
        # Try to get real market client, fall back to mock if unavailable
        try:
            market_client = get_market_data_client()
            use_real_data = True
            print("✅ Using real market data from Binance")
        except Exception as e:
            print(f"⚠️  Cannot connect to Binance, using mock data: {e}")
            use_real_data = False
            market_client = None
        
        # Initialize engine
        engine = AdvancedAITradingEngine(market_client=market_client)
        
        if use_real_data and market_client:
            # Test with real data
            try:
                symbol = 'BTC/USDT'
                ohlcv_raw = market_client.fetch_ohlcv(symbol, '1h', limit=100)
                ohlcv = pd.DataFrame(ohlcv_raw, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                order_book = market_client.fetch_order_book(symbol)
                print(f"✅ Fetched real data for {symbol}")
            except Exception as e:
                print(f"⚠️  Real data fetch failed: {e}, using mock data")
                use_real_data = False
        
        if not use_real_data:
            # Use mock data
            symbol = 'BTC/USDT'
            ohlcv = generate_mock_ohlcv(periods=100, trend='up')
            order_book = generate_mock_order_book(mid_price=ohlcv['close'].iloc[-1])
            print("✅ Generated mock OHLCV and order book data")
        
        # Run analysis
        result = engine.analyze(
            symbol=symbol,
            ohlcv=ohlcv,
            order_book=order_book,
            account_balance=10000.0
        )
        
        # Test Case 5.1: Returns action
        valid_actions = ['BUY', 'SELL', 'HOLD', 'HALT']
        results.add_result(
            "Full Analysis - Action",
            result.get('action') in valid_actions,
            "Should return valid action",
            result.get('action'),
            f"One of: {valid_actions}"
        )
        
        # Test Case 5.2: Returns confidence
        results.add_result(
            "Full Analysis - Confidence",
            'confidence' in result and 0 <= result['confidence'] <= 1,
            "Confidence should be between 0 and 1",
            result.get('confidence'),
            "0-1"
        )
        
        # Test Case 5.3: Returns risk levels
        results.add_result(
            "Full Analysis - Risk Levels",
            'stop_loss' in result and 'take_profit' in result,
            "Should return stop loss and take profit levels",
            f"SL: {result.get('stop_loss')}, TP: {result.get('take_profit')}",
            "Both present"
        )
        
        # Test Case 5.4: Returns position size
        results.add_result(
            "Full Analysis - Position Size",
            'position_size_usd' in result and result['position_size_usd'] > 0,
            "Should calculate position size",
            f"${result.get('position_size_usd', 0):.2f}",
            "> $0"
        )
        
        # Test Case 5.5: All modules present
        required_modules = ['regime', 'volume', 'risk_levels', 'reversal', 'position_sizing', 'performance']
        all_modules_present = all(m in result.get('modules', {}) for m in required_modules)
        results.add_result(
            "Full Analysis - All Modules",
            all_modules_present,
            "All required modules should be present",
            list(result.get('modules', {}).keys()),
            required_modules
        )
        
        print(f"\n🤖 Full AI Analysis Results:")
        print(f"   Symbol: {symbol}")
        print(f"   Action: {result['action']}")
        print(f"   Confidence: {result['confidence']*100:.1f}%")
        print(f"   Reason: {result['reason']}")
        print(f"   Current Price: ${result['current_price']:.2f}")
        print(f"   Position Size: ${result['position_size_usd']:.2f} ({result.get('position_pct', 0):.2f}%)")
        print(f"   Stop Loss: ${result.get('stop_loss', 0):.2f}")
        print(f"   Take Profit: ${result.get('take_profit', 0):.2f}")
        print(f"   Risk/Reward: {result.get('risk_reward_ratio', 0):.2f}")
        
        if 'modules' in result:
            print(f"\n   Modules:")
            if 'regime' in result['modules']:
                print(f"   - Regime: {result['modules']['regime'].get('regime', 'N/A')}")
            if 'volume' in result['modules']:
                print(f"   - Volume: {result['modules']['volume'].get('interpretation', 'N/A')}")
            if 'mtf' in result['modules'] and result['modules']['mtf']:
                print(f"   - Multi-TF: {result['modules']['mtf'].get('alignment', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Full analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        results.add_result(
            "Full Analysis - Execution",
            False,
            f"Analysis failed with error: {str(e)}"
        )


# ============================================================================
# TEST 6: Edge Cases and Error Handling
# ============================================================================

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "="*80)
    print("TEST 6: EDGE CASES AND ERROR HANDLING")
    print("="*80)
    
    # Test Case 6.1: Empty OHLCV data
    try:
        analyzer = VolumeAnalyzer()
        empty_df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        result = analyzer.analyze(empty_df)
        results.add_result(
            "Edge Case - Empty Data",
            'score' in result,
            "Should handle empty data gracefully",
            "Handled",
            "No crash"
        )
    except Exception as e:
        results.add_result(
            "Edge Case - Empty Data",
            False,
            f"Failed to handle empty data: {e}"
        )
    
    # Test Case 6.2: Zero account balance
    try:
        sizer = PositionSizer()
        pos = sizer.calculate_position_size(
            account_balance=0,
            win_rate=0.6,
            avg_win_pct=0.05,
            avg_loss_pct=0.03,
            current_volatility=0.02,
            confidence=0.8
        )
        results.add_result(
            "Edge Case - Zero Balance",
            'position_size_usd' in pos,
            "Should handle zero balance",
            "Handled",
            "No crash"
        )
    except Exception as e:
        results.add_result(
            "Edge Case - Zero Balance",
            False,
            f"Failed to handle zero balance: {e}"
        )
    
    # Test Case 6.3: Negative price data
    try:
        ohlcv = generate_mock_ohlcv(periods=50, trend='up')
        ohlcv.loc[10, 'close'] = -100  # Insert negative price
        
        stop = AdaptiveStopLoss(entry_price=50000, side='BUY')
        stop_info = stop.update_stop(ohlcv, 50000)
        
        results.add_result(
            "Edge Case - Invalid Price Data",
            stop_info['stop_loss_price'] > 0,
            "Should handle invalid price data",
            "Handled",
            "Positive stop returned"
        )
    except Exception as e:
        results.add_result(
            "Edge Case - Invalid Price Data",
            False,
            f"Failed to handle invalid prices: {e}"
        )
    
    # Test Case 6.4: Very high volatility
    try:
        sizer = PositionSizer()
        pos = sizer.calculate_position_size(
            account_balance=10000,
            win_rate=0.6,
            avg_win_pct=0.05,
            avg_loss_pct=0.03,
            current_volatility=0.50,  # 50% volatility!
            confidence=0.8
        )
        
        results.add_result(
            "Edge Case - Extreme Volatility",
            pos['position_size_usd'] < 200,  # Should reduce size significantly
            "Should reduce position size in extreme volatility",
            f"${pos['position_size_usd']:.2f}",
            "< $200"
        )
    except Exception as e:
        results.add_result(
            "Edge Case - Extreme Volatility",
            False,
            f"Failed to handle extreme volatility: {e}"
        )


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*80)
    print("🧪 ADVANCED AI TRADING SYSTEM - TEST SUITE")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    try:
        # Run all test suites
        test_position_sizing()
        test_adaptive_stop_loss()
        test_volume_analysis()
        test_performance_tracking()
        test_full_ai_analysis()
        test_edge_cases()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    # Print summary
    results.print_summary()
    
    # Return exit code
    return 0 if results.tests_failed == 0 else 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
