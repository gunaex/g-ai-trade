import { TrendingUp, TrendingDown, DollarSign, Activity, Target, Percent, AlertCircle } from 'lucide-react'

interface Performance {
  total_pnl: number
  total_trades: number
  win_trades: number
  loss_trades: number
  win_rate: number
  total_fees: number
  open_position_value: number
}

interface Props {
  performance: Performance
  isRunning: boolean
}

export default function PerformanceDashboard({ performance, isRunning }: Props) {
  const isProfitable = performance.total_pnl >= 0

  return (
    <div className="performance-dashboard">
      <div className="dashboard-header">
        <h2>📊 Performance Metrics</h2>
        <div className="performance-badge">
          {isProfitable ? (
            <span className="badge-profit">� Profitable</span>
          ) : (
            <span className="badge-loss">📉 Loss</span>
          )}
        </div>
      </div>

      {/* Main Metrics */}
      <div className="metrics-grid-large">
        {/* Total P/L */}
        <div className="metric-card-large">
          <div className="metric-icon-large" style={{
            background: isProfitable 
              ? 'linear-gradient(135deg, #10b981, #059669)' 
              : 'linear-gradient(135deg, #ef4444, #dc2626)'
          }}>
            {isProfitable ? <TrendingUp size={40} /> : <TrendingDown size={40} />}
          </div>
          <div className="metric-content-large">
            <div className="metric-label">Total P/L</div>
            <div className={`metric-value-large ${isProfitable ? 'positive' : 'negative'}`}>
              {isProfitable ? '+' : ''}${performance.total_pnl.toFixed(2)}
            </div>
            <div className="metric-sub">
              {performance.total_trades} total trades
            </div>
          </div>
        </div>

        {/* Win Rate */}
        <div className="metric-card-large">
          <div className="metric-icon-large" style={{
            background: 'linear-gradient(135deg, #3b82f6, #2563eb)'
          }}>
            <Target size={40} />
          </div>
          <div className="metric-content-large">
            <div className="metric-label">Win Rate</div>
            <div className="metric-value-large">
              {performance.win_rate.toFixed(1)}%
            </div>
            <div className="metric-sub">
              {performance.win_trades}W / {performance.loss_trades}L
            </div>
          </div>
        </div>

        {/* Total Fees */}
        <div className="metric-card-large">
          <div className="metric-icon-large" style={{
            background: 'linear-gradient(135deg, #f59e0b, #d97706)'
          }}>
            <DollarSign size={40} />
          </div>
          <div className="metric-content-large">
            <div className="metric-label">Total Fees</div>
            <div className="metric-value-large negative">
              ${performance.total_fees.toFixed(2)}
            </div>
            <div className="metric-sub">
              Trading commissions
            </div>
          </div>
        </div>

        {/* Open Position Value */}
        <div className="metric-card-large">
          <div className="metric-icon-large" style={{
            background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)'
          }}>
            <Activity size={40} />
          </div>
          <div className="metric-content-large">
            <div className="metric-label">Open Position</div>
            <div className="metric-value-large">
              ${performance.open_position_value.toFixed(2)}
            </div>
            <div className="metric-sub">
              {performance.open_position_value > 0 ? 'Active' : 'No position'}
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Stats */}
      <div className="stats-section">
        <h3>Detailed Statistics</h3>
        <div className="stats-grid">
          <div className="stat-item">
            <Percent size={20} className="stat-icon" />
            <div className="stat-content">
              <span className="stat-label">Win Trades</span>
              <span className="stat-value success">{performance.win_trades}</span>
            </div>
          </div>

          <div className="stat-item">
            <Percent size={20} className="stat-icon" />
            <div className="stat-content">
              <span className="stat-label">Loss Trades</span>
              <span className="stat-value error">{performance.loss_trades}</span>
            </div>
          </div>

          <div className="stat-item">
            <Activity size={20} className="stat-icon" />
            <div className="stat-content">
              <span className="stat-label">Total Trades</span>
              <span className="stat-value">{performance.total_trades}</span>
            </div>
          </div>

          <div className="stat-item">
            <DollarSign size={20} className="stat-icon" />
            <div className="stat-content">
              <span className="stat-label">Net P/L (After Fees)</span>
              <span className={`stat-value ${isProfitable ? 'success' : 'error'}`}>
                ${(performance.total_pnl - performance.total_fees).toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Breakdown */}
      <div className="breakdown-section">
        <h3>Performance Breakdown</h3>
        <div className="breakdown-bars">
          <div className="breakdown-item">
            <div className="breakdown-header">
              <span>Winning Trades</span>
              <span className="success">{performance.win_trades}</span>
            </div>
            <div className="breakdown-bar">
              <div 
                className="breakdown-fill success"
                style={{ 
                  width: `${(performance.win_trades / Math.max(performance.total_trades, 1)) * 100}%` 
                }}
              />
            </div>
          </div>

          <div className="breakdown-item">
            <div className="breakdown-header">
              <span>Losing Trades</span>
              <span className="error">{performance.loss_trades}</span>
            </div>
            <div className="breakdown-bar">
              <div 
                className="breakdown-fill error"
                style={{ 
                  width: `${(performance.loss_trades / Math.max(performance.total_trades, 1)) * 100}%` 
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {!isRunning && (
        <div className="performance-warning">
          <AlertCircle size={20} />
          <span>Bot is not running. Performance data may be outdated.</span>
        </div>
      )}
    </div>
  )
}
