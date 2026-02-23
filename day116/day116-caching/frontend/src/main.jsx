import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

// Suppress "Download the React DevTools" console message in development
if (typeof window !== 'undefined' && import.meta.env.DEV) {
  const orig = console.info
  console.info = (...args) => {
    if (args[0] && String(args[0]).includes('React DevTools')) return
    orig.apply(console, args)
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode><App /></React.StrictMode>
)
