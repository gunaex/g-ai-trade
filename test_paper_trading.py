"""
Automated Paper Trading Test Suite

Runs comprehensive tests to validate the God's Hand bot in paper trading mode.
Tests cover:
- Basic buy/sell operations
- Balance management
- Fee calculations
- Edge cases (insufficient balance, etc.)
- Performance metrics
- Multi-trade scenarios
"""

import sys
from datetime import datetime, timezone, timedelta
from app.paper_trading import (
    PaperTradingEngine,
    OrderSide,
    OrderStatus,
)


def test_basic_buy_sell():
    """Test 1: Basic buy and sell flow"""
    print("\n" + "="*60)
    print("TEST 1: Basic Buy/Sell Flow")
    print("="*60)
    
    engine = PaperTradingEngine(initial_balance=10000)
    
    # Buy 0.1 BTC at 50,000
    success, order, msg = engine.place_market_order(
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        quantity=0.1,
        current_price=50000
    )
    
    print(f"BUY Order: {msg}")
    print(f"  Status: {order.status.value}")
    print(f"  Fill Price: ${order.filled_price:.2f}")
    print(f"  Fee: ${order.fee:.2f}")
    print(f"  USDT Balance: ${engine.balance.usdt:.2f}")
    print(f"  BTC Balance: {engine.balance.base_asset:.6f}")
    
    assert success, "Buy order should succeed"
    assert order.status == OrderStatus.FILLED
    assert engine.current_position is not None
    assert engine.balance.base_asset == 0.1
    
    # Sell at profit (55,000 = 10% gain)
    success, order, msg = engine.place_market_order(
        symbol="BTC/USDT",
        side=OrderSide.SELL,
        quantity=0.1,
        current_price=55000
    )
    
    print(f"\nSELL Order: {msg}")
    print(f"  Status: {order.status.value}")
    print(f"  Fill Price: ${order.filled_price:.2f}")
    print(f"  Fee: ${order.fee:.2f}")
    print(f"  USDT Balance: ${engine.balance.usdt:.2f}")
    print(f"  BTC Balance: {engine.balance.base_asset:.6f}")
    
    assert success, "Sell order should succeed"
    assert engine.current_position is None
    assert len(engine.trade_history) == 1
    
    trade = engine.trade_history[0]
    print(f"\nTrade Result:")
    print(f"  Gross P&L: ${trade.gross_pnl:.2f}")
    print(f"  Fees: ${trade.fees:.2f}")
    print(f"  Net P&L: ${trade.net_pnl:.2f}")
    print(f"  ROI: {trade.pnl_percent:.2f}%")
    
    assert trade.net_pnl > 0, "Should have profit"
    
    print("\n✅ TEST 1 PASSED")


def test_insufficient_balance():
    """Test 2: Insufficient balance rejection"""
    print("\n" + "="*60)
    print("TEST 2: Insufficient Balance Handling")
    print("="*60)
    
    engine = PaperTradingEngine(initial_balance=1000)
    
    # Try to buy more than we can afford
    success, order, msg = engine.place_market_order(
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        quantity=1.0,  # 1 BTC at 50k = way over budget
        current_price=50000
    )
    
    print(f"Attempted large buy: {msg}")
    print(f"  Status: {order.status.value}")
    print(f"  Balance unchanged: ${engine.balance.usdt:.2f}")
    
    assert not success, "Should reject order"
    assert order.status == OrderStatus.REJECTED
    assert engine.balance.usdt == 1000, "Balance should be unchanged"
    
    print("\n✅ TEST 2 PASSED")


def test_fee_calculation():
    """Test 3: Fee calculation accuracy"""
    print("\n" + "="*60)
    print("TEST 3: Fee Calculation")
    print("="*60)
    
    engine = PaperTradingEngine(
        initial_balance=10000,
        maker_fee=0.001,  # 0.1%
        taker_fee=0.001,
        slippage_bps=0  # No slippage for exact fee test
    )
    
    # Buy exactly $5000 worth
    quantity = 0.1
    price = 50000
    expected_cost = quantity * price  # 5000
    expected_fee = expected_cost * 0.001  # 5.0
    expected_total = expected_cost + expected_fee  # 5005
    
    success, order, _ = engine.place_market_order(
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        quantity=quantity,
        current_price=price
    )
    
    print(f"Buy Order:")
    print(f"  Cost: ${expected_cost:.2f}")
    print(f"  Fee: ${order.fee:.2f} (expected ${expected_fee:.2f})")
    print(f"  Total: ${expected_total:.2f}")
    print(f"  Remaining USDT: ${engine.balance.usdt:.2f}")
    
    assert abs(order.fee - expected_fee) < 0.01, "Fee should match"
    assert abs(engine.balance.usdt - (10000 - expected_total)) < 0.01
    
    print("\n✅ TEST 3 PASSED")


def test_multiple_trades():
    """Test 4: Multiple trades with mixed results"""
    print("\n" + "="*60)
    print("TEST 4: Multiple Trades Scenario")
    print("="*60)
    
    engine = PaperTradingEngine(initial_balance=10000)
    
    # Simulate 5 trades with different outcomes
    scenarios = [
        (50000, 52000, "win"),   # +4% win
        (52000, 51000, "loss"),  # -1.9% loss
        (51000, 53000, "win"),   # +3.9% win
        (53000, 52500, "loss"),  # -0.9% loss
        (52500, 55000, "win"),   # +4.7% win
    ]
    
    quantity = 0.1  # Fixed quantity
    
    for i, (entry, exit, expected) in enumerate(scenarios, 1):
        # Buy
        engine.place_market_order("BTC/USDT", OrderSide.BUY, quantity, entry)
        
        # Sell
        engine.place_market_order("BTC/USDT", OrderSide.SELL, quantity, exit)
        
        trade = engine.trade_history[-1]
        result_type = "WIN" if trade.net_pnl > 0 else "LOSS"
        print(f"Trade {i}: ${entry} → ${exit} | {result_type} ${trade.net_pnl:.2f} ({trade.pnl_percent:.2f}%)")
    
    perf = engine.get_performance_summary()
    
    print(f"\nPerformance Summary:")
    print(f"  Total Trades: {perf['total_trades']}")
    print(f"  Winning: {perf['winning_trades']} | Losing: {perf['losing_trades']}")
    print(f"  Win Rate: {perf['win_rate']:.1f}%")
    print(f"  Total P&L: ${perf['total_pnl']:.2f}")
    print(f"  ROI: {perf['roi_percent']:.2f}%")
    print(f"  Total Fees: ${perf['total_fees_paid']:.2f}")
    print(f"  Avg Win: ${perf['avg_win']:.2f}")
    print(f"  Avg Loss: ${perf['avg_loss']:.2f}")
    print(f"  Profit Factor: {perf['profit_factor']:.2f}")
    
    assert perf['total_trades'] == 5
    assert perf['winning_trades'] == 3
    assert perf['losing_trades'] == 2
    assert perf['win_rate'] == 60.0
    
    print("\n✅ TEST 4 PASSED")


def test_slippage_simulation():
    """Test 5: Slippage simulation"""
    print("\n" + "="*60)
    print("TEST 5: Slippage Simulation")
    print("="*60)
    
    engine = PaperTradingEngine(
        initial_balance=10000,
        slippage_bps=10  # 10 basis points = 0.1%
    )
    
    price = 50000
    
    # Buy should get worse fill (higher price)
    success, buy_order, _ = engine.place_market_order(
        "BTC/USDT", OrderSide.BUY, 0.1, price
    )
    
    expected_buy_slippage = price * 0.001  # 0.1%
    actual_buy_slippage = buy_order.filled_price - price
    
    print(f"BUY Slippage:")
    print(f"  Market Price: ${price:.2f}")
    print(f"  Fill Price: ${buy_order.filled_price:.2f}")
    print(f"  Slippage: ${actual_buy_slippage:.2f} (expected ~${expected_buy_slippage:.2f})")
    
    assert buy_order.filled_price > price, "Buy should have worse fill"
    
    # Sell should get worse fill (lower price)
    success, sell_order, _ = engine.place_market_order(
        "BTC/USDT", OrderSide.SELL, 0.1, price
    )
    
    expected_sell_slippage = price * 0.001
    actual_sell_slippage = price - sell_order.filled_price
    
    print(f"\nSELL Slippage:")
    print(f"  Market Price: ${price:.2f}")
    print(f"  Fill Price: ${sell_order.filled_price:.2f}")
    print(f"  Slippage: ${actual_sell_slippage:.2f} (expected ~${expected_sell_slippage:.2f})")
    
    assert sell_order.filled_price < price, "Sell should have worse fill"
    
    print("\n✅ TEST 5 PASSED")


def test_drawdown_tracking():
    """Test 6: Maximum drawdown tracking"""
    print("\n" + "="*60)
    print("TEST 6: Drawdown Tracking")
    print("="*60)
    
    engine = PaperTradingEngine(initial_balance=10000)
    
    # Simulate a losing streak
    trades = [
        (50000, 48000),  # -4% loss
        (48000, 46000),  # -4.1% loss
        (46000, 47000),  # +2.1% recovery
    ]
    
    for entry, exit in trades:
        engine.place_market_order("BTC/USDT", OrderSide.BUY, 0.1, entry)
        engine.place_market_order("BTC/USDT", OrderSide.SELL, 0.1, exit)
        
        perf = engine.get_performance_summary()
        print(f"After trade: Balance ${perf['current_balance_usdt']:.2f} | Drawdown: {perf['max_drawdown']:.2f}%")
    
    perf = engine.get_performance_summary()
    
    print(f"\nFinal Metrics:")
    print(f"  Peak Balance: ${engine.peak_balance:.2f}")
    print(f"  Current Balance: ${perf['current_balance_usdt']:.2f}")
    print(f"  Max Drawdown: {perf['max_drawdown']:.2f}%")
    
    assert perf['max_drawdown'] > 0, "Should have recorded drawdown"
    
    print("\n✅ TEST 6 PASSED")


def test_report_export():
    """Test 7: Report export functionality"""
    print("\n" + "="*60)
    print("TEST 7: Report Export")
    print("="*60)
    
    engine = PaperTradingEngine(initial_balance=10000)
    
    # Execute some trades
    engine.place_market_order("BTC/USDT", OrderSide.BUY, 0.1, 50000)
    engine.place_market_order("BTC/USDT", OrderSide.SELL, 0.1, 52000)
    
    # Export report
    filepath = engine.export_report("test_report.json")
    
    print(f"Report exported to: {filepath}")
    
    import json
    with open(filepath, 'r') as f:
        report = json.load(f)
    
    print(f"\nReport contains:")
    print(f"  Summary keys: {list(report['summary'].keys())}")
    print(f"  Total trades: {len(report['trades'])}")
    print(f"  Total orders: {len(report['orders'])}")
    
    assert 'summary' in report
    assert 'trades' in report
    assert 'orders' in report
    assert len(report['trades']) == 1
    assert len(report['orders']) == 2
    
    # Cleanup
    import os
    os.remove(filepath)
    
    print("\n✅ TEST 7 PASSED")


def run_all_tests():
    """Run all automated tests"""
    print("\n" + "🤖 "*30)
    print("AUTOMATED PAPER TRADING TEST SUITE")
    print("God's Hand Bot - Risk-Free Validation")
    print("🤖 "*30)
    
    tests = [
        test_basic_buy_sell,
        test_insufficient_balance,
        test_fee_calculation,
        test_multiple_trades,
        test_slippage_simulation,
        test_drawdown_tracking,
        test_report_export,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n💥 TEST ERROR: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed} PASSED | {failed} FAILED")
    print("="*60)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED - Paper Trading Engine is Ready!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
