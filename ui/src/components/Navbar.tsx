import { Link, useLocation } from 'react-router-dom'
import { TrendingUp, Activity, Settings } from 'lucide-react'

export default function Navbar() {
  const location = useLocation()

  const isActive = (path: string) => {
    return location.pathname === path ? 'nav-link active' : 'nav-link'
  }

  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-brand">
          <TrendingUp size={32} />
          <h1>G-AI-TRADE</h1>
        </div>
        
        <div className="nav-links">
          <Link to="/" className={isActive('/')}>
            <TrendingUp size={20} />
            <span>Trade</span>
          </Link>
          <Link to="/monitoring" className={isActive('/monitoring')}>
            <Activity size={20} />
            <span>Monitor</span>
          </Link>
          <Link to="/settings" className={isActive('/settings')}>
            <Settings size={20} />
            <span>Settings</span>
          </Link>
        </div>
      </div>
    </nav>
  )
}
