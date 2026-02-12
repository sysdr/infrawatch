import React, { useState, useCallback } from 'react';
import ReactFlow, { MiniMap, Controls, Background, useNodesState, useEdgesState, addEdge } from 'reactflow';
import 'reactflow/dist/style.css';
import { Box, Paper, Button, TextField, Dialog, DialogTitle, DialogContent, DialogActions, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SaveIcon from '@mui/icons-material/Save';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { workflowApi } from '../../services/api';
import { toast } from 'react-toastify';

const nodeTypes = [
  { value: 'http_request', label: 'HTTP Request' },
  { value: 'database_query', label: 'Database Query' },
  { value: 'notification', label: 'Send Notification' },
  { value: 'script', label: 'Run Script' },
  { value: 'condition', label: 'Conditional' },
];

const WorkflowBuilder = ({ workflow, onSave }) => {
  const defNodes = workflow?.definition?.nodes || [];
  const defEdges = workflow?.definition?.edges || [];
  const [nodes, setNodes, onNodesChange] = useNodesState(defNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(defEdges);
  const [name, setName] = useState(workflow?.name || '');
  const [description, setDescription] = useState(workflow?.description || '');
  const [showNodeDialog, setShowNodeDialog] = useState(false);
  const [newNode, setNewNode] = useState({ type: 'http_request', label: '' });
  const [savedWorkflow, setSavedWorkflow] = useState(workflow);

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const addNode = () => {
    const id = `node_${Date.now()}`;
    setNodes((nds) => [...nds, {
      id,
      type: 'default',
      data: { label: newNode.label || newNode.type, type: newNode.type },
      position: { x: Math.random() * 400, y: Math.random() * 400 },
    }]);
    setShowNodeDialog(false);
    setNewNode({ type: 'http_request', label: '' });
  };

  const handleSave = async () => {
    const workflowData = { name, description, definition: { nodes, edges } };
    try {
      if (savedWorkflow?.id) {
        await workflowApi.update(savedWorkflow.id, workflowData);
        toast.success('Workflow updated');
      } else {
        const res = await workflowApi.create(workflowData);
        setSavedWorkflow(res.data);
        toast.success('Workflow created');
        if (onSave) onSave(res.data);
      }
    } catch (e) {
      toast.error('Failed to save workflow');
    }
  };

  const handleExecute = async () => {
    if (!savedWorkflow?.id) { toast.warning('Save workflow first'); return; }
    try {
      await workflowApi.execute(savedWorkflow.id, { trigger_type: 'manual' });
      toast.success('Execution started');
    } catch (e) { toast.error('Failed to execute'); }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField label="Workflow Name" value={name} onChange={(e) => setName(e.target.value)} fullWidth />
          <TextField label="Description" value={description} onChange={(e) => setDescription(e.target.value)} fullWidth />
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setShowNodeDialog(true)}>Add Step</Button>
          <Button variant="contained" color="primary" startIcon={<SaveIcon />} onClick={handleSave}>Save Workflow</Button>
          {savedWorkflow?.id && <Button variant="contained" color="success" startIcon={<PlayArrowIcon />} onClick={handleExecute}>Execute</Button>}
        </Box>
      </Paper>
      <Paper sx={{ flexGrow: 1, height: 600 }}>
        <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} fitView>
          <Controls /><MiniMap /><Background variant="dots" gap={12} size={1} />
        </ReactFlow>
      </Paper>
      <Dialog open={showNodeDialog} onClose={() => setShowNodeDialog(false)}>
        <DialogTitle>Add Step</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2, minWidth: 400 }}>
            <FormControl fullWidth>
              <InputLabel>Step Type</InputLabel>
              <Select value={newNode.type} onChange={(e) => setNewNode({ ...newNode, type: e.target.value })} label="Step Type">
                {nodeTypes.map((t) => <MenuItem key={t.value} value={t.value}>{t.label}</MenuItem>)}
              </Select>
            </FormControl>
            <TextField label="Step Label" value={newNode.label} onChange={(e) => setNewNode({ ...newNode, label: e.target.value })} fullWidth />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowNodeDialog(false)}>Cancel</Button>
          <Button onClick={addNode} variant="contained">Add</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkflowBuilder;
