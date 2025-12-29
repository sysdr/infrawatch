import React, { useState, useEffect } from 'react';
import {
  Paper, Typography, TextField, Button, Box, Alert, List, ListItem,
  ListItemText, Chip, CircularProgress
} from '@mui/material';
import { addTeamMember, getTeamMembers } from '../../services/api';

function TeamMembers({ teamId }) {
  const [userId, setUserId] = useState('');
  const [message, setMessage] = useState(null);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMembers();
  }, [teamId]);

  const loadMembers = async () => {
    try {
      setLoading(true);
      const membersList = await getTeamMembers(teamId);
      setMembers(membersList);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load members:', error);
      setMessage({ type: 'error', text: 'Failed to load team members' });
      setLoading(false);
    }
  };

  const handleAddMember = async () => {
    if (!userId.trim()) {
      setMessage({ type: 'error', text: 'Please enter a user ID' });
      return;
    }
    
    try {
      const member = await addTeamMember(teamId, {
        user_id: parseInt(userId),
        role_id: 1  // Assume role ID 1 exists
      });
      
      // Reload members to get updated list
      await loadMembers();
      setMessage({ type: 'success', text: 'Member added successfully' });
      setUserId('');
    } catch (error) {
      console.error('Failed to add member:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to add member';
      setMessage({ type: 'error', text: errorMsg });
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>Team Members</Typography>
      
      {message && (
        <Alert severity={message.type} onClose={() => setMessage(null)} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>Add Member</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            label="User ID"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            type="number"
            size="small"
          />
          <Button variant="contained" onClick={handleAddMember}>
            Add Member
          </Button>
        </Box>
      </Paper>

      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>Current Members ({members.length})</Typography>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : members.length > 0 ? (
          <List>
            {members.map((member) => (
              <ListItem key={member.id}>
                <ListItemText
                  primary={`User ID: ${member.user_id}`}
                  secondary={`Role ID: ${member.role_id} | Joined: ${new Date(member.joined_at).toLocaleString()}`}
                />
                <Box>
                  {(member.effective_permissions || []).map(perm => (
                    <Chip key={perm} label={perm} size="small" sx={{ ml: 0.5 }} />
                  ))}
                </Box>
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body2" color="textSecondary" sx={{ p: 2 }}>
            No members yet. Add members using the form above.
          </Typography>
        )}
      </Paper>
    </Box>
  );
}

export default TeamMembers;
