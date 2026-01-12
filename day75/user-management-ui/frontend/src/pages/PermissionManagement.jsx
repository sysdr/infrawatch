import React, { useState, useEffect } from 'react'
import {
  Box, Paper, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Switch, Chip
} from '@mui/material'
import { roleAPI, userAPI } from '../services/api'

export default function PermissionManagement() {
  const [users, setUsers] = useState([])
  const [roles, setRoles] = useState([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [usersRes, rolesRes] = await Promise.all([
        userAPI.getAll({}),
        roleAPI.getAll()
      ])
      setUsers(usersRes.data)
      setRoles(rolesRes.data)
    } catch (error) {
      console.error('Failed to load data:', error)
    }
  }

  const handleRoleToggle = async (userId, roleId, hasRole) => {
    try {
      if (hasRole) {
        await roleAPI.revoke(userId, roleId)
      } else {
        await roleAPI.assign(userId, roleId)
      }
      loadData()
    } catch (error) {
      console.error('Failed to toggle role:', error)
    }
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3 }}>Permission Management</Typography>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Email</TableCell>
                {roles.map((role) => (
                  <TableCell key={role.id} align="center">
                    <Box>
                      <Typography variant="body2">{role.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {role.permission_count} perms
                      </Typography>
                    </Box>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  {roles.map((role) => {
                    const hasRole = user.roles.includes(role.name)
                    return (
                      <TableCell key={role.id} align="center">
                        <Switch
                          checked={hasRole}
                          onChange={() => handleRoleToggle(user.id, role.id, hasRole)}
                          color="primary"
                        />
                      </TableCell>
                    )
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  )
}
