import React from 'react';
import { Button, ButtonGroup } from '@mui/material';

const BulkActions = ({ selectedCount, onBulkAction }) => {
  if (!selectedCount) return null;
  return (
    <ButtonGroup variant="outlined">
      <Button color="error" onClick={() => onBulkAction('delete')}>Delete Selected</Button>
    </ButtonGroup>
  );
};

export default BulkActions;
