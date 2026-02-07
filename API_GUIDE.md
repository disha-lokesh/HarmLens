# Running the HarmLens API Server

## Quick Start

### 1. Start the API Server

```bash
cd harmlens
python api_server.py
```

Or with uvicorn directly:
```bash
uvicorn api_server:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`

### 2. Test the API

```bash
# Test single content analysis
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "URGENT! Share this NOW before they remove it!",
    "content_id": "test_001",
    "platform": "demo"
  }'
```

### 3. View API Documentation

Open in browser: `http://localhost:8000/docs`

This shows interactive Swagger UI with all endpoints.

## API Endpoints

### `POST /api/v1/analyze`
Analyze single piece of content

**Request:**
```json
{
  "text": "Content to analyze",
  "content_id": "optional_id",
  "user_id": "optional_user",
  "platform": "reddit|twitter|facebook"
}
```

**Response:**
```json
{
  "content_id": "test_001",
  "risk_score": 85,
  "risk_label": "High",
  "categories": ["Panic/Fear-mongering", "Mobilization/Call-to-Action"],
  "action": "Human Review Required",
  "priority": "HIGH",
  "queue": "Priority Review Queue",
  "reasons": ["High emotional intensity...", "Contains urgent CTAs..."],
  "child_escalation": false,
  "processing_time_ms": 342.5
}
```

### `POST /api/v1/batch`
Batch analysis

**Request:**
```json
{
  "contents": [
    {"text": "Post 1", "content_id": "1"},
    {"text": "Post 2", "content_id": "2"}
  ]
}
```

### `POST /api/v1/webhook/configure`
Set up webhooks for alerts

**Request:**
```json
{
  "url": "https://yourplatform.com/alerts",
  "events": ["high_risk", "child_safety"],
  "secret": "webhook_secret"
}
```

## Integration Examples

See `http://localhost:8000/integration/examples` for:
- Reddit bot integration code
- Twitter streaming setup
- Facebook webhook handler

## Running Both UI and API

**Terminal 1** - Streamlit UI (port 8501):
```bash
streamlit run app.py
```

**Terminal 2** - FastAPI server (port 8000):
```bash
python api_server.py
```

Now you have:
- **UI for demos**: http://localhost:8501
- **API for integration**: http://localhost:8000

## Production Deployment

### Using Docker:
```bash
docker build -t harmlens .
docker run -p 8000:8000 harmlens
```

### Using Gunicorn (production):
```bash
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Environment Variables:
```bash
export HARMLENS_API_KEY="your_api_key"
export WEBHOOK_SECRET="your_webhook_secret"
export DATABASE_URL="postgresql://..."
```

## Performance

- **Latency**: <500ms per request (CPU), <100ms (GPU)
- **Throughput**: ~100 requests/second (single instance)
- **Scaling**: Deploy multiple instances behind load balancer

## Next Steps

1. **Database integration**: Store results in PostgreSQL/MongoDB
2. **Queue system**: Use Redis/RabbitMQ for queue management
3. **Monitoring**: Add Prometheus metrics
4. **Authentication**: Add API key validation
5. **Rate limiting**: Prevent abuse
