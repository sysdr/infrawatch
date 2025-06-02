"""
Web server version of the distributed log processor with API endpoints.
"""

import asyncio
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from log_processor import DistributedLogProcessor, LogLevel


class LogProcessorHandler(BaseHTTPRequestHandler):
    """HTTP request handler for log processor API."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/stats':
            self.serve_stats()
        elif self.path == '/health':
            self.serve_health()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests for log ingestion."""
        if self.path == '/api/logs':
            self.ingest_log()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the HTML dashboard."""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Distributed Log Processor Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .stat { text-align: center; padding: 20px; background: #e3f2fd; border-radius: 8px; }
        .stat h3 { margin: 0; color: #1976d2; }
        .stat p { font-size: 24px; font-weight: bold; margin: 10px 0 0 0; }
        .logs { max-height: 400px; overflow-y: auto; font-family: monospace; font-size: 12px; }
        .log-entry { padding: 5px; border-bottom: 1px solid #eee; }
        .ERROR { background: #ffebee; }
        .WARNING { background: #fff3e0; }
        .INFO { background: #e8f5e8; }
        .button { background: #1976d2; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Distributed Log Processing System</h1>
        
        <div class="card">
            <h2>System Statistics</h2>
            <div class="stats" id="stats">
                Loading...
            </div>
        </div>
        
        <div class="card">
            <h2>Recent Log Events</h2>
            <div class="logs" id="logs">
                Loading...
            </div>
        </div>
        
        <div class="card">
            <h2>Test Log Ingestion</h2>
            <button class="button" onclick="sendTestLog()">Send Test Log</button>
            <button class="button" onclick="sendErrorLog()">Send Error Log</button>
        </div>
    </div>
    
    <script>
        let logBuffer = [];
        
        async function updateStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('stats').innerHTML = `
                    <div class="stat">
                        <h3>Processed</h3>
                        <p>${stats.processed_count}</p>
                    </div>
                    <div class="stat">
                        <h3>Errors</h3>
                        <p>${stats.error_count}</p>
                    </div>
                    <div class="stat">
                        <h3>Buffer Size</h3>
                        <p>${stats.buffer_size}</p>
                    </div>
                    <div class="stat">
                        <h3>Success Rate</h3>
                        <p>${stats.success_rate}%</p>
                    </div>`;
                
                // Update recent logs
                if (stats.recent_events) {
                    const logsDiv = document.getElementById('logs');
                    logsDiv.innerHTML = stats.recent_events.map(event => 
                        `<div class="log-entry ${event.level}">
                            [${event.timestamp}] ${event.level} ${event.service}: ${event.message}
                        </div>`
                    ).join('');
                }
            } catch (error) {
                console.error('Error updating stats:', error);
            }
        }
        
        async function sendTestLog() {
            const testLog = {
                timestamp: new Date().toISOString(),
                level: "INFO",
                message: "Test log from dashboard",
                service: "dashboard-test",
                metadata: { user: "demo", action: "test" }
            };
            
            try {
                await fetch('/api/logs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(testLog)
                });
                updateStats();
            } catch (error) {
                console.error('Error sending test log:', error);
            }
        }
        
        async function sendErrorLog() {
            const errorLog = {
                timestamp: new Date().toISOString(),
                level: "ERROR",
                message: "Simulated error from dashboard",
                service: "dashboard-error",
                metadata: { error_code: 500, retry_count: 1 }
            };
            
            try {
                await fetch('/api/logs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(testLog)
                });
                updateStats();
            } catch (error) {
                console.error('Error sending error log:', error);
            }
        }
        
        // Update stats every 2 seconds
        updateStats();
        setInterval(updateStats, 2000);
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_stats(self):
        """Serve processing statistics as JSON."""
        stats = self.server.processor.get_stats()
        
        # Add recent events
        recent_events = []
        for event in self.server.processor.event_buffer[-10:]:
            recent_events.append({
                "timestamp": event.timestamp.strftime("%H:%M:%S"),
                "level": event.level.value,
                "service": event.service,
                "message": event.message[:50] + "..." if len(event.message) > 50 else event.message
            })
        
        stats["recent_events"] = recent_events
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode())
    
    def serve_health(self):
        """Health check endpoint."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "healthy"}).encode())
    
    def ingest_log(self):
        """Handle log ingestion via POST."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            log_data = json.loads(post_data.decode('utf-8'))
            
            # Process the log
            raw_event = json.dumps(log_data)
            result = self.server.processor.process_event(raw_event)
            
            if result:
                response = {"status": "success", "message": "Log processed"}
            else:
                response = {"status": "error", "message": "Failed to process log"}
            
            self.send_response(200 if result else 400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())


class LogProcessorServer:
    """HTTP server with integrated log processor."""
    
    def __init__(self, host='0.0.0.0', port=8000):
        self.host = host
        self.port = port
        self.processor = DistributedLogProcessor(buffer_size=100)
        self.server = None
        
    def start(self):
        """Start the HTTP server."""
        self.server = HTTPServer((self.host, self.port), LogProcessorHandler)
        self.server.processor = self.processor
        
        print(f"🚀 Starting Distributed Log Processor Server")
        print(f"📊 Dashboard: http://localhost:{self.port}")
        print(f"🔧 API: http://localhost:{self.port}/api/stats")
        print(f"❤️ Health: http://localhost:{self.port}/health")
        print("Press Ctrl+C to stop\n")
        
        # Start log simulation in background
        simulation_thread = threading.Thread(target=self.simulate_logs, daemon=True)
        simulation_thread.start()
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            self.server.shutdown()
    
    def simulate_logs(self):
        """Simulate incoming log events."""
        sample_events = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "User authentication successful",
                "service": "auth-service",
                "metadata": {"user_id": "user123", "session_id": "sess456"}
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "WARNING",
                "message": "High CPU usage detected", 
                "service": "monitoring-service",
                "metadata": {"cpu_usage": "85%", "threshold": "80%"}
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "message": "Database connection failed",
                "service": "user-service", 
                "metadata": {"error_code": "CONN_TIMEOUT", "retry_count": 3}
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "DEBUG",
                "message": "Cache miss for user profile",
                "service": "cache-service",
                "metadata": {"cache_key": "profile:user123", "miss_rate": "8%"}
            }
        ]
        
        while True:
            # Process a random event every 3-8 seconds
            import random
            event = random.choice(sample_events)
            event["timestamp"] = datetime.now().isoformat()
            
            raw_event = json.dumps(event)
            processed = self.processor.process_event(raw_event)
            
            if processed:
                print(f"📝 [{processed.level.value}] {processed.service}: {processed.message}")
            
            time.sleep(random.uniform(3, 8))


if __name__ == "__main__":
    server = LogProcessorServer()
    server.start()