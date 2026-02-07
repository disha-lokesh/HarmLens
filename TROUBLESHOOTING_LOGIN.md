# Login Troubleshooting Guide

## Problem: "Connection Refused" Error

### Error Message
```
API Error: HTTPConnectionPool(host='localhost', port=8000): 
Max retries exceeded with url: /api/v1/auth/login
(Caused by NewConnectionError("HTTPConnection(host='localhost', port=8000): 
Failed to establish a new connection: [Errno 111] Connection refused"))
```

## Solution Steps

### Step 1: Check if API Server is Running
```bash
# Check if port 8000 is in use
lsof -i :8000
```

**Expected Output:**
```
COMMAND   PID  USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
Python  12345  user    6u  IPv4  ...      0t0  TCP *:8000 (LISTEN)
```

**If No Output:** API server is NOT running

### Step 2: Start API Server
```bash
# Make sure you're in the project directory
cd /path/to/HarmLens-main

# Activate virtual environment
source venv/bin/activate

# Start API server
python api_server.py
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Step 3: Start Dashboard (in new terminal)
```bash
# Open new terminal
cd /path/to/HarmLens-main

# Activate virtual environment
source venv/bin/activate

# Start dashboard
streamlit run moderator_dashboard.py
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### Step 4: Login
1. Open browser to http://localhost:8501
2. Enter credentials:
   - **Admin**: username=`admin`, user_id=`admin_001`
   - **Moderator**: username=`moderator`, user_id=`moderator_001`
3. Click "Login"

## Common Issues

### Issue 1: Port Already in Use
**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
uvicorn api_server:app --port 8001
```

### Issue 2: Virtual Environment Not Activated
**Symptom:** `ModuleNotFoundError`

**Solution:**
```bash
# Activate venv
source venv/bin/activate

# Verify activation (should show venv path)
which python
```

### Issue 3: Dependencies Missing
**Symptom:** Import errors

**Solution:**
```bash
# Install dependencies
pip install -r requirements.txt
```

### Issue 4: Database Not Found
**Symptom:** `No such file or directory: harmlens_production.db`

**Solution:**
```bash
# Initialize database
python -c "from core.database import ModerationDatabase; ModerationDatabase()"
```

### Issue 5: API Server Crashed
**Symptom:** Server was running but stopped

**Solution:**
```bash
# Check API server logs
# Look for error messages in terminal where api_server.py is running

# Common fixes:
# 1. Restart API server
python api_server.py

# 2. Check for syntax errors
python -m py_compile api_server.py

# 3. Check database permissions
ls -la harmlens_production.db
```

## Quick Diagnostic Commands

### Check Everything
```bash
# 1. Check API server
curl http://localhost:8000/api/v1/blockchain/stats

# 2. Check if can login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","user_id":"admin_001"}'

# 3. Check database
python -c "from core.database import ModerationDatabase; db = ModerationDatabase(); print(db.get_stats())"

# 4. Check users exist
cat users.json | python -m json.tool
```

## Step-by-Step Fresh Start

If nothing works, try this:

```bash
# 1. Stop everything
# Press Ctrl+C in both terminals (API server and dashboard)

# 2. Kill any lingering processes
pkill -f api_server.py
pkill -f streamlit

# 3. Navigate to project
cd /path/to/HarmLens-main

# 4. Activate venv
source venv/bin/activate

# 5. Verify dependencies
pip install -r requirements.txt

# 6. Test database
python -c "from core.database import ModerationDatabase; print('DB OK')"

# 7. Start API server (Terminal 1)
python api_server.py
# Wait for "Application startup complete"

# 8. Start dashboard (Terminal 2)
streamlit run moderator_dashboard.py
# Wait for "You can now view your Streamlit app"

# 9. Open browser
# Go to http://localhost:8501

# 10. Login
# Use admin/admin_001 or moderator/moderator_001
```

## Verification Checklist

Before attempting login:
- [ ] API server running (check with `lsof -i :8000`)
- [ ] Dashboard running (check with `lsof -i :8501`)
- [ ] Virtual environment activated (prompt shows `(venv)`)
- [ ] Database exists (`ls harmlens_production.db`)
- [ ] Users file exists (`ls users.json`)
- [ ] Can curl API (`curl http://localhost:8000/api/v1/blockchain/stats`)

## Browser Issues

### Clear Cache
1. Open browser DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"

### Try Incognito/Private Mode
- Chrome: Ctrl+Shift+N
- Firefox: Ctrl+Shift+P
- Safari: Cmd+Shift+N

### Check Console for Errors
1. Open DevTools (F12)
2. Go to Console tab
3. Look for red error messages
4. Share errors if asking for help

## Network Issues

### Check Firewall
```bash
# macOS: Check if firewall is blocking
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Allow Python through firewall if needed
```

### Check Localhost Resolution
```bash
# Verify localhost resolves
ping localhost

# Should show 127.0.0.1
```

## Still Not Working?

### Collect Debug Info
```bash
# 1. Check Python version
python --version

# 2. Check installed packages
pip list | grep -E "(streamlit|fastapi|uvicorn)"

# 3. Check API server status
ps aux | grep api_server

# 4. Check ports
lsof -i :8000
lsof -i :8501

# 5. Check logs
# Look at terminal output from both servers
```

### Create Issue Report
Include:
1. Error message (full text)
2. Python version
3. Operating system
4. Output of diagnostic commands above
5. Steps you've already tried

## Contact

For persistent issues:
1. Check UPDATE_SUMMARY_FEB7.md
2. Review MODERATOR_ESCALATION_GUIDE.md
3. Run test suite: `python test_escalation_system.py`
4. Check API logs in terminal

---

**Last Updated**: February 7, 2026
**Version**: 1.0.0
