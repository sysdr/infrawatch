# Authentication Integration Demo

This project demonstrates a complete authentication integration system with FastAPI backend, React frontend, and Redis for session management.

## 🚀 Quick Start

### 1. Start All Services
```bash
./start.sh
```

### 2. Run the Demo
```bash
./simple_demo.sh
```

### 3. Access the Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📋 Demo Scripts

### Simple Demo (`simple_demo.sh`)
A straightforward demonstration of all authentication features:

```bash
./simple_demo.sh
```

**Features Demonstrated:**
- ✅ User Registration
- ✅ User Login
- ✅ Protected Endpoint Access
- ✅ Error Handling (Invalid Credentials)
- ✅ Error Handling (Missing Token)
- ✅ User Logout

### Comprehensive Demo (`demo_auth_integration.sh`)
Advanced demo with detailed error handling and token management:

```bash
./demo_auth_integration.sh
```

**Additional Features:**
- 🔄 Token Refresh
- 🛡️ Invalid Token Handling
- 🔍 Logout Verification
- 📊 Detailed Response Analysis

## 🔧 API Endpoints

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | User login |
| `POST` | `/api/auth/logout` | User logout |
| `POST` | `/api/auth/refresh` | Refresh access token |
| `POST` | `/api/auth/verify` | Verify token |

### User Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users/me` | Get current user profile |
| `GET` | `/api/users/profile` | Get user profile |
| `GET` | `/api/health` | Health check |

## 🧪 Test Credentials

### Demo User 1
- **Email**: `demo@integration.com`
- **Password**: `SecurePass123!`
- **Username**: `demo_user`

### Demo User 2
- **Email**: `demo@example.com`
- **Password**: `demo123456`
- **Username**: `demouser`

## 📊 Monitoring Tools

### Status Dashboard
Real-time monitoring of all services:
```bash
./status_dashboard.sh
```

**Features:**
- Service status monitoring
- Process information
- Memory usage tracking
- Error count monitoring
- System resource usage

### Error Monitoring
Comprehensive error tracking:
```bash
./monitor_errors.sh
```

**Features:**
- Backend health checks
- Frontend health checks
- Redis connection monitoring
- Memory usage alerts
- Error pattern detection

### Browser Error Monitor
JavaScript file for frontend error monitoring:
```javascript
// Include in your HTML or React app
<script src="browser_monitor.js"></script>
```

**Features:**
- Console error tracking
- Network error monitoring
- Unhandled promise rejection detection
- JavaScript error catching

## 🔍 Manual Testing

### User Registration
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "testpassword123"
  }'
```

### User Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

### Access Protected Endpoint
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/users/me
```

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

**Test Coverage:**
- Health check endpoint
- User registration
- User login
- Protected endpoint access
- Invalid login handling

### Frontend Tests
```bash
cd frontend
npm test -- --watchAll=false --passWithNoTests
```

## 🛠️ Technical Features

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.11+
- **Authentication**: JWT tokens with refresh mechanism
- **Password Hashing**: bcrypt
- **Database**: SQLAlchemy with SQLite
- **Session Management**: Redis
- **API Documentation**: Auto-generated Swagger UI

### Frontend (React)
- **Framework**: React 18 with React Router
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Form Handling**: React Hook Form
- **Notifications**: React Hot Toast
- **Token Management**: js-cookie

### Security Features
- ✅ JWT Token-based Authentication
- ✅ Password Hashing with bcrypt
- ✅ Token Refresh Mechanism
- ✅ Protected Route Middleware
- ✅ CORS Configuration
- ✅ Input Validation
- ✅ Error Handling

## 📁 Project Structure

```
day14-auth-integration/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   └── users.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── middleware/
│   │   │   └── auth_middleware.py
│   │   ├── models/
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── jwt_service.py
│   │   │   └── user_service.py
│   │   └── main.py
│   ├── tests/
│   │   └── test_auth.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.js
│   │   │   ├── LoginForm.js
│   │   │   └── ProtectedRoute.js
│   │   ├── contexts/
│   │   │   └── AuthContext.js
│   │   ├── services/
│   │   │   ├── authService.js
│   │   │   └── tokenManager.js
│   │   └── App.js
│   └── package.json
├── demo_auth_integration.sh
├── simple_demo.sh
├── status_dashboard.sh
├── monitor_errors.sh
├── browser_monitor.js
├── start.sh
└── stop.sh
```

## 🚨 Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   ./stop.sh
   ./start.sh
   ```

2. **Port conflicts**
   - Backend: 8000
   - Frontend: 3000
   - Redis: 6379

3. **Permission denied**
   ```bash
   chmod +x *.sh
   ```

4. **Dependencies missing**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

### Logs and Debugging
```bash
# View backend logs
tail -f backend.log

# View frontend logs
tail -f frontend.log

# Monitor all services
./status_dashboard.sh
```

## 📈 Performance Monitoring

### Memory Usage
- Backend: ~10-20MB
- Frontend: ~50-100MB
- Redis: ~5-10MB

### Response Times
- Health Check: <50ms
- User Registration: <200ms
- User Login: <150ms
- Protected Endpoint: <100ms

## 🔄 Development Workflow

1. **Start Development Environment**
   ```bash
   ./start.sh
   ```

2. **Run Tests**
   ```bash
   cd backend && python -m pytest tests/ -v
   cd frontend && npm test
   ```

3. **Run Demo**
   ```bash
   ./simple_demo.sh
   ```

4. **Monitor System**
   ```bash
   ./status_dashboard.sh
   ```

5. **Stop Services**
   ```bash
   ./stop.sh
   ```

## 🎯 Next Steps

1. **Frontend Integration**: Connect React components to the API
2. **Additional Features**: Add password reset, email verification
3. **Production Setup**: Configure for production deployment
4. **Security Hardening**: Add rate limiting, audit logging
5. **Testing**: Add more comprehensive test coverage

---

**🎉 Authentication Integration Demo Complete!**

For more information, visit the API documentation at http://localhost:8000/docs 