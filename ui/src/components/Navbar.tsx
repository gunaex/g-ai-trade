import { Link, useLocation, useNavigate } from 'react-router-dom'
import { TrendingUp, Activity, Settings, BarChart3, Brain, LogOut } from 'lucide-react'
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
            className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-sm"
          >
            <div className="w-7 h-7 rounded-full bg-indigo-600 flex items-center justify-center text-white font-semibold text-xs">
              {(user.username || 'U').charAt(0).toUpperCase()}
            </div>
            <span className="hidden md:inline">{user.username || 'User'}</span>
          </button>

          {showUserMenu && (
            <>
              <div 
                className="fixed inset-0 z-40" 
                onClick={() => setShowUserMenu(false)}
              />
              <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50 overflow-hidden">
                <div className="p-3 bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-gray-700 dark:to-gray-700 border-b border-gray-200 dark:border-gray-600">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold">
                      {(user.username || 'U').charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                        {user.username}
                      </p>
                      <p className="text-xs text-gray-600 dark:text-gray-300 truncate">
                        {user.email}
                      </p>
                    </div>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors font-medium"
                >
                  <LogOut size={16} />
                  <span>Logout</span>
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

