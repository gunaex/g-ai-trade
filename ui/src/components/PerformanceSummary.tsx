import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Trophy, AlertCircle, Activity, Percent, DollarSign } from 'lucide-react'
import apiClient, { PerformanceData } from '../lib/api'

interface Props {
  period: 'today' | 'week' | 'month' | 'year'
}

export default function PerformanceSummary({ period }: Props) {
  const [performance, setPerformance] = useState<PerformanceData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchPerformance()
    const interval = setInterval(fetchPerformance, 60000) // Update every minute
    return () => clearInterval(interval)
  }, [period])

  const fetchPerformance = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiClient.getPerformance(period)
      setPerformance(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch performance data')
      console.error('Performance fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  // Skeleton Loader Component
  const SkeletonLoader = () => (
    <div className="card">
      <div className="skeleton-header">
        <div className="skeleton-title"></div>
      </div>
      <div className="skeleton-stats">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="skeleton-stat">
            <div className="skeleton-label"></div>
            <div className="skeleton-value"></div>
          </div>
        ))}
      </div>
    </div>
  )

  if (loading && !performance) {
    return <SkeletonLoader />
  }

  if (error) {
    return (
      <div className="card">
        <div className="error-state">
          <AlertCircle size={32} />
          <p>Failed to load performance data</p>
          <button onClick={fetchPerformance} className="btn btn-secondary">
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!performance) {
    return (
      <div className="card">
        <div className="error-state">
          <p>Failed to load performance data</p>
        </div>
      </div>
    )
  }

  if (!performance.has_data) {
    return (
      <div className="card">
        <div className="no-data-state">
          <div className="no-data-icon">📊</div>
          <h4>No trading data</h4>
          <p>Start trading to see your performance metrics</p>
        </div>
      </div>
    )
  }

  const periodLabel = {
    today: 'Today',
    week: 'This Week',
    month: 'This Month',
    year: 'This Year'
  }[period]

  return (
    <div className="card performance-card">
      <div className="card-header">
        <h3>
          <Activity size={20} />
          Performance - {periodLabel}
        </h3>
        <button onClick={fetchPerformance} disabled={loading} className="btn btn-secondary btn-sm">
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      <div className="performance-stats">
        <div className="stat-card">
          <div className="stat-icon">
            <DollarSign size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Profit/Loss</span>
            <span className={`stat-value ${performance.profit_loss >= 0 ? 'text-success' : 'text-error'}`}>
              {performance.profit_loss >= 0 ? '+' : ''}${performance.profit_loss.toLocaleString()}
            </span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <Percent size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">P/L %</span>
            <span className={`stat-value ${performance.profit_loss_percent >= 0 ? 'text-success' : 'text-error'}`}>
              {performance.profit_loss_percent >= 0 ? '+' : ''}
              {performance.profit_loss_percent.toFixed(2)}%
            </span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <Activity size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Total Trades</span>
            <span className="stat-value">{performance.total_trades}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-success">
            <Trophy size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Win Rate</span>
            <span className="stat-value">{performance.win_rate.toFixed(1)}%</span>
          </div>
        </div>
      </div>

      <div className="performance-details">
        <div className="detail-item">
          <TrendingUp size={18} className="text-success" />
          <div className="detail-content">
            <span className="detail-label">Best Trade</span>
            <span className="detail-value text-success">
              +${performance.best_trade.toLocaleString()}
            </span>
          </div>
        </div>

        <div className="detail-item">
          <TrendingDown size={18} className="text-error" />
          <div className="detail-content">
            <span className="detail-label">Worst Trade</span>
            <span className="detail-value text-error">
              {performance.worst_trade >= 0 ? '+' : ''}${performance.worst_trade.toLocaleString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

