# HarmLens Deployment Guide

## Quick Deploy Options

### Option 1: Render.com (Easiest - Free Tier Available)

1. **Create account** at [render.com](https://render.com)

2. **Create New Web Service**
   - Connect your GitHub repository
   - Or upload code directly

3. **Configure Service**
   ```
   Name: harmlens-api
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn api_server:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Environment Variables**
   ```
   USE_BLOCKCHAIN=false
   ```

5. **Deploy** - Click "Create Web Service"

Your API will be live at: `https://harmlens-api.onrender.com`

---

### Option 2: Railway.app (Easy - Free $5 Credit)

1. **Create account** at [railway.app](https://railway.app)

2. **New Project** → **Deploy from GitHub**

3. **Configure**
   - Railway auto-detects Python
   - Uses `Procfile` automatically

4. **Add Variables**
   ```
   USE_BLOCKCHAIN=false
   ```

5. **Deploy** - Automatic

Your API will be live at: `https://your-app.up.railway.app`

---

### Option 3: Heroku (Classic)

1. **Install Heroku CLI**
   ```bash
   brew install heroku/brew/heroku  # macOS
   ```

2. **Login**
   ```bash
   heroku login
   ```

3. **Create App**
   ```bash
   heroku create harmlens-api
   ```

4. **Set Config**
   ```bash
   heroku config:set USE_BLOCKCHAIN=false
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

Your API will be live at: `https://harmlens-api.herokuapp.com`

---

### Option 4: Docker (Self-Hosted)

1. **Build Image**
   ```bash
   docker build -t harmlens-api .
   ```

2. **Run Container**
   ```bash
   docker run -d -p 8000:8000 \
     -e USE_BLOCKCHAIN=false \
     --name harmlens \
     harmlens-api
   ```

3. **Or use Docker Compose**
   ```bash
   docker-compose up -d
   ```

Your API will be live at: `http://localhost:8000`

---

### Option 5: DigitalOcean App Platform

1. **Create account** at [digitalocean.com](https://digitalocean.com)

2. **Create App** → **From GitHub**

3. **Configure**
   ```
   Type: Web Service
   Build Command: pip install -r requirements.txt
   Run Command: uvicorn api_server:app --host 0.0.0.0 --port 8080
   ```

4. **Environment Variables**
   ```
   USE_BLOCKCHAIN=false
   PORT=8080
   ```

5. **Deploy**

Your API will be live at: `https://harmlens-api-xxxxx.ondigitalocean.app`

---

### Option 6: AWS (Production)

#### Using AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize**
   ```bash
   eb init -p python-3.11 harmlens-api
   ```

3. **Create Environment**
   ```bash
   eb create harmlens-prod
   ```

4. **Set Environment Variables**
   ```bash
   eb setenv USE_BLOCKCHAIN=false
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

#### Using AWS Lambda + API Gateway

1. **Install Serverless Framework**
   ```bash
   npm install -g serverless
   ```

2. **Create serverless.yml**
   ```yaml
   service: harmlens-api
   
   provider:
     name: aws
     runtime: python3.11
     region: us-east-1
   
   functions:
     api:
       handler: api_server.handler
       events:
         - http:
             path: /{proxy+}
             method: ANY
   ```

3. **Deploy**
   ```bash
   serverless deploy
   ```

---

### Option 7: Google Cloud Run

1. **Install gcloud CLI**
   ```bash
   brew install google-cloud-sdk  # macOS
   ```

2. **Login**
   ```bash
   gcloud auth login
   ```

3. **Build & Deploy**
   ```bash
   gcloud run deploy harmlens-api \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars USE_BLOCKCHAIN=false
   ```

Your API will be live at: `https://harmlens-api-xxxxx.run.app`

---

### Option 8: Vercel (Serverless)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   vercel
   ```

3. **Set Environment Variables** (in Vercel dashboard)
   ```
   USE_BLOCKCHAIN=false
   ```

Your API will be live at: `https://harmlens-api.vercel.app`

---

## Testing Your Deployment

Once deployed, test your API:

```bash
# Replace with your actual URL
curl -X POST "https://your-app-url.com/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "URGENT! Share this NOW!",
    "content_id": "test_001"
  }'
```

Expected response:
```json
{
  "content_id": "test_001",
  "risk_score": 75,
  "risk_label": "High",
  "action": "Human Review Required",
  "blockchain": {
    "logged": false
  }
}
```

---

## API Documentation

Once deployed, visit:
- **Swagger UI**: `https://your-app-url.com/docs`
- **ReDoc**: `https://your-app-url.com/redoc`

---

## Environment Variables

### Required
- `USE_BLOCKCHAIN` - Set to `false` for basic deployment

### Optional (for blockchain)
- `ETH_PROVIDER_URL` - Ethereum node URL
- `CONTRACT_ADDRESS` - Smart contract address
- `ETH_PRIVATE_KEY` - Private key (keep secret!)
- `IPFS_GATEWAY` - IPFS gateway URL

### Optional (for webhooks)
- `WEBHOOK_HIGH_RISK` - Webhook URL for high-risk alerts
- `WEBHOOK_CHILD_SAFETY` - Webhook URL for child safety
- `WEBHOOK_ESCALATION` - Webhook URL for escalations

---

## Custom Domain

### Render.com
1. Go to Settings → Custom Domain
2. Add your domain
3. Update DNS records

### Railway.app
1. Go to Settings → Domains
2. Add custom domain
3. Update DNS records

### Heroku
```bash
heroku domains:add www.yourdomain.com
```

---

## SSL/HTTPS

All platforms provide free SSL certificates automatically:
- ✅ Render.com - Automatic
- ✅ Railway.app - Automatic
- ✅ Heroku - Automatic
- ✅ Vercel - Automatic
- ✅ Google Cloud Run - Automatic

---

## Monitoring

### Health Check Endpoint
```bash
curl https://your-app-url.com/
```

### Stats Endpoint
```bash
curl https://your-app-url.com/api/v1/stats
```

### Blockchain Stats
```bash
curl https://your-app-url.com/api/v1/blockchain/stats
```

---

## Scaling

### Render.com
- Free tier: 512MB RAM
- Paid: Scale up in dashboard

### Railway.app
- Auto-scales based on usage
- Pay per usage

### Heroku
```bash
heroku ps:scale web=2  # Scale to 2 dynos
```

### Docker
```bash
docker-compose up --scale harmlens-api=3
```

---

## Cost Estimates

### Free Tier Options
- **Render.com**: Free (with limitations)
- **Railway.app**: $5 credit/month
- **Vercel**: Free (serverless)
- **Google Cloud Run**: Free tier (2M requests/month)

### Paid Options
- **Render.com**: $7/month (starter)
- **Railway.app**: ~$5-20/month (usage-based)
- **Heroku**: $7/month (hobby)
- **DigitalOcean**: $5/month (basic droplet)
- **AWS**: ~$10-50/month (depends on usage)

---

## Recommended for Production

**Best Overall**: Railway.app or Render.com
- Easy deployment
- Automatic SSL
- Good free tier
- Scales easily

**Best for Scale**: AWS or Google Cloud
- Enterprise-grade
- Full control
- Advanced features

**Best for Serverless**: Vercel or Google Cloud Run
- Pay per request
- Auto-scaling
- No server management

---

## Support

- **Documentation**: See README.md
- **API Guide**: See API_GUIDE.md
- **Blockchain**: See BLOCKCHAIN_GUIDE.md

---

**Ready to deploy!** Choose your platform and follow the steps above.
