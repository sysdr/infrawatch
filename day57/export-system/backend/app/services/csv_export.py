import csv
from io import StringIO
from typing import List, Dict, Any

class CSVExportService:
    def __init__(self):
        self.buffer = StringIO()
        self.writer = None
        
    def initialize(self, headers: List[str]):
        self.writer = csv.DictWriter(
            self.buffer,
            fieldnames=headers,
            quoting=csv.QUOTE_MINIMAL
        )
        # Add BOM for Excel compatibility
        self.buffer.write('\ufeff')
        self.writer.writeheader()
        
    def write_batch(self, records: List[Dict[str, Any]]):
        for record in records:
            # Handle None values
            cleaned_record = {k: (v if v is not None else '') for k, v in record.items()}
            self.writer.writerow(cleaned_record)
            
    def get_content(self) -> str:
        return self.buffer.getvalue()
        
    def close(self):
        self.buffer.close()
