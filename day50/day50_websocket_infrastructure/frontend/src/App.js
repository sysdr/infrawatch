import React, { useState } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  const [token, setToken] = useState(null);
  const [username, setUsername] = useState('');

  const handleLogin = (authToken, user) => {
    setToken(authToken);
    setUsername(user);
  };

  const handleLogout = () => {
    setToken(null);
    setUsername('');
  };

  return (
    <div className="App">
      {!token ? (
        <Login onLogin={handleLogin} />
      ) : (
        <Dashboard token={token} username={username} onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;
