# Fee Protection System - Quick Reference

## What It Does

Prevents excessive trading fees from draining your account through:
- ✅ Minimum profit threshold (3x fees)
- ✅ Trade frequency limits (2/hour, 10/day)
- ✅ Minimum hold time (30 minutes)
- ✅ Net profit calculation (after fees)
- ✅ Breakeven price tracking
- ✅ 24-hour fee monitoring

## Default Settings

```
Binance Fees: 0.1% maker + 0.1% taker
Minimum Profit: 3x total fees (0.6%)
Max Trades: 2 per hour, 10 per day
Min Hold Time: 30 minutes
```

## Example

**Without Protection**:
- 20 trades/day = $40/day fees = $1,200/month ❌
- Need +10% monthly just to break even

**With Protection**:
- 6 trades/day = $12/day fees = $360/month ✅
- Need +1-2% monthly to be profitable

**Result**: 80% fee reduction, 5x easier to profit!

## Key Messages You'll See

**Entry (BUY)**:
```
💰 Breakeven Price: $50,100.00 (+0.20%)
💰 Min Profitable Price: $50,300.00 (+0.60%)
```

**Exit (SELL)**:
```
💵 Gross Profit: $500.00 (1.00%)
💸 Trading Fees: $100.00 (0.20%)
💰 Net Profit: $400.00 (0.80%)
```

**Blocked Trades**:
```
🚫 Trade limit: 2/2 trades in last hour
⚠️  Net profit $100 below 3x fees ($300)
🚫 Must hold for 15 more minutes
```

## Files

- `app/ai/fee_protection.py` - Fee protection module
- `app/auto_trader.py` - Integrated into God's Hand
- `FEE_PROTECTION_GUIDE.md` - Complete documentation

## See Also

Read `FEE_PROTECTION_GUIDE.md` for detailed scenarios and configuration options.
