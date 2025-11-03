# G-AI-TRADE v1.0

Full-Stack AI-Powered Crypto Trading System

## Features

- **🔐 JWT Authentication**: Secure user authentication with token-based access control
- **AI Decision Engine**: 4D analysis (Market, Fundamental, Sentiment, On-Chain)
- **Grid Trading Bot**: Automated grid trading with dynamic ATR
- **DCA Bot**: Dollar-cost averaging with customizable intervals
- **Real-time Market Data**: Live prices from Binance
- **Risk Management**: Max drawdown, correlation filters, position sizing
- **Security**: Encrypted API keys, JWT authentication, password hashing, audit logging

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, ccxt, python-binance
- **Frontend**: React, TypeScript, Vite, Recharts
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Deploy**: Railway.app

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Binance API credentials

### Installation

1. Clone repository
```bash
git clone https://github.com/gunaex/g-ai-trade.git
cd g-ai-trade


---------------------------------------------------------

How AI Recommendations Work:
1. Automatic Analysis (Every 30 seconds)
Fetches BTC/USDT market data

Analyzes 4 dimensions:

Market (RSI, volume trends, price movement)

Sentiment (X/Twitter sentiment)

Whale (Large holder movements)

Fundamental (Coin strength)

2. Actions Explained:
Action	When It Triggers	What It Means
BUY 🟢	Combined score ≥ 65%	Strong bullish signals - AI recommends buying
SELL 🔴	Combined score ≤ 35%	Strong bearish signals - AI recommends selling
HOLD 🟡	Score between 35-65%	Market is neutral - wait for better opportunity
HALT ⚠️	Error or extreme volatility	Stop trading - something unusual detected
3. Your Current State (HOLD):
Market: 52% - Slightly bullish technical indicators

Sentiment: 50% - Neutral social media sentiment

Whale: 48% - No major whale movements

Fundamental: 50% - Normal fundamentals

→ Combined: 50% = HOLD

4. How to Get BUY/SELL Signals:
The AI will automatically change to BUY or SELL when:

BUY triggers when market shows:

RSI < 30 (oversold)

Strong volume increase

Positive sentiment spike

Whale accumulation

SELL triggers when market shows:

RSI > 70 (overbought)

Volume dropping

Negative sentiment

Whale distribution

5. Test Different Scenarios:
Try changing the trading pair to see different AI analysis:

Select ETH/USDT - Different market conditions

Select BNB/USDT - Different signals

Select XRP/USDT - Your current holding

The AI is already working and updating automatically! It's showing HOLD because current market conditions for BTC are neutral.
-------------------------------------------------------------------------

## 🔒 Security

### Authentication

The system uses **JWT (JSON Web Token)** authentication to protect trading endpoints:

- **Access tokens**: Expire after 30 minutes (automatic refresh)
- **Refresh tokens**: Expire after 7 days
- **Protected endpoints**: All trading and bot management operations require authentication

### Setup Authentication

1. **Install dependencies**:
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

Or use the automated setup script:
```bash
setup-jwt-auth.bat  # Windows
```

2. **Generate JWT secret key**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. **Add to .env**:
```bash
JWT_SECRET_KEY=your-generated-secret-key-here
```

4. **Create first user**:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"SecurePassword123"}'
```

### Protected Endpoints

The following endpoints require authentication (Bearer token):
- POST `/api/trade` - Execute trades
- POST `/api/grid-bot/{symbol}` - Start grid bot
- POST `/api/dca-bot/{symbol}` - Start DCA bot
- POST `/api/auto-bot/*` - Auto bot management

### Documentation

For detailed information about authentication and security:
- **JWT_AUTHENTICATION.md** - Complete JWT implementation guide
- **SECURITY.md** - Security best practices and guidelines
- **JWT_IMPLEMENTATION_SUMMARY.md** - Quick reference for developers

---