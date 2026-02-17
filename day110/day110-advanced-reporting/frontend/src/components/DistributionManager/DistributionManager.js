import React, { useState, useEffect } from 'react';
import {
  Box, Paper, Typography, Grid, Button, TextField, Card, CardContent,
  Alert, Chip, IconButton, List, ListItem, ListItemText
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { distributionAPI } from '../../services/api';

export default function DistributionManager() {
  const [distributionLists, setDistributionLists] = useState([]);
  const [listName, setListName] = useState('');
  const [recipients, setRecipients] = useState(['']);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadDistributionLists();
  }, []);

  const loadDistributionLists = async () => {
    try {
      const res = await distributionAPI.listDistributionLists();
      setDistributionLists(res.data);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to load distribution lists' });
    }
  };

  const handleAddRecipient = () => {
    setRecipients([...recipients, '']);
  };

  const handleRemoveRecipient = (index) => {
    setRecipients(recipients.filter((_, i) => i !== index));
  };

  const handleRecipientChange = (index, value) => {
    const updated = [...recipients];
    updated[index] = value;
    setRecipients(updated);
  };

  const handleCreateList = async () => {
    if (!listName || recipients.filter(r => r.trim()).length === 0) {
      setMessage({ type: 'error', text: 'Please provide list name and at least one recipient' });
      return;
    }

    try {
      await distributionAPI.createDistributionList({
        name: listName,
        recipients: recipients.filter(r => r.trim()).map(email => ({
          type: 'email',
          address: email.trim()
        })),
        channels: ['email']
      });

      setMessage({ type: 'success', text: 'Distribution list created' });
      setListName('');
      setRecipients(['']);
      await loadDistributionLists();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to create distribution list' });
    }
  };

  return (
    <Box>
      {message && (
        <Alert severity={message.type} onClose={() => setMessage(null)} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Create Distribution List</Typography>
            
            <TextField
              fullWidth
              label="List Name"
              value={listName}
              onChange={(e) => setListName(e.target.value)}
              margin="normal"
            />
            
            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>Recipients</Typography>
            {recipients.map((recipient, index) => (
              <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <TextField
                  fullWidth
                  label={`Email ${index + 1}`}
                  value={recipient}
                  onChange={(e) => handleRecipientChange(index, e.target.value)}
                  size="small"
                />
                <IconButton
                  color="error"
                  onClick={() => handleRemoveRecipient(index)}
                  disabled={recipients.length === 1}
                >
                  <DeleteIcon />
                </IconButton>
              </Box>
            ))}
            
            <Button
              startIcon={<AddIcon />}
              onClick={handleAddRecipient}
              size="small"
              sx={{ mb: 2 }}
            >
              Add Recipient
            </Button>
            
            <Button
              fullWidth
              variant="contained"
              onClick={handleCreateList}
            >
              Create List
            </Button>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={7}>
          <Typography variant="h6" gutterBottom>Distribution Lists</Typography>
          
          <Grid container spacing={2}>
            {distributionLists.map(list => (
              <Grid item xs={12} key={list.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{list.name}</Typography>
                    <Box sx={{ mt: 1 }}>
                      <Chip 
                        label={`${list.recipients.length} recipients`} 
                        size="small"
                        sx={{ mr: 1 }}
                      />
                      <Chip 
                        label={`Channels: ${list.channels.join(', ')}`} 
                        size="small"
                        variant="outlined"
                      />
                    </Box>
                    
                    <List dense sx={{ mt: 1 }}>
                      {list.recipients.slice(0, 5).map((recipient, idx) => (
                        <ListItem key={idx}>
                          <ListItemText 
                            primary={recipient.address}
                            secondary={recipient.type}
                          />
                        </ListItem>
                      ))}
                      {list.recipients.length > 5 && (
                        <ListItem>
                          <ListItemText secondary={`... and ${list.recipients.length - 5} more`} />
                        </ListItem>
                      )}
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
}
