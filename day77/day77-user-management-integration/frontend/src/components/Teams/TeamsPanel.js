import React, { useState, useEffect } from 'react';
import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  Box, Typography, IconButton, Select, MenuItem, FormControl, InputLabel
} from '@mui/material';
import { teamAPI, userAPI } from '../../services/api';
import toast from 'react-hot-toast';
import AddIcon from '@mui/icons-material/Add';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import RefreshIcon from '@mui/icons-material/Refresh';

function TeamsPanel() {
  const [teams, setTeams] = useState([]);
  const [users, setUsers] = useState([]);
  const [openTeam, setOpenTeam] = useState(false);
  const [openMember, setOpenMember] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teamData, setTeamData] = useState({
    name: '',
    description: '',
    parent_id: null
  });
  const [memberData, setMemberData] = useState({
    user_id: '',
    role: 'member'
  });

  useEffect(() => {
    loadTeams();
    loadUsers();
  }, []);

  const loadTeams = async () => {
    try {
      const response = await teamAPI.getAll();
      setTeams(response.data);
    } catch (error) {
      toast.error('Error loading teams');
    }
  };

  const loadUsers = async () => {
    try {
      const response = await userAPI.getAll();
      setUsers(response.data);
    } catch (error) {
      console.error('Error loading users');
    }
  };

  const handleCreateTeam = async () => {
    try {
      await teamAPI.create(teamData);
      toast.success('Team created successfully');
      setOpenTeam(false);
      setTeamData({ name: '', description: '', parent_id: null });
      loadTeams();
    } catch (error) {
      toast.error('Error creating team');
    }
  };

  const handleAddMember = async () => {
    try {
      await teamAPI.addMember(selectedTeam, memberData);
      toast.success('Member added successfully');
      setOpenMember(false);
      setMemberData({ user_id: '', role: 'member' });
      loadTeams();
    } catch (error) {
      toast.error('Error adding member');
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Team Management</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadTeams}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenTeam(true)}
          >
            Create Team
          </Button>
        </Box>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Parent Team</TableCell>
              <TableCell>Created At</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {teams.map((team) => (
              <TableRow key={team.id}>
                <TableCell>{team.id}</TableCell>
                <TableCell>{team.name}</TableCell>
                <TableCell>{team.description || '-'}</TableCell>
                <TableCell>
                  {team.parent_id ? teams.find(t => t.id === team.parent_id)?.name || '-' : '-'}
                </TableCell>
                <TableCell>{new Date(team.created_at).toLocaleDateString()}</TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={() => {
                      setSelectedTeam(team.id);
                      setOpenMember(true);
                    }}
                    color="primary"
                  >
                    <PersonAddIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openTeam} onClose={() => setOpenTeam(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Team</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Name"
            value={teamData.name}
            onChange={(e) => setTeamData({ ...teamData, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Description"
            value={teamData.description}
            onChange={(e) => setTeamData({ ...teamData, description: e.target.value })}
            margin="normal"
            multiline
            rows={3}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Parent Team</InputLabel>
            <Select
              value={teamData.parent_id || ''}
              onChange={(e) => setTeamData({ ...teamData, parent_id: e.target.value || null })}
            >
              <MenuItem value="">None</MenuItem>
              {teams.map((team) => (
                <MenuItem key={team.id} value={team.id}>{team.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenTeam(false)}>Cancel</Button>
          <Button onClick={handleCreateTeam} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={openMember} onClose={() => setOpenMember(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Team Member</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>User</InputLabel>
            <Select
              value={memberData.user_id}
              onChange={(e) => setMemberData({ ...memberData, user_id: e.target.value })}
            >
              {users.map((user) => (
                <MenuItem key={user.id} value={user.id}>
                  {user.username} ({user.email})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Role</InputLabel>
            <Select
              value={memberData.role}
              onChange={(e) => setMemberData({ ...memberData, role: e.target.value })}
            >
              <MenuItem value="member">Member</MenuItem>
              <MenuItem value="maintainer">Maintainer</MenuItem>
              <MenuItem value="owner">Owner</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenMember(false)}>Cancel</Button>
          <Button onClick={handleAddMember} variant="contained">Add Member</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default TeamsPanel;
