import pandas as pd
import json
from typing import Dict, Any
from datetime import datetime

class JSONConverter:
    """Convert report data to JSON format"""
    
    def convert(self, data: pd.DataFrame, structure: Dict[str, Any], output_path: str) -> str:
        """Convert DataFrame to JSON"""
        
        # Create structured JSON
        report_data = {
            "metadata": {
                "title": structure.get("title", "Report"),
                "generated_at": datetime.utcnow().isoformat(),
                "row_count": len(data),
                "columns": data.columns.tolist()
            },
            "data": json.loads(data.to_json(orient='records', date_format='iso')),
            "summary": {
                "numeric_summary": {}
            }
        }
        
        # Add numeric summaries
        numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            report_data["summary"]["numeric_summary"][col] = {
                "mean": float(data[col].mean()),
                "min": float(data[col].min()),
                "max": float(data[col].max()),
                "std": float(data[col].std())
            }
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return output_path
