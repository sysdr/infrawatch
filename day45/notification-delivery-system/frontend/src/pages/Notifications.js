import React, { useState, useEffect } from 'react';
import { Send, Plus, Filter, Search } from 'lucide-react';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newNotification, setNewNotification] = useState({
    user_id: '',
    channel: 'email',
    priority: 'normal',
    recipient: '',
    subject: '',
    content: ''
  });

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await fetch('/api/notifications/');
      const data = await response.json();
      setNotifications(data.notifications || []);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  const sendNotification = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/notifications/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newNotification,
          user_id: parseInt(newNotification.user_id) || 1
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`Notification sent! Tracking ID: ${result.tracking_id}`);
        setNewNotification({
          user_id: '',
          channel: 'email',
          priority: 'normal',
          recipient: '',
          subject: '',
          content: ''
        });
        fetchNotifications();
      } else {
        throw new Error('Failed to send notification');
      }
    } catch (error) {
      alert('Failed to send notification: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const sendBulkNotifications = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/notifications/bulk-send');
      const data = await response.json();
      alert(`Sent ${data.notifications.length} demo notifications!`);
      fetchNotifications();
    } catch (error) {
      alert('Failed to send bulk notifications: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'delivered': return 'text-green-600 bg-green-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'processing': return 'text-blue-600 bg-blue-100';
      case 'queued': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'normal': return 'text-blue-600 bg-blue-100';
      case 'low': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
        <div className="flex space-x-3">
          <button
            onClick={sendBulkNotifications}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
          >
            <Send className="h-4 w-4" />
            <span>Send Demo Batch</span>
          </button>
        </div>
      </div>

      {/* Send New Notification */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
          <Plus className="h-5 w-5" />
          <span>Send New Notification</span>
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">User ID</label>
            <input
              type="number"
              value={newNotification.user_id}
              onChange={(e) => setNewNotification({...newNotification, user_id: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter user ID"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Channel</label>
            <select
              value={newNotification.channel}
              onChange={(e) => setNewNotification({...newNotification, channel: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="email">Email</option>
              <option value="sms">SMS</option>
              <option value="push">Push</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              value={newNotification.priority}
              onChange={(e) => setNewNotification({...newNotification, priority: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="low">Low</option>
              <option value="normal">Normal</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Recipient</label>
            <input
              type="text"
              value={newNotification.recipient}
              onChange={(e) => setNewNotification({...newNotification, recipient: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="email@example.com or +1234567890"
            />
          </div>
          
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Subject (for email)</label>
            <input
              type="text"
              value={newNotification.subject}
              onChange={(e) => setNewNotification({...newNotification, subject: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Notification subject"
            />
          </div>
          
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
            <textarea
              value={newNotification.content}
              onChange={(e) => setNewNotification({...newNotification, content: e.target.value})}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Notification content"
            />
          </div>
        </div>
        
        <button
          onClick={sendNotification}
          disabled={loading || !newNotification.recipient || !newNotification.content}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
        >
          <Send className="h-4 w-4" />
          <span>{loading ? 'Sending...' : 'Send Notification'}</span>
        </button>
      </div>

      {/* Notifications List */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-900">Recent Notifications</h2>
            <div className="flex space-x-3">
              <div className="relative">
                <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search notifications..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center space-x-2">
                <Filter className="h-4 w-4" />
                <span>Filter</span>
              </button>
            </div>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Notification
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Channel
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {notifications.map((notification) => (
                <tr key={notification.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {notification.subject || 'No Subject'}
                      </div>
                      <div className="text-sm text-gray-500 truncate max-w-xs">
                        {notification.content}
                      </div>
                      <div className="text-xs text-gray-400 mt-1">
                        To: {notification.recipient}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                      {notification.channel}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${getPriorityColor(notification.priority)}`}>
                      {notification.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${getStatusColor(notification.status)}`}>
                      {notification.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(notification.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {notifications.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-500">No notifications found</div>
              <div className="text-sm text-gray-400 mt-1">
                Send your first notification using the form above
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Notifications;
