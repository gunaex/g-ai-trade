import { Settings, DollarSign, Target, Shield, TrendingUp } from 'lucide-react'

interface Config {
  id: number
  name: string
  symbol: string
  budget: number
  risk_level: string
  min_confidence: number
  position_size_ratio: number
  max_daily_loss: number
  is_active: boolean
}

interface Props {
  config: Config
}

export default function ConfigDisplay({ config }: Props) {
  const getRiskColor = (level: string) => {
    switch (level) {
      case 'conservative':
        return '#10b981'
      case 'aggressive':
        return '#ef4444'
      default:
        return '#3b82f6'
    }
  }

  const getRiskLabel = (level: string) => {
    return level.charAt(0).toUpperCase() + level.slice(1)
  }

  return (
    <div className="config-display">
      <div className="config-header">
        <Settings size={24} />
        <h2>Current Configuration</h2>
      </div>

      <div className="config-grid">
        {/* Bot Name & Symbol */}
        <div className="config-card">
          <div className="config-icon" style={{ background: 'linear-gradient(135deg, #3b82f6, #2563eb)' }}>
            <TrendingUp size={24} />
          </div>
          <div className="config-content">
            <div className="config-label">Trading Pair</div>
            <div className="config-value">{config.symbol}</div>
            <div className="config-sub">{config.name}</div>
          </div>
        </div>

        {/* Budget */}
        <div className="config-card">
          <div className="config-icon" style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }}>
            <DollarSign size={24} />
          </div>
          <div className="config-content">
            <div className="config-label">Budget</div>
            <div className="config-value">${config.budget.toLocaleString()}</div>
            <div className="config-sub">Total capital</div>
          </div>
        </div>

        {/* Risk Level */}
        <div className="config-card">
          <div className="config-icon" style={{ background: `linear-gradient(135deg, ${getRiskColor(config.risk_level)}, ${getRiskColor(config.risk_level)}dd)` }}>
            <Shield size={24} />
          </div>
          <div className="config-content">
            <div className="config-label">Risk Level</div>
            <div className="config-value">{getRiskLabel(config.risk_level)}</div>
            <div className="config-sub">Max loss: {config.max_daily_loss}%/day</div>
          </div>
        </div>

        {/* AI Confidence */}
        <div className="config-card">
          <div className="config-icon" style={{ background: 'linear-gradient(135deg, #8b5cf6, #7c3aed)' }}>
            <Target size={24} />
          </div>
          <div className="config-content">
            <div className="config-label">Min Confidence</div>
            <div className="config-value">{(config.min_confidence * 100).toFixed(0)}%</div>
            <div className="config-sub">AI decision threshold</div>
          </div>
        </div>
      </div>

      {/* Advanced Settings */}
      <div className="config-details">
        <h3>Advanced Settings</h3>
        <div className="details-grid">
          <div className="detail-row">
            <span className="detail-label">Position Size:</span>
            <span className="detail-value">{(config.position_size_ratio * 100).toFixed(0)}% of budget</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Max Daily Loss:</span>
            <span className="detail-value error">{config.max_daily_loss}%</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Status:</span>
            <span className={`detail-value ${config.is_active ? 'success' : 'inactive'}`}>
              {config.is_active ? '✓ Active' : '○ Inactive'}
            </span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Config ID:</span>
            <span className="detail-value">#{config.id}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
