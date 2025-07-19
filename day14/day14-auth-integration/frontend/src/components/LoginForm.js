import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import RegisterForm from './RegisterForm';

const LoginForm = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const { login, loading } = useAuth();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(formData);
      toast.success('Login successful!');
    } catch (error) {
      toast.error(error.message);
    }
  };

  const toggleMode = () => {
    setIsRegisterMode(!isRegisterMode);
    setFormData({ email: '', password: '' });
  };

  // If in register mode, show the registration form
  if (isRegisterMode) {
    return <RegisterForm onToggleMode={toggleMode} />;
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h2>Sign in</h2>
          <p>Continue to your account</p>
        </div>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Enter your email"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="password-input-container">
              <input
                type={showPassword ? "text" : "password"}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Enter your password"
                className="form-input"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="password-toggle"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="login-button"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="auth-toggle">
          <p>
            Don't have an account?{' '}
            <button
              type="button"
              onClick={toggleMode}
              className="toggle-link"
            >
              Sign up
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
