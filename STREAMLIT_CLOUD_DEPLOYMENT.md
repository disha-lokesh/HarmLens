# Streamlit Cloud Deployment Guide

## Problem: API Server Not Available on Deployed Link

When you deploy the dashboard to Streamlit Cloud, it can't connect to `localhost:8000` because:
1. The API server is not running on Streamlit Cloud
2. Streamlit Cloud only hosts the Streamlit app, not FastAPI servers

## Solution Options

### Option 1: Deploy API Server Separately (Recommended)

#### Step 1: Deploy API Server
Deploy `api_server.py` to a hosting service:

**Recommended Services:**
- **Render** (Free tier available)
- **Railway** (Free tier available)
- **Heroku** (Paid)
- **DigitalOcean App Platform**
- **AWS EC2/Lambda**
- **Google Cloud Run**

**Example: Deploy to Render**
1. Go to https://render.com
2. Create new "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
5. Add environment variables if needed
6. Deploy
7. Copy the deployed URL (e.g., `https://harmlens-api.onrender.com`)

#### Step 2: Configure Dashboard
In Streamlit Cloud:
1. Go to your app settings
2. Click "Secrets"
3. Add:
```toml
API_BASE_URL = "https://your-api-server.onrender.com"
```
4. Save and restart app

### Option 2: Combined Deployment (Not Recommended)

Run both in the same container (complex, not ideal for Streamlit Cloud):
- Requires custom Docker setup
- Not supported on Streamlit Cloud free tier
- Better to use separate deployments

### Option 3: Mock API for Demo (Quick Fix)

If you just want to demo the UI without backend:

1. Create a mock API mode in the dashboard
2. Return fake data for demo purposes
3. Show "Demo Mode" banner

## Quick Fix: Add Demo Mode

Let me add a demo mode that works without API server:

### Step 1: Update Dashboard

Add this to `moderator_dashboard.py`:

```python
# At the top, after imports
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# In api_request function
def api_request(endpoint, method="GET", data=None, auth_required=True):
    if DEMO_MODE:
        return get_mock_response(endpoint, method, data)
    # ... rest of existing code
```

### Step 2: Configure Streamlit Cloud

In Streamlit Cloud secrets:
```toml
DEMO_MODE = "true"
```

## Current Deployment Architecture

### Local Development
```
┌─────────────────┐         ┌─────────────────┐
│   Dashboard     │ ──────> │   API Server    │
│  localhost:8501 │         │  localhost:8000 │
└─────────────────┘         └─────────────────┘
```

### Deployed (Recommended)
```
┌─────────────────────┐         ┌──────────────────────┐
│   Dashboard         │ ──────> │   API Server         │
│  streamlit.app      │         │  render.com          │
│  (Streamlit Cloud)  │         │  (Render/Railway)    │
└─────────────────────┘         └──────────────────────┘
```

## Step-by-Step: Full Deployment

### 1. Deploy API Server to Render

**Create `render.yaml`:**
```yaml
services:
  - type: web
    name: harmlens-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api_server:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: HARMLENS_LIGHTWEIGHT
        value: "1"
```

**Deploy:**
1. Push code to GitHub
2. Go to Render.com
3. New Web Service → Connect GitHub repo
4. Render will auto-detect `render.yaml`
5. Deploy
6. Note the URL: `https://harmlens-api.onrender.com`

### 2. Deploy Dashboard to Streamlit Cloud

**Configure Secrets:**
1. Go to Streamlit Cloud
2. Your app → Settings → Secrets
3. Add:
```toml
API_BASE_URL = "https://harmlens-api.onrender.com"
```

**Deploy:**
1. Push code to GitHub
2. Go to Streamlit Cloud
3. New app → Connect GitHub repo
4. Main file: `moderator_dashboard.py`
5. Deploy

### 3. Test

1. Open Streamlit Cloud URL
2. Should now connect to deployed API
3. Login with credentials
4. Everything should work!

## Environment Variables

### For API Server (Render/Railway)
```bash
HARMLENS_LIGHTWEIGHT=1          # Use lightweight models
DATABASE_URL=sqlite:///harmlens.db  # Database path
BLOCKCHAIN_MODE=simulator       # Blockchain mode
```

### For Dashboard (Streamlit Cloud)
```toml
API_BASE_URL = "https://your-api-server.com"
DEMO_MODE = "false"
```

## Cost Estimates

### Free Tier Options
- **Streamlit Cloud**: Free (dashboard)
- **Render**: Free tier (API server, sleeps after 15min inactivity)
- **Railway**: $5 credit/month free
- **Total**: $0-5/month

### Paid Options
- **Render**: $7/month (always on)
- **Heroku**: $7/month per dyno
- **DigitalOcean**: $5/month droplet
- **Total**: $12-14/month

## Troubleshooting

### Dashboard Shows "API Server Not Responding"

**Check:**
1. Is API server deployed and running?
2. Is API_BASE_URL correct in secrets?
3. Is API server URL accessible? (try in browser)
4. Check API server logs for errors

**Test API Server:**
```bash
curl https://your-api-server.com/api/v1/blockchain/stats
```

Should return JSON response.

### API Server Sleeping (Render Free Tier)

**Problem:** Render free tier sleeps after 15min inactivity

**Solutions:**
1. Upgrade to paid tier ($7/month)
2. Use a ping service (UptimeRobot) to keep it awake
3. Accept 30-second cold start delay
4. Use Railway instead (better free tier)

### CORS Errors

If you see CORS errors in browser console:

**Fix in `api_server.py`:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific Streamlit Cloud URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Alternative: All-in-One Deployment

### Using Docker + Cloud Run

**Create `Dockerfile.combined`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

# Start both services
CMD uvicorn api_server:app --host 0.0.0.0 --port 8000 & \
    streamlit run moderator_dashboard.py --server.port 8501
```

**Deploy to Google Cloud Run:**
```bash
gcloud run deploy harmlens \
  --source . \
  --port 8501 \
  --allow-unauthenticated
```

## Recommended Setup

For production:

1. **API Server**: Render ($7/month, always on)
2. **Dashboard**: Streamlit Cloud (Free)
3. **Database**: Render PostgreSQL (Free tier)
4. **Blockchain**: Polygon testnet (Free)

**Total Cost**: $7/month

## Quick Demo Mode (No API Server)

If you just want to show the UI:

1. In Streamlit Cloud secrets:
```toml
DEMO_MODE = "true"
```

2. Dashboard will use mock data
3. Show "Demo Mode" banner
4. All UI features work, no real backend

## Next Steps

Choose your deployment strategy:
1. **Full Production**: Deploy API + Dashboard separately
2. **Demo Only**: Enable demo mode
3. **Local Only**: Keep using localhost

For full production deployment, follow the Render + Streamlit Cloud guide above.

---

**Last Updated**: February 7, 2026
**Recommended**: Deploy API to Render, Dashboard to Streamlit Cloud
