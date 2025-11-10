from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_cors import CORS
import jwt
import logging
from datetime import datetime, timedelta
import os
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO with engineio settings
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    ping_timeout=60,
    ping_interval=25,
    logger=True,
    engineio_logger=True
)

# Connection registry
active_connections = {}
room_members = {}
connection_stats = {
    'total_connections': 0,
    'current_connections': 0,
    'total_messages': 0,
    'failed_authentications': 0
}

# JWT helper functions
def generate_token(user_id, username):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    # Ensure token is always a string (PyJWT 2.x returns string, but be safe)
    if isinstance(token, bytes):
        return token.decode('utf-8')
    return str(token)

def verify_token(token):
    """Verify JWT token"""
    try:
        if not token:
            logger.error("Token is None or empty")
            return None
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError as e:
        logger.error(f"Token expired: {str(e)}")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {type(e).__name__}: {str(e)}")
        return None

# Authentication decorator for socket events
def authenticated_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if request.sid not in active_connections:
            disconnect()
            return False
        return f(*args, **kwargs)
    return wrapped

# REST API endpoints
@app.route('/', methods=['GET'])
def index():
    """Root endpoint - API information"""
    return jsonify({
        'name': 'WebSocket Infrastructure API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'login': '/api/auth/login (POST)',
            'stats': '/api/stats (GET)',
            'websocket': '/socket.io'
        },
        'frontend': 'http://localhost:3000'
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint to get JWT token"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Simple validation (in production, check against database)
    if username and password:
        user_id = f"user_{username}"
        token = generate_token(user_id, username)
        return jsonify({
            'success': True,
            'token': token,
            'user_id': user_id,
            'username': username
        })
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get connection statistics"""
    return jsonify({
        'stats': connection_stats,
        'active_connections': len(active_connections),
        'rooms': {room: len(members) for room, members in room_members.items()}
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'connections': len(active_connections),
        'uptime': 'running'
    })

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect(auth=None):
    """Handle client connection"""
    try:
        # Extract token from auth
        token = None
        logger.info(f"Connection attempt from {request.sid}, auth type: {type(auth)}, auth: {auth}")
        
        # Try multiple ways to get the token
        if auth:
            if isinstance(auth, dict):
                # Auth is a dict, check for 'token' key
                if 'token' in auth:
                    token = auth['token']
                # Also check if auth itself contains token as a nested structure
                elif 'auth' in auth and isinstance(auth['auth'], dict) and 'token' in auth['auth']:
                    token = auth['auth']['token']
            elif isinstance(auth, str):
                # Auth might be the token string directly
                token = auth
        
        # Fallback to query parameter
        if not token and request.args.get('token'):
            token = request.args.get('token')
        
        # Fallback to request.event (Flask-SocketIO internal)
        if not token and hasattr(request, 'event') and request.event:
            if isinstance(request.event, dict):
                if 'auth' in request.event:
                    event_auth = request.event['auth']
                    if isinstance(event_auth, dict) and 'token' in event_auth:
                        token = event_auth['token']
                    elif isinstance(event_auth, str):
                        token = event_auth
        
        if not token:
            logger.warning(f"Connection attempt without token from {request.sid}, auth received: {auth}")
            connection_stats['failed_authentications'] += 1
            return False
        
        # Sanitize token (remove whitespace, handle string encoding)
        if isinstance(token, str):
            token = token.strip()
        elif token is not None:
            token = str(token).strip()
        
        logger.info(f"Token received for {request.sid}, verifying... Token length: {len(token) if token else 0}")
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            logger.warning(f"Invalid token for connection {request.sid}. Token preview: {token[:50] if token else 'None'}...")
            connection_stats['failed_authentications'] += 1
            return False
        
        logger.info(f"Token verified successfully for {request.sid}, user: {payload.get('username', 'unknown')}")
        
        # Register connection
        active_connections[request.sid] = {
            'user_id': payload['user_id'],
            'username': payload['username'],
            'connected_at': datetime.utcnow().isoformat(),
            'rooms': set()
        }
        
        connection_stats['total_connections'] += 1
        connection_stats['current_connections'] = len(active_connections)
        
        logger.info(f"Client connected: {request.sid} - User: {payload['username']}")
        
        # Send connection confirmation
        emit('connected', {
            'socket_id': request.sid,
            'user_id': payload['user_id'],
            'username': payload['username'],
            'message': 'Successfully connected to WebSocket server'
        })
        
        # Broadcast stats update
        socketio.emit('stats_update', {
            'active_connections': len(active_connections),
            'total_connections': connection_stats['total_connections']
        })
        
        return True
        
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        return False

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    try:
        if request.sid in active_connections:
            user_info = active_connections[request.sid]
            username = user_info['username']
            
            # Leave all rooms
            for room in user_info['rooms']:
                if room in room_members:
                    room_members[room].discard(request.sid)
                    if len(room_members[room]) == 0:
                        del room_members[room]
            
            # Remove from active connections
            del active_connections[request.sid]
            connection_stats['current_connections'] = len(active_connections)
            
            logger.info(f"Client disconnected: {request.sid} - User: {username}")
            
            # Broadcast stats update
            socketio.emit('stats_update', {
                'active_connections': len(active_connections),
                'total_connections': connection_stats['total_connections']
            })
            
    except Exception as e:
        logger.error(f"Disconnection error: {str(e)}")

@socketio.on('join_room')
@authenticated_only
def handle_join_room(*args):
    """Handle room join request"""
    try:
        # Extract data from args
        if args and len(args) > 0:
            data = args[0] if isinstance(args[0], dict) else {}
        else:
            data = {}
        
        room = data.get('room')
        if not room:
            emit('error', {'message': 'Room name required'})
            return
        
        join_room(room)
        
        # Update room members
        if room not in room_members:
            room_members[room] = set()
        room_members[room].add(request.sid)
        
        # Update user's room list
        active_connections[request.sid]['rooms'].add(room)
        
        user_info = active_connections[request.sid]
        logger.info(f"User {user_info['username']} joined room: {room}")
        
        # Notify room members
        emit('room_joined', {
            'room': room,
            'user_id': user_info['user_id'],
            'username': user_info['username'],
            'members_count': len(room_members[room])
        }, room=room)
        
        # Send current room member list to joiner
        emit('room_members', {
            'room': room,
            'members': [
                {
                    'socket_id': sid,
                    'username': active_connections[sid]['username']
                }
                for sid in room_members[room] if sid in active_connections
            ]
        })
        
    except Exception as e:
        logger.error(f"Join room error: {str(e)}")
        emit('error', {'message': f'Failed to join room: {str(e)}'})

@socketio.on('leave_room')
@authenticated_only
def handle_leave_room(*args):
    """Handle room leave request"""
    try:
        # Extract data from args
        if args and len(args) > 0:
            data = args[0] if isinstance(args[0], dict) else {}
        else:
            data = {}
        
        room = data.get('room')
        if not room:
            emit('error', {'message': 'Room name required'})
            return
        
        leave_room(room)
        
        # Update room members
        if room in room_members:
            room_members[room].discard(request.sid)
            if len(room_members[room]) == 0:
                del room_members[room]
        
        # Update user's room list
        if request.sid in active_connections:
            active_connections[request.sid]['rooms'].discard(room)
            user_info = active_connections[request.sid]
            
            logger.info(f"User {user_info['username']} left room: {room}")
            
            # Notify room members
            emit('room_left', {
                'room': room,
                'user_id': user_info['user_id'],
                'username': user_info['username']
            }, room=room)
        
    except Exception as e:
        logger.error(f"Leave room error: {str(e)}")
        emit('error', {'message': f'Failed to leave room: {str(e)}'})

@socketio.on('send_message')
@authenticated_only
def handle_send_message(*args):
    """Handle message broadcast to room"""
    try:
        # Extract data from args (Flask-SocketIO may pass it differently)
        if args and len(args) > 0:
            data = args[0] if isinstance(args[0], dict) else {}
        else:
            data = {}
        
        room = data.get('room')
        message = data.get('message')
        
        if not room or not message:
            emit('error', {'message': 'Room and message required'})
            return
        
        user_info = active_connections[request.sid]
        
        # Broadcast message to room
        message_data = {
            'room': room,
            'user_id': user_info['user_id'],
            'username': user_info['username'],
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        logger.info(f"Broadcasting message to room {room}: {message_data}")
        emit('message', message_data, room=room)
        
        connection_stats['total_messages'] += 1
        logger.info(f"Message sent to room {room} by {user_info['username']}, room members: {len(room_members.get(room, set()))}")
        
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        emit('error', {'message': f'Failed to send message: {str(e)}'})

@socketio.on('ping')
@authenticated_only
def handle_ping():
    """Handle ping for connection health check"""
    emit('pong', {'timestamp': datetime.utcnow().isoformat()})

@socketio.on('error')
def handle_error(e):
    """Handle errors"""
    logger.error(f"SocketIO error: {str(e)}")

if __name__ == '__main__':
    logger.info("Starting WebSocket server on http://0.0.0.0:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
