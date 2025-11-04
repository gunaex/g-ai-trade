# God's Hand Auto Trading - When It Buys & Sells

## 🎯 Quick Answer

**God's Hand will BUY when:**
1. ✅ Market is **TRENDING_UP** (ADX > 40 + Price above moving average)
2. ✅ AI Confidence ≥ **Your min_confidence setting** (default 70%)
3. ✅ On-Chain filter approves (no whale dump detected)
4. ✅ Trade frequency limits allow (max 2/hour, 10/day)

**God's Hand will SELL when:**
1. 📈 Take Profit hit (default: +4% profit)
2. 📉 Stop Loss hit (default: -2% loss)
3. 🔄 Market regime changes to **TRENDING_DOWN**

---

## 📊 Detailed BUY Conditions

### Step 1: Market Regime Detection (Most Important!)

God's Hand analyzes the market using **ADX (Average Directional Index)** and **Moving Averages**:

| ADX Value | MA Ratio | Result | Action |
|-----------|----------|--------|--------|
| **< 20** | Any | **SIDEWAYS** | ⏸️ HOLD (No trading) |
| **20-40** | > 1.02 | **TRENDING_UP** | ✅ Consider BUY |
| **20-40** | < 0.98 | **TRENDING_DOWN** | ❌ No BUY |
| **20-40** | 0.98-1.02 | **SIDEWAYS** | ⏸️ HOLD |
| **> 40** | > 1.00 | **TRENDING_UP** 🔥 | ✅ BUY Signal! |
| **> 40** | < 1.00 | **TRENDING_DOWN** | ❌ No BUY |

**What this means:**
- **ADX > 40** = Strong trend (best for trading)
- **MA Ratio > 1** = Price above moving average (bullish)
- **Combination** = TRENDING_UP = God's Hand will look to BUY

### Step 2: AI Confidence Score

Once market is TRENDING_UP, AI calculates confidence:

```
Base Confidence = 70%
+ Volume Adjustment = -20% to +20% (based on volume strength)
+ Multi-Timeframe Boost = 0% to +15% (if higher timeframes align)
= Final Confidence = 50% to 95%
```

**Example Scenarios:**

| Scenario | Base | Volume | MTF | Final | Result |
|----------|------|--------|-----|-------|--------|
| Strong uptrend + high volume | 70% | +15% | +10% | **95%** | ✅ BUY |
| Uptrend + normal volume | 70% | +5% | 0% | **75%** | ✅ BUY |
| Uptrend + low volume | 70% | -10% | 0% | **60%** | ❌ Below 70% = No BUY |

**Your min_confidence setting determines the threshold!**
- Default: 70% (conservative)
- Aggressive: 60% (more trades, higher risk)
- Very Conservative: 80% (fewer trades, lower risk)

### Step 3: On-Chain Filter (Veto Power)

Even if AI says BUY, the On-Chain filter can **veto** if it detects:

❌ **Whale dump signals** (large holders selling)  
❌ **Exchange inflows spike** (people moving to exchanges to sell)  
❌ **Suspicious wallet activity**  

✅ **If On-Chain status = SAFE** → Proceed to BUY

### Step 4: Trade Frequency Limits

Fee Protection System prevents over-trading:

- **Max 2 trades per hour** (prevents rapid buying/selling)
- **Max 10 trades per day** (daily limit)
- **Min 30 minutes hold time** (must hold position for 30+ min)

If you already made 2 trades in the past hour → **No BUY** (wait for next hour)

### Step 5: Execute BUY Order

If all above conditions pass:

```python
✅ Market: TRENDING_UP (ADX > 40)
✅ AI Confidence: 75% (≥ 70%)
✅ On-Chain: SAFE
✅ Trade Frequency: OK (1/2 trades this hour)
→ 🛒 Execute BUY Order!
```

**What happens:**
1. Calculate position size from budget × position_size_ratio (default 100% = all budget)
2. Send market BUY order to Binance
3. Set Stop Loss at -2% (protects from big losses)
4. Set Take Profit at +4% (auto-sell when profit hit)
5. Log trade in database
6. Send notification (if enabled)

---

## 📈 SELL Conditions (Exit Position)

God's Hand will SELL your position when:

### 1. Take Profit Hit (Auto-Profit) 🎉

**Default: +4% profit**

Example:
- Bought BTC at $50,000
- Take Profit set at $52,000 (+4%)
- Price reaches $52,000 → **Auto SELL** ✅

You can adjust this in `max_daily_loss` and risk settings.

### 2. Stop Loss Hit (Protect Capital) 🛡️

**Default: -2% loss**

Example:
- Bought BTC at $50,000
- Stop Loss set at $49,000 (-2%)
- Price drops to $49,000 → **Auto SELL** ❌ (Cut losses)

This prevents small losses from becoming big losses.

### 3. Market Regime Change to TRENDING_DOWN 🔻

If the market shifts:
- **TRENDING_UP → TRENDING_DOWN** → God's Hand will SELL to exit
- **TRENDING_UP → SIDEWAYS** → Usually HOLD (unless patterns suggest exit)

Example:
- You bought during uptrend
- ADX drops below 20 → Market now SIDEWAYS → May exit
- ADX > 40 but MA Ratio < 1 → Market now DOWN → SELL to protect

### 4. AI Confidence Drops Below Threshold

If AI re-analyzes and confidence drops significantly:
- Was 80% confident → Now 40% confident → May exit position

---

## 🎮 Real Examples

### Example 1: Perfect BUY Setup

```
Time: 2025-11-04 10:00 AM
Symbol: BTC/USDT
Price: $68,000

Market Analysis:
- ADX: 52 (strong trend)
- MA Ratio: 1.08 (price 8% above MA)
- Volume: High (spike detected)
- Regime: TRENDING_UP ✅

AI Decision:
- Base Confidence: 70%
- Volume Adjustment: +18% (high volume)
- MTF Alignment: STRONG_BULLISH (+15%)
- Final Confidence: 93% ✅

On-Chain:
- Whale accumulation: Yes
- Exchange outflows: High (people withdrawing, bullish)
- Status: SAFE ✅

Trade Frequency:
- Trades this hour: 0/2 ✅
- Trades today: 3/10 ✅

RESULT: 🛒 BUY 0.147 BTC @ $68,000
- Stop Loss: $66,640 (-2%)
- Take Profit: $70,720 (+4%)
```

### Example 2: No BUY - Low Confidence

```
Time: 2025-11-04 11:30 AM
Symbol: ETH/USDT
Price: $3,200

Market Analysis:
- ADX: 28 (moderate trend)
- MA Ratio: 1.01 (barely above MA)
- Volume: Normal
- Regime: SIDEWAYS ⏸️

AI Decision:
- Regime: SIDEWAYS → Action: HOLD
- Confidence: 50%
- Reason: "Market in SIDEWAYS - waiting for clear signal"

RESULT: ⏸️ NO ACTION (Waiting for stronger signal)
```

### Example 3: BUY Blocked - Frequency Limit

```
Time: 2025-11-04 2:15 PM
Symbol: SOL/USDT
Price: $180

Market Analysis:
- ADX: 48 (strong uptrend)
- Regime: TRENDING_UP ✅
- AI Confidence: 82% ✅
- On-Chain: SAFE ✅

Trade Frequency:
- Trades this hour: 2/2 ❌ (Already made 2 trades 2:05 PM and 2:10 PM)

RESULT: 🚫 BUY BLOCKED
Reason: "Trade frequency limit - max 2 trades per hour"
Action: Wait until 3:00 PM for next allowed trade
```

### Example 4: Auto SELL - Take Profit

```
Time: 2025-11-04 3:45 PM
Symbol: BTC/USDT
Entry Price: $68,000 (bought at 10:00 AM)
Current Price: $70,720
P&L: +$400 (+4%)

Position Check:
- Take Profit: $70,720 ✅ HIT!
- Hold Time: 5h 45min ✅ (> 30 min requirement)

RESULT: 💰 SELL (Take Profit)
- Sold: 0.147 BTC @ $70,720
- Profit: $400 (4%)
- Fee: ~$14 (0.2% total)
- Net Profit: $386
```

---

## ⚙️ Configuration Settings That Affect Trading

### In God's Hand Config:

| Setting | Default | What It Does |
|---------|---------|--------------|
| **min_confidence** | 70% | AI must be ≥ this confident to BUY |
| **budget** | $10,000 | Total capital available |
| **position_size_ratio** | 100% | % of budget to use per trade |
| **risk_level** | moderate | Affects stop loss % and take profit % |
| **max_daily_loss** | 5% | Max loss allowed per day |
| **paper_trading** | true | If true, simulate only (no real trades) |

### Advanced Settings:

```python
# In app/auto_trader.py
interval_seconds = 300  # Check every 5 minutes

# In app/ai/fee_protection.py
min_profit_multiple = 3.0  # Profit must be 3x fees
max_trades_per_hour = 2
max_trades_per_day = 10
min_hold_time_minutes = 30

# In app/ai/advanced_modules.py
base_confidence = 0.7  # 70% base
```

---

## 🔧 How to Adjust Trading Behavior

### Want More Trades? (Aggressive)

1. **Lower min_confidence**: 60% instead of 70%
2. **Increase trade frequency**: 3/hour instead of 2/hour
3. **Lower ADX threshold**: Accept ADX 30+ instead of 40+

⚠️ **Risk**: More trades = more fees, potentially lower quality signals

### Want Fewer, Higher Quality Trades? (Conservative)

1. **Raise min_confidence**: 80% instead of 70%
2. **Require stronger trends**: ADX > 50 only
3. **Stricter On-Chain filter**: Only trade when whale accumulation confirmed

✅ **Benefit**: Higher win rate, lower fees, less stress

### Want to Avoid Losses? (Max Protection)

1. **Tighter Stop Loss**: -1% instead of -2%
2. **Wider Take Profit**: +6% instead of +4%
3. **Shorter hold time requirement**: 15 min instead of 30 min

⚠️ **Tradeoff**: May exit too early on -1% dips in volatile markets

---

## 📱 Monitoring Your Bot

### Check Current Status:

1. **God's Hand Dashboard** → Shows current position, P&L, activity log
2. **Advanced Analysis** → See current regime, AI confidence, sentiment
3. **Activity Log** → Last 100 actions with timestamps

### Key Indicators to Watch:

- **Market Regime**: If stuck in SIDEWAYS for hours → No trades (normal)
- **AI Confidence**: Consistently below 70%? → Market conditions not ideal
- **On-Chain Status**: If often VETO → Whale activity blocking trades
- **Trade Frequency**: Hitting limits? → May need to adjust settings

---

## ❓ FAQ

**Q: Why isn't God's Hand buying even though I see BUY signal?**

A: Check these in order:
1. Is `paper_trading = true`? (It's simulating, not real trading)
2. Is bot actually **started**? (Click "Start AI God's Hand")
3. Is AI confidence < min_confidence? (Lower your min_confidence setting)
4. Did you hit trade frequency limit? (Wait for next hour)
5. Is On-Chain filter vetoing? (Check activity log for "On-Chain VETO")

**Q: Can I manually force a BUY?**

A: God's Hand is designed for autonomous trading. Manual intervention defeats the purpose. If you want control, use the regular Trade page instead of God's Hand.

**Q: How long does it take to make a trade?**

A: Checks run every **5 minutes**. So maximum 5 min delay from signal appearing to trade executing. Average: 2-3 minutes.

**Q: Will it trade 24/7?**

A: Yes! Once started, God's Hand runs continuously checking for opportunities every 5 minutes, even when you're sleeping.

**Q: What if I run out of budget?**

A: Bot will pause and log "Insufficient balance". You need to add funds or close existing position to free up capital.

**Q: Can I change settings while bot is running?**

A: Yes! Changes take effect on next check cycle (within 5 minutes). But changing mid-trade may cause unexpected behavior.

---

## 🚀 Quick Start Checklist

To ensure God's Hand starts trading:

- [ ] **Set paper_trading = false** (if you want real trades)
- [ ] **Add API keys** (Binance API key + secret)
- [ ] **Set reasonable min_confidence** (70% recommended)
- [ ] **Choose volatile symbol** (BTC/USDT, ETH/USDT work best)
- [ ] **Allocate budget** (min $100 recommended)
- [ ] **Click "Start AI God's Hand"**
- [ ] **Wait for TRENDING_UP market** (may take hours if currently SIDEWAYS)
- [ ] **Monitor activity log** for "BUY EXECUTED" message

**Patience is key!** God's Hand waits for **quality setups** rather than forcing trades in poor conditions.

---

## 📊 Current Status Check

To see what's preventing a BUY right now:

1. Go to **Advanced Analysis** page
2. Check **Market Regime** card:
   - TRENDING_UP → Good! ✅
   - SIDEWAYS → Waiting... ⏸️
   - TRENDING_DOWN → No BUY ❌

3. Check **Sentiment Analysis**:
   - Score > 0.1 → Bullish sentiment ✅
   - Score < -0.1 → Bearish → May block BUY ❌

4. Check **God's Hand** activity log:
   - Last message shows reason for HOLD/BUY/VETO

---

**Last Updated**: 2025-11-04  
**Version**: 1.0  
**Author**: AI Trading System Team
