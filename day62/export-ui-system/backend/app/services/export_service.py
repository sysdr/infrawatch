import pandas as pd
import json
import csv
import io
from datetime import datetime, timedelta
import uuid
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

class ExportService:
    def __init__(self):
        self.export_dir = "/tmp/exports"
        os.makedirs(self.export_dir, exist_ok=True)
    
    def generate_sample_data(self, row_count=100):
        """Generate sample data for exports"""
        data = []
        for i in range(row_count):
            data.append({
                "id": i + 1,
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                "metric_name": f"metric_{i % 10}",
                "value": round(50 + (i % 100) * 0.5, 2),
                "status": "active" if i % 3 == 0 else "inactive",
                "region": ["us-east-1", "us-west-2", "eu-west-1"][i % 3]
            })
        return data
    
    def export_to_csv(self, data, options=None):
        """Export data to CSV format"""
        df = pd.DataFrame(data)
        output = io.StringIO()
        
        delimiter = options.get("delimiter", ",") if options else ","
        df.to_csv(output, index=False, sep=delimiter)
        
        return output.getvalue()
    
    def export_to_json(self, data, options=None):
        """Export data to JSON format"""
        pretty = options.get("pretty", True) if options else True
        
        if pretty:
            return json.dumps(data, indent=2, default=str)
        return json.dumps(data, default=str)
    
    def export_to_excel(self, data, options=None):
        """Export data to Excel format"""
        df = pd.DataFrame(data)
        
        filename = f"{uuid.uuid4()}.xlsx"
        filepath = os.path.join(self.export_dir, filename)
        
        sheet_name = options.get("sheet_name", "Export") if options else "Export"
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return filepath
    
    def export_to_pdf(self, data, options=None):
        """Export data to PDF format"""
        filename = f"{uuid.uuid4()}.pdf"
        filepath = os.path.join(self.export_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        
        # Title
        styles = getSampleStyleSheet()
        title = Paragraph("Export Report", styles['Title'])
        elements.append(title)
        
        # Convert data to table format
        if data:
            headers = list(data[0].keys())
            table_data = [headers]
            
            for row in data[:50]:  # Limit to 50 rows for PDF
                table_data.append([str(row.get(h, "")) for h in headers])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
        
        doc.build(elements)
        return filepath
    
    def get_preview_data(self, config, limit=10):
        """Get preview data for the export"""
        # In real implementation, this would query the actual data source
        data = self.generate_sample_data(limit)
        
        # Apply filters if specified
        if config.get("filters"):
            # Filter logic would go here
            pass
        
        # Select specific fields if specified
        if config.get("fields"):
            fields = config["fields"]
            data = [{k: v for k, v in row.items() if k in fields} for row in data]
        
        return data
