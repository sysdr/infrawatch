import React, { useState } from 'react';
import { Calendar, Filter, Search, Download } from 'lucide-react';
import './TaskHistory.css';

const TaskHistory = ({ tasks = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [queueFilter, setQueueFilter] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || task.status === statusFilter;
    const matchesQueue = queueFilter === 'all' || task.queue === queueFilter;
    return matchesSearch && matchesStatus && matchesQueue;
  });

  const sortedTasks = [...filteredTasks].sort((a, b) => {
    switch (sortBy) {
      case 'created_at':
        return new Date(b.created_at) - new Date(a.created_at);
      case 'duration':
        return (b.duration || 0) - (a.duration || 0);
      case 'retry_count':
        return b.retry_count - a.retry_count;
      default:
        return 0;
    }
  });

  const getStatusBadge = (status) => (
    <span className={`status-badge ${status}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );

  const formatDuration = (duration) => {
    if (!duration) return '-';
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    return `${minutes}m ${seconds}s`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="task-history">
      <div className="history-header">
        <h2>Task History</h2>
        <button className="export-btn">
          <Download className="btn-icon" />
          Export
        </button>
      </div>

      {/* Filters */}
      <div className="history-filters">
        <div className="search-box">
          <Search className="search-icon" />
          <input
            type="text"
            placeholder="Search tasks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="running">Running</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>

          <select value={queueFilter} onChange={(e) => setQueueFilter(e.target.value)}>
            <option value="all">All Queues</option>
            <option value="default">Default</option>
            <option value="priority">Priority</option>
            <option value="batch">Batch</option>
          </select>

          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="created_at">Sort by Date</option>
            <option value="duration">Sort by Duration</option>
            <option value="retry_count">Sort by Retries</option>
          </select>
        </div>
      </div>

      {/* Results Summary */}
      <div className="results-summary">
        Showing {sortedTasks.length} of {tasks.length} tasks
      </div>

      {/* Task History Table */}
      <div className="history-table">
        <div className="table-header">
          <span>Task Name</span>
          <span>Status</span>
          <span>Queue</span>
          <span>Created</span>
          <span>Duration</span>
          <span>Retries</span>
          <span>Worker</span>
        </div>

        <div className="table-body">
          {sortedTasks.map(task => (
            <div key={task.id} className="table-row">
              <div className="task-name-cell">
                <div className="task-name">{task.name}</div>
                <div className="task-id">{task.id}</div>
              </div>
              
              <div className="status-cell">
                {getStatusBadge(task.status)}
              </div>
              
              <div className="queue-cell">
                <span className="queue-badge">{task.queue}</span>
              </div>
              
              <div className="date-cell">
                {formatDate(task.created_at)}
              </div>
              
              <div className="duration-cell">
                {formatDuration(task.duration)}
              </div>
              
              <div className="retry-cell">
                {task.retry_count > 0 ? (
                  <span className="retry-count">{task.retry_count}</span>
                ) : (
                  <span className="no-retries">0</span>
                )}
              </div>
              
              <div className="worker-cell">
                {task.worker}
              </div>
            </div>
          ))}
        </div>
      </div>

      {sortedTasks.length === 0 && (
        <div className="no-results">
          No tasks match your current filters.
        </div>
      )}
    </div>
  );
};

export default TaskHistory;
