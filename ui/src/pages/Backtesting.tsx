import { useState } from 'react'
import { Play, Download, TrendingUp, TrendingDown, Activity, DollarSign } from 'lucide-react'
import apiClient, { BacktestConfig, BacktestResult } from '../lib/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import '../styles/backtest.css'


export default function Backtesting() {
  const [config, setConfig] = useState<BacktestConfig>({
    symbol: 'BTC/USDT',
    timeframe: '5m',
    days: 30,
    initial_capital: 10000,
    position_size_percent: 0.95
  })
  
  const [result, setResult] = useState<BacktestResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const runBacktest = async () => {
    try {
      setLoading(true)
      setError(null)

      const resp = await apiClient.runBacktest(config)
      setResult(resp.data)
    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'Failed to run backtest'
      setError(message)
      console.error('Backtest error:', err)
    } finally {
      setLoading(false)
    }
  }
  const loadPreset = (preset: any) => {
    setConfig({
      symbol: preset.symbol,
      timeframe: preset.timeframe,
      days: preset.days,
      initial_capital: preset.initial_capital,
      position_size_percent: 0.95
    })
  }

  const exportResults = () => {
    if (!result) return
    
    const dataStr = JSON.stringify(result, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `backtest_${config.symbol}_${Date.now()}.json`
    link.click()
  }

  return (
    <div className="backtest-page">
      <div className="backtest-header">
        <div>
          <h1>Strategy Backtesting</h1>
          <p>Test your AI trading strategy with historical data</p>
        </div>
      </div>

      {/* Configuration Panel */}
      <div className="backtest-config">
        <h2>Configuration</h2>
        
        <div className="config-grid">
          <div className="form-group">
            <label>Symbol</label>
            <select 
              value={config.symbol}
              onChange={(e) => setConfig({...config, symbol: e.target.value})}
            >
              <option value="BTC/USDT">BTC/USDT</option>
              <option value="ETH/USDT">ETH/USDT</option>
              <option value="BNB/USDT">BNB/USDT</option>
            </select>
          </div>

          <div className="form-group">
            <label>Timeframe</label>
            <select 
              value={config.timeframe}
              onChange={(e) => setConfig({...config, timeframe: e.target.value})}
            >
              <option value="1m">1 minute</option>
              <option value="5m">5 minutes</option>
              <option value="15m">15 minutes</option>
              <option value="1h">1 hour</option>
              <option value="4h">4 hours</option>
              <option value="1d">1 day</option>
            </select>
          </div>

          <div className="form-group">
            <label>Days Back</label>
            <input 
              type="number"
              value={config.days}
              onChange={(e) => setConfig({...config, days: parseInt(e.target.value)})}
              min={1}
              max={365}
            />
          </div>

          <div className="form-group">
            <label>Initial Capital ($)</label>
            <input 
              type="number"
              value={config.initial_capital}
              onChange={(e) => setConfig({...config, initial_capital: parseFloat(e.target.value)})}
              min={100}
              step={100}
            />
          </div>
        </div>

        {/* Presets */}
        <div className="presets">
          <h3>Quick Presets</h3>
          <div className="preset-buttons">
            <button onClick={() => loadPreset({ symbol: 'BTC/USDT', timeframe: '5m', days: 7, initial_capital: 10000 })}>
              Quick (7d)
            </button>
            <button onClick={() => loadPreset({ symbol: 'BTC/USDT', timeframe: '15m', days: 30, initial_capital: 10000 })}>
              Short (30d)
            </button>
            <button onClick={() => loadPreset({ symbol: 'BTC/USDT', timeframe: '1h', days: 90, initial_capital: 10000 })}>
              Medium (90d)
            </button>
            <button onClick={() => loadPreset({ symbol: 'BTC/USDT', timeframe: '4h', days: 180, initial_capital: 10000 })}>
              Long (180d)
            </button>
          </div>
        </div>

        {/* Run Button */}
        <button
          className="btn btn--primary btn--lg run-button"
          onClick={runBacktest}
          disabled={loading}
        >
          {loading ? (
            <>
              <Activity size={20} className="spinner" />
              Running Backtest...
            </>
          ) : (
            <>
              <Play size={20} />
              Run Backtest
            </>
          )}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <p>{error}</p>
        </div>
      )}

      {/* Results Display */}
      {result && result.success && (
        <div className="backtest-results">
          {/* Metrics Summary */}
          <div className="results-header">
            <h2>Backtest Results</h2>
            <button className="btn btn--outline" onClick={exportResults}>
              <Download size={18} />
              Export JSON
            </button>
          </div>

          <div className="metrics-grid">
            {/* Total Return */}
            <div className="metric-card">
              <div className="metric-icon" style={{ 
                background: result.metrics.total_return_percent >= 0 
                  ? 'rgba(var(--color-success-rgb), 0.15)' 
                  : 'rgba(var(--color-error-rgb), 0.15)'
              }}>
                {result.metrics.total_return_percent >= 0 ? (
                  <TrendingUp size={32} style={{ color: 'var(--color-success)' }} />
                ) : (
                  <TrendingDown size={32} style={{ color: 'var(--color-error)' }} />
                )}
              </div>
              <div className="metric-content">
                <div className="metric-label">Total Return</div>
                <div className={`metric-value ${result.metrics.total_return_percent >= 0 ? 'positive' : 'negative'}`}>
                  {result.metrics.total_return_percent >= 0 ? '+' : ''}
                  {result.metrics.total_return_percent.toFixed(2)}%
                </div>
                <div className="metric-sub">
                  ${result.metrics.final_equity.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </div>
              </div>
            </div>

            {/* Max Drawdown */}
            <div className="metric-card">
              <div className="metric-icon" style={{ background: 'rgba(var(--color-error-rgb), 0.15)' }}>
                <TrendingDown size={32} style={{ color: 'var(--color-error)' }} />
              </div>
              <div className="metric-content">
                <div className="metric-label">Max Drawdown</div>
                <div className="metric-value negative">
                  {result.metrics.max_drawdown_percent.toFixed(2)}%
                </div>
                <div className="metric-sub">Risk metric</div>
              </div>
            </div>

            {/* Sharpe Ratio */}
            <div className="metric-card">
              <div className="metric-icon" style={{ background: 'rgba(var(--color-info-rgb), 0.15)' }}>
                <Activity size={32} style={{ color: 'var(--color-info)' }} />
              </div>
              <div className="metric-content">
                <div className="metric-label">Sharpe Ratio</div>
                <div className="metric-value">
                  {result.metrics.sharpe_ratio.toFixed(2)}
                </div>
                <div className="metric-sub">
                  Sortino: {result.metrics.sortino_ratio.toFixed(2)}
                </div>
              </div>
            </div>

            {/* Win Rate */}
            <div className="metric-card">
              <div className="metric-icon" style={{ background: 'rgba(var(--color-success-rgb), 0.15)' }}>
                <DollarSign size={32} style={{ color: 'var(--color-success)' }} />
              </div>
              <div className="metric-content">
                <div className="metric-label">Win Rate</div>
                <div className="metric-value">
                  {result.metrics.win_rate_percent.toFixed(1)}%
                </div>
                <div className="metric-sub">
                  {result.metrics.completed_rounds} rounds
                </div>
              </div>
            </div>

            {/* Profit Factor */}
            <div className="metric-card">
              <div className="metric-icon" style={{ background: 'rgba(var(--color-info-rgb), 0.15)' }}>
                <Activity size={32} style={{ color: 'var(--color-info)' }} />
              </div>
              <div className="metric-content">
                <div className="metric-label">Profit Factor</div>
                <div className="metric-value">
                  {isFinite(result.metrics.profit_factor) ? result.metrics.profit_factor.toFixed(2) : '∞'}
                </div>
                <div className="metric-sub">
                  {result.metrics.total_trades} total trades
                </div>
              </div>
            </div>
          </div>

          {/* Equity Curve Chart */}
          <div className="chart-section">
            <h3>Equity Curve</h3>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={result.equity_curve}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis 
                  dataKey="timestamp" 
                  stroke="var(--color-text-secondary)"
                  tick={{ fill: 'var(--color-text-secondary)' }}
                />
                <YAxis 
                  stroke="var(--color-text-secondary)"
                  tick={{ fill: 'var(--color-text-secondary)' }}
                />
                <Tooltip 
                  contentStyle={{ 
                    background: 'var(--color-surface)', 
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-base)'
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="equity" 
                  stroke="var(--color-primary)" 
                  strokeWidth={2}
                  dot={false}
                  name="Portfolio Value ($)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Trade Log */}
          <div className="trades-section">
            <h3>Recent Trades ({result.trades.length})</h3>
            <div className="trades-table-wrapper">
              <table className="trades-table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Symbol</th>
                    <th>Side</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Commission</th>
                    <th>P/L</th>
                  </tr>
                </thead>
                <tbody>
                  {result.trades.map((trade, idx) => (
                    <tr key={idx}>
                      <td>{new Date(trade.timestamp).toLocaleString()}</td>
                      <td>{trade.symbol}</td>
                      <td>
                        <span className={`trade-side ${trade.direction.toLowerCase()}`}>
                          {trade.direction}
                        </span>
                      </td>
                      <td>{trade.quantity.toFixed(6)}</td>
                      <td>${trade.price.toFixed(2)}</td>
                      <td>${trade.commission.toFixed(2)}</td>
                      <td className={trade.pnl >= 0 ? 'positive' : 'negative'}>
                        {trade.pnl !== null ? `$${trade.pnl.toFixed(2)}` : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
