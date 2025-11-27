import json
from typing import List, Dict, Any
from datetime import datetime

class JSONExportService:
    def __init__(self):
        self.items = []
        
    def initialize(self, metadata: Dict[str, Any]):
        self.metadata = metadata
        self.items = []
        
    def write_batch(self, records: List[Dict[str, Any]]):
        for record in records:
            # Convert datetime objects to ISO format strings
            serializable_record = {}
            for key, value in record.items():
                if isinstance(value, datetime):
                    serializable_record[key] = value.isoformat()
                else:
                    serializable_record[key] = value
            self.items.append(serializable_record)
            
    def get_content(self) -> str:
        output = {
            "metadata": self.metadata,
            "data": self.items
        }
        return json.dumps(output, indent=2, ensure_ascii=False)
        
    def close(self):
        self.items = []
