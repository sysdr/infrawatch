import React, { useState, useEffect } from 'react'
import {
  Box, Paper, Typography, Button, Grid, Card, CardContent, CardActions,
  List, ListItem, ListItemText, ListItemAvatar, Avatar, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  MenuItem, Select, FormControl, InputLabel
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import GroupsIcon from '@mui/icons-material/Groups'
import PersonAddIcon from '@mui/icons-material/PersonAdd'
import { teamAPI, userAPI } from '../services/api'
import { useWebSocket } from '../contexts/WebSocketContext'

export default function TeamManagement() {
  const [teams, setTeams] = useState([])
  const [users, setUsers] = useState([])
  const [selectedTeam, setSelectedTeam] = useState(null)
  const [openDialog, setOpenDialog] = useState(false)
  const [openAddMemberDialog, setOpenAddMemberDialog] = useState(false)
  const [selectedUserId, setSelectedUserId] = useState('')
  const [formData, setFormData] = useState({ name: '', description: '' })
  const { messages } = useWebSocket()

  useEffect(() => {
    loadTeams()
    loadUsers()
  }, [])

  useEffect(() => {
    const lastMessage = messages[0]
    if (lastMessage?.type?.startsWith('team_')) {
      loadTeams()
    }
  }, [messages])

  const loadTeams = async () => {
    try {
      const response = await teamAPI.getAll()
      setTeams(response.data)
    } catch (error) {
      console.error('Failed to load teams:', error)
    }
  }

  const loadUsers = async () => {
    try {
      const response = await userAPI.getAll({})
      setUsers(response.data)
    } catch (error) {
      console.error('Failed to load users:', error)
    }
  }

  const handleCreateTeam = async () => {
    try {
      await teamAPI.create(formData)
      setOpenDialog(false)
      setFormData({ name: '', description: '' })
      loadTeams()
    } catch (error) {
      console.error('Failed to create team:', error)
    }
  }

  const handleOpenAddMember = (team) => {
    setSelectedTeam(team)
    setOpenAddMemberDialog(true)
    setSelectedUserId('')
  }

  const handleAddMember = async () => {
    if (!selectedTeam || !selectedUserId) return
    
    try {
      await teamAPI.addMember(selectedTeam.id, selectedUserId)
      setOpenAddMemberDialog(false)
      setSelectedTeam(null)
      setSelectedUserId('')
      loadTeams()
    } catch (error) {
      console.error('Failed to add member:', error)
      alert('Failed to add member: ' + (error.response?.data?.detail || error.message))
    }
  }

  // Get all available users (backend handles duplicate prevention)
  const getAvailableUsers = () => {
    return users
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Team Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Create Team
        </Button>
      </Box>

      <Grid container spacing={3}>
        {teams.map((team) => (
          <Grid item xs={12} md={6} lg={4} key={team.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <GroupsIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">{team.name}</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {team.description}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {team.member_count} members
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  size="small" 
                  startIcon={<PersonAddIcon />}
                  onClick={() => handleOpenAddMember(team)}
                >
                  Add Member
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Team</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Team Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Description"
            multiline
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateTeam} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={openAddMemberDialog} onClose={() => setOpenAddMemberDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Member to {selectedTeam?.name}</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>Select User</InputLabel>
            <Select
              value={selectedUserId}
              label="Select User"
              onChange={(e) => setSelectedUserId(e.target.value)}
            >
              {getAvailableUsers().map((user) => (
                <MenuItem key={user.id} value={user.id}>
                  {user.name} ({user.email})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddMemberDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleAddMember} 
            variant="contained"
            disabled={!selectedUserId}
          >
            Add Member
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
