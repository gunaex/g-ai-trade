import { Brain, Cpu, Network, MessageSquare, Eye, BookOpen, Activity } from 'lucide-react'

interface AIModule {
  name: string
  icon: React.ReactNode
  percentage: number
  color: string
  description: string
}

interface Props {
  modules: {
    brain: number
    decision: number
    ml: number
    network: number
    nlp: number
    perception: number
    learning: number
  } | undefined
  isRunning: boolean
}

export default function AIStatusMonitor({ modules, isRunning }: Props) {
  const safeModules = modules ?? {
    brain: 0,
    decision: 0,
    ml: 0,
    network: 0,
    nlp: 0,
    perception: 0,
    learning: 0,
  }
  const aiModules: AIModule[] = [
    {
      name: 'Brain',
      icon: <Brain size={32} />,
      percentage: safeModules.brain,
      color: '#3b82f6',
      description: 'Core Decision Engine'
    },
    {
      name: 'Decision',
      icon: <Activity size={32} />,
      percentage: safeModules.decision,
      color: '#8b5cf6',
      description: 'Trading Logic Pipeline'
    },
    {
      name: 'ML',
      icon: <Cpu size={32} />,
      percentage: safeModules.ml,
      color: '#06b6d4',
      description: 'Machine Learning Models'
    },
    {
      name: 'Network',
      icon: <Network size={32} />,
      percentage: safeModules.network,
      color: '#10b981',
      description: 'API Connectivity'
    },
    {
      name: 'NLP',
      icon: <MessageSquare size={32} />,
      percentage: safeModules.nlp,
      color: '#f59e0b',
      description: 'Sentiment Analysis'
    },
    {
      name: 'Perception',
      icon: <Eye size={32} />,
      percentage: safeModules.perception,
      color: '#ef4444',
      description: 'Market Pattern Recognition'
    },
    {
      name: 'Learning',
      icon: <BookOpen size={32} />,
      percentage: safeModules.learning,
      color: '#ec4899',
      description: 'Continuous Improvement'
    }
  ]

  const getStatusColor = (percentage: number): string => {
    if (percentage >= 90) return '#10b981' // green
    if (percentage >= 70) return '#f59e0b' // yellow
    return '#ef4444' // red
  }

  const getStatusLabel = (percentage: number): string => {
    if (percentage >= 90) return 'OPTIMAL'
    if (percentage >= 70) return 'STABLE'
    if (percentage >= 50) return 'WARNING'
    return 'CRITICAL'
  }

  return (
    <div className="ai-status-monitor">
      <div className="monitor-header">
        <h2>🧠 AI Module Status</h2>
        <div className="overall-status">
          <span className="status-label">Overall Health:</span>
          <span 
            className="status-value"
            style={{ 
              color: getStatusColor(
                Object.values(safeModules).reduce((a, b) => a + b, 0) / 7
              )
            }}
          >
            {getStatusLabel(
              Object.values(safeModules).reduce((a, b) => a + b, 0) / 7
            )}
          </span>
        </div>
      </div>

      <div className="modules-grid">
        {aiModules.map((module, index) => (
          <div 
            key={module.name} 
            className="module-card"
            style={{ 
              animationDelay: `${index * 0.1}s`,
              opacity: isRunning ? 1 : 0.5
            }}
          >
            <div className="module-header">
              <div 
                className="module-icon"
                style={{ color: module.color }}
              >
                {module.icon}
              </div>
              <div className="module-info">
                <h4>{module.name}</h4>
                <p>{module.description}</p>
              </div>
            </div>

            <div className="module-progress">
              <div className="progress-info">
                <span className="progress-label">Status</span>
                <span 
                  className="progress-value"
                  style={{ color: getStatusColor(module.percentage) }}
                >
                  {module.percentage}%
                </span>
              </div>
              
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{
                    width: `${module.percentage}%`,
                    background: `linear-gradient(90deg, ${module.color}aa, ${module.color})`,
                    boxShadow: `0 0 10px ${module.color}66`
                  }}
                >
                  {isRunning && (
                    <div className="progress-pulse" style={{ background: module.color }} />
                  )}
                </div>
              </div>
            </div>

            {/* Health Indicator */}
            <div className="module-health">
              <div 
                className={`health-dot ${module.percentage >= 70 ? 'healthy' : 'warning'}`}
                style={{
                  background: getStatusColor(module.percentage),
                  boxShadow: `0 0 8px ${getStatusColor(module.percentage)}`
                }}
              />
              <span className="health-label">
                {module.percentage >= 90 ? 'Excellent' : 
                 module.percentage >= 70 ? 'Good' : 
                 module.percentage >= 50 ? 'Fair' : 'Poor'}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Risk Assessment */}
      <div className="risk-assessment">
        <h3>⚠️ Risk Assessment</h3>
        <div className="risk-grid">
          <div className="risk-item">
            <span className="risk-label">Market Volatility:</span>
            <span className={`risk-badge ${safeModules.perception > 85 ? 'low' : 'medium'}`}>
              {safeModules.perception > 85 ? 'LOW' : 'MEDIUM'}
            </span>
          </div>
          <div className="risk-item">
            <span className="risk-label">System Stability:</span>
            <span className={`risk-badge ${safeModules.network > 80 ? 'low' : 'medium'}`}>
              {safeModules.network > 80 ? 'STABLE' : 'MONITORING'}
            </span>
          </div>
          <div className="risk-item">
            <span className="risk-label">Decision Confidence:</span>
            <span className={`risk-badge ${safeModules.decision > 90 ? 'high' : 'medium'}`}>
              {safeModules.decision > 90 ? 'HIGH' : 'MODERATE'}
            </span>
          </div>
          <div className="risk-item">
            <span className="risk-label">Learning Rate:</span>
            <span className={`risk-badge ${safeModules.learning > 85 ? 'optimal' : 'normal'}`}>
              {safeModules.learning > 85 ? 'OPTIMAL' : 'NORMAL'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
