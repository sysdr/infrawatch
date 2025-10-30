import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { User, Plus } from 'lucide-react';
import axios from 'axios';

const Container = styled.div`
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
`;

const Card = styled.div`
  background: #ffffff;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
`;

const UserGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
`;

const UserCard = styled.div`
  border: 2px solid #e5e7eb; /* gray-200 */
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    border-color: #4f46e5; /* indigo-600 */
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(79, 70, 229, 0.15);
  }
`;

const CreateUserForm = styled.form`
  display: grid;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1rem;
  border: 2px dashed #cbd5e0;
  border-radius: 8px;
`;

const Input = styled.input`
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
`;

const Button = styled.button`
  background: #4f46e5; /* indigo-600 */
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
  
  &:hover {
    background: #4338ca; /* indigo-700 */
  }
`;

function UserSelector() {
  const [users, setUsers] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    phone: '',
    timezone: 'UTC'
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get('/api/v1/users/');
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const createUser = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/v1/users/', newUser);
      
      // Create default preferences for the new user
      await axios.post('/api/v1/preferences/', {
        user_id: response.data.id,
        global_quiet_hours_enabled: false
      });
      
      await fetchUsers();
      setShowCreateForm(false);
      setNewUser({ username: '', email: '', phone: '', timezone: 'UTC' });
    } catch (error) {
      console.error('Error creating user:', error);
    }
  };

  return (
    <Container>
      <Card>
        <h2>Select User</h2>
        <p>Choose a user to configure their notification preferences</p>
        
        <UserGrid>
          {users.map(user => (
            <UserCard key={user.id} onClick={() => navigate(`/preferences/${user.id}`)}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <User size={20} />
                <strong>{user.username}</strong>
              </div>
              <div style={{ marginTop: '0.5rem', color: '#718096' }}>
                {user.email}
              </div>
              <div style={{ marginTop: '0.25rem', fontSize: '0.85rem', color: '#a0aec0' }}>
                Timezone: {user.timezone}
              </div>
            </UserCard>
          ))}
          
          <UserCard onClick={() => setShowCreateForm(!showCreateForm)} style={{ 
            borderStyle: 'dashed',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '120px'
          }}>
            <div style={{ textAlign: 'center' }}>
              <Plus size={24} style={{ marginBottom: '0.5rem' }} />
              <div>Create New User</div>
            </div>
          </UserCard>
        </UserGrid>

        {showCreateForm && (
          <CreateUserForm onSubmit={createUser}>
            <h3>Create New User</h3>
            <Input
              placeholder="Username"
              value={newUser.username}
              onChange={(e) => setNewUser({...newUser, username: e.target.value})}
              required
            />
            <Input
              type="email"
              placeholder="Email"
              value={newUser.email}
              onChange={(e) => setNewUser({...newUser, email: e.target.value})}
              required
            />
            <Input
              placeholder="Phone (optional)"
              value={newUser.phone}
              onChange={(e) => setNewUser({...newUser, phone: e.target.value})}
            />
            <Input
              placeholder="Timezone"
              value={newUser.timezone}
              onChange={(e) => setNewUser({...newUser, timezone: e.target.value})}
            />
            <div style={{ display: 'flex', gap: '1rem' }}>
              <Button type="submit">Create User</Button>
              <Button type="button" onClick={() => setShowCreateForm(false)} style={{ background: '#gray' }}>
                Cancel
              </Button>
            </div>
          </CreateUserForm>
        )}
      </Card>
    </Container>
  );
}

export default UserSelector;
