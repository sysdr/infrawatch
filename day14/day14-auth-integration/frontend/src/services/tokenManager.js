import { jwtDecode } from 'jwt-decode';

class TokenManager {
  constructor() {
    this.ACCESS_TOKEN_KEY = 'access_token';
    this.REFRESH_THRESHOLD = parseInt(process.env.REACT_APP_TOKEN_REFRESH_THRESHOLD) || 300; // 5 minutes
  }

  setTokens(tokens) {
    if (tokens.access_token) {
      localStorage.setItem(this.ACCESS_TOKEN_KEY, tokens.access_token);
    }
    // Refresh token is handled by httpOnly cookies
  }

  getAccessToken() {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  removeTokens() {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    // httpOnly cookie will be cleared by logout endpoint
  }

  isTokenExpired(token) {
    if (!token) return true;
    
    try {
      const decoded = jwtDecode(token);
      const currentTime = Date.now() / 1000;
      return decoded.exp < currentTime;
    } catch (error) {
      return true;
    }
  }

  shouldRefreshToken(token) {
    if (!token) return false;
    
    try {
      const decoded = jwtDecode(token);
      const currentTime = Date.now() / 1000;
      return decoded.exp - currentTime < this.REFRESH_THRESHOLD;
    } catch (error) {
      return false;
    }
  }

  getTokenExpiration(token) {
    if (!token) return null;
    
    try {
      const decoded = jwtDecode(token);
      return decoded.exp * 1000; // Convert to milliseconds
    } catch (error) {
      return null;
    }
  }
}

export const tokenManager = new TokenManager();
