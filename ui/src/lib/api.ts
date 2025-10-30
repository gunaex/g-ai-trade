import axios from 'axios'

const API_BASE = import.meta.env.PROD ? '/api' : 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface AIDecision {
  action: 'BUY' | 'SELL' | 'HOLD' | 'HALT'
  principle: string
  predicted_pl_percent: number
  confidence: number
  scores: {
    market: number
    fundamental: number
    sentiment: number
    whale: number
  }
  timestamp: string
  symbol: string
}

export interface TradeRequest {
  symbol: string
  side: 'BUY' | 'SELL'
  amount: number
  price?: number
}

export interface GridBotConfig {
  symbol: string
  lower_price: number
  upper_price: number
  grid_levels: number
  amount_per_grid: number
}

export interface DCABotConfig {
  symbol: string
  amount_per_period: number
  interval_days: number
  total_periods: number
}

export interface MarketData {
  symbol: string
  price: number
  change_24h: number
  volume_24h: number
  high_24h: number
  low_24h: number
  ohlcv: number[][]
  currency: string
}

export interface WhaleData {
  symbol: string
  movements: Array<{
    timestamp: string
    amount: number
    type: string
    wallet: string
    usd_value: number
  }>
  whale_score: number
  net_flow: number
  interpretation: string
}

export interface Portfolio {
  total_trades: number
  total_invested: number
  total_returns: number
  profit_loss: number
  roi_percent: number
}

// API Methods
export const apiClient = {
  // Health Check
  healthCheck: () => api.get('/health'),

  // AI Decision
  getDecision: (symbol: string, currency: string = 'USD') =>
    api.get<AIDecision>(`/decision/${symbol}?currency=${currency}`),

  // Trading
  executeTrade: (trade: TradeRequest) =>
    api.post('/trade', trade),

  // Grid Bot
  startGridBot: (config: GridBotConfig) =>
    api.post(`/grid-bot/${config.symbol}`, config),

  // DCA Bot
  startDCABot: (config: DCABotConfig) =>
    api.post(`/dca-bot/${config.symbol}`, config),

  // Market Data
  getMarketData: (symbol: string, currency: string = 'USD') =>
    api.get<MarketData>(`/market/${symbol}?currency=${currency}`),

  // Whale Tracking
  getWhaleData: (symbol: string) =>
    api.get<WhaleData>(`/whale/${symbol}`),

  // Portfolio
  getPortfolio: () =>
    api.get<Portfolio>('/portfolio'),
}

export default apiClient
