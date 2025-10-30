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
