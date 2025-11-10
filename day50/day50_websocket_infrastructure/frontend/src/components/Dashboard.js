import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import './Dashboard.css';

const Dashboard = ({ token, username, onLogout }) => {
  const { isConnected, socketId, error, reconnectAttempts, joinRoom, leaveRoom, sendMessage, on, off } = useWebSocket(token);
  
  const [stats, setStats] = useState({ active_connections: 0, total_connections: 0 });
  const [rooms, setRooms] = useState([]);
  const [currentRoom, setCurrentRoom] = useState('');
  const [roomInput, setRoomInput] = useState('');
  const [messageInput, setMessageInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [roomMembers, setRoomMembers] = useState([]);

  useEffect(() => {
    const handleStatsUpdate = (data) => {
      setStats({
        active_connections: data.active_connections,
        total_connections: data.total_connections
      });
    };

    const handleRoomJoined = (data) => {
      if (!rooms.includes(data.room)) {
        setRooms(prev => [...prev, data.room]);
      }
      setMessages(prev => [...prev, {
        type: 'system',
        room: data.room,
        message: `${data.username} joined the room`,
        timestamp: new Date().toISOString()
      }]);
    };

    const handleRoomLeft = (data) => {
      setMessages(prev => [...prev, {
        type: 'system',
        room: data.room,
        message: `${data.username} left the room`,
        timestamp: new Date().toISOString()
      }]);
    };

    const handleRoomMembers = (data) => {
      setRoomMembers(data.members);
    };

    const handleMessage = (data) => {
      setMessages(prev => [...prev, {
        type: 'message',
        ...data
      }]);
    };

    on('stats_update', handleStatsUpdate);
    on('room_joined', handleRoomJoined);
    on('room_left', handleRoomLeft);
    on('room_members', handleRoomMembers);
    on('message', handleMessage);

    return () => {
      off('stats_update', handleStatsUpdate);
      off('room_joined', handleRoomJoined);
      off('room_left', handleRoomLeft);
      off('room_members', handleRoomMembers);
      off('message', handleMessage);
    };
  }, [on, off, rooms]);

  const handleJoinRoom = () => {
    if (roomInput.trim()) {
      joinRoom(roomInput.trim());
      setCurrentRoom(roomInput.trim());
      setRoomInput('');
    }
  };

  const handleLeaveRoom = (room) => {
    leaveRoom(room);
    setRooms(prev => prev.filter(r => r !== room));
    if (currentRoom === room) {
      setCurrentRoom('');
    }
  };

  const handleSendMessage = () => {
    if (messageInput.trim() && currentRoom) {
      sendMessage(currentRoom, messageInput.trim());
      setMessageInput('');
    }
  };

  const getConnectionStatusColor = () => {
    if (isConnected) return '#10b981';
    if (reconnectAttempts > 0) return '#f59e0b';
    return '#ef4444';
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>WebSocket Infrastructure</h1>
          <div className="connection-status">
            <div 
              className="status-indicator"
              style={{ backgroundColor: getConnectionStatusColor() }}
            />
            <span className="status-text">
              {isConnected ? 'Connected' : reconnectAttempts > 0 ? `Reconnecting (${reconnectAttempts})` : 'Disconnected'}
            </span>
            {socketId && <span className="socket-id">ID: {socketId.substring(0, 8)}</span>}
          </div>
        </div>
        <div className="header-right">
          <span className="username">👤 {username}</span>
          <button onClick={onLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          ⚠️ Connection Error: {error}
        </div>
      )}

      <div className="dashboard-content">
        <div className="stats-section">
          <div className="stat-card">
            <div className="stat-value">{stats.active_connections}</div>
            <div className="stat-label">Active Connections</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_connections}</div>
            <div className="stat-label">Total Connections</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{rooms.length}</div>
            <div className="stat-label">Joined Rooms</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{messages.length}</div>
            <div className="stat-label">Messages Received</div>
          </div>
        </div>

        <div className="main-content">
          <div className="sidebar">
            <div className="room-controls">
              <h3>Rooms</h3>
              <div className="room-input-group">
                <input
                  type="text"
                  value={roomInput}
                  onChange={(e) => setRoomInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleJoinRoom()}
                  placeholder="Enter room name"
                  className="room-input"
                />
                <button onClick={handleJoinRoom} className="join-btn" disabled={!isConnected}>
                  Join
                </button>
              </div>
            </div>

            <div className="room-list">
              {rooms.length === 0 ? (
                <div className="empty-state">No rooms joined</div>
              ) : (
                rooms.map(room => (
                  <div 
                    key={room} 
                    className={`room-item ${currentRoom === room ? 'active' : ''}`}
                    onClick={() => setCurrentRoom(room)}
                  >
                    <span className="room-name">#{room}</span>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleLeaveRoom(room);
                      }} 
                      className="leave-btn"
                    >
                      ×
                    </button>
                  </div>
                ))
              )}
            </div>

            {currentRoom && roomMembers.length > 0 && (
              <div className="members-section">
                <h4>Members ({roomMembers.length})</h4>
                <div className="member-list">
                  {roomMembers.map(member => (
                    <div key={member.socket_id} className="member-item">
                      👤 {member.username}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="chat-section">
            <div className="chat-header">
              {currentRoom ? (
                <>
                  <span className="room-title">#{currentRoom}</span>
                  <span className="member-count">{roomMembers.length} members</span>
                </>
              ) : (
                <span className="room-title">Select or join a room</span>
              )}
            </div>

            <div className="messages-container">
              {messages
                .filter(msg => !currentRoom || msg.room === currentRoom)
                .map((msg, idx) => (
                  <div key={idx} className={`message ${msg.type}`}>
                    {msg.type === 'system' ? (
                      <div className="system-message">
                        <span className="message-text">{msg.message}</span>
                        <span className="message-time">{formatTimestamp(msg.timestamp)}</span>
                      </div>
                    ) : (
                      <div className="user-message">
                        <div className="message-header">
                          <span className="message-user">{msg.username}</span>
                          <span className="message-time">{formatTimestamp(msg.timestamp)}</span>
                        </div>
                        <div className="message-content">{msg.message}</div>
                      </div>
                    )}
                  </div>
                ))}
              {messages.length === 0 && (
                <div className="empty-state">No messages yet</div>
              )}
            </div>

            {currentRoom && (
              <div className="message-input-container">
                <input
                  type="text"
                  value={messageInput}
                  onChange={(e) => setMessageInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder={`Message #${currentRoom}`}
                  className="message-input"
                  disabled={!isConnected}
                />
                <button 
                  onClick={handleSendMessage} 
                  className="send-btn"
                  disabled={!isConnected || !messageInput.trim()}
                >
                  Send
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
