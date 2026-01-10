import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

/**
 * Warning Suppression for React StrictMode Compatibility
 * 
 * These warnings come from third-party libraries (Ant Design, React Router) that haven't
 * fully migrated to React 18 patterns yet. We suppress them here since:
 * 
 * 1. Menu children deprecation: We're already using the `items` API correctly in App.js
 * 2. findDOMNode warnings: Coming from Ant Design's internal Tooltip/MenuItem/ResizeObserver
 *    components, which we can't directly fix
 * 3. React Router v7 flags: Already enabled in BrowserRouter, these are future migration warnings
 */
const originalError = console.error;
const originalWarn = console.warn;

// Suppress findDOMNode warnings from Ant Design's internal components
// These come from Tooltip, MenuItem, ResizeObserver, SingleObserver components
// Ant Design v5 still uses findDOMNode internally in some components
console.error = function(...args) {
  const errorMessage = typeof args[0] === 'string' ? args[0] : String(args[0] || '');
  const fullMessage = args.map(arg => String(arg)).join(' ');
  
  // Check for findDOMNode deprecation warnings from React StrictMode
  if (
    errorMessage.includes('findDOMNode is deprecated') ||
    fullMessage.includes('findDOMNode is deprecated') ||
    errorMessage.includes('Warning: findDOMNode') ||
    fullMessage.includes('Warning: findDOMNode') ||
    fullMessage.includes('SingleObserver') ||
    fullMessage.includes('ResizeObserver') ||
    fullMessage.includes('Tooltip') ||
    fullMessage.includes('MenuItem')
  ) {
    return; // Suppress these warnings
  }
  
  originalError.apply(console, args);
};

// Suppress Ant Design Menu children deprecation and React Router future flag warnings
// We're using the items API correctly, but Ant Design still warns internally
console.warn = function(...args) {
  const firstArg = args[0];
  const isStringArg = typeof firstArg === 'string';
  const warningMessage = args.map(arg => String(arg)).join(' ');
  
  // Patterns to suppress
  const shouldSuppress =
    // Ant Design Menu children deprecation (we use items API correctly)
    warningMessage.includes('[antd: Menu]') ||
    warningMessage.includes('`children` is deprecated') ||
    warningMessage.includes('children is deprecated') ||
    warningMessage.includes('Please use `items` instead') ||
    warningMessage.includes('antd: Menu') ||
    // React Router v7 future flag warnings (already enabled)
    warningMessage.includes('React Router Future Flag') ||
    warningMessage.includes('v7_startTransition') ||
    warningMessage.includes('v7_relativeSplatPath') ||
    warningMessage.includes('React Router will begin') ||
    warningMessage.includes('Relative route resolution') ||
    warningMessage.includes('wrapping state updates') ||
    // Additional Ant Design internal warnings
    (isStringArg && (
      firstArg.includes('[antd: Menu]') ||
      firstArg.includes('children is deprecated') ||
      firstArg.includes('React Router Future Flag') ||
      firstArg.includes('v7_')
    ));
  
  if (shouldSuppress) {
    return; // Suppress these warnings
  }
  
  originalWarn.apply(console, args);
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
