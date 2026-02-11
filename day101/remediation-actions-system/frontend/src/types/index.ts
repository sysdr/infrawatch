export interface RemediationAction {
  id: number;
  template_name: string;
  incident_id: string;
  status: ActionStatus;
  risk_score: number;
  blast_radius: number;
  parameters?: Record<string, any>;
  dry_run_result?: any;
  execution_result?: any;
  created_at: string;
  approved_at?: string;
  executed_at?: string;
  can_rollback: boolean;
}

export type ActionStatus = 
  | 'pending' | 'approved' | 'rejected' | 'validating' 
  | 'dry_run' | 'executing' | 'completed' | 'failed' | 'rolled_back';

export interface Template {
  id: number;
  name: string;
  description: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  requires_approval: boolean;
}

export interface Stats {
  total_actions: number;
  pending: number;
  completed: number;
  failed: number;
  success_rate: number;
}
