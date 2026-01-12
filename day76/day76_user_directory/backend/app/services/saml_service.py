from typing import Optional, Dict
from datetime import datetime
import base64
import uuid
from lxml import etree

class SAMLService:
    def __init__(self):
        self.sp_entity_id = "http://localhost:8000/saml/metadata"
        self.acs_url = "http://localhost:8000/saml/acs"
    
    def generate_authn_request(self, idp_sso_url: str, relay_state: Optional[str] = None) -> str:
        """Generate SAML authentication request"""
        request_id = f"__{uuid.uuid4()}"
        issue_instant = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        saml_request = f'''<?xml version="1.0"?>
<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                    ID="{request_id}"
                    Version="2.0"
                    IssueInstant="{issue_instant}"
                    Destination="{idp_sso_url}"
                    AssertionConsumerServiceURL="{self.acs_url}">
    <saml:Issuer>{self.sp_entity_id}</saml:Issuer>
</samlp:AuthnRequest>'''
        
        # Base64 encode
        encoded = base64.b64encode(saml_request.encode('utf-8')).decode('utf-8')
        return encoded
    
    def parse_saml_response(self, saml_response: str) -> Optional[Dict]:
        """Parse and validate SAML response (simplified for demo)"""
        try:
            decoded = base64.b64decode(saml_response)
            root = etree.fromstring(decoded)
            
            # Extract attributes (simplified - production would validate signatures)
            namespaces = {
                'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
                'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol'
            }
            
            # Get NameID
            nameid_elem = root.find('.//saml:NameID', namespaces)
            nameid = nameid_elem.text if nameid_elem is not None else None
            
            # Get attributes
            attributes = {}
            for attr in root.findall('.//saml:Attribute', namespaces):
                name = attr.get('Name')
                value_elem = attr.find('saml:AttributeValue', namespaces)
                if value_elem is not None:
                    attributes[name] = value_elem.text
            
            return {
                'nameid': nameid,
                'email': attributes.get('email', nameid),
                'full_name': attributes.get('displayName', ''),
                'department': attributes.get('department', ''),
                'employee_type': attributes.get('employeeType', '')
            }
        except Exception as e:
            print(f"SAML parsing error: {e}")
            return None
    
    def create_jit_user(self, saml_data: Dict, db_session) -> 'User':
        """Create user from SAML assertion (Just-in-Time provisioning)"""
        from ..models import User, ProvisioningMethod, UserStatus
        
        username = saml_data['email'].split('@')[0]
        
        user = User(
            username=username,
            email=saml_data['email'],
            full_name=saml_data.get('full_name', ''),
            department=saml_data.get('department', ''),
            employee_type=saml_data.get('employee_type', ''),
            saml_nameid=saml_data['nameid'],
            provisioning_method=ProvisioningMethod.SSO_JIT,
            status=UserStatus.ACTIVE,
            last_login=datetime.utcnow()
        )
        
        db_session.add(user)
        db_session.commit()
        return user
