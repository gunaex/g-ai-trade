import { Link, useLocation } from 'react-router-dom'
import { TrendingUp, Activity, Settings, BarChart3, Brain } from 'lucide-react'

export default function Navbar() {
  const location = useLocation()

  const isActive = (path: string) => {
    return location.pathname === path ? 'nav-link active' : 'nav-link'
  }

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <TrendingUp size={24} />
        <span>G-AI-TRADE</span>
      </div>
      
      <div className="nav-links">
        <Link to="/" className={isActive('/')}>
          <TrendingUp size={20} />
          <span>Trade</span>
        </Link>
        
        <Link to="/monitor" className={isActive('/monitor')}>
          <Activity size={20} />
          <span>Monitor</span>
        </Link>
        
        <Link to="/backtest" className={isActive('/backtest')}>
          <BarChart3 size={20} />
          <span>Backtest</span>
        </Link>
        
        <Link to="/gods-hand" className={isActive('/gods-hand')}>
          <Brain size={20} />
          <span>God's Hand</span>
        </Link>
        
        <Link to="/settings" className={isActive('/settings')}>
          <Settings size={20} />
          <span>Settings</span>
        </Link>
      </div>
    </nav>
  )
}
