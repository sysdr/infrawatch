import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Plus, Trash2 } from 'lucide-react';
import axios from 'axios';

const RulesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const RuleCard = styled.div`
  border: 1px solid #e5e7eb; /* gray-200 */
  border-radius: 8px;
  padding: 1rem;
  background: #f9fafb;
`;

const RuleHeader = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 0.5rem;
`;

const AddRuleForm = styled.form`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1rem;
  border: 2px dashed #e5e7eb;
  border-radius: 8px;
  margin-top: 1rem;
`;

const Input = styled.input`
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
`;

const Select = styled.select`
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
`;

const Button = styled.button`
  background: ${props => props.danger ? '#ef4444' : '#4f46e5'}; /* red-500 | indigo-600 */
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

function EscalationRules({ userId }) {
  const [rules, setRules] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newRule, setNewRule] = useState({
    category: 'security',
    priority_threshold: 'high',
    escalation_delay_minutes: 15,
    escalation_channels: [],
    escalation_contacts: [],
    max_attempts: 3
  });

  useEffect(() => {
    fetchRules();
  }, [userId]);

  const fetchRules = async () => {
    try {
      const response = await axios.get(`/api/v1/preferences/${userId}/escalation-rules`);
      setRules(response.data);
    } catch (error) {
      console.error('Error fetching escalation rules:', error);
    }
  };

  const addRule = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`/api/v1/preferences/${userId}/escalation-rules`, newRule);
      await fetchRules();
      setShowAddForm(false);
      setNewRule({
        category: 'security',
        priority_threshold: 'high',
        escalation_delay_minutes: 15,
        escalation_channels: [],
        escalation_contacts: [],
        max_attempts: 3
      });
    } catch (error) {
      console.error('Error adding escalation rule:', error);
    }
  };

  return (
    <div>
      <p style={{ color: '#718096', marginBottom: '1rem' }}>
        Define how notifications should escalate when not acknowledged
      </p>

      <RulesList>
        {rules.map(rule => (
          <RuleCard key={rule.id}>
            <RuleHeader>
              <div>
                <strong>{rule.category.toUpperCase()}</strong> notifications
                <span style={{ marginLeft: '1rem', color: '#718096' }}>
                  Priority: {rule.priority_threshold}
                </span>
              </div>
            </RuleHeader>
            <div style={{ fontSize: '0.9rem', color: '#4a5568' }}>
              Escalate after {rule.escalation_delay_minutes} minutes • 
              Max {rule.max_attempts} attempts
            </div>
            {rule.escalation_channels && rule.escalation_channels.length > 0 && (
              <div style={{ marginTop: '0.5rem', fontSize: '0.85rem' }}>
                Additional channels: {rule.escalation_channels.join(', ')}
              </div>
            )}
          </RuleCard>
        ))}
      </RulesList>

      {!showAddForm ? (
        <Button onClick={() => setShowAddForm(true)}>
          <Plus size={16} />
          Add Escalation Rule
        </Button>
      ) : (
        <AddRuleForm onSubmit={addRule}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Category
            </label>
            <Select
              value={newRule.category}
              onChange={(e) => setNewRule({ ...newRule, category: e.target.value })}
            >
              <option value="security">Security</option>
              <option value="system">System</option>
              <option value="social">Social</option>
              <option value="updates">Updates</option>
            </Select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Priority Threshold
            </label>
            <Select
              value={newRule.priority_threshold}
              onChange={(e) => setNewRule({ ...newRule, priority_threshold: e.target.value })}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </Select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Delay (minutes)
            </label>
            <Input
              type="number"
              value={newRule.escalation_delay_minutes}
              onChange={(e) => setNewRule({ ...newRule, escalation_delay_minutes: parseInt(e.target.value) })}
              min="1"
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Max Attempts
            </label>
            <Input
              type="number"
              value={newRule.max_attempts}
              onChange={(e) => setNewRule({ ...newRule, max_attempts: parseInt(e.target.value) })}
              min="1"
              max="10"
            />
          </div>

          <div style={{ gridColumn: '1 / -1', display: 'flex', gap: '1rem' }}>
            <Button type="submit">Add Rule</Button>
            <Button type="button" onClick={() => setShowAddForm(false)} danger>
              Cancel
            </Button>
          </div>
        </AddRuleForm>
      )}
    </div>
  );
}

export default EscalationRules;
