from app.database import SessionLocal
from app.models import Job, Dependency, Execution
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DependencyResolver:
    def __init__(self):
        pass
    
    def add_dependency(self, upstream_job_id: str, downstream_job_id: str, condition_type: str = "success"):
        """Add a dependency between two jobs"""
        db = SessionLocal()
        try:
            # Check for circular dependency
            if self.would_create_cycle(db, upstream_job_id, downstream_job_id):
                raise ValueError("Adding this dependency would create a circular dependency")
            
            # Add dependency
            dep = Dependency(
                upstream_job_id=upstream_job_id,
                downstream_job_id=downstream_job_id,
                condition_type=condition_type
            )
            db.add(dep)
            db.commit()
            logger.info(f"Added dependency: {upstream_job_id} -> {downstream_job_id}")
            return dep
            
        finally:
            db.close()
    
    def would_create_cycle(self, db: Session, upstream_id: str, downstream_id: str) -> bool:
        """Check if adding this dependency would create a cycle using DFS"""
        visited = set()
        
        def dfs(node_id: str) -> bool:
            if node_id == upstream_id:
                return True
            if node_id in visited:
                return False
            
            visited.add(node_id)
            
            # Get all downstream dependencies of this node
            deps = db.query(Dependency).filter(Dependency.upstream_job_id == node_id).all()
            for dep in deps:
                if dfs(dep.downstream_job_id):
                    return True
            
            return False
        
        # Start DFS from the proposed downstream job
        return dfs(downstream_id)
    
    def check_dependencies(self, job_id: str) -> tuple[bool, str]:
        """Check if all dependencies for a job are met"""
        db = SessionLocal()
        try:
            # Get all upstream dependencies
            deps = db.query(Dependency).filter(Dependency.downstream_job_id == job_id).all()
            
            if not deps:
                return True, "No dependencies"
            
            for dep in deps:
                # Get last execution of upstream job
                last_exec = db.query(Execution).filter(
                    Execution.job_id == dep.upstream_job_id
                ).order_by(Execution.created_at.desc()).first()
                
                if not last_exec:
                    return False, f"Dependency {dep.upstream_job.name} has never run"
                
                if dep.condition_type == "success":
                    if last_exec.state != "COMPLETED":
                        return False, f"Dependency {dep.upstream_job.name} state is {last_exec.state}, expected COMPLETED"
                
                elif dep.condition_type == "completion":
                    if last_exec.state not in ["COMPLETED", "FAILED"]:
                        return False, f"Dependency {dep.upstream_job.name} has not completed"
            
            return True, "All dependencies met"
            
        finally:
            db.close()
    
    def get_dependency_graph(self, job_id: str) -> dict:
        """Get the dependency graph for a job"""
        db = SessionLocal()
        try:
            nodes = {}
            edges = []
            
            def traverse(jid: str, visited: set):
                if jid in visited:
                    return
                visited.add(jid)
                
                job = db.query(Job).filter(Job.id == jid).first()
                if job:
                    # Get last execution
                    last_exec = db.query(Execution).filter(
                        Execution.job_id == jid
                    ).order_by(Execution.created_at.desc()).first()
                    
                    nodes[jid] = {
                        'id': jid,
                        'name': job.name,
                        'state': last_exec.state if last_exec else 'never_run'
                    }
                    
                    # Traverse upstream
                    for dep in job.upstream_deps:
                        edges.append({
                            'from': dep.upstream_job_id,
                            'to': dep.downstream_job_id,
                            'condition': dep.condition_type
                        })
                        traverse(dep.upstream_job_id, visited)
                    
                    # Traverse downstream
                    for dep in job.downstream_deps:
                        edges.append({
                            'from': dep.upstream_job_id,
                            'to': dep.downstream_job_id,
                            'condition': dep.condition_type
                        })
                        traverse(dep.downstream_job_id, visited)
            
            traverse(job_id, set())
            
            return {'nodes': list(nodes.values()), 'edges': edges}
            
        finally:
            db.close()
    
    def notify_downstream(self, job_id: str, execution_state: str):
        """Notify downstream jobs when an upstream job completes"""
        if execution_state not in ["COMPLETED", "FAILED"]:
            return
        
        db = SessionLocal()
        try:
            # Get all downstream dependencies
            deps = db.query(Dependency).filter(Dependency.upstream_job_id == job_id).all()
            
            for dep in deps:
                # Check if downstream job's dependencies are now met
                deps_met, msg = self.check_dependencies(dep.downstream_job_id)
                if deps_met:
                    logger.info(f"Dependencies met for {dep.downstream_job.name}, triggering")
                    # Trigger downstream job
                    from app.event_bus import event_bus
                    execution = Execution(
                        job_id=dep.downstream_job_id,
                        state="TRIGGERED",
                        trigger_type="dependency"
                    )
                    db.add(execution)
                    db.commit()
                    
                    event_bus.publish('job.triggered', 'job.triggered', {
                        'execution_id': execution.id,
                        'job_id': dep.downstream_job_id,
                        'trigger_type': 'dependency'
                    })
        finally:
            db.close()

dependency_resolver = DependencyResolver()
