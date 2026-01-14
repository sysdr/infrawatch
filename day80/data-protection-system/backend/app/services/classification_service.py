from enum import Enum
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ClassificationLevel(Enum):
    PUBLIC = 1
    INTERNAL = 2
    CONFIDENTIAL = 3
    RESTRICTED = 4

class ClassificationService:
    def __init__(self):
        self.field_classifications = {}
        self.retention_policies = {}
    
    async def initialize(self):
        """Initialize classification rules"""
        self.field_classifications = {
            # Public data
            "username": ClassificationLevel.PUBLIC,
            "display_name": ClassificationLevel.PUBLIC,
            "avatar_url": ClassificationLevel.PUBLIC,
            
            # Internal data
            "email": ClassificationLevel.INTERNAL,
            "full_name": ClassificationLevel.INTERNAL,
            "department": ClassificationLevel.INTERNAL,
            
            # Confidential data
            "phone": ClassificationLevel.CONFIDENTIAL,
            "address": ClassificationLevel.CONFIDENTIAL,
            "date_of_birth": ClassificationLevel.CONFIDENTIAL,
            
            # Restricted data
            "ssn": ClassificationLevel.RESTRICTED,
            "credit_card": ClassificationLevel.RESTRICTED,
            "bank_account": ClassificationLevel.RESTRICTED,
            "medical_records": ClassificationLevel.RESTRICTED
        }
        
        # Retention policies in days
        self.retention_policies = {
            ClassificationLevel.PUBLIC: 3650,  # 10 years
            ClassificationLevel.INTERNAL: 2555,  # 7 years
            ClassificationLevel.CONFIDENTIAL: 1825,  # 5 years
            ClassificationLevel.RESTRICTED: 1095  # 3 years
        }
        
        logger.info(f"Classification service initialized with {len(self.field_classifications)} field rules")
    
    def classify_field(self, field_name: str) -> ClassificationLevel:
        """Classify a field based on its name"""
        return self.field_classifications.get(field_name, ClassificationLevel.INTERNAL)
    
    def requires_encryption(self, classification: ClassificationLevel) -> bool:
        """Check if classification level requires encryption"""
        return classification in [ClassificationLevel.CONFIDENTIAL, ClassificationLevel.RESTRICTED]
    
    def get_retention_days(self, classification: ClassificationLevel) -> int:
        """Get retention period for classification level"""
        return self.retention_policies.get(classification, 2555)
    
    def classify_data(self, data: Dict[str, Any]) -> Dict[str, ClassificationLevel]:
        """Classify all fields in a data dictionary"""
        classifications = {}
        for field_name in data.keys():
            classifications[field_name] = self.classify_field(field_name)
        return classifications
    
    def get_encryption_strategy(self, classification: ClassificationLevel) -> str:
        """Get encryption strategy for classification level"""
        strategies = {
            ClassificationLevel.PUBLIC: "none",
            ClassificationLevel.INTERNAL: "transit_only",
            ClassificationLevel.CONFIDENTIAL: "at_rest_and_transit",
            ClassificationLevel.RESTRICTED: "at_rest_and_transit_with_key_separation"
        }
        return strategies.get(classification, "none")

# Global instance
classification_service = ClassificationService()
