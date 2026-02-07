# 🔐 HarmLens Login Credentials

## Access Dashboard
**URL**: http://localhost:8501

---

## Available Accounts

### 1. Admin Account (Full Access)
```
Username: admin
User ID: admin_001
Role: Admin
Email: admin@harmlens.ai
```

**Permissions**:
- ✅ View all content
- ✅ Analyze content
- ✅ View audit logs
- ✅ Export audit logs
- ✅ Manage moderation queue
- ✅ Review content
- ✅ Escalate issues
- ✅ **Manage users** (Admin only)
- ✅ View blockchain records
- ✅ Verify blockchain integrity

---

### 2. Moderator Account (Content Moderation)
```
Username: moderator
User ID: moderator_001
Role: Moderator
Email: moderator@harmlens.ai
ETH Address: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

**Permissions**:
- ✅ View all content
- ✅ Analyze content
- ✅ View audit logs
- ✅ Export audit logs
- ✅ Manage moderation queue
- ✅ Review content
- ✅ Escalate issues
- ✅ View blockchain records
- ✅ Verify blockchain integrity
- ❌ Manage users (Admin only)

---

## How to Login

### Step 1: Open Dashboard
Open your browser and go to:
```
http://localhost:8501
```

### Step 2: Enter Credentials
Choose one of the accounts above and enter:
- **Username**: (e.g., `admin` or `moderator`)
- **User ID**: (e.g., `admin_001` or `moderator_001`)

### Step 3: Click Login
Click the "🔓 Login" button

### Step 4: Access Dashboard
You'll be redirected to the main dashboard with full access based on your role.

---

## Features by Role

| Feature | Admin | Moderator | Reviewer | Viewer |
|---------|-------|-----------|----------|--------|
| **Dashboard** | ✅ | ✅ | ✅ | ✅ |
| **Analyze Content** | ✅ | ✅ | ❌ | ❌ |
| **View Audit Logs** | ✅ | ✅ | ✅ | ❌ |
| **Export Logs** | ✅ | ✅ | ❌ | ❌ |
| **Blockchain Verification** | ✅ | ✅ | ✅ | ❌ |
| **User Management** | ✅ | ❌ | ❌ | ❌ |

---

## Create New Users

### As Admin:
1. Login with admin credentials
2. Click "👥 User Management" in sidebar
3. Fill in new user details:
   - Username
   - Role (moderator, reviewer, or viewer)
   - Email (optional)
   - ETH Address (optional)
4. Click "Create User"
5. Share the generated User ID with the new user

---

## Content Types Available

When analyzing content, you can select from:
- Social Media Post
- Comment
- Article
- Forum Post
- Review
- Message
- Video Description
- Image Caption
- Other

---

## Platforms Supported

- Twitter/X
- Facebook
- Instagram
- Reddit
- TikTok
- YouTube
- LinkedIn
- Discord
- Other

---

## Security Notes

### Token Expiration
- Tokens expire after **24 hours**
- You'll need to login again after expiration

### Session Management
- Only one active session per user
- Logout from "Settings" or sidebar

### Audit Trail
- All audit log access is **logged on blockchain**
- Every action is tracked for compliance
- Immutable proof of who accessed what

---

## Troubleshooting

### "Invalid credentials"
- ✅ Check spelling of username and user ID
- ✅ Make sure you're using the exact credentials above
- ✅ Try copying and pasting instead of typing

### "Session expired"
- ✅ Your token has expired (24 hours)
- ✅ Simply login again with your credentials

### Can't access certain features
- ✅ Check your role permissions above
- ✅ Some features are admin-only
- ✅ Contact admin to upgrade your role if needed

---

## API Access

If you need programmatic access:

### Get Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "moderator",
    "user_id": "moderator_001"
  }'
```

### Use Token
```bash
curl -X GET "http://localhost:8000/api/v1/audit/logs" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Quick Reference

| Account | Username | User ID | Best For |
|---------|----------|---------|----------|
| **Admin** | `admin` | `admin_001` | System administration, user management |
| **Moderator** | `moderator` | `moderator_001` | Content moderation, audit review |

---

## Support

- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Full Guide**: COMPLETE_SYSTEM_GUIDE.md

---

**Remember**: Keep your credentials secure and don't share them publicly!
