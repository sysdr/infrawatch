import React, { useState } from 'react';
import styled from 'styled-components';
import { createTask } from '../../utils/api';

const Overlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const Modal = styled.div`
  background: #fff;
  border-radius: 4px;
  width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
`;

const Header = styled.div`
  padding: 20px;
  border-bottom: 1px solid #c3c4c7;
`;

const Title = styled.h2`
  margin: 0;
  font-size: 18px;
  color: #1d2327;
`;

const Body = styled.div`
  padding: 20px;
`;

const FormGroup = styled.div`
  margin-bottom: 15px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #1d2327;
`;

const Select = styled.select`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #8c8f94;
  border-radius: 4px;
  background: #fff;
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #8c8f94;
  border-radius: 4px;
  resize: vertical;
  min-height: 100px;
`;

const Footer = styled.div`
  padding: 20px;
  border-top: 1px solid #c3c4c7;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
`;

const Button = styled.button`
  padding: 8px 16px;
  border: 1px solid #8c8f94;
  border-radius: 3px;
  cursor: pointer;
  font-size: 14px;
  
  ${props => props.primary && `
    background: #2271b1;
    color: #fff;
    border-color: #2271b1;
    
    &:hover {
      background: #135e96;
    }
  `}
  
  ${props => !props.primary && `
    background: #fff;
    color: #2c3338;
    
    &:hover {
      background: #f6f7f7;
    }
  `}
`;

function CreateTaskModal({ onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    task_type: 'collect_system_metrics',
    priority: 'NORMAL',
    payload: '{}'
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      let payload = {};
      if (formData.payload.trim()) {
        payload = JSON.parse(formData.payload);
      }
      
      await createTask({
        task_type: formData.task_type,
        priority: formData.priority,
        payload: payload
      });
      
      onSuccess();
      onClose();
    } catch (error) {
      alert('Error creating task: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Overlay onClick={onClose}>
      <Modal onClick={e => e.stopPropagation()}>
        <Header>
          <Title>Create New Task</Title>
        </Header>
        <form onSubmit={handleSubmit}>
          <Body>
            <FormGroup>
              <Label>Task Type</Label>
              <Select
                value={formData.task_type}
                onChange={e => setFormData({...formData, task_type: e.target.value})}
              >
                <option value="collect_system_metrics">Collect System Metrics</option>
                <option value="process_csv">Process CSV File</option>
                <option value="generate_report">Generate Report</option>
              </Select>
            </FormGroup>
            
            <FormGroup>
              <Label>Priority</Label>
              <Select
                value={formData.priority}
                onChange={e => setFormData({...formData, priority: e.target.value})}
              >
                <option value="LOW">Low</option>
                <option value="NORMAL">Normal</option>
                <option value="HIGH">High</option>
              </Select>
            </FormGroup>
            
            <FormGroup>
              <Label>Payload (JSON)</Label>
              <TextArea
                placeholder='{"key": "value"}'
                value={formData.payload}
                onChange={e => setFormData({...formData, payload: e.target.value})}
              />
            </FormGroup>
          </Body>
          <Footer>
            <Button type="button" onClick={onClose} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" primary disabled={loading}>
              {loading ? 'Creating...' : 'Create Task'}
            </Button>
          </Footer>
        </form>
      </Modal>
    </Overlay>
  );
}

export default CreateTaskModal;
