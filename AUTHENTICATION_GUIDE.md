# Authentication & Authorization Guide

## Overview

HarmLens implements role-based access control (RBAC) to protect sensitive audit logs and blockchain data. Only authenticated moderators and admins can access audit trails.

---

## User Roles

### 1. Admin
**Full system access**
- ✅ View all content
- ✅ Analyze content
- ✅ View audit logs
- ✅ Export audit logs
- ✅ Manage moderation queue
- ✅ Review content
- ✅ Escalate issues
- ✅ Manage users
- ✅ View blockchain records
- ✅ Verify blockchain integrity

### 2. Moderator
**Content moderation and audit access**
- ✅ View all content
- ✅ Analyze content
- ✅ View audit logs
- ✅ Export audit logs
- ✅ Manage moderation queue
- ✅ Review content
- ✅ Escalate issues
- ✅ View blockchain records
- ✅ Verify blockchain integrity
- ❌ Manage users

### 3. Reviewer
**Review-only access**
- ✅ View content
- ✅ View audit logs
- ✅ Review content
- ✅ View blockchain records
- ❌ Analyze new content
- ❌ Export audit logs
- ❌ Manage queue
- ❌ Verify blockchain

### 4. Viewer
**Read-only access**
- ✅ View content
- ❌ All other permissions

---

## Default Users

### Admin Account
```
Username: admin
User ID: admin_001
Role: admin
Email: admin@harmlens.ai
```

**Note**: In production, change default credentials immediately!

---

## Authentication Flow

### 1. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "user_id": "admin_001"
  }'
```

**Response**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "admin_001",
    "username": "admin",
    "role": "admin",
    "permissions": [
      "view_content",
      "analyze_content",
      "view_audit_log",
      "export_audit_log",
      "manage_queue",
      "review_content",
      "escalate",
      "manage_users",
      "view_blockchain",
      "verify_blockchain"
    ]
  },
  "message": "Login successful"
}
```

### 2. Use Token

Include token in Authorization header:

```bash
curl -X GET "http://localhost:8000/api/v1/audit/logs" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Logout

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Protected Endpoints

### Audit Logs (Moderator/Admin Only)

#### Get Audit Logs
```bash
GET /api/v1/audit/logs
Authorization: Bearer {token}
```

**Query Parameters**:
- `limit` (default: 100, max: 1000)
- `offset` (default: 0)
- `risk_label` (optional: "Low", "Medium", "High")
- `priority` (optional: "LOW", "MEDIUM", "HIGH", "CRITICAL")
- `start_date` (optional: ISO format)
- `end_date` (optional: ISO format)

**Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/audit/logs?limit=50&risk_label=High" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get Specific Audit Log
```bash
GET /api/v1/audit/logs/{content_id}
Authorization: Bearer {token}
```

#### Get Blockchain Audit Record
```bash
GET /api/v1/audit/blockchain/{content_id}
Authorization: Bearer {token}
```

#### Verify Blockchain Integrity
```bash
GET /api/v1/audit/blockchain/{content_id}/verify
Authorization: Bearer {token}
```

#### Export Audit Logs
```bash
GET /api/v1/audit/export?format=json
Authorization: Bearer {token}
```

#### Get Audit Statistics
```bash
GET /api/v1/audit/stats
Authorization: Bearer {token}
```

---

## User Management (Admin Only)

### Create User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/users" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "moderator1",
    "role": "moderator",
    "email": "mod1@example.com",
    "eth_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
  }'
```

**Response**:
```json
{
  "user": {
    "user_id": "moderator_a1b2c3d4",
    "username": "moderator1",
    "role": "moderator",
    "email": "mod1@example.com",
    "eth_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "permissions": [...]
  },
  "message": "User created successfully"
}
```

### List Users

```bash
curl -X GET "http://localhost:8000/api/v1/auth/users" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Get Current User Info

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Python Client Example

```python
import requests

class HarmLensClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def login(self, username, user_id):
        """Login and get token"""
        response = requests.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"username": username, "user_id": user_id}
        )
        data = response.json()
        self.token = data['token']
        return data
    
    def get_headers(self):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def get_audit_logs(self, limit=100, risk_label=None):
        """Get audit logs (requires moderator/admin)"""
        params = {"limit": limit}
        if risk_label:
            params["risk_label"] = risk_label
        
        response = requests.get(
            f"{self.base_url}/api/v1/audit/logs",
            headers=self.get_headers(),
            params=params
        )
        return response.json()
    
    def get_blockchain_audit(self, content_id):
        """Get blockchain audit record"""
        response = requests.get(
            f"{self.base_url}/api/v1/audit/blockchain/{content_id}",
            headers=self.get_headers()
        )
        return response.json()
    
    def verify_blockchain_integrity(self, content_id):
        """Verify blockchain integrity"""
        response = requests.get(
            f"{self.base_url}/api/v1/audit/blockchain/{content_id}/verify",
            headers=self.get_headers()
        )
        return response.json()
    
    def export_audit_logs(self, format="json", start_date=None, end_date=None):
        """Export audit logs"""
        params = {"format": format}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = requests.get(
            f"{self.base_url}/api/v1/audit/export",
            headers=self.get_headers(),
            params=params
        )
        return response.json()


# Usage
client = HarmLensClient()

# Login as admin
client.login("admin", "admin_001")

# Get audit logs
logs = client.get_audit_logs(limit=50, risk_label="High")
print(f"Found {logs['total']} high-risk logs")

# Get blockchain audit
audit = client.get_blockchain_audit("post_12345")
print(f"Blockchain record: {audit}")

# Verify integrity
verification = client.verify_blockchain_integrity("post_12345")
print(f"Integrity verified: {verification['verified']}")

# Export logs
export = client.export_audit_logs(format="json")
print(f"Export URL: {export['download_url']}")
```

---

## JavaScript Client Example

```javascript
class HarmLensClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.token = null;
  }

  async login(username, userId) {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, user_id: userId })
    });
    const data = await response.json();
    this.token = data.token;
    return data;
  }

  getHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }

  async getAuditLogs(limit = 100, riskLabel = null) {
    const params = new URLSearchParams({ limit });
    if (riskLabel) params.append('risk_label', riskLabel);

    const response = await fetch(
      `${this.baseUrl}/api/v1/audit/logs?${params}`,
      { headers: this.getHeaders() }
    );
    return response.json();
  }

  async getBlockchainAudit(contentId) {
    const response = await fetch(
      `${this.baseUrl}/api/v1/audit/blockchain/${contentId}`,
      { headers: this.getHeaders() }
    );
    return response.json();
  }

  async verifyBlockchainIntegrity(contentId) {
    const response = await fetch(
      `${this.baseUrl}/api/v1/audit/blockchain/${contentId}/verify`,
      { headers: this.getHeaders() }
    );
    return response.json();
  }
}

// Usage
const client = new HarmLensClient();

// Login
await client.login('admin', 'admin_001');

// Get audit logs
const logs = await client.getAuditLogs(50, 'High');
console.log(`Found ${logs.total} high-risk logs`);

// Get blockchain audit
const audit = await client.getBlockchainAudit('post_12345');
console.log('Blockchain record:', audit);

// Verify integrity
const verification = await client.verifyBlockchainIntegrity('post_12345');
console.log('Integrity verified:', verification.verified);
```

---

## Security Best Practices

### 1. Token Management
- ✅ Tokens expire after 24 hours (configurable)
- ✅ Store tokens securely (never in localStorage for production)
- ✅ Use HTTPS in production
- ✅ Implement token refresh mechanism

### 2. Password Security (Production)
- 🔐 Use bcrypt/argon2 for password hashing
- 🔐 Implement password complexity requirements
- 🔐 Add rate limiting for login attempts
- 🔐 Enable 2FA for admin accounts

### 3. Audit Trail
- 📝 All audit log access is logged
- 📝 Blockchain records who accessed what
- 📝 Immutable proof of access
- 📝 Compliance-ready

### 4. API Security
- 🔒 Rate limiting per user
- 🔒 IP whitelisting for sensitive endpoints
- 🔒 API key rotation
- 🔒 Request signing for critical operations

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

**Solution**: Login again to get new token

### 403 Forbidden
```json
{
  "detail": "Permission denied: view_audit_log required"
}
```

**Solution**: User doesn't have required permission. Contact admin.

### 404 Not Found
```json
{
  "detail": "Content not found"
}
```

**Solution**: Content ID doesn't exist in database

---

## Production Deployment

### Environment Variables

```bash
# Authentication
AUTH_SECRET_KEY=your-secret-key-here
TOKEN_EXPIRY_HOURS=24

# Database
DATABASE_URL=postgresql://user:pass@host:5432/harmlens

# Blockchain
USE_BLOCKCHAIN=true
ETH_PROVIDER_URL=https://polygon-mainnet.infura.io/v3/YOUR_KEY
CONTRACT_ADDRESS=0x...
```

### Enable HTTPS

```python
# In production, use HTTPS only
if not request.is_secure:
    raise HTTPException(status_code=403, detail="HTTPS required")
```

### Add Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/audit/logs")
@limiter.limit("100/hour")
async def get_audit_logs(...):
    ...
```

---

## Monitoring

### Track Audit Access

```python
# Log every audit log access
@app.get("/api/v1/audit/logs")
async def get_audit_logs(user: User = Depends(get_current_user)):
    # Log access
    log_audit_access(
        user_id=user.user_id,
        action="view_audit_logs",
        timestamp=datetime.utcnow()
    )
    ...
```

### Alerts

Set up alerts for:
- Multiple failed login attempts
- Unusual audit log access patterns
- Bulk export requests
- Admin privilege escalation

---

## Compliance

### GDPR
- ✅ Audit trail of all data access
- ✅ User consent tracking
- ✅ Right to access (users can see their data)
- ✅ Right to erasure (with blockchain considerations)

### SOC 2
- ✅ Access control
- ✅ Audit logging
- ✅ Encryption in transit (HTTPS)
- ✅ Encryption at rest (database)

### HIPAA (if handling health data)
- ✅ Role-based access control
- ✅ Audit trails
- ✅ Encryption
- ✅ Access logging

---

## Support

- **Documentation**: See README.md
- **API Reference**: http://localhost:8000/docs
- **Security Issues**: security@harmlens.ai

---

**Remember**: Audit logs contain sensitive moderation data. Only grant access to trusted moderators and admins!
