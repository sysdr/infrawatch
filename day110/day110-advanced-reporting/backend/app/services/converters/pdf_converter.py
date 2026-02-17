from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import pandas as pd
from typing import Dict, Any
from io import BytesIO
import matplotlib.pyplot as plt
import os

class PDFConverter:
    """Convert report data to PDF format"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()
    
    def _add_custom_styles(self):
        """Add custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12
        ))
    
    def convert(self, data: pd.DataFrame, structure: Dict[str, Any], output_path: str) -> str:
        """Convert DataFrame to PDF"""
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Title
        title = Paragraph(structure.get("title", "Report"), self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Generated timestamp
        timestamp = Paragraph(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal'])
        story.append(timestamp)
        story.append(Spacer(1, 0.3*inch))
        
        # Sections
        for section in structure.get("sections", []):
            section_title = Paragraph(section.get("title", "Section"), self.styles['SectionHeader'])
            story.append(section_title)
            story.append(Spacer(1, 0.1*inch))
            
            if section.get("type") == "table":
                table_data = self._create_table(data, section)
                if table_data:
                    story.append(table_data)
                    story.append(Spacer(1, 0.2*inch))
            
            elif section.get("type") == "chart":
                chart = self._create_chart(data, section)
                if chart:
                    story.append(chart)
                    story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def _create_table(self, data: pd.DataFrame, section: Dict[str, Any]) -> Table:
        """Create table from DataFrame"""
        
        # Limit rows for PDF display
        display_data = data.head(20)
        
        # Prepare table data
        table_data = [display_data.columns.tolist()]
        for _, row in display_data.iterrows():
            formatted_row = []
            for val in row:
                if isinstance(val, float):
                    formatted_row.append(f"{val:.2f}")
                else:
                    formatted_row.append(str(val))
            table_data.append(formatted_row)
        
        # Create table
        table = Table(table_data)
        
        # Style
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        return table
    
    def _create_chart(self, data: pd.DataFrame, section: Dict[str, Any]) -> Image:
        """Create chart from DataFrame"""
        
        fig, ax = plt.subplots(figsize=(6, 4))
        
        # Plot first few numeric columns
        numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns[:3]
        
        for col in numeric_cols:
            ax.plot(data.index[:50], data[col].iloc[:50], label=col, marker='o', markersize=3)
        
        ax.set_xlabel('Data Points')
        ax.set_ylabel('Values')
        ax.set_title(section.get("title", "Chart"))
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save to BytesIO
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        # Create Image object
        img = Image(buf, width=5*inch, height=3.3*inch)
        return img
