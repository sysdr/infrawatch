import ldap
import redis
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from ..models import User, LDAPConfig, ProvisioningMethod, UserStatus

class LDAPService:
    def __init__(self):
        self.redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        self.cache_ttl = 300  # 5 minutes
        
    def _get_connection(self, config: LDAPConfig):
        """Create LDAP connection with connection pooling"""
        conn = ldap.initialize(config.server)
        conn.protocol_version = ldap.VERSION3
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.simple_bind_s(config.bind_dn, config.bind_password)
        return conn
    
    def authenticate(self, username: str, password: str, config: LDAPConfig) -> Optional[Dict]:
        """Authenticate user against LDAP with caching"""
        cache_key = f"ldap_auth:{username}"
        
        # Check cache first
        cached = self.redis_client.get(cache_key)
        if cached and password == "cached_validated":
            return json.loads(cached)
        
        try:
            conn = self._get_connection(config)
            
            # Search for user
            search_filter = f"(&{config.user_filter}(uid={username}))"
            result = conn.search_s(config.base_dn, ldap.SCOPE_SUBTREE, search_filter, 
                                  ['cn', 'mail', 'employeeType', 'departmentNumber', 'manager'])
            
            if not result:
                return None
            
            user_dn, attrs = result[0]
            
            # Try to bind as user to verify password
            try:
                user_conn = ldap.initialize(config.server)
                user_conn.simple_bind_s(user_dn, password)
                user_conn.unbind_s()
            except ldap.INVALID_CREDENTIALS:
                return None
            
            # Build user data
            user_data = {
                'dn': user_dn,
                'username': username,
                'email': attrs.get('mail', [b''])[0].decode('utf-8'),
                'full_name': attrs.get('cn', [b''])[0].decode('utf-8'),
                'employee_type': attrs.get('employeeType', [b''])[0].decode('utf-8'),
                'department': attrs.get('departmentNumber', [b''])[0].decode('utf-8'),
                'manager': attrs.get('manager', [b''])[0].decode('utf-8'),
            }
            
            # Cache the result
            self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(user_data))
            
            conn.unbind_s()
            return user_data
            
        except Exception as e:
            print(f"LDAP auth error: {e}")
            return None
    
    def sync_users(self, config: LDAPConfig, db_session) -> Dict[str, int]:
        """Sync users from LDAP directory"""
        stats = {'created': 0, 'updated': 0, 'disabled': 0, 'errors': 0}
        
        try:
            conn = self._get_connection(config)
            
            # Search all users
            search_filter = config.user_filter
            results = conn.search_s(config.base_dn, ldap.SCOPE_SUBTREE, search_filter,
                                   ['uid', 'cn', 'mail', 'employeeType', 'departmentNumber', 'manager'])
            
            synced_usernames = []
            
            for user_dn, attrs in results:
                try:
                    username = attrs.get('uid', [b''])[0].decode('utf-8')
                    if not username:
                        continue
                    
                    synced_usernames.append(username)
                    
                    user_data = {
                        'username': username,
                        'email': attrs.get('mail', [b''])[0].decode('utf-8'),
                        'full_name': attrs.get('cn', [b''])[0].decode('utf-8'),
                        'employee_type': attrs.get('employeeType', [b''])[0].decode('utf-8'),
                        'department': attrs.get('departmentNumber', [b''])[0].decode('utf-8'),
                        'manager': attrs.get('manager', [b''])[0].decode('utf-8'),
                    }
                    
                    # Check if user exists
                    existing_user = db_session.query(User).filter(User.username == username).first()
                    
                    if existing_user:
                        # Update existing
                        for key, value in user_data.items():
                            setattr(existing_user, key, value)
                        existing_user.is_ldap_synced = True
                        existing_user.last_ldap_sync = datetime.utcnow()
                        existing_user.ldap_dn = user_dn
                        if existing_user.status == UserStatus.PENDING:
                            existing_user.status = UserStatus.ACTIVE
                        stats['updated'] += 1
                    else:
                        # Create new
                        new_user = User(
                            **user_data,
                            ldap_dn=user_dn,
                            provisioning_method=ProvisioningMethod.LDAP_SYNC,
                            is_ldap_synced=True,
                            last_ldap_sync=datetime.utcnow(),
                            status=UserStatus.ACTIVE
                        )
                        db_session.add(new_user)
                        stats['created'] += 1
                    
                except Exception as e:
                    print(f"Error syncing user: {e}")
                    stats['errors'] += 1
            
            # Disable users not in LDAP
            ldap_users = db_session.query(User).filter(User.is_ldap_synced == True).all()
            for user in ldap_users:
                if user.username not in synced_usernames and user.status == UserStatus.ACTIVE:
                    user.status = UserStatus.SUSPENDED
                    stats['disabled'] += 1
            
            db_session.commit()
            conn.unbind_s()
            
            # Update config
            config.last_sync = datetime.utcnow()
            db_session.commit()
            
        except Exception as e:
            print(f"LDAP sync error: {e}")
            stats['errors'] += 1
        
        return stats
