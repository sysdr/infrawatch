from sqlalchemy.orm import Session
from models.log_entry import LogEntry, StorageTier, StorageMetrics
from datetime import datetime
from typing import Dict

class CostService:
    # Cost per GB per month in USD
    TIER_COSTS = {
        StorageTier.HOT: 0.023,
        StorageTier.WARM: 0.004,
        StorageTier.COLD: 0.001
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_storage_costs(self) -> Dict:
        """Calculate current storage costs across all tiers"""
        costs = {}
        
        for tier in [StorageTier.HOT, StorageTier.WARM, StorageTier.COLD]:
            logs = self.db.query(LogEntry).filter(
                LogEntry.storage_tier == tier,
                LogEntry.deleted_at == None
            ).all()
            
            total_size = sum(log.compressed_size or log.original_size or 0 for log in logs)
            size_gb = total_size / (1024 ** 3)  # Convert to GB
            cost = size_gb * self.TIER_COSTS[tier]
            
            costs[tier.value] = {
                "log_count": len(logs),
                "total_size_bytes": total_size,
                "total_size_gb": round(size_gb, 2),
                "cost_per_gb": self.TIER_COSTS[tier],
                "total_cost": round(cost, 2)
            }
            
            # Save metrics
            metric = StorageMetrics(
                tier=tier,
                log_count=len(logs),
                total_size=total_size,
                compressed_size=sum(log.compressed_size or 0 for log in logs),
                cost_per_gb=self.TIER_COSTS[tier],
                total_cost=cost
            )
            self.db.add(metric)
        
        self.db.commit()
        
        # Calculate total
        total_cost = sum(c["total_cost"] for c in costs.values())
        total_size_gb = sum(c["total_size_gb"] for c in costs.values())
        
        return {
            "tiers": costs,
            "total_cost": round(total_cost, 2),
            "total_size_gb": round(total_size_gb, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_cost_optimization_recommendations(self) -> list:
        """Identify logs that could be archived more aggressively"""
        recommendations = []
        
        # Find logs in HOT tier that haven't been accessed recently
        hot_logs = self.db.query(LogEntry).filter(
            LogEntry.storage_tier == StorageTier.HOT,
            LogEntry.deleted_at == None
        ).all()
        
        for log in hot_logs:
            if log.query_count == 0 or (log.last_accessed and (datetime.utcnow() - log.last_accessed).days > 14):
                age_days = (datetime.utcnow() - log.timestamp).days
                if age_days > 3:  # More than 3 days old and never queried
                    recommendations.append({
                        "log_id": log.id,
                        "source": log.source,
                        "age_days": age_days,
                        "current_tier": "hot",
                        "recommended_tier": "warm",
                        "potential_savings": self._calculate_savings(log, StorageTier.HOT, StorageTier.WARM)
                    })
        
        return recommendations
    
    def _calculate_savings(self, log: LogEntry, current_tier: StorageTier, target_tier: StorageTier) -> float:
        size_gb = (log.compressed_size or log.original_size or 0) / (1024 ** 3)
        current_cost = size_gb * self.TIER_COSTS[current_tier]
        target_cost = size_gb * self.TIER_COSTS[target_tier]
        return round(current_cost - target_cost, 4)

def get_cost_service(db: Session):
    return CostService(db)
