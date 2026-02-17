import numpy as np
from typing import List, Dict, Set, Tuple
from datetime import datetime
from models.database import Metric, CausalRelation, ImpactAssessment, SessionLocal
from collections import deque
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImpactAssessor:
    def __init__(self):
        self.db = SessionLocal()
    
    def assess_impact(self, root_metric_id: int, causal_graph: Dict[int, List[Tuple[int, float]]]) -> Dict:
        """
        Compute impact radius from a root cause metric
        Performs BFS traversal of causal graph to find all affected metrics
        """
        logger.info(f"Assessing impact from metric {root_metric_id}...")
        
        affected_metrics = []
        visited = set()
        queue = deque([(root_metric_id, 1.0, 0)])  # (metric_id, cumulative_probability, depth)
        
        services_affected = set()
        
        while queue:
            current_id, cum_prob, depth = queue.popleft()
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            # Get metric details
            metric = self.db.query(Metric).filter(Metric.id == current_id).first()
            if metric and current_id != root_metric_id:
                affected_metrics.append({
                    'metric_id': current_id,
                    'metric_name': metric.name,
                    'service': metric.service,
                    'probability': cum_prob,
                    'severity': self.calculate_severity(cum_prob, depth),
                    'depth': depth
                })
                services_affected.add(metric.service)
            
            # Explore children
            if current_id in causal_graph:
                for child_id, edge_prob in causal_graph[current_id]:
                    if child_id not in visited:
                        # Propagate probability
                        new_prob = cum_prob * edge_prob
                        if new_prob > 0.1:  # Only propagate significant probabilities
                            queue.append((child_id, new_prob, depth + 1))
        
        # Sort by probability
        affected_metrics.sort(key=lambda x: x['probability'], reverse=True)
        
        # Save assessment
        root_metric = self.db.query(Metric).filter(Metric.id == root_metric_id).first()
        
        assessment = ImpactAssessment(
            root_metric_id=root_metric_id,
            affected_metrics=affected_metrics,
            impact_radius=len(affected_metrics),
            total_services_affected=len(services_affected)
        )
        self.db.add(assessment)
        self.db.commit()
        
        result = {
            'root_metric_id': root_metric_id,
            'root_metric_name': root_metric.name if root_metric else f"Metric_{root_metric_id}",
            'affected_metrics': affected_metrics,
            'impact_radius': len(affected_metrics),
            'services_affected': list(services_affected),
            'total_services': len(services_affected)
        }
        
        logger.info(f"Impact assessment complete: {len(affected_metrics)} metrics, "
                   f"{len(services_affected)} services affected")
        
        return result
    
    def calculate_severity(self, probability: float, depth: int) -> str:
        """Calculate severity level based on probability and distance"""
        if probability > 0.8 and depth <= 1:
            return "critical"
        elif probability > 0.6 or depth <= 2:
            return "high"
        elif probability > 0.4:
            return "medium"
        else:
            return "low"
    
    def get_impact_summary(self, root_metric_ids: List[int]) -> Dict:
        """Get impact summary for multiple root causes"""
        summaries = []
        
        for metric_id in root_metric_ids:
            latest = self.db.query(ImpactAssessment).filter(
                ImpactAssessment.root_metric_id == metric_id
            ).order_by(ImpactAssessment.assessment_time.desc()).first()
            
            if latest:
                metric = self.db.query(Metric).filter(Metric.id == metric_id).first()
                summaries.append({
                    'root_metric_id': metric_id,
                    'root_metric_name': metric.name if metric else f"Metric_{metric_id}",
                    'impact_radius': latest.impact_radius,
                    'services_affected': latest.total_services_affected,
                    'assessment_time': latest.assessment_time.isoformat()
                })
        
        return {'impact_summaries': summaries}
    
    def __del__(self):
        self.db.close()
