import { useState, useEffect } from 'react'
import { TrendingUp, Activity, DollarSign, Percent } from 'lucide-react'
import apiClient, { Portfolio } from '../lib/api'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'

export default function Monitoring() {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchPortfolio()
    const interval = setInterval(fetchPortfolio, 60000) // Update every minute
    return () => clearInterval(interval)
  }, [])

  const fetchPortfolio = async () => {
    try {
      setLoading(true)
      const res = await apiClient.getPortfolio()
      setPortfolio(res.data)
    } catch (err) {
      console.error('Failed to fetch portfolio', err)
    } finally {
      setLoading(false)
    }
  }

  // Generate mock chart data (in production, fetch from backend)
  const generateChartData = () => {
    const data = []
    for (let i = 30; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      data.push({
        date: date.toLocaleDateString(),
        portfolio: 10000 + Math.random() * 2000,
        profit: Math.random() * 500
      })
    }
    return data
  }

  const chartData = generateChartData()

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Performance Monitoring</h1>
        <button onClick={fetchPortfolio} disabled={loading} className="btn btn-primary">
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {portfolio ? (
        <>
          {/* Portfolio Overview Cards */}
          <div className="grid grid-4">
            <div className="stat-card">
              <div className="stat-icon">
                <Activity size={24} />
              </div>
              <div className="stat-content">
                <span className="stat-label">Total Trades</span>
                <span className="stat-value">{portfolio.total_trades}</span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <DollarSign size={24} />
              </div>
              <div className="stat-content">
                <span className="stat-label">Total Invested</span>
                <span className="stat-value">${portfolio.total_invested.toLocaleString()}</span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon stat-icon-success">
                <TrendingUp size={24} />
              </div>
              <div className="stat-content">
                <span className="stat-label">Profit/Loss</span>
                <span className={`stat-value ${portfolio.profit_loss >= 0 ? 'text-success' : 'text-error'}`}>
                  {portfolio.profit_loss >= 0 ? '+' : ''}${portfolio.profit_loss.toLocaleString()}
                </span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon stat-icon-primary">
                <Percent size={24} />
              </div>
              <div className="stat-content">
                <span className="stat-label">ROI</span>
                <span className={`stat-value ${portfolio.roi_percent >= 0 ? 'text-success' : 'text-error'}`}>
                  {portfolio.roi_percent >= 0 ? '+' : ''}{portfolio.roi_percent}%
                </span>
              </div>
            </div>
          </div>

          {/* Performance Chart */}
          <div className="card">
            <h3>Portfolio Performance (Last 30 Days)</h3>
            <div style={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="date" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      border: '1px solid #334155',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="portfolio"
                    stroke="#10b981"
                    strokeWidth={2}
                    name="Portfolio Value"
                  />
                  <Line
                    type="monotone"
                    dataKey="profit"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    name="Profit"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Active Bots */}
          <div className="card">
            <h3>Active Trading Bots</h3>
            <div className="bot-list">
              <div className="bot-item">
                <div className="bot-info">
                  <strong>Grid Bot - BTCUSDT</strong>
                  <span className="text-secondary">25 levels • Running for 2 days</span>
                </div>
                <div className="bot-status">
                  <span className="status-badge status-success">Active</span>
                  <span className="text-success">+3.2%</span>
                </div>
              </div>
              
              <div className="bot-item">
                <div className="bot-info">
                  <strong>DCA Bot - ETHUSDT</strong>
                  <span className="text-secondary">$50/week • 8/12 periods completed</span>
                </div>
                <div className="bot-status">
                  <span className="status-badge status-success">Active</span>
                  <span className="text-success">+1.8%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Trades */}
          <div className="card">
            <h3>Recent Trades</h3>
            <div className="table-container">
              <table className="trade-table">
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
                  <tr>
                    <td>{new Date().toLocaleString()}</td>
                    <td>BTCUSDT</td>
                    <td><span className="badge badge-success">BUY</span></td>
                    <td>0.05</td>
                    <td>$68,500</td>
                    <td><span className="status-badge status-success">Filled</span></td>
                  </tr>
                  <tr>
                    <td>{new Date().toLocaleString()}</td>
                    <td>ETHUSDT</td>
                    <td><span className="badge badge-error">SELL</span></td>
                    <td>1.2</td>
                    <td>$3,450</td>
                    <td><span className="status-badge status-success">Filled</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : (
        <div className="loading-state">Loading portfolio data...</div>
      )}
    </div>
  )
}
