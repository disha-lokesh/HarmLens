# HarmLens - Quick Reference Card

## 🌐 Access URLs

| Service | URL | Status |
|---------|-----|--------|
| **API Server** | http://localhost:8000 | ✅ Running |
| **API Docs** | http://localhost:8000/docs | ✅ Available |
| **Web UI** | http://localhost:8501 | ✅ Running |

---

## 🔐 Default Login

```
Username: admin
User ID: admin_001
Role: admin (full access)
```

---

## 🚀 Quick Commands

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "user_id": "admin_001"}'
```

### Analyze Content
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "URGENT! Share NOW!", "content_id": "test_001"}'
```

### View Audit Logs (Protected)
```bash
curl -X GET "http://localhost:8000/api/v1/audit/logs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Blockchain Stats
```bash
curl "http://localhost:8000/api/v1/blockchain/stats"
```

---

## 📊 API Endpoints

### Public Endpoints
- `POST /api/v1/analyze` - Analyze content
- `POST /api/v1/batch` - Batch analysis
- `GET /api/v1/stats` - Platform statistics
- `GET /api/v1/blockchain/stats` - Blockchain status

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Current user info

### Protected (Moderator/Admin Only)
- `GET /api/v1/audit/logs` - Audit logs
- `GET /api/v1/audit/blockchain/{id}` - Blockchain audit
- `GET /api/v1/audit/blockchain/{id}/verify` - Verify integrity
- `GET /api/v1/audit/export` - Export logs

### Admin Only
- `POST /api/v1/auth/users` - Create user
- `GET /api/v1/auth/users` - List users

---

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Everything |
| **Moderator** | Content + Audit logs + Blockchain |
| **Reviewer** | Content + Audit logs (read-only) |
| **Viewer** | Content only |

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `api_server.py` | API server |
| `app.py` | Web UI |
| `core/auth.py` | Authentication |
| `core/blockchain.py` | Blockchain integration |
| `core/database.py` | Database |
| `contracts/ModerationAudit.sol` | Smart contract |

---

## 📚 Documentation

| Guide | Purpose |
|-------|---------|
| `README.md` | Project overview |
| `AUTHENTICATION_GUIDE.md` | Auth documentation |
| `BLOCKCHAIN_GUIDE.md` | Blockchain guide |
| `DEPLOYMENT.md` | Deployment options |
| `FINAL_SUMMARY.md` | Complete summary |

---

## 🔧 Troubleshooting

### API Not Responding
```bash
# Check if running
lsof -i :8000

# Restart
python api_server.py
```

### Web UI Not Loading
```bash
# Check if running
lsof -i :8501

# Restart
streamlit run app.py
```

### Authentication Failed
```bash
# Use default admin credentials
username: admin
user_id: admin_001
```

---

## 💡 Quick Tips

1. **API Docs**: Visit http://localhost:8000/docs for interactive testing
2. **Token Expiry**: Tokens expire after 24 hours
3. **Blockchain**: Currently in simulator mode (no network needed)
4. **Audit Logs**: Require moderator authentication
5. **Export**: Use `/api/v1/audit/export` for compliance

---

## 🚀 Deploy to Web

### Fastest (5 minutes)
1. Sign up at render.com
2. Connect GitHub
3. Deploy automatically

### Docker (2 minutes)
```bash
docker-compose up -d
```

### Manual
See `DEPLOYMENT.md` for all options

---

## 📞 Support

- **API Docs**: http://localhost:8000/docs
- **Documentation**: See markdown files
- **Test Suite**: `python test_blockchain_integration.py`

---

**Quick Start**: http://localhost:8501 (Web UI)  
**API Testing**: http://localhost:8000/docs (Swagger)  
**Full Docs**: See `FINAL_SUMMARY.md`
