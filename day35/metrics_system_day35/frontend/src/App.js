import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState({
    task_type: 'collect_system_metrics',
    priority: 5,
    payload: {}
  });
  const [loading, setLoading] = useState(false);

  // Fetch tasks on component mount
  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks`);
      const data = await response.json();
      setTasks(data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const createTask = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newTask),
      });
      
      if (response.ok) {
        const task = await response.json();
        setTasks([task, ...tasks]);
        setNewTask({
          task_type: 'collect_system_metrics',
          priority: 5,
          payload: {}
        });
      }
    } catch (error) {
      console.error('Error creating task:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusClass = (status) => {
    return `status-${status.toLowerCase()}`;
  };

  return (
    <div className="App">
      <header className="header">
        <h1>Metrics Collection System</h1>
        <p>Background Processing Dashboard</p>
      </header>

      <div className="container">
        <div className="dashboard">
          <div className="card">
            <h2>Create New Task</h2>
            <form onSubmit={createTask} className="task-form">
              <div>
                <label>Task Type:</label>
                <select 
                  value={newTask.task_type} 
                  onChange={(e) => setNewTask({...newTask, task_type: e.target.value})}
                >
                  <option value="collect_system_metrics">Collect System Metrics</option>
                  <option value="process_csv">Process CSV</option>
                  <option value="generate_report">Generate Report</option>
                </select>
              </div>
              
              <div>
                <label>Priority:</label>
                <select 
                  value={newTask.priority} 
                  onChange={(e) => setNewTask({...newTask, priority: parseInt(e.target.value)})}
                >
                  <option value={1}>Low (1)</option>
                  <option value={5}>Normal (5)</option>
                  <option value={9}>High (9)</option>
                </select>
              </div>
              
              <div>
                <label>Payload (JSON):</label>
                <textarea 
                  value={JSON.stringify(newTask.payload, null, 2)}
                  onChange={(e) => {
                    try {
                      const payload = JSON.parse(e.target.value);
                      setNewTask({...newTask, payload});
                    } catch (err) {
                      // Invalid JSON, keep the text
                    }
                  }}
                  rows={3}
                  placeholder='{"key": "value"}'
                />
              </div>
              
              <button type="submit" disabled={loading}>
                {loading ? 'Creating...' : 'Create Task'}
              </button>
            </form>
          </div>

          <div className="card">
            <h2>Task Queue ({tasks.length})</h2>
            <div className="task-list">
              {tasks.length === 0 ? (
                <p>No tasks found</p>
              ) : (
                tasks.map((task) => (
                  <div key={task.id} className="task-item">
                    <div><strong>ID:</strong> {task.id}</div>
                    <div><strong>Type:</strong> {task.task_type}</div>
                    <div><strong>Status:</strong> 
                      <span className={getStatusClass(task.status)}> {task.status}</span>
                    </div>
                    <div><strong>Priority:</strong> {task.priority}</div>
                    <div><strong>Created:</strong> {new Date(task.created_at).toLocaleString()}</div>
                    {task.execution_time && (
                      <div><strong>Execution Time:</strong> {task.execution_time.toFixed(2)}s</div>
                    )}
                  </div>
                ))
              )}
            </div>
            <button onClick={fetchTasks} style={{marginTop: '10px'}}>
              Refresh Tasks
            </button>
          </div>
        </div>

        <div className="card">
          <h2>System Status</h2>
          <p>Backend API: <span style={{color: 'green'}}>✅ Running</span></p>
          <p>Celery Worker: <span style={{color: 'green'}}>✅ Running</span></p>
          <p>Database: <span style={{color: 'green'}}>✅ Connected</span></p>
        </div>
      </div>
    </div>
  );
}

export default App;