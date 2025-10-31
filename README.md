# G-AI-TRADE v1.0

Full-Stack AI-Powered Crypto Trading System

## Features

- **AI Decision Engine**: 4D analysis (Market, Fundamental, Sentiment, On-Chain)
- **Grid Trading Bot**: Automated grid trading with dynamic ATR
- **DCA Bot**: Dollar-cost averaging with customizable intervals
- **Real-time Market Data**: Live prices from Binance
- **Risk Management**: Max drawdown, correlation filters, position sizing
- **Security**: Encrypted API keys, audit logging

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