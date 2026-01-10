import React from 'react';

function ArchitectureDiagram() {
  return (
    <svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
      {/* White background */}
      <rect width="800" height="600" fill="#ffffff" />
      
      {/* Title */}
      <text x="400" y="30" textAnchor="middle" fontSize="20" fontWeight="bold" fill="#333">
        User Management API Architecture
      </text>
      
      {/* API Layer */}
      <g transform="translate(100, 80)">
        {/* Container with shadow */}
        <ellipse cx="300" cy="60" rx="280" ry="55" fill="#e8f5e9" opacity="0.3" transform="translate(3, 3)" />
        <ellipse cx="300" cy="60" rx="280" ry="55" fill="#e8f5e9" stroke="#4caf50" strokeWidth="2" />
        <text x="300" y="40" textAnchor="middle" fontSize="16" fontWeight="bold" fill="#2e7d32">
          API Layer
        </text>
        <text x="300" y="60" textAnchor="middle" fontSize="12" fill="#555">
          FastAPI • HTTP Endpoints
        </text>
        <text x="300" y="78" textAnchor="middle" fontSize="11" fill="#666">
          /users • /teams • /permissions • /activity
        </text>
      </g>
      
      {/* Service Layer */}
      <g transform="translate(100, 220)">
        <rect x="30" y="0" width="150" height="90" rx="15" fill="#fff3e0" opacity="0.3" transform="translate(2, 2)" />
        <rect x="30" y="0" width="150" height="90" rx="15" fill="#fff3e0" stroke="#ff9800" strokeWidth="2" />
        <text x="105" y="30" textAnchor="middle" fontSize="14" fontWeight="bold" fill="#e65100">
          Permission
        </text>
        <text x="105" y="48" textAnchor="middle" fontSize="11" fill="#666">
          Service
        </text>
        <text x="105" y="70" textAnchor="middle" fontSize="10" fill="#777">
          Compute • Check
        </text>
        <text x="105" y="84" textAnchor="middle" fontSize="10" fill="#777">
          Invalidate Cache
        </text>
        
        <rect x="220" y="0" width="150" height="90" rx="15" fill="#fff3e0" opacity="0.3" transform="translate(2, 2)" />
        <rect x="220" y="0" width="150" height="90" rx="15" fill="#fff3e0" stroke="#ff9800" strokeWidth="2" />
        <text x="295" y="30" textAnchor="middle" fontSize="14" fontWeight="bold" fill="#e65100">
          Cache
        </text>
        <text x="295" y="48" textAnchor="middle" fontSize="11" fill="#666">
          Service
        </text>
        <text x="295" y="70" textAnchor="middle" fontSize="10" fill="#777">
          Get • Set • Delete
        </text>
        <text x="295" y="84" textAnchor="middle" fontSize="10" fill="#777">
          Pattern Match
        </text>
        
        <rect x="410" y="0" width="150" height="90" rx="15" fill="#fff3e0" opacity="0.3" transform="translate(2, 2)" />
        <rect x="410" y="0" width="150" height="90" rx="15" fill="#fff3e0" stroke="#ff9800" strokeWidth="2" />
        <text x="485" y="30" textAnchor="middle" fontSize="14" fontWeight="bold" fill="#e65100">
          Activity
        </text>
        <text x="485" y="48" textAnchor="middle" fontSize="11" fill="#666">
          Service
        </text>
        <text x="485" y="70" textAnchor="middle" fontSize="10" fill="#777">
          Track • Aggregate
        </text>
        <text x="485" y="84" textAnchor="middle" fontSize="10" fill="#777">
          Time-Series
        </text>
      </g>
      
      {/* Data Layer */}
      <g transform="translate(100, 390)">
        <ellipse cx="150" cy="60" rx="140" ry="55" fill="#e3f2fd" opacity="0.3" transform="translate(2, 2)" />
        <ellipse cx="150" cy="60" rx="140" ry="55" fill="#e3f2fd" stroke="#2196f3" strokeWidth="2" />
        <text x="150" y="48" textAnchor="middle" fontSize="14" fontWeight="bold" fill="#1565c0">
          PostgreSQL
        </text>
        <text x="150" y="68" textAnchor="middle" fontSize="11" fill="#666">
          Persistent Storage
        </text>
        <text x="150" y="84" textAnchor="middle" fontSize="10" fill="#777">
          Users • Teams • Permissions
        </text>
        
        <ellipse cx="450" cy="60" rx="140" ry="55" fill="#e3f2fd" opacity="0.3" transform="translate(2, 2)" />
        <ellipse cx="450" cy="60" rx="140" ry="55" fill="#e3f2fd" stroke="#2196f3" strokeWidth="2" />
        <text x="450" y="48" textAnchor="middle" fontSize="14" fontWeight="bold" fill="#1565c0">
          Redis
        </text>
        <text x="450" y="68" textAnchor="middle" fontSize="11" fill="#666">
          Hot Cache
        </text>
        <text x="450" y="84" textAnchor="middle" fontSize="10" fill="#777">
          Permissions • User Data
        </text>
      </g>
      
      {/* Arrows - API to Services */}
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <polygon points="0 0, 10 3, 0 6" fill="#666" />
        </marker>
        <marker id="arrowhead2" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
          <polygon points="0 0, 10 3, 0 6" fill="#666" />
        </marker>
      </defs>
      
      <g stroke="#666" strokeWidth="2" fill="none" markerEnd="url(#arrowhead)">
        <path d="M 300 145 L 235 220" strokeDasharray="5,5" />
        <path d="M 400 145 L 395 220" />
        <path d="M 500 145 L 565 220" strokeDasharray="5,5" />
      </g>
      
      {/* Services to Data */}
      <g stroke="#666" strokeWidth="2" fill="none" markerEnd="url(#arrowhead2)">
        <path d="M 205 315 L 235 390" />
        <path d="M 395 315 L 465 390" />
      </g>
      
      {/* Legend */}
      <g transform="translate(580, 80)">
        <text x="0" y="0" fontSize="12" fontWeight="bold" fill="#333">Performance</text>
        <text x="0" y="25" fontSize="10" fill="#4caf50">● API: &lt;50ms</text>
        <text x="0" y="45" fontSize="10" fill="#ff9800">● Service: &lt;5ms</text>
        <text x="0" y="65" fontSize="10" fill="#2196f3">● Cache: &lt;1ms</text>
        
        <text x="0" y="100" fontSize="12" fontWeight="bold" fill="#333">Scale</text>
        <text x="0" y="120" fontSize="10" fill="#666">10K+ requests/sec</text>
        <text x="0" y="140" fontSize="10" fill="#666">100K+ users</text>
        <text x="0" y="160" fontSize="10" fill="#666">95%+ cache hit</text>
      </g>
      
      {/* Cache flow indicator */}
      <g transform="translate(50, 500)">
        <path d="M 0 0 Q 100 -50, 200 0" stroke="#ff9800" strokeWidth="2" fill="none" strokeDasharray="3,3" />
        <text x="100" y="-60" textAnchor="middle" fontSize="10" fill="#e65100">Cache Shortcut</text>
      </g>
    </svg>
  );
}

export default ArchitectureDiagram;

