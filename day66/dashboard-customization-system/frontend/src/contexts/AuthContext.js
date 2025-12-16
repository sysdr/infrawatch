import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      const userData = JSON.parse(localStorage.getItem('user') || '{}');
      setUser(userData);
    }
    setLoading(false);
  }, [token]);

  const login = async (email, password) => {
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    const response = await axios.post(`${apiUrl}/api/auth/login`, {
      email,
      password
    });
    const { access_token, user: userData } = response.data;
    setToken(access_token);
    setUser(userData);
    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(userData));
    return userData;
  };

  const register = async (email, username, password) => {
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    await axios.post(`${apiUrl}/api/auth/register`, {
      email,
      username,
      password
    });
    return login(email, password);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
