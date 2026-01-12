import React, { useState, useEffect } from 'react'
import {
  Box, Paper, Typography, Button, TextField, MenuItem,
  Dialog, DialogTitle, DialogContent, DialogActions,
  Chip, Avatar, IconButton, Tooltip
} from '@mui/material'
import { DataGrid } from '@mui/x-data-grid'
import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import SearchIcon from '@mui/icons-material/Search'
import { userAPI } from '../services/api'
import { useWebSocket } from '../contexts/WebSocketContext'

export default function UserManagement() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [roleFilter, setRoleFilter] = useState('all')
  const [openDialog, setOpenDialog] = useState(false)
  const [editUser, setEditUser] = useState(null)
  const [formData, setFormData] = useState({ email: '', name: '', avatar: '' })
  const { messages } = useWebSocket()

  useEffect(() => {
    loadUsers()
  }, [searchTerm, statusFilter, roleFilter])

  useEffect(() => {
    // Real-time updates via WebSocket
    const lastMessage = messages[0]
    if (lastMessage?.type === 'user_created' || lastMessage?.type === 'user_updated' || lastMessage?.type === 'user_deleted') {
      loadUsers()
    }
  }, [messages])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const params = {}
      if (searchTerm) params.search = searchTerm
      if (statusFilter !== 'all') params.status = statusFilter
      if (roleFilter !== 'all') params.role = roleFilter
      
      const response = await userAPI.getAll(params)
      setUsers(response.data)
    } catch (error) {
      console.error('Failed to load users:', error)
    }
    setLoading(false)
  }

  const handleCreate = async () => {
    try {
      await userAPI.create(formData)
      setOpenDialog(false)
      setFormData({ email: '', name: '', avatar: '' })
      loadUsers()
    } catch (error) {
      console.error('Failed to create user:', error)
    }
  }

  const handleUpdate = async () => {
    try {
      await userAPI.update(editUser.id, formData)
      setOpenDialog(false)
      setEditUser(null)
      setFormData({ email: '', name: '', avatar: '' })
      loadUsers()
    } catch (error) {
      console.error('Failed to update user:', error)
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Delete this user?')) {
      try {
        await userAPI.delete(id)
        loadUsers()
      } catch (error) {
        console.error('Failed to delete user:', error)
      }
    }
  }

  const columns = [
    {
      field: 'avatar',
      headerName: '',
      width: 70,
      renderCell: (params) => <Avatar src={params.value} alt={params.row.name} />,
    },
    { field: 'name', headerName: 'Name', width: 200 },
    { field: 'email', headerName: 'Email', width: 250 },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={params.value === 'active' ? 'success' : 'default'}
          size="small"
        />
      ),
    },
    {
      field: 'roles',
      headerName: 'Roles',
      width: 200,
      renderCell: (params) => (
        <Box>
          {params.value.map((role) => (
            <Chip key={role} label={role} size="small" sx={{ mr: 0.5 }} />
          ))}
        </Box>
      ),
    },
    {
      field: 'teams',
      headerName: 'Teams',
      width: 200,
      renderCell: (params) => (
        <Box>
          {params.value.map((team) => (
            <Chip key={team} label={team} size="small" variant="outlined" sx={{ mr: 0.5 }} />
          ))}
        </Box>
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      renderCell: (params) => (
        <Box>
          <Tooltip title="Edit">
            <IconButton
              size="small"
              onClick={() => {
                setEditUser(params.row)
                setFormData({ name: params.row.name, email: params.row.email, avatar: params.row.avatar })
                setOpenDialog(true)
              }}
            >
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton size="small" onClick={() => handleDelete(params.row.id)} color="error">
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">User Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            setEditUser(null)
            setFormData({ email: '', name: '', avatar: '' })
            setOpenDialog(true)
          }}
        >
          Add User
        </Button>
      </Box>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.disabled' }} />,
            }}
            sx={{ flexGrow: 1 }}
          />
          <TextField
            select
            label="Status"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            sx={{ width: 150 }}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="inactive">Inactive</MenuItem>
          </TextField>
          <TextField
            select
            label="Role"
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            sx={{ width: 150 }}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="Admin">Admin</MenuItem>
            <MenuItem value="Editor">Editor</MenuItem>
            <MenuItem value="Viewer">Viewer</MenuItem>
          </TextField>
        </Box>
      </Paper>

      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={users}
          columns={columns}
          pageSize={10}
          rowsPerPageOptions={[10, 25, 50]}
          loading={loading}
          disableSelectionOnClick
        />
      </Paper>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editUser ? 'Edit User' : 'Create User'}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            margin="normal"
            disabled={!!editUser}
          />
          <TextField
            fullWidth
            label="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Avatar URL"
            value={formData.avatar}
            onChange={(e) => setFormData({ ...formData, avatar: e.target.value })}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={editUser ? handleUpdate : handleCreate} variant="contained">
            {editUser ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
