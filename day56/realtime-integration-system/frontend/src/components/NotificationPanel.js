import React from 'react';

const NotificationPanel = ({ notifications }) => {
  return (
    <div className="panel-card">
      <h3>📧 Recent Notifications</h3>
      
      <div className="items-list">
        {notifications.map((notif, index) => (
          <div key={index} className="item">
            <div className="item-header">
              <span className="item-id">{notif.notification_id}</span>
              <span className={`item-status status-${notif.status}`}>
                {notif.status}
              </span>
            </div>
            <div className="item-details">
              <span>Channel: {notif.channel}</span>
              <span>Time: {new Date(notif.sent_at).toLocaleTimeString()}</span>
            </div>
          </div>
        ))}
        
        {notifications.length === 0 && (
          <p className="empty-state">No notifications yet</p>
        )}
      </div>
    </div>
  );
};

export default NotificationPanel;
