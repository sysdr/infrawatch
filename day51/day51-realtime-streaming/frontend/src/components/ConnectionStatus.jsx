import React from 'react'

function ConnectionStatus({ connected }) {
  return (
    <div className="connection-status">
      <div className={`status-indicator ${connected ? 'connected' : 'disconnected'}`} />
      <span>{connected ? 'Connected' : 'Disconnected'}</span>
    </div>
  )
}

export default ConnectionStatus
