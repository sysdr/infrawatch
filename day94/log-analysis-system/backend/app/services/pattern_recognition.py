import re
import hashlib
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.database import LogPattern
import json

class PatternRecognitionEngine:
    """
    Pattern recognition engine that tokenizes log messages and identifies recurring patterns.
    Uses regex-based tokenization similar to Splunk's pattern detection.
    """
    
    # Token patterns for common variable types
    TOKEN_PATTERNS = [
        (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '{IP}'),
        (r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b', '{UUID}'),
        (r'\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', '{TIMESTAMP}'),
        (r'\b\d{10,13}\b', '{UNIX_TIME}'),
        (r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', '{EMAIL}'),
        (r'\b/[\w/\-\.]+', '{PATH}'),
        (r'\b\d+\.\d+\b', '{FLOAT}'),
        (r'\b\d+\b', '{NUMBER}'),
        (r'\b[0-9a-fA-F]{32,}\b', '{HASH}'),
    ]
    
    CRITICAL_KEYWORDS = ['error', 'fail', 'critical', 'fatal', 'exception', 'timeout', 'denied']
    
    def __init__(self, db: Session):
        self.db = db
    
    def tokenize_message(self, message: str) -> Tuple[str, Dict]:
        """
        Tokenize variable portions of log message to create pattern template.
        Returns (pattern_template, extracted_variables)
        """
        variables = {}
        template = message
        
        for pattern, token in self.TOKEN_PATTERNS:
            matches = list(re.finditer(pattern, template))
            for i, match in enumerate(reversed(matches)):
                var_name = f"{token}_{len(matches)-i}"
                variables[var_name] = match.group()
                template = template[:match.start()] + token + template[match.end():]
        
        return template, variables
    
    def generate_signature(self, template: str) -> str:
        """Generate unique signature for pattern template"""
        return hashlib.md5(template.encode()).hexdigest()
    
    def detect_severity(self, message: str, template: str) -> Tuple[str, bool]:
        """Detect severity level and criticality based on keywords"""
        message_lower = message.lower()
        template_lower = template.lower()
        
        is_critical = any(keyword in message_lower or keyword in template_lower 
                         for keyword in self.CRITICAL_KEYWORDS)
        
        if 'fatal' in message_lower or 'critical' in message_lower:
            severity = 'critical'
        elif 'error' in message_lower or 'fail' in message_lower:
            severity = 'high'
        elif 'warn' in message_lower:
            severity = 'medium'
        else:
            severity = 'low'
        
        return severity, is_critical
    
    def categorize_pattern(self, template: str) -> str:
        """Categorize pattern based on content"""
        template_lower = template.lower()
        
        if 'auth' in template_lower or 'login' in template_lower:
            return 'authentication'
        elif 'database' in template_lower or 'sql' in template_lower:
            return 'database'
        elif 'api' in template_lower or 'request' in template_lower:
            return 'api'
        elif 'network' in template_lower or 'connection' in template_lower:
            return 'network'
        else:
            return 'general'
    
    def match_or_create_pattern(self, log_message: str, log_level: str, 
                                source: str) -> Optional[LogPattern]:
        """
        Match log message against existing patterns or create new pattern.
        Returns the matched/created pattern.
        """
        template, variables = self.tokenize_message(log_message)
        signature = self.generate_signature(template)
        
        # Try to find existing pattern
        pattern = self.db.query(LogPattern).filter(
            LogPattern.pattern_signature == signature
        ).first()
        
        if pattern:
            # Update existing pattern
            pattern.frequency_count += 1
            pattern.last_seen = datetime.utcnow()
            self.db.commit()
            return pattern
        
        # Create new pattern
        severity, is_critical = self.detect_severity(log_message, template)
        category = self.categorize_pattern(template)
        
        pattern = LogPattern(
            pattern_signature=signature,
            pattern_template=template,
            category=category,
            severity=severity,
            frequency_count=1,
            is_critical=is_critical,
            extra_data={
                'sample_message': log_message,
                'sample_variables': variables,
                'log_level': log_level,
                'source': source
            }
        )
        
        self.db.add(pattern)
        self.db.commit()
        self.db.refresh(pattern)
        
        return pattern
    
    def get_pattern_statistics(self, hours: int = 24) -> List[Dict]:
        """Get pattern frequency statistics for analysis"""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        patterns = self.db.query(LogPattern).filter(
            LogPattern.last_seen >= cutoff
        ).order_by(LogPattern.frequency_count.desc()).limit(100).all()
        
        return [
            {
                'id': p.id,
                'template': p.pattern_template,
                'category': p.category,
                'severity': p.severity,
                'frequency': p.frequency_count,
                'is_critical': p.is_critical,
                'first_seen': p.first_seen.isoformat(),
                'last_seen': p.last_seen.isoformat()
            }
            for p in patterns
        ]
