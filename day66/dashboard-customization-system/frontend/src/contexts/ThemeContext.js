import React, { createContext, useContext, useState, useEffect } from 'react';

const themes = {
  light: {
    primary: '#1976d2',
    secondary: '#dc004e',
    background: '#ffffff',
    paper: '#f5f5f5',
    text: '#000000',
    border: '#e0e0e0'
  },
  dark: {
    primary: '#90caf9',
    secondary: '#f48fb1',
    background: '#121212',
    paper: '#1e1e1e',
    text: '#ffffff',
    border: '#333333'
  },
  ocean: {
    primary: '#0066cc',
    secondary: '#00cccc',
    background: '#f0f8ff',
    paper: '#e6f3ff',
    text: '#1a1a1a',
    border: '#b3d9ff'
  },
  sunset: {
    primary: '#ff6b35',
    secondary: '#f7931e',
    background: '#fff5f0',
    paper: '#ffe6d9',
    text: '#2d2d2d',
    border: '#ffccb3'
  }
};

const ThemeContext = createContext(null);

export const ThemeProvider = ({ children }) => {
  const [currentTheme, setCurrentTheme] = useState('light');

  useEffect(() => {
    const root = document.documentElement;
    const theme = themes[currentTheme];
    
    Object.keys(theme).forEach(key => {
      root.style.setProperty(`--${key}`, theme[key]);
    });
  }, [currentTheme]);

  return (
    <ThemeContext.Provider value={{ currentTheme, setCurrentTheme, themes }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext);
