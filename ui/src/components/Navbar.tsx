import { Link, useLocation, useNavigate } from 'react-router-dom'
import { TrendingUp, Activity, Settings, BarChart3, Brain, LogOut, User } from 'lucide-react'
import { useState } from 'react'
import apiClient from '../lib/api'

export default function Navbar() {
  const location = useLocation()
  const navigate = useNavigate()
  const [showUserMenu, setShowUserMenu] = useState(false)
  
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  const isActive = (path: string) => {
    return location.pathname === path ? 'nav-link active' : 'nav-link'
  }

  const handleLogout = () => {
    apiClient.logout()
    navigate('/login')
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
        
        <Link to="/monitoring" className={isActive('/monitoring')}>
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

        <div className="relative ml-4">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <User size={20} />
            <span className="text-sm">{user.username || 'User'}</span>
          </button>

          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
              <div className="p-3 border-b border-gray-200 dark:border-gray-700">
                <p className="text-sm font-medium text-gray-900 dark:text-white">{user.username}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{user.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                <LogOut size={16} />
                <span>Logout</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}

