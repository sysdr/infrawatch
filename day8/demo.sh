# InfraWatch Auth Demo - Web Interface Guide

## Quick Setup & Demo

### 1. Run the Application

```bash
# Navigate to project directory
cd infrawatch-auth

# Activate virtual environment
source venv/bin/activate

# Start the Flask app
export FLASK_APP=run.py
export FLASK_ENV=development
python run.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 2. Test Health Endpoint

```bash
# Open new terminal
curl http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "infrawatch-auth"
}
```

### 3. Create a User via API

```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@infrawatch.com",
    "password": "SecurePass123!",
    "first_name": "Demo",
    "last_name": "User"
  }'
```

**Expected Response:**
```json
{
  "message": "User created successfully",
  "user": {
    "id": "uuid-string-here",
    "email": "demo@infrawatch.com",
    "first_name": "Demo",
    "last_name": "User",
    "is_active": true,
    "created_at": "2025-01-XX...",
    "login_count": 0
  }
}
```

### 4. List Users

```bash
curl http://localhost:5000/api/users
```

**Expected Response:**
```json
{
  "users": [
    {
      "id": "uuid-string",
      "email": "demo@infrawatch.com",
      "first_name": "Demo",
      "last_name": "User",
      "is_active": true
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 1,
    "pages": 1
  }
}
```

### 5. Verify Password

```bash
curl -X POST http://localhost:5000/api/users/verify-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@infrawatch.com",
    "password": "SecurePass123!"
  }'
```

**Expected Response:**
```json
{
  "message": "Password verified successfully",
  "user_id": "uuid-string-here"
}
```

## Create Simple Web Interface

Add this to your project:

### Create `templates/index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>InfraWatch Auth Demo</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        .form-group { margin: 15px 0; }
        input { padding: 8px; width: 200px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; }
        .result { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>InfraWatch Authentication Demo</h1>
    
    <h2>Create User</h2>
    <form id="userForm">
        <div class="form-group">
            <input type="email" id="email" placeholder="Email" required>
        </div>
        <div class="form-group">
            <input type="password" id="password" placeholder="Password" required>
        </div>
        <div class="form-group">
            <input type="text" id="firstName" placeholder="First Name">
        </div>
        <div class="form-group">
            <input type="text" id="lastName" placeholder="Last Name">
        </div>
        <button type="submit">Create User</button>
    </form>
    
    <h2>Verify Password</h2>
    <form id="loginForm">
        <div class="form-group">
            <input type="email" id="loginEmail" placeholder="Email" required>
        </div>
        <div class="form-group">
            <input type="password" id="loginPassword" placeholder="Password" required>
        </div>
        <button type="submit">Verify Password</button>
    </form>
    
    <button onclick="loadUsers()">Load All Users</button>
    
    <div id="result" class="result" style="display: none;"></div>

    <script>
        function showResult(data) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            resultDiv.style.display = 'block';
        }

        document.getElementById('userForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const response = await fetch('/api/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: document.getElementById('email').value,
                    password: document.getElementById('password').value,
                    first_name: document.getElementById('firstName').value,
                    last_name: document.getElementById('lastName').value
                })
            });
            const data = await response.json();
            showResult(data);
        });

        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const response = await fetch('/api/users/verify-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: document.getElementById('loginEmail').value,
                    password: document.getElementById('loginPassword').value
                })
            });
            const data = await response.json();
            showResult(data);
        });

        async function loadUsers() {
            const response = await fetch('/api/users');
            const data = await response.json();
            showResult(data);
        }
    </script>
</body>
</html>
```

### Update `app/__init__.py` to serve the HTML:

```python
# Add this route to app/__init__.py
@app.route('/')
def index():
    return render_template('index.html')

# Also add this import at the top
from flask import render_template
```

### Create templates directory:

```bash
mkdir -p templates
# Copy the HTML content above into templates/index.html
```

## Access Web Interface

1. Restart Flask app: `python run.py`
2. Open browser: `http://localhost:5000`
3. Use the web form to create users and verify passwords
4. See real-time API responses

## Docker Demo

```bash
# Build and run with Docker
docker-compose up --build

# Test in browser: http://localhost:5000
# All endpoints work the same way
```

## Troubleshooting

**Port not showing output:**
- Check Flask is running: `ps aux | grep python`
- Verify port 5000 is free: `lsof -i :5000`
- Check logs for errors in terminal

**Database issues:**
- Run migrations: `flask db upgrade`
- Check PostgreSQL: `docker-compose ps`

**API returns 404:**
- Verify blueprint registration in `app/__init__.py`
- Check route definitions in `app/api/users.py`