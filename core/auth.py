"""
Authentication and Authorization Module
Role-based access control for moderators
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
import hashlib
import secrets
import json
from pathlib import Path
from enum import Enum


class Role(Enum):
    """User roles with different permissions"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


class Permission(Enum):
    """Granular permissions"""
    VIEW_CONTENT = "view_content"
    ANALYZE_CONTENT = "analyze_content"
    VIEW_AUDIT_LOG = "view_audit_log"
    EXPORT_AUDIT_LOG = "export_audit_log"
    MANAGE_QUEUE = "manage_queue"
    REVIEW_CONTENT = "review_content"
    ESCALATE = "escalate"
    MANAGE_USERS = "manage_users"
    VIEW_BLOCKCHAIN = "view_blockchain"
    VERIFY_BLOCKCHAIN = "verify_blockchain"


# Role-Permission Mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.VIEW_CONTENT,
        Permission.ANALYZE_CONTENT,
        Permission.VIEW_AUDIT_LOG,
        Permission.EXPORT_AUDIT_LOG,
        Permission.MANAGE_QUEUE,
        Permission.REVIEW_CONTENT,
        Permission.ESCALATE,
        Permission.MANAGE_USERS,
        Permission.VIEW_BLOCKCHAIN,
        Permission.VERIFY_BLOCKCHAIN,
    ],
    Role.MODERATOR: [
        Permission.VIEW_CONTENT,
        Permission.ANALYZE_CONTENT,
        Permission.VIEW_AUDIT_LOG,
        Permission.EXPORT_AUDIT_LOG,
        Permission.MANAGE_QUEUE,
        Permission.REVIEW_CONTENT,
        Permission.ESCALATE,
        Permission.VIEW_BLOCKCHAIN,
        Permission.VERIFY_BLOCKCHAIN,
    ],
    Role.REVIEWER: [
        Permission.VIEW_CONTENT,
        Permission.VIEW_AUDIT_LOG,
        Permission.REVIEW_CONTENT,
        Permission.VIEW_BLOCKCHAIN,
    ],
    Role.VIEWER: [
        Permission.VIEW_CONTENT,
    ],
}


class User:
    """User model with role and permissions"""
    
    def __init__(self, user_id: str, username: str, role: Role, 
                 eth_address: Optional[str] = None, email: Optional[str] = None):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.eth_address = eth_address
        self.email = email
        self.created_at = datetime.utcnow()
        self.last_login = None
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission"""
        return permission in ROLE_PERMISSIONS.get(self.role, [])
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role.value,
            "eth_address": self.eth_address,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "permissions": [p.value for p in ROLE_PERMISSIONS.get(self.role, [])]
        }


class AuthManager:
    """Manages authentication and authorization"""
    
    def __init__(self, users_file: str = "users.json", tokens_file: str = "tokens.json"):
        self.users_file = Path(users_file)
        self.tokens_file = Path(tokens_file)
        self.users: Dict[str, User] = {}
        self.tokens: Dict[str, Dict] = {}
        self._load_users()
        self._load_tokens()
        self._create_default_admin()
    
    def _load_users(self):
        """Load users from file"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r') as f:
                    data = json.load(f)
                    for user_data in data.get('users', []):
                        user = User(
                            user_id=user_data['user_id'],
                            username=user_data['username'],
                            role=Role(user_data['role']),
                            eth_address=user_data.get('eth_address'),
                            email=user_data.get('email')
                        )
                        if user_data.get('created_at'):
                            user.created_at = datetime.fromisoformat(user_data['created_at'])
                        if user_data.get('last_login'):
                            user.last_login = datetime.fromisoformat(user_data['last_login'])
                        self.users[user.user_id] = user
            except Exception as e:
                print(f"Error loading users: {e}")
    
    def _save_users(self):
        """Save users to file"""
        try:
            data = {
                'users': [user.to_dict() for user in self.users.values()]
            }
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def _load_tokens(self):
        """Load tokens from file"""
        if self.tokens_file.exists():
            try:
                with open(self.tokens_file, 'r') as f:
                    self.tokens = json.load(f)
            except Exception as e:
                print(f"Error loading tokens: {e}")
    
    def _save_tokens(self):
        """Save tokens to file"""
        try:
            with open(self.tokens_file, 'w') as f:
                json.dump(self.tokens, f, indent=2)
        except Exception as e:
            print(f"Error saving tokens: {e}")
    
    def _create_default_admin(self):
        """Create default admin user if none exists"""
        if not any(user.role == Role.ADMIN for user in self.users.values()):
            admin = User(
                user_id="admin_001",
                username="admin",
                role=Role.ADMIN,
                email="admin@harmlens.ai"
            )
            self.users[admin.user_id] = admin
            self._save_users()
            print("✓ Default admin user created: admin / admin_001")
    
    def create_user(self, username: str, role: Role, 
                   eth_address: Optional[str] = None,
                   email: Optional[str] = None) -> User:
        """Create a new user"""
        user_id = f"{role.value}_{secrets.token_hex(4)}"
        user = User(user_id, username, role, eth_address, email)
        self.users[user_id] = user
        self._save_users()
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def generate_token(self, user_id: str, expires_in_hours: int = 24) -> str:
        """Generate authentication token"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        self.tokens[token] = {
            "user_id": user_id,
            "username": user.username,
            "role": user.role.value,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        user.last_login = datetime.utcnow()
        self._save_users()
        self._save_tokens()
        
        return token
    
    def validate_token(self, token: str) -> Optional[User]:
        """Validate token and return user"""
        token_data = self.tokens.get(token)
        if not token_data:
            return None
        
        # Check expiration
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        if datetime.utcnow() > expires_at:
            del self.tokens[token]
            self._save_tokens()
            return None
        
        return self.get_user(token_data['user_id'])
    
    def revoke_token(self, token: str):
        """Revoke a token"""
        if token in self.tokens:
            del self.tokens[token]
            self._save_tokens()
    
    def check_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has permission"""
        return user.has_permission(permission)
    
    def list_users(self, role: Optional[Role] = None) -> List[User]:
        """List all users, optionally filtered by role"""
        users = list(self.users.values())
        if role:
            users = [u for u in users if u.role == role]
        return users
    
    def update_user_role(self, user_id: str, new_role: Role) -> bool:
        """Update user's role"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        user.role = new_role
        self._save_users()
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        if user_id in self.users:
            del self.users[user_id]
            self._save_users()
            return True
        return False
    
    def get_audit_access_log(self) -> List[Dict]:
        """Get log of who accessed audit logs"""
        # This would track audit log access
        # For now, return token usage as proxy
        access_log = []
        for token, data in self.tokens.items():
            user = self.get_user(data['user_id'])
            if user and user.has_permission(Permission.VIEW_AUDIT_LOG):
                access_log.append({
                    "user_id": data['user_id'],
                    "username": data['username'],
                    "role": data['role'],
                    "last_access": data['created_at']
                })
        return access_log


# Dependency for FastAPI
def get_current_user(token: str, auth_manager: AuthManager) -> Optional[User]:
    """Get current user from token (for FastAPI dependency)"""
    return auth_manager.validate_token(token)


def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def decorator(func):
        def wrapper(user: User, *args, **kwargs):
            if not user.has_permission(permission):
                raise PermissionError(f"User does not have permission: {permission.value}")
            return func(user, *args, **kwargs)
        return wrapper
    return decorator
