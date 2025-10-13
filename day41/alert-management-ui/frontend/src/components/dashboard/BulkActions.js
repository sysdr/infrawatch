import React from 'react';

const BulkActions = ({ selectedCount, onAction }) => {
  if (selectedCount === 0) return null;

  return (
    <div className="bulk-actions">
      <span>{selectedCount} selected</span>
      <button 
        className="btn btn-primary" 
        onClick={() => onAction('acknowledge')}
      >
        Acknowledge
      </button>
      <button 
        className="btn btn-success" 
        onClick={() => onAction('resolve')}
      >
        Resolve
      </button>
    </div>
  );
};

export default BulkActions;
