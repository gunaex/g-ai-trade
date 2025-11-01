import { useState, useEffect } from 'react'

export function useDarkMode() {
  const [darkMode, setDarkMode] = useState(() => {
    // Check localStorage first
    const saved = localStorage.getItem('darkMode')
    if (saved !== null) {
      return JSON.parse(saved)
    }
    // Then check system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    // Apply dark mode class to document
    if (darkMode) {
      document.documentElement.setAttribute('data-color-scheme', 'dark')
    } else {
      document.documentElement.setAttribute('data-color-scheme', 'light')
    }
    
    // Save to localStorage
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
  }, [darkMode])

  const toggleDarkMode = () => {
    setDarkMode((prev: boolean) => !prev)
  }

  return { darkMode, toggleDarkMode, setDarkMode }
}

