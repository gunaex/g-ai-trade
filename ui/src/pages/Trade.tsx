import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-react'
import apiClient, { AIDecision, MarketData } from '../lib/api'
import Chart from '../components/Chart'

export default function Trade() {
  const [symbol, setSymbol] = useState('BTCUSDT')
  const [currency, setCurrency] = useState<'USD' | 'THB'>('USD')
  const [amount, setAmount] = useState(0.01)
  const [decision, setDecision] = useState<AIDecision | null>(null)
  const [marketData, setMarketData] = useState<MarketData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [symbol, currency])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [decisionRes, marketRes] = await Promise.all([
        apiClient.getDecision(symbol, currency),
        apiClient.getMarketData(symbol, currency)
      ])
      
      setDecision(decisionRes.data)
      setMarketData(marketRes.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }

  const handleTrade = async (side: 'BUY' | 'SELL') => {
    if (!marketData) return
    
    try {
      setLoading(true)
      await apiClient.executeTrade({
        symbol,
        side,
        amount,
        price: marketData.price
      })
      alert(`${side} order executed successfully!`)
      fetchData()
    } catch (err: any) {
      alert(`Error: ${err.response?.data?.detail || 'Trade failed'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleGridBot = async () => {
    if (!marketData) return
    
    const lowerPrice = marketData.price * 0.95
    const upperPrice = marketData.price * 1.05
    
    try {
      setLoading(true)
      await apiClient.startGridBot({
        symbol,
        lower_price: lowerPrice,
        upper_price: upperPrice,
        grid_levels: 25,
        amount_per_grid: 50
      })
      alert('Grid Bot started successfully!')
    } catch (err: any) {
      alert(`Error: ${err.response?.data?.detail || 'Failed to start Grid Bot'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDCABot = async () => {
    try {
      setLoading(true)
      await apiClient.startDCABot({
        symbol,
        amount_per_period: 50,
        interval_days: 7,
        total_periods: 12
      })
      alert('DCA Bot started successfully!')
    } catch (err: any) {
      alert(`Error: ${err.response?.data?.detail || 'Failed to start DCA Bot'}`)
    } finally {
      setLoading(false)
    }
  }

  const getActionIcon = () => {
    if (!decision) return <Minus />
    switch (decision.action) {
      case 'BUY': return <TrendingUp className="text-success" />
      case 'SELL': return <TrendingDown className="text-error" />
      case 'HALT': return <AlertTriangle className="text-warning" />
      default: return <Minus className="text-secondary" />
    }
  }

  const getActionClass = () => {
    if (!decision) return 'decision-card'
    return `decision-card decision-${decision.action.toLowerCase()}`
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>AI Trading Dashboard</h1>
        <div className="header-controls">
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="BTCUSDT"
            className="input symbol-input"
          />
          <select
            value={currency}
            onChange={(e) => setCurrency(e.target.value as 'USD' | 'THB')}
            className="select"
          >
            <option value="USD">USD</option>
            <option value="THB">THB</option>
          </select>
          <button onClick={fetchData} disabled={loading} className="btn btn-primary">
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-2">
        {/* AI Decision Card */}
        <div className={getActionClass()}>
          <div className="card-header">
            <h3>AI Recommendation</h3>
            {getActionIcon()}
          </div>
          
          {decision ? (
            <>
              <div className="decision-action">
                <span className="action-label">Action:</span>
                <span className={`action-value action-${decision.action.toLowerCase()}`}>
                  {decision.action}
                </span>
              </div>
              
              <div className="decision-principle">
                <strong>Principle:</strong>
                <p>{decision.principle}</p>
              </div>
              
              <div className="decision-metrics">
                <div className="metric">
                  <span>Predicted P/L</span>
                  <strong className={decision.predicted_pl_percent >= 0 ? 'text-success' : 'text-error'}>
                    {decision.predicted_pl_percent >= 0 ? '+' : ''}
                    {decision.predicted_pl_percent}%
                  </strong>
                </div>
                <div className="metric">
                  <span>Confidence</span>
                  <strong>{(decision.confidence * 100).toFixed(0)}%</strong>
                </div>
              </div>
              
              <div className="scores-grid">
                <div className="score-item">
                  <span>Market</span>
                  <div className="score-bar">
                    <div className="score-fill" style={{width: `${decision.scores.market * 100}%`}} />
                  </div>
                  <strong>{(decision.scores.market * 100).toFixed(0)}%</strong>
                </div>
                <div className="score-item">
                  <span>Sentiment</span>
                  <div className="score-bar">
                    <div className="score-fill" style={{width: `${decision.scores.sentiment * 100}%`}} />
                  </div>
                  <strong>{(decision.scores.sentiment * 100).toFixed(0)}%</strong>
                </div>
                <div className="score-item">
                  <span>Whale</span>
                  <div className="score-bar">
                    <div className="score-fill" style={{width: `${decision.scores.whale * 100}%`}} />
                  </div>
                  <strong>{(decision.scores.whale * 100).toFixed(0)}%</strong>
                </div>
                <div className="score-item">
                  <span>Fundamental</span>
                  <div className="score-bar">
                    <div className="score-fill" style={{width: `${decision.scores.fundamental * 100}%`}} />
                  </div>
                  <strong>{(decision.scores.fundamental * 100).toFixed(0)}%</strong>
                </div>
              </div>
            </>
          ) : (
            <div className="loading-state">Loading AI analysis...</div>
          )}
        </div>

        {/* Market Data Card */}
        <div className="card">
          <div className="card-header">
            <h3>Market Data</h3>
            <span className="text-secondary">{symbol}</span>
          </div>
          
          {marketData ? (
            <>
              <div className="price-display">
                <span className="price-label">Current Price</span>
                <span className="price-value">
                  {currency === 'THB' ? '฿' : '$'}
                  {marketData.price.toLocaleString()}
                </span>
                <span className={`price-change ${marketData.change_24h >= 0 ? 'positive' : 'negative'}`}>
                  {marketData.change_24h >= 0 ? '+' : ''}
                  {marketData.change_24h.toFixed(2)}%
                </span>
              </div>
              
              <div className="market-stats">
                <div className="stat">
                  <span>24h High</span>
                  <strong>{currency === 'THB' ? '฿' : '$'}{marketData.high_24h.toLocaleString()}</strong>
                </div>
                <div className="stat">
                  <span>24h Low</span>
                  <strong>{currency === 'THB' ? '฿' : '$'}{marketData.low_24h.toLocaleString()}</strong>
                </div>
                <div className="stat">
                  <span>24h Volume</span>
                  <strong>{(marketData.volume_24h / 1000000).toFixed(2)}M</strong>
                </div>
              </div>
            </>
          ) : (
            <div className="loading-state">Loading market data...</div>
          )}
        </div>
      </div>

      {/* Trading Controls */}
      <div className="card">
        <h3>Manual Trading</h3>
        <div className="trading-controls">
          <div className="form-group">
            <label>Amount</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(parseFloat(e.target.value))}
              step="0.001"
              min="0.001"
              className="input"
            />
          </div>
          
          <div className="button-group">
            <button
              onClick={() => handleTrade('BUY')}
              disabled={loading || !marketData}
              className="btn btn-success"
            >
              Buy {symbol.replace('USDT', '')}
            </button>
            <button
              onClick={() => handleTrade('SELL')}
              disabled={loading || !marketData}
              className="btn btn-error"
            >
              Sell {symbol.replace('USDT', '')}
            </button>
          </div>
        </div>
      </div>

      {/* Bot Controls */}
      <div className="grid grid-2">
        <div className="card">
          <h3>Grid Bot</h3>
          <p className="text-secondary">Automated grid trading with 25 levels, 5% range</p>
          <button
            onClick={handleGridBot}
            disabled={loading || !marketData}
            className="btn btn-primary btn-full"
          >
            Start Grid Bot
          </button>
        </div>
        
        <div className="card">
          <h3>DCA Bot</h3>
          <p className="text-secondary">Auto-buy $50 every 7 days (12 periods)</p>
          <button
            onClick={handleDCABot}
            disabled={loading}
            className="btn btn-primary btn-full"
          >
            Start DCA Bot
          </button>
        </div>
      </div>

      {/* Chart */}
      {marketData && <Chart data={marketData.ohlcv} symbol={symbol} />}
    </div>
  )
}
