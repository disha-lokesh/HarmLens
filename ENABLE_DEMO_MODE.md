# Enable Demo Mode on Streamlit Cloud

## Quick Fix for Published Link

Your dashboard is deployed on Streamlit Cloud but can't connect to the API server because it's looking for `localhost:8000` which doesn't exist on the cloud.

## Solution: Enable Demo Mode

### Step 1: Go to Streamlit Cloud
1. Open https://share.streamlit.io
2. Login to your account
3. Find your HarmLens app

### Step 2: Add Secrets
1. Click on your app
2. Click the **⋮** (three dots) menu
3. Select **Settings**
4. Click **Secrets** tab
5. Add this configuration:

```toml
DEMO_MODE = "true"
```

6. Click **Save**

### Step 3: Restart App
1. The app will automatically restart
2. Or click **Reboot app** if needed
3. Wait for it to come back online

### Step 4: Test
1. Open your published link
2. You should now see:
   - ✅ No "API Server Not Responding" error
   - ✅ Login page loads
   - ✅ Demo mode banner in sidebar: "🎭 DEMO MODE - Using mock data"
3. Login with:
   - Username: `admin` or `moderator`
   - User ID: `admin_001` or `moderator_001`
4. Dashboard should work with demo data!

## What Demo Mode Does

### ✅ Works
- Login page
- Dashboard UI
- Sidebar navigation
- All page layouts
- Dark mode theme
- Escalation queue UI
- User interface elements

### ⚠️ Limited (Mock Data)
- No real content analysis
- No real database
- No blockchain verification
- No real audit logs
- Demo users only

### ❌ Doesn't Work
- Actual content moderation
- Real-time analysis
- Database persistence
- API integrations
- Webhook delivery

## For Full Functionality

To get real functionality, you need to deploy the API server separately:

### Option 1: Deploy API to Render (Recommended)
1. Go to https://render.com
2. Create account
3. New Web Service
4. Connect GitHub repo
5. Configure:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
6. Deploy
7. Copy URL (e.g., `https://harmlens-api.onrender.com`)

### Option 2: Update Streamlit Secrets
Once API is deployed, update secrets:

```toml
DEMO_MODE = "false"
API_BASE_URL = "https://harmlens-api.onrender.com"
```

## Visual Indicators

### Demo Mode ON
- 🎭 Yellow banner in sidebar: "DEMO MODE"
- Login message: "Login successful (Demo Mode)"
- System status shows: "Demo Mode"

### Demo Mode OFF (Real API)
- No demo banner
- Normal login messages
- Real system status

## Troubleshooting

### Still Shows "API Server Not Responding"
1. Check secrets are saved correctly
2. Restart the app
3. Clear browser cache
4. Check spelling: `DEMO_MODE = "true"` (lowercase true)

### Demo Mode Not Activating
1. Verify secrets syntax (TOML format)
2. Check for typos
3. Ensure quotes around "true"
4. Try redeploying the app

### Want to Disable Demo Mode
Change secrets to:
```toml
DEMO_MODE = "false"
API_BASE_URL = "http://localhost:8000"
```

Or remove the DEMO_MODE line entirely.

## Screenshots Guide

### 1. Find Your App
![Streamlit Cloud Dashboard]
- Go to share.streamlit.io
- See list of your apps

### 2. Open Settings
![App Menu]
- Click ⋮ (three dots)
- Select "Settings"

### 3. Add Secrets
![Secrets Tab]
- Click "Secrets" tab
- Paste: `DEMO_MODE = "true"`
- Click "Save"

### 4. Verify Demo Mode
![Demo Banner]
- Open your app
- See 🎭 DEMO MODE banner in sidebar
- Login works without API server

## Cost Comparison

### Demo Mode
- **Cost**: $0
- **Functionality**: UI only
- **Use Case**: Demos, presentations, UI testing

### Full Deployment
- **Cost**: $0-7/month
- **Functionality**: Full features
- **Use Case**: Production, real moderation

## Next Steps

### For Demo/Presentation
✅ Enable demo mode (you're done!)

### For Production
1. Deploy API server to Render
2. Update API_BASE_URL in secrets
3. Disable demo mode
4. Test full functionality

## Quick Reference

### Enable Demo Mode
```toml
DEMO_MODE = "true"
```

### Disable Demo Mode + Use Deployed API
```toml
DEMO_MODE = "false"
API_BASE_URL = "https://your-api-server.com"
```

### Disable Demo Mode + Use Local API
```toml
DEMO_MODE = "false"
API_BASE_URL = "http://localhost:8000"
```

---

**Quick Fix**: Add `DEMO_MODE = "true"` to Streamlit Cloud secrets
**Full Solution**: Deploy API server + configure API_BASE_URL
**Documentation**: See STREAMLIT_CLOUD_DEPLOYMENT.md for details
