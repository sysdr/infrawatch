from typing import List, Dict
import os

class ThreatModeler:
    def __init__(self):
        self.stride_categories = {
            "Spoofing": "Impersonating something or someone else",
            "Tampering": "Modifying data or code",
            "Repudiation": "Claiming to not have performed an action",
            "Information Disclosure": "Exposing information to unauthorized individuals",
            "Denial of Service": "Denying or degrading service to users",
            "Elevation of Privilege": "Gaining capabilities without proper authorization"
        }
    
    def model_threats(self, project_path: str) -> List[Dict]:
        """Generate threat model for system components"""
        components = self._identify_components(project_path)
        threats = []
        
        for component in components:
            threats.extend(self._analyze_component_threats(component))
        
        return threats
    
    def _identify_components(self, project_path: str) -> List[Dict]:
        """Identify system components from project structure"""
        components = []
        
        # Identify common component types
        component_patterns = {
            "Authentication Service": ["auth", "login", "user"],
            "API Gateway": ["api", "gateway", "router"],
            "Database": ["db", "database", "models"],
            "File Storage": ["storage", "upload", "file"],
            "External Integration": ["external", "third_party", "integration"]
        }
        
        for root, dirs, files in os.walk(project_path):
            for dir_name in dirs:
                for component_type, patterns in component_patterns.items():
                    if any(pattern in dir_name.lower() for pattern in patterns):
                        components.append({
                            "name": component_type,
                            "path": os.path.join(root, dir_name),
                            "type": component_type
                        })
        
        # Ensure at least default components
        if not components:
            components = [
                {"name": "Authentication Service", "path": project_path, "type": "Authentication Service"},
                {"name": "API Gateway", "path": project_path, "type": "API Gateway"},
                {"name": "Database", "path": project_path, "type": "Database"}
            ]
        
        return components
    
    def _analyze_component_threats(self, component: Dict) -> List[Dict]:
        """Analyze threats for a specific component using STRIDE"""
        threats = []
        component_name = component["name"]
        
        # Generate STRIDE threats based on component type
        threat_templates = self._get_threat_templates(component["type"])
        
        for threat_template in threat_templates:
            threat = {
                "component_name": component_name,
                "threat_category": threat_template["category"],
                "threat_description": threat_template["description"].format(component=component_name),
                "likelihood": threat_template["likelihood"],
                "impact": threat_template["impact"],
                "risk_score": threat_template["likelihood"] * threat_template["impact"],
                "mitigation": threat_template["mitigation"]
            }
            threats.append(threat)
        
        return threats
    
    def _get_threat_templates(self, component_type: str) -> List[Dict]:
        """Get threat templates for component type"""
        templates = {
            "Authentication Service": [
                {
                    "category": "Spoofing",
                    "description": "{component} vulnerable to credential stuffing attacks",
                    "likelihood": 4,
                    "impact": 5,
                    "mitigation": "Implement rate limiting, MFA, and account lockout policies"
                },
                {
                    "category": "Tampering",
                    "description": "{component} session tokens could be manipulated",
                    "likelihood": 3,
                    "impact": 5,
                    "mitigation": "Use cryptographically signed JWT tokens with short expiry"
                },
                {
                    "category": "Elevation of Privilege",
                    "description": "{component} may allow privilege escalation through role manipulation",
                    "likelihood": 3,
                    "impact": 5,
                    "mitigation": "Implement strict RBAC validation and audit all role changes"
                }
            ],
            "API Gateway": [
                {
                    "category": "Denial of Service",
                    "description": "{component} vulnerable to rate-based DoS attacks",
                    "likelihood": 5,
                    "impact": 4,
                    "mitigation": "Implement rate limiting, request throttling, and DDoS protection"
                },
                {
                    "category": "Information Disclosure",
                    "description": "{component} may expose sensitive API endpoints or error details",
                    "likelihood": 4,
                    "impact": 3,
                    "mitigation": "Implement API authentication, sanitize error messages"
                },
                {
                    "category": "Tampering",
                    "description": "{component} requests could be intercepted and modified",
                    "likelihood": 3,
                    "impact": 4,
                    "mitigation": "Enforce TLS 1.3, implement request signing"
                }
            ],
            "Database": [
                {
                    "category": "Information Disclosure",
                    "description": "{component} vulnerable to SQL injection and data exfiltration",
                    "likelihood": 4,
                    "impact": 5,
                    "mitigation": "Use parameterized queries, implement database encryption"
                },
                {
                    "category": "Tampering",
                    "description": "{component} data could be modified by unauthorized users",
                    "likelihood": 3,
                    "impact": 5,
                    "mitigation": "Implement row-level security and audit logging"
                },
                {
                    "category": "Denial of Service",
                    "description": "{component} vulnerable to resource exhaustion attacks",
                    "likelihood": 3,
                    "impact": 4,
                    "mitigation": "Implement query timeouts and connection pooling"
                }
            ],
            "File Storage": [
                {
                    "category": "Tampering",
                    "description": "{component} files could be modified or replaced",
                    "likelihood": 4,
                    "impact": 4,
                    "mitigation": "Implement file integrity checking and versioning"
                },
                {
                    "category": "Information Disclosure",
                    "description": "{component} may expose sensitive files to unauthorized users",
                    "likelihood": 4,
                    "impact": 5,
                    "mitigation": "Implement access controls and encrypt files at rest"
                }
            ],
            "External Integration": [
                {
                    "category": "Spoofing",
                    "description": "{component} may connect to spoofed external services",
                    "likelihood": 3,
                    "impact": 4,
                    "mitigation": "Implement certificate pinning and API key validation"
                },
                {
                    "category": "Information Disclosure",
                    "description": "{component} may leak sensitive data to external services",
                    "likelihood": 3,
                    "impact": 5,
                    "mitigation": "Implement data minimization and encryption in transit"
                }
            ]
        }
        
        # Return specific templates or default
        return templates.get(component_type, templates["API Gateway"])
