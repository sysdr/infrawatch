import React, { useState } from 'react';
import { Send, Mail, MessageSquare, Smartphone, Webhook, Bell } from 'lucide-react';

const NotificationForm = ({ onSend, loading }) => {
  const [formData, setFormData] = useState({
    title: '',
    message: '',
    channel: 'email',
    recipient: '',
    priority: 'medium'
  });
  
  const [result, setResult] = useState(null);

  const channels = [
    { id: 'email', name: 'Email', icon: Mail, placeholder: 'user@example.com' },
    { id: 'sms', name: 'SMS', icon: Smartphone, placeholder: '+1234567890' },
    { id: 'slack', name: 'Slack', icon: MessageSquare, placeholder: '#channel or @user' },
    { id: 'webhook', name: 'Webhook', icon: Webhook, placeholder: 'https://api.example.com/webhook' },
    { id: 'push', name: 'Push', icon: Bell, placeholder: 'device_token_here' }
  ];

  const priorities = [
    { id: 'low', name: 'Low', color: 'text-emerald-700 bg-emerald-100 border-emerald-200' },
    { id: 'medium', name: 'Medium', color: 'text-amber-700 bg-amber-100 border-amber-200' },
    { id: 'high', name: 'High', color: 'text-orange-700 bg-orange-100 border-orange-200' },
    { id: 'critical', name: 'Critical', color: 'text-red-700 bg-red-100 border-red-200' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult(null);
    
    const response = await onSend(formData);
    setResult(response);
    
    if (response.success) {
      setFormData({
        title: '',
        message: '',
        channel: 'email',
        recipient: '',
        priority: 'medium'
      });
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const selectedChannel = channels.find(c => c.id === formData.channel);
  const ChannelIcon = selectedChannel?.icon || Mail;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white shadow-xl rounded-xl border border-slate-200">
        <div className="px-6 py-5 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-slate-100">
          <h3 className="text-xl font-bold text-slate-900">Send Notification</h3>
          <p className="mt-1 text-sm text-slate-600 font-medium">
            Send a notification through your preferred channel
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-semibold text-slate-700 mb-2">
              Title
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              className="w-full px-4 py-3 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200"
              placeholder="Alert: System Performance Issue"
            />
          </div>

          {/* Message */}
          <div>
            <label htmlFor="message" className="block text-sm font-semibold text-slate-700 mb-2">
              Message
            </label>
            <textarea
              id="message"
              name="message"
              value={formData.message}
              onChange={handleChange}
              required
              rows={4}
              className="w-full px-4 py-3 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200"
              placeholder="We are experiencing elevated response times on our API endpoints. Our team is investigating the issue."
            />
          </div>

          {/* Channel */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-3">
              Channel
            </label>
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
              {channels.map((channel) => {
                const Icon = channel.icon;
                return (
                  <label
                    key={channel.id}
                    className={`relative flex flex-col items-center p-4 border-2 rounded-xl cursor-pointer hover:bg-slate-50 transition-all duration-200 ${
                      formData.channel === channel.id
                        ? 'border-indigo-500 bg-indigo-50 shadow-md'
                        : 'border-slate-300 hover:border-slate-400'
                    }`}
                  >
                    <input
                      type="radio"
                      name="channel"
                      value={channel.id}
                      checked={formData.channel === channel.id}
                      onChange={handleChange}
                      className="sr-only"
                    />
                    <Icon className={`h-6 w-6 mb-2 ${
                      formData.channel === channel.id ? 'text-indigo-600' : 'text-slate-400'
                    }`} />
                    <span className={`text-xs font-semibold ${
                      formData.channel === channel.id ? 'text-indigo-700' : 'text-slate-600'
                    }`}>
                      {channel.name}
                    </span>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Recipient */}
          <div>
            <label htmlFor="recipient" className="block text-sm font-semibold text-slate-700 mb-2">
              Recipient
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <ChannelIcon className="h-5 w-5 text-slate-400" />
              </div>
              <input
                type="text"
                id="recipient"
                name="recipient"
                value={formData.recipient}
                onChange={handleChange}
                required
                className="w-full pl-12 pr-4 py-3 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors duration-200"
                placeholder={selectedChannel?.placeholder || ''}
              />
            </div>
          </div>

          {/* Priority */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-3">
              Priority
            </label>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              {priorities.map((priority) => (
                <label
                  key={priority.id}
                  className={`relative flex items-center justify-center p-3 border-2 rounded-xl cursor-pointer hover:bg-slate-50 transition-all duration-200 ${
                    formData.priority === priority.id
                      ? 'border-indigo-500 bg-indigo-50 shadow-md'
                      : 'border-slate-300 hover:border-slate-400'
                  }`}
                >
                  <input
                    type="radio"
                    name="priority"
                    value={priority.id}
                    checked={formData.priority === priority.id}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <span className={`px-3 py-2 text-xs font-bold rounded-lg border ${
                    formData.priority === priority.id ? priority.color : 'text-slate-600 bg-slate-100 border-slate-200'
                  }`}>
                    {priority.name}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center px-6 py-3 border border-transparent rounded-lg shadow-lg text-sm font-bold text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <Send className="h-4 w-4 mr-2" />
              )}
              {loading ? 'Sending...' : 'Send Notification'}
            </button>
          </div>

          {/* Result */}
          {result && (
            <div className={`p-4 rounded-md ${
              result.success 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-red-50 border border-red-200'
            }`}>
              <div className="flex">
                <div className={`flex-shrink-0 ${
                  result.success ? 'text-green-400' : 'text-red-400'
                }`}>
                  {result.success ? (
                    <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
                <div className="ml-3">
                  <h3 className={`text-sm font-medium ${
                    result.success ? 'text-green-800' : 'text-red-800'
                  }`}>
                    {result.success ? 'Notification sent successfully!' : 'Failed to send notification'}
                  </h3>
                  {result.error && (
                    <p className="mt-1 text-sm text-red-700">{result.error}</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default NotificationForm;
