import pandas as pd
from typing import Dict, Any

class CSVConverter:
    """Convert report data to CSV format"""
    
    def convert(self, data: pd.DataFrame, structure: Dict[str, Any], output_path: str) -> str:
        """Convert DataFrame to CSV"""
        
        # Add metadata as comments
        with open(output_path, 'w') as f:
            f.write(f"# Report: {structure.get('title', 'Report')}\n")
            f.write(f"# Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("#\n")
        
        # Append data
        data.to_csv(output_path, mode='a', index=False)
        
        return output_path
