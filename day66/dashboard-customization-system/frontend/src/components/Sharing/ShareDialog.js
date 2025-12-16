import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Box,
  Typography,
  Alert
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { dashboardApi } from '../../services/api';

const ShareDialog = ({ open, dashboardId, onClose }) => {
  const [shares, setShares] = useState([]);
  const [permission, setPermission] = useState('view');
  const [expiresIn, setExpiresIn] = useState(24);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (open && dashboardId) {
      loadShares();
    }
  }, [open, dashboardId]);

  const loadShares = async () => {
    try {
      const response = await dashboardApi.listShares(dashboardId);
      setShares(response.data);
    } catch (error) {
      console.error('Failed to load shares:', error);
    }
  };

  const handleCreateShare = async () => {
    try {
      await dashboardApi.createShare(dashboardId, {
        permission,
        expires_in_hours: expiresIn
      });
      loadShares();
    } catch (error) {
      console.error('Failed to create share:', error);
    }
  };

  const handleRevokeShare = async (shareId) => {
    try {
      await dashboardApi.revokeShare(shareId);
      loadShares();
    } catch (error) {
      console.error('Failed to revoke share:', error);
    }
  };

  const handleCopyLink = (token) => {
    const url = `${window.location.origin}/shared/${token}`;
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      aria-labelledby="share-dialog-title"
    >
      <DialogTitle id="share-dialog-title">Share Dashboard</DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>Create New Share Link</Typography>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>Permission</InputLabel>
              <Select
                value={permission}
                onChange={(e) => setPermission(e.target.value)}
              >
                <MenuItem value="view">View Only</MenuItem>
                <MenuItem value="edit">Edit</MenuItem>
                <MenuItem value="admin">Admin</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              label="Expires in (hours)"
              type="number"
              value={expiresIn}
              onChange={(e) => setExpiresIn(parseInt(e.target.value))}
              sx={{ width: 150 }}
            />
            
            <Button variant="contained" onClick={handleCreateShare}>
              Generate Link
            </Button>
          </Box>
          
          {copied && <Alert severity="success">Link copied to clipboard!</Alert>}
        </Box>

        <Typography variant="h6" gutterBottom>Active Shares</Typography>
        <List>
          {shares.map((share) => (
            <ListItem
              key={share.id}
              secondaryAction={
                <Box>
                  <IconButton
                    edge="end"
                    onClick={() => handleCopyLink(share.share_token)}
                    sx={{ mr: 1 }}
                  >
                    <ContentCopyIcon />
                  </IconButton>
                  <IconButton
                    edge="end"
                    onClick={() => handleRevokeShare(share.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              }
            >
              <ListItemText
                primary={`Permission: ${share.permission}`}
                secondary={
                  share.expires_at
                    ? `Expires: ${new Date(share.expires_at).toLocaleString()}`
                    : 'No expiration'
                }
              />
            </ListItem>
          ))}
        </List>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ShareDialog;
