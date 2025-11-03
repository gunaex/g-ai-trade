# 🤖 G-AI-Trade - AI-Powered Crypto Trading Platform

A full-stack cryptocurrency trading system with AI-driven analysis and automated trading bots.

---

## 🎯 What It Does

**Automatically trades cryptocurrency using AI** to analyze market conditions and execute profitable trades 24/7.

---

## ✨ Key Features

### 🧠 AI Trading Intelligence
- **4D Market Analysis**: Analyzes Market trends, Sentiment, Whale movements, and Fundamentals
- **Real-time Recommendations**: BUY/SELL/HOLD signals updated every 30 seconds
- **Smart Decision Engine**: Combines multiple data sources for accurate predictions
- **God's Hand Bot**: Fully autonomous AI trading with configurable risk levels

### 🤖 Trading Bots
1. **Grid Bot** - Places buy/sell orders in a grid pattern to profit from volatility
2. **DCA Bot** - Dollar-Cost Averaging for systematic accumulation
3. **AI Force Bot** - AI-driven automated trading with confidence thresholds
4. **God's Hand** - Advanced autonomous trading with multi-module AI analysis

### 📊 Features
- **Live Market Data**: Real-time prices from Binance Thailand
- **Performance Tracking**: PnL, win rate, trade history, and analytics
- **Risk Management**: Stop-loss, position sizing, max daily loss limits
- **Backtesting**: Test strategies on historical data before live trading
- **Multi-User Support**: Each user has their own isolated trading environment

### 🔐 Security
- **JWT Authentication**: Secure login with auto-refreshing tokens
- **Encrypted API Keys**: Your Binance credentials are encrypted at rest
- **Access Control**: Users can only see and control their own bots
- **Audit Logging**: All trading actions are logged for review

---

## 🖥️ Tech Stack

**Backend:**
- Python + FastAPI
- SQLAlchemy (PostgreSQL/SQLite)
- ccxt + python-binance for exchange integration
- AI/ML modules for market analysis

**Frontend:**
- React 18 + TypeScript
- Vite (fast development)
- Recharts for charts and analytics
- TailwindCSS styling

**Deployment:**
- Backend: Render.com
- Frontend: Vercel
- Database: PostgreSQL (production)

---

## 📱 User Interface

### Pages:
1. **Trade** - Manual trading with AI recommendations
2. **God's Hand** - Autonomous AI bot with full control panel
3. **Monitoring** - Real-time bot performance and activity logs
4. **Backtesting** - Test strategies on historical data
5. **Settings** - Configure API keys and preferences

### Dashboard Shows:
- 💰 Current balance (USDT & crypto)
- 📈 AI recommendation scores (Market, Sentiment, Whale, Fundamental)
- 🎯 Current action (BUY/SELL/HOLD)
- 📊 Live charts with technical indicators
- 🤖 Active bots and their performance

---

## 🚀 How It Works

### 1. **Setup** (One-time)
- Create account with username/password
- Add your Binance API keys (encrypted and stored securely)
- Choose your trading strategy

### 2. **AI Analysis** (Automatic)
Every 30 seconds, AI analyzes:
- **Market**: RSI, MACD, volume, price trends
- **Sentiment**: Social media and news sentiment
- **Whale**: Large holder movements and accumulation
- **Fundamental**: Project strength and metrics

### 3. **Trading** (Automated or Manual)
**Manual Mode:**
- AI shows BUY/SELL/HOLD recommendation
- You click to execute trades

**Bot Mode:**
- Configure your bot (budget, risk level, strategy)
- Bot trades automatically based on AI signals
- Monitor performance in real-time

### 4. **Results** (Track Performance)
- View all trades with entry/exit prices
- See profit/loss per trade and total
- Win rate and performance metrics
- Activity log of all bot actions

---

## 💡 Example Use Cases

### Conservative Investor
- Use **DCA Bot** to accumulate Bitcoin weekly
- Set low risk level and high AI confidence threshold
- Let it run for months with minimal monitoring

### Active Trader
- Use **God's Hand** with moderate risk
- Check AI recommendations before major decisions
- Combine with manual trades on opportunities

### Day Trader
- Use **Grid Bot** on volatile pairs
- Profit from price swings within a range
- Quick scalps with tight grids

---

## 📈 Sample AI Recommendation

```
Current Analysis (BTC/USDT):
├─ Market Score: 72% 🟢 (RSI oversold, volume increasing)
├─ Sentiment: 65% 🟢 (Positive social media trends)
├─ Whale: 58% 🟡 (Moderate accumulation)
└─ Fundamental: 70% 🟢 (Strong project metrics)

→ Combined Score: 66% → BUY 🟢

AI Recommendation: Strong buy signal detected
Confidence: High (66%)
```

---

## ⚙️ God's Hand Bot Configuration

**Risk Levels:**
- **Conservative**: 50-70% confidence, 5% max daily loss
- **Moderate**: 60-80% confidence, 10% max daily loss
- **Aggressive**: 70-90% confidence, 15% max daily loss

**Customizable Settings:**
- Budget allocation per trade
- AI confidence threshold
- Position size percentage
- Max daily loss limit
- Trading symbols (BTC, ETH, BNB, etc.)

---

## 📊 Performance Metrics Tracked

- **Total P&L**: Overall profit/loss in USDT
- **Win Rate**: Percentage of profitable trades
- **Total Trades**: Number of completed trades
- **Fees Paid**: Total trading fees
- **Best/Worst Trade**: Largest gains and losses
- **Average Hold Time**: How long positions are held
- **Sharpe Ratio**: Risk-adjusted returns

---

## 🛡️ Safety Features

✅ **Max Daily Loss**: Bot stops if daily losses exceed limit  
✅ **Position Limits**: Maximum open positions controlled  
✅ **Emergency Stop**: Instantly halt all trading  
✅ **Paper Trading**: Test strategies with fake money first  
✅ **Stop Loss**: Automatic exit on significant losses  
✅ **API Key Encryption**: Keys never stored in plain text  

---

## 🎓 Perfect For

- ✅ Crypto investors who want to automate their trading
- ✅ Traders looking for AI-powered market insights
- ✅ Anyone wanting to trade 24/7 without manual monitoring
- ✅ People who want to learn algorithmic trading
- ✅ Investors seeking systematic, emotion-free trading

---

## 📝 Quick Stats

- **Trading Pairs**: BTC, ETH, BNB, XRP, and more
- **AI Update Frequency**: Every 30 seconds
- **Supported Exchange**: Binance Thailand
- **Bot Types**: 4 (Grid, DCA, AI Force, God's Hand)
- **Max Users**: Unlimited (multi-tenant architecture)
- **Uptime**: 99.9% (hosted on Render + Vercel)

---

## 🚦 Getting Started

1. **Visit**: https://your-frontend-url.vercel.app
2. **Register**: Create your account
3. **Setup API Keys**: Add Binance credentials in Settings
4. **Start Trading**: 
   - Try AI recommendations manually first
   - Configure and launch God's Hand bot
   - Monitor performance on dashboard

---

## 🔗 Links

- **Live Demo**: [Your Vercel URL]
- **Backend API**: https://g-ai-trade-backend.onrender.com
- **GitHub**: https://github.com/gunaex/g-ai-trade
- **Documentation**: See README.md for full details

---

## ⚠️ Disclaimer

**Trading cryptocurrency involves risk.** This platform is a tool to assist with trading decisions using AI analysis, but it does not guarantee profits. Always:
- Start with small amounts to test
- Never invest more than you can afford to lose
- Understand the risks of automated trading
- Review bot configurations carefully
- Monitor your bots regularly

**Past performance does not guarantee future results.**

---

## 💬 Questions?

**How much can I make?**  
Depends on market conditions, your strategy, and risk tolerance. Start small and scale up as you gain confidence.

**Is it safe?**  
Your API keys are encrypted, and you maintain full control. The platform uses read/write API keys (not withdrawal permissions).

**Do I need trading experience?**  
No! The AI handles analysis and bots execute automatically. However, understanding basic trading concepts helps.

**Can I test without real money?**  
Yes! Use backtesting to test strategies on historical data before going live.

**What if the bot loses money?**  
Bots have max daily loss limits and stop-loss protections. You can stop them anytime with one click.

---

**Built with ❤️ for automated crypto trading**
