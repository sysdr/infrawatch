import psutil
import time
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, Any
import random

class MetricsProcessor:
    def __init__(self):
        self.start_time = time.time()
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Simulate additional processing time
        time.sleep(2)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "memory_available": memory.available,
            "disk_usage": disk.percent,
            "disk_free": disk.free,
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0],
            "processing_time": time.time() - self.start_time,
            "records_count": 1
        }
    
    def process_csv_file(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process CSV file data"""
        file_content = payload.get("file_content", "")
        
        # Simulate CSV processing
        lines = file_content.split('\n')
        processed_data = []
        
        for i, line in enumerate(lines[:100]):  # Process first 100 lines
            if line.strip():
                processed_data.append({
                    "line_number": i + 1,
                    "content": line[:50],  # First 50 characters
                    "length": len(line)
                })
            
            # Simulate processing delay
            if i % 10 == 0:
                time.sleep(0.1)
        
        return {
            "total_lines": len(lines),
            "processed_lines": len(processed_data),
            "sample_data": processed_data[:10],
            "processing_time": time.time() - self.start_time,
            "records_count": len(processed_data)
        }
    
    def generate_metrics_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive metrics report"""
        start_date = payload.get("start_date", (datetime.utcnow() - timedelta(days=7)).isoformat())
        end_date = payload.get("end_date", datetime.utcnow().isoformat())
        
        # Simulate report generation
        time.sleep(3)
        
        # Generate sample metrics data
        metrics = []
        for i in range(100):
            metrics.append({
                "timestamp": (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
                "cpu_usage": random.uniform(10, 90),
                "memory_usage": random.uniform(20, 80),
                "disk_usage": random.uniform(30, 70),
                "network_io": random.uniform(100, 1000)
            })
        
        return {
            "report_period": {"start": start_date, "end": end_date},
            "total_metrics": len(metrics),
            "avg_cpu": sum(m["cpu_usage"] for m in metrics) / len(metrics),
            "avg_memory": sum(m["memory_usage"] for m in metrics) / len(metrics),
            "peak_values": {
                "cpu": max(m["cpu_usage"] for m in metrics),
                "memory": max(m["memory_usage"] for m in metrics)
            },
            "metrics_data": metrics[:20],  # Return sample data
            "processing_time": time.time() - self.start_time,
            "records_count": len(metrics)
        }
