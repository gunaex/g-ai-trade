import { useState, useEffect } from 'react'
import { 
  TrendingUp, TrendingDown, Activity, DollarSign, Percent, 
  Clock, CheckCircle, XCircle, Target, Moon, Sun, Bell 
} from 'lucide-react'
import apiClient, { PerformanceData, RecentTrade } from '../lib/api'
import { useToast } from '../hooks/useToast'
import { useDarkMode } from '../hooks/useDarkMode'

export default function Monitoring() {
  const [period, setPeriod] = useState<'today' | 'week' | 'month' | 'year'>('today')
  const [performance, setPerformance] = useState<PerformanceData | null>(null)
  const [recentTrades, setRecentTrades] = useState<RecentTrade[]>([])
  const [loading, setLoading] = useState(false)
  
  const { showToast, ToastContainer } = useToast()
  const { darkMode, toggleDarkMode } = useDarkMode()

  useEffect(() => {
    fetchPerformance()
    fetchRecentTrades()
    
    const interval = setInterval(() => {
      fetchPerformance()
      fetchRecentTrades()
    }, 60000) // Update every minute
    
    return () => clearInterval(interval)
  }, [period])

  const fetchPerformance = async () => {
    try {
      setLoading(true)
      const response = await apiClient.getPerformance(period)
      setPerformance(response.data)
      
      // Show notification if new data
      if (response.data.has_data && response.data.total_trades > 0) {
        // Check if performance improved
        if (response.data.profit_loss > 0) {
          showToast(`Performance updated: +$${response.data.profit_loss.toFixed(2)}`, 'success')
        }
      }
    } catch (error: any) {
      console.error('Failed to fetch performance:', error)
      showToast('Failed to load performance data', 'error')
    } finally {
      setLoading(false)
    }
  }

  const fetchRecentTrades = async () => {
    try {
      const response = await apiClient.getRecentTrades(10)
      setRecentTrades(response.data.trades)
    } catch (error) {
      console.error('Failed to fetch recent trades:', error)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="monitoring-page">
      <ToastContainer />
      
      {/* Header */}
      <div className="monitoring-header">
        <div>
          <h1>Performance Monitor</h1>
          <p>Real-time trading performance and analytics</p>
        </div>
        
        <button 
          className="dark-mode-toggle"
          onClick={toggleDarkMode}
          title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>

      {/* Period Selector */}
      <div className="period-selector">
        {(['today', 'week', 'month', 'year'] as const).map((p) => (
          <button
            key={p}
            className={`period-btn ${period === p ? 'active' : ''}`}
            onClick={() => setPeriod(p)}
          >
            {p.charAt(0).toUpperCase() + p.slice(1)}
          </button>
        ))}
      </div>

      {/* Performance Summary Card */}
      <div className="performance-card">
        {loading ? (
          <SkeletonLoader />
        ) : performance ? (
          performance.has_data ? (
            <>
              <div className="performance-stats-horizontal">
                {/* P/L */}
                <div className="stat-item">
                  <div className="stat-icon" style={{ 
                    background: performance.profit_loss >= 0 
                      ? 'rgba(var(--color-success-rgb), 0.15)' 
                      : 'rgba(var(--color-error-rgb), 0.15)'
                  }}>
                    {performance.profit_loss >= 0 ? (
                      <TrendingUp size={24} style={{ color: 'var(--color-success)' }} />
                    ) : (
                      <TrendingDown size={24} style={{ color: 'var(--color-error)' }} />
                    )}
                  </div>
                  <div className="stat-content">
                    <div className="stat-label">Profit/Loss</div>
                    <div className={`stat-value ${performance.profit_loss >= 0 ? 'positive' : 'negative'}`}>
                      {formatCurrency(performance.profit_loss)}
                    </div>
                    <div className="stat-sub">
                      {performance.profit_loss_percent >= 0 ? '+' : ''}
                      {performance.profit_loss_percent.toFixed(2)}%
                    </div>
                  </div>
                </div>

                {/* Total Trades */}
                <div className="stat-item">
                  <div className="stat-icon" style={{ background: 'rgba(var(--color-info-rgb), 0.15)' }}>
                    <Activity size={24} style={{ color: 'var(--color-info)' }} />
                  </div>
                  <div className="stat-content">
                    <div className="stat-label">Total Trades</div>
                    <div className="stat-value">{performance.total_trades}</div>
                    <div className="stat-sub">{performance.completed_rounds} rounds</div>
                  </div>
                </div>

                {/* Win Rate */}
                <div className="stat-item">
                  <div className="stat-icon" style={{ background: 'rgba(var(--color-success-rgb), 0.15)' }}>
                    <Target size={24} style={{ color: 'var(--color-success)' }} />
                  </div>
                  <div className="stat-content">
                    <div className="stat-label">Win Rate</div>
                    <div className="stat-value">{performance.win_rate.toFixed(1)}%</div>
                    <div className="stat-sub">
                      {Math.round(performance.completed_rounds * performance.win_rate / 100)} wins
                    </div>
                  </div>
                </div>

                {/* Best Trade */}
                <div className="stat-item">
                  <div className="stat-icon" style={{ background: 'rgba(var(--color-success-rgb), 0.15)' }}>
                    <CheckCircle size={24} style={{ color: 'var(--color-success)' }} />
                  </div>
                  <div className="stat-content">
                    <div className="stat-label">Best Trade</div>
                    <div className="stat-value positive">{formatCurrency(performance.best_trade)}</div>
                    <div className="stat-sub">
                      Worst: {formatCurrency(performance.worst_trade)}
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="no-data-state">
              <div className="no-data-icon">
                <Activity size={48} />
              </div>
              <h3>No Trading Data</h3>
              <p>{performance.message || 'Start trading to see your performance metrics'}</p>
              <p className="no-data-hint">Execute trades on the Trade page to populate this dashboard</p>
            </div>
          )
        ) : (
          <div className="error-state">
            <XCircle size={48} />
            <p>Failed to load performance data</p>
          </div>
        )}
      </div>

      {/* Recent Trades Table */}
      <div className="recent-trades-section">
        <div className="section-header">
          <h2>
            <Clock size={20} />
            Recent Trades
          </h2>
          <span className="trade-count">{recentTrades.length} trades</span>
        </div>

        {recentTrades.length > 0 ? (
          <div className="trades-table-wrapper">
            <table className="trades-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Symbol</th>
                  <th>Side</th>
                  <th>Amount</th>
                  <th>Price</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentTrades.map((trade) => (
                  <tr key={trade.id} className="trade-row">
                    <td className="trade-time">{formatDate(trade.timestamp)}</td>
                    <td className="trade-symbol">{trade.symbol}</td>
                    <td>
                      <span className={`trade-side ${trade.side.toLowerCase()}`}>
                        {trade.side}
                      </span>
                    </td>
                    <td>{trade.amount.toFixed(6)}</td>
                    <td>{formatCurrency(trade.price)}</td>
                    <td>
                      <span className={`trade-status ${trade.status}`}>
                        {trade.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="no-trades-message">
            <p>No recent trades found</p>
          </div>
        )}
      </div>
    </div>
  )
}

// Skeleton Loader Component
function SkeletonLoader() {
  return (
    <div className="skeleton-loader">
      <div className="skeleton-stats-horizontal">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="skeleton-stat">
            <div className="skeleton-icon"></div>
            <div className="skeleton-content">
              <div className="skeleton-line short"></div>
              <div className="skeleton-line long"></div>
              <div className="skeleton-line short"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
