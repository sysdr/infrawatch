from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import List, Dict, Any
from io import BytesIO
from datetime import datetime

class PDFExportService:
    def __init__(self):
        self.buffer = BytesIO()
        self.elements = []
        self.styles = getSampleStyleSheet()
        
    def initialize(self, title: str, metadata: Dict[str, Any]):
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=30
        )
        self.elements.append(Paragraph(title, title_style))
        
        # Metadata
        meta_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
        meta_text += f"Total Records: {metadata.get('total_records', 0)}"
        self.elements.append(Paragraph(meta_text, self.styles['Normal']))
        self.elements.append(Spacer(1, 0.3*inch))
        
        self.table_data = []
        
    def write_batch(self, records: List[Dict[str, Any]], headers: List[str]):
        if not self.table_data:
            # Add headers
            self.table_data.append(headers)
            
        for record in records:
            row = [str(record.get(h, '')) for h in headers]
            self.table_data.append(row)
            
    def finalize(self):
        if self.table_data:
            # Create table with styling
            table = Table(self.table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            self.elements.append(table)
            
        self.doc.build(self.elements)
        
    def get_content(self) -> bytes:
        return self.buffer.getvalue()
        
    def close(self):
        self.buffer.close()
