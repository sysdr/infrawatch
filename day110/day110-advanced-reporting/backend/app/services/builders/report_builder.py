import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random

class ReportBuilder:
    """Builds report data from query configuration"""
    
    def execute_query(self, query_config: Dict[str, Any], parameters: Dict[str, Any]) -> pd.DataFrame:
        """Execute query and return DataFrame"""
        
        # Simulate fetching metrics data
        metrics = query_config.get("metrics", ["cpu_usage", "memory_usage", "error_rate"])
        time_range = parameters.get("time_range", "7d")
        
        # Generate sample data
        days = int(time_range.replace("d", ""))
        data = []
        
        for i in range(days * 24):  # Hourly data
            timestamp = datetime.utcnow() - timedelta(hours=days*24-i)
            row = {"timestamp": timestamp}
            
            for metric in metrics:
                if metric == "cpu_usage":
                    row[metric] = random.uniform(20, 90)
                elif metric == "memory_usage":
                    row[metric] = random.uniform(30, 85)
                elif metric == "error_rate":
                    row[metric] = random.uniform(0, 5)
                elif metric == "response_time":
                    row[metric] = random.uniform(50, 500)
                else:
                    row[metric] = random.uniform(0, 100)
                    
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Apply aggregations if specified
        aggregations = query_config.get("aggregations", {})
        if aggregations:
            df = self._apply_aggregations(df, aggregations)
            
        return df
    
    def _apply_aggregations(self, df: pd.DataFrame, aggregations: Dict[str, str]) -> pd.DataFrame:
        """Apply aggregation functions"""
        agg_dict = {}
        
        for column, func in aggregations.items():
            if column in df.columns and column != "timestamp":
                if func == "mean":
                    agg_dict[column] = "mean"
                elif func == "max":
                    agg_dict[column] = "max"
                elif func == "min":
                    agg_dict[column] = "min"
                elif func == "p95":
                    agg_dict[column] = lambda x: x.quantile(0.95)
        
        if agg_dict:
            # Group by day for aggregation
            df["date"] = pd.to_datetime(df["timestamp"]).dt.date
            result = df.groupby("date").agg(agg_dict).reset_index()
            return result
        
        return df
