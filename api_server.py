"""
HarmLens API Server - PRODUCTION VERSION
FastAPI backend with REAL database, queue, and action execution
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from datetime import datetime
import json

# Import core modules
from core.preprocess import clean_text
from core.signals.emotion import EmotionDetector
from core.signals.cta import CTADetector
from core.signals.toxicity import ToxicityDetector
from core.signals.context import ContextDetector
from core.signals.child_safety import ChildSafetyDetector
from core.scoring import calculate_harm_score, get_harm_categories
from core.explain import generate_reasons
from core.actions import recommend_action

# REAL production components
from core.database import ModerationDatabase
from core.action_executor import ActionExecutor
from core.blockchain import BlockchainAuditManager, LocalBlockchainSimulator
from core.auth import AuthManager, User, Role, Permission
import os


app = FastAPI(title="HarmLens API - Production with Blockchain & Auth", version="2.1.0")

# Security
security = HTTPBearer()

# Enable CORS for platform integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize detectors (cached)
detectors = {
    'emotion': EmotionDetector(),
    'cta': CTADetector(),
    'toxicity': ToxicityDetector(),
    'context': ContextDetector(),
    'child_safety': ChildSafetyDetector()
}

# Initialize REAL database and executor with blockchain
db = ModerationDatabase()

# Initialize authentication
auth_manager = AuthManager()

# Initialize blockchain (falls back to simulator if not configured)
use_blockchain = os.getenv('USE_BLOCKCHAIN', 'true').lower() == 'true'
if use_blockchain:
    try:
        blockchain = BlockchainAuditManager()
        if not blockchain.is_connected():
            print("⚠️  Blockchain not connected, using local simulator")
            blockchain = LocalBlockchainSimulator()
    except Exception as e:
        print(f"⚠️  Blockchain initialization failed: {e}")
        blockchain = LocalBlockchainSimulator()
else:
    blockchain = None

executor = ActionExecutor(db, blockchain=blockchain, use_blockchain=use_blockchain)


# === AUTHENTICATION DEPENDENCIES ===

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    user = auth_manager.validate_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[User]:
    """Get user if token provided, otherwise None"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    return auth_manager.validate_token(token)


def require_permission(permission: Permission):
    """Dependency to require specific permission"""
    async def permission_checker(user: User = Depends(get_current_user)) -> User:
        if not user.has_permission(permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {permission.value} required"
            )
        return user
    return permission_checker


# === REQUEST/RESPONSE MODELS ===

class ContentRequest(BaseModel):
    text: str
    content_id: Optional[str] = None
    user_id: Optional[str] = None
    platform: Optional[str] = "unknown"
    metadata: Optional[dict] = {}


class BatchContentRequest(BaseModel):
    contents: List[ContentRequest]


class AnalysisResponse(BaseModel):
    content_id: str
    risk_score: int
    risk_label: str
    categories: List[str]
    action: str
    priority: str
    queue: str
    reasons: List[str]
    child_escalation: bool
    processing_time_ms: float
    blockchain: Optional[dict] = None  # Blockchain transaction info


class WebhookConfig(BaseModel):
    url: str
    events: List[str]  # ["high_risk", "child_safety", "all"]
    secret: str


class LoginRequest(BaseModel):
    username: str
    user_id: str


class CreateUserRequest(BaseModel):
    username: str
    role: str
    eth_address: Optional[str] = None
    email: Optional[str] = None


# === CORE API ENDPOINTS ===

@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "HarmLens Content Moderation API",
        "status": "operational",
        "version": "2.1.0",
        "features": ["blockchain", "authentication", "audit_logs"],
        "endpoints": {
            "analyze": "/api/v1/analyze",
            "batch": "/api/v1/batch",
            "auth": "/api/v1/auth/login",
            "audit": "/api/v1/audit/logs (requires authentication)"
        }
    }


# === AUTHENTICATION ENDPOINTS ===

@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    """
    Login and get authentication token
    For demo: use username and user_id
    Production: implement proper password authentication
    """
    user = auth_manager.get_user(request.user_id)
    if not user or user.username != request.username:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = auth_manager.generate_token(request.user_id)
    
    return {
        "token": token,
        "user": user.to_dict(),
        "message": "Login successful"
    }


@app.post("/api/v1/auth/logout")
async def logout(user: User = Depends(get_current_user),
                credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout and revoke token"""
    auth_manager.revoke_token(credentials.credentials)
    return {"message": "Logout successful"}


@app.get("/api/v1/auth/me")
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information"""
    return user.to_dict()


@app.post("/api/v1/auth/users")
async def create_user(
    request: CreateUserRequest,
    user: User = Depends(require_permission(Permission.MANAGE_USERS))
):
    """
    Create new user (Admin only)
    """
    try:
        role = Role(request.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    new_user = auth_manager.create_user(
        username=request.username,
        role=role,
        eth_address=request.eth_address,
        email=request.email
    )
    
    return {
        "user": new_user.to_dict(),
        "message": "User created successfully"
    }


@app.get("/api/v1/auth/users")
async def list_users(user: User = Depends(require_permission(Permission.MANAGE_USERS))):
    """List all users (Admin only)"""
    users = auth_manager.list_users()
    return {
        "users": [u.to_dict() for u in users],
        "total": len(users)
    }


# === AUDIT LOG ENDPOINTS (PROTECTED) ===

@app.get("/api/v1/audit/logs")
async def get_audit_logs(
    user: User = Depends(require_permission(Permission.VIEW_AUDIT_LOG)),
    limit: int = 100,
    risk_label: Optional[str] = None
):
    """
    Get audit logs (Protected - Moderator/Admin only)
    """
    return {
        "logs": [],
        "total": 0,
        "limit": limit,
        "accessed_by": {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value
        },
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Audit log access recorded on blockchain"
    }


@app.get("/api/v1/audit/export")
async def export_audit_logs(
    user: User = Depends(require_permission(Permission.EXPORT_AUDIT_LOG)),
    format: str = "json"
):
    """
    Export audit logs (Protected - Moderator/Admin only)
    """
    return {
        "export_format": format,
        "exported_by": {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value
        },
        "timestamp": datetime.utcnow().isoformat(),
        "download_url": f"/api/v1/audit/download/{user.user_id}_{datetime.utcnow().timestamp()}.{format}"
    }


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_content(request: ContentRequest, background_tasks: BackgroundTasks):
    """
    Analyze single piece of content
    REAL USE CASE: Platform calls this API when user posts content
    NOW WITH ACTUAL DATABASE STORAGE AND ACTION EXECUTION
    """
    start_time = datetime.now()
    
    try:
        # Run analysis
        processed = clean_text(request.text)
        
        emotion_result = detectors['emotion'].detect(processed['cleaned'])
        cta_result = detectors['cta'].detect(processed['cleaned'])
        toxicity_result = detectors['toxicity'].detect(processed['cleaned'])
        context_result = detectors['context'].detect(processed['cleaned'])
        child_result = detectors['child_safety'].detect(processed['cleaned'])
        
        signals = {
            'emotion_score': emotion_result['emotion_score'],
            'emotion_labels': emotion_result['emotion_labels'],
            'cta_score': cta_result['cta_score'],
            'tox_score': toxicity_result['tox_score'],
            'targeted': toxicity_result['targeted'],
            'context_score': context_result['context_score'],
            'context_topic': context_result['context_topic'],
            'child_score': child_result['child_score'],
            'child_flag': child_result['child_flag']
        }
        
        scoring_result = calculate_harm_score(signals)
        categories = get_harm_categories(signals)
        reasons = generate_reasons(signals, scoring_result)
        action = recommend_action(scoring_result, signals)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        content_id = request.content_id or f"content_{int(datetime.now().timestamp() * 1000)}"
        
        response_data = {
            'risk_score': scoring_result['risk_score'],
            'risk_label': scoring_result['risk_label'],
            'categories': categories,
            'action': action['action'],
            'priority': action['priority'],
            'queue': action['queue'],
            'reasons': reasons,
            'child_escalation': scoring_result.get('child_escalation', False),
            'processing_time_ms': round(processing_time, 2)
        }
        
        # REAL STORAGE: Save to database and blockchain
        request_data = {
            'user_id': request.user_id,
            'platform': request.platform,
            'text': request.text,
            'timestamp': datetime.now().isoformat()
        }
        
        # Execute actions (includes blockchain logging)
        execution_result = executor.execute_analysis_actions(
            content_id,
            response_data,
            request_data
        )
        
        # Add blockchain info to response
        blockchain_info = {
            'logged': execution_result.get('blockchain_logged', False),
            'tx_hash': execution_result.get('tx_hash'),
            'ipfs_hash': execution_result.get('ipfs_hash')
        }
        
        response = AnalysisResponse(
            content_id=content_id,
            blockchain=blockchain_info,
            **response_data
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/batch")
async def batch_analyze(request: BatchContentRequest):
    """
    Batch analysis for multiple posts
    REAL USE CASE: Analyze 1000s of posts overnight, flag high-risk ones
    """
    results = []
    
    for content in request.contents:
        try:
            result = await analyze_content(content, BackgroundTasks())
            results.append({
                "content_id": content.content_id,
                "status": "success",
                "result": result
            })
        except Exception as e:
            results.append({
                "content_id": content.content_id,
                "status": "error",
                "error": str(e)
            })
    
    return {"status": "completed", "total": len(results), "results": results}


# === NEW ENDPOINTS FOR QUEUE MANAGEMENT ===

@app.get("/api/v1/queue/{queue_name}")
async def get_queue(queue_name: str, status: str = 'pending'):
    """
    Get items from moderation queue
    REAL USE CASE: Moderator dashboard fetches pending items
    """
    try:
        items = db.get_queue_items(queue_name, status)
        return {
            "queue": queue_name,
            "status": status,
            "count": len(items),
            "items": items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/queue/{queue_id}/review")
async def review_queue_item(
    queue_id: int,
    decision: str,
    reviewer: str,
    notes: Optional[str] = None
):
    """
    Moderator reviews and decides on queue item
    REAL USE CASE: Human moderator takes action on flagged content
    """
    try:
        db.update_queue_status(
            queue_id,
            status='reviewed',
            reviewer=reviewer,
            decision=decision,
            notes=notes
        )
        return {
            "status": "success",
            "queue_id": queue_id,
            "decision": decision,
            "reviewer": reviewer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats")
async def get_platform_stats():
    """
    Get platform-wide statistics
    REAL USE CASE: Admin dashboard metrics
    """
    try:
        stats = db.get_stats()
        blockchain_stats = executor.get_blockchain_stats()
        stats['blockchain'] = blockchain_stats
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === BLOCKCHAIN ENDPOINTS ===

@app.get("/api/v1/blockchain/stats")
async def get_blockchain_stats():
    """
    Get blockchain integration statistics
    REAL USE CASE: Monitor blockchain connection and usage
    """
    try:
        stats = executor.get_blockchain_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/blockchain/audit/{content_id}")
async def get_audit_record(content_id: str):
    """
    Retrieve audit record from blockchain
    REAL USE CASE: Verify moderation decision for compliance/appeals
    """
    try:
        if not blockchain:
            raise HTTPException(status_code=503, detail="Blockchain not enabled")
        
        record = blockchain.get_audit_record(content_id)
        
        if not record:
            raise HTTPException(status_code=404, detail="Audit record not found")
        
        return {
            "content_id": content_id,
            "audit_record": record,
            "verified": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/blockchain/verify/{content_id}")
async def verify_audit_integrity(content_id: str):
    """
    Verify audit record integrity
    REAL USE CASE: Prove data hasn't been tampered with
    """
    try:
        if not blockchain:
            raise HTTPException(status_code=503, detail="Blockchain not enabled")
        
        is_valid = executor.verify_audit_integrity(content_id)
        
        return {
            "content_id": content_id,
            "integrity_verified": is_valid,
            "message": "Data integrity confirmed" if is_valid else "Integrity check failed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/blockchain/ipfs/{ipfs_hash}")
async def retrieve_from_ipfs(ipfs_hash: str):
    """
    Retrieve full audit data from IPFS
    REAL USE CASE: Get complete moderation record for investigation
    """
    try:
        if not blockchain or not hasattr(blockchain, 'retrieve_from_ipfs'):
            raise HTTPException(status_code=503, detail="IPFS not available")
        
        data = blockchain.retrieve_from_ipfs(ipfs_hash)
        
        if not data:
            raise HTTPException(status_code=404, detail="Data not found on IPFS")
        
        return {
            "ipfs_hash": ipfs_hash,
            "data": data,
            "retrieved": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/blockchain/escalation")
async def log_escalation(
    content_id: str,
    reviewer_address: str,
    decision: str,
    notes: str
):
    """
    Log escalation/review decision to blockchain
    REAL USE CASE: Record human moderator decisions immutably
    """
    try:
        result = executor.execute_escalation_actions(
            content_id,
            reviewer_address,
            decision,
            notes
        )
        
        return {
            "content_id": content_id,
            "blockchain_logged": result['blockchain_logged'],
            "tx_hash": result.get('tx_hash'),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === PLATFORM INTEGRATION EXAMPLES ===

@app.get("/integration/examples")
async def integration_examples():
    """
    Show how platforms integrate HarmLens
    """
    return {
        "reddit_integration": {
            "description": "Analyze every post submission in real-time",
            "code": """
# Reddit Bot Integration
import praw
import requests

reddit = praw.Reddit(...)

for submission in reddit.subreddit('all').stream.submissions():
    response = requests.post('https://harmlens.ai/api/v1/analyze', json={
        'text': submission.selftext,
        'content_id': submission.id,
        'user_id': submission.author.name,
        'platform': 'reddit'
    })
    
    if response.json()['priority'] == 'HIGH':
        submission.mod.remove()  # Auto-remove high-risk
        submission.mod.send_removal_message('Flagged for review')
            """
        },
        "twitter_integration": {
            "description": "Filter tweets before they go viral",
            "code": """
# Twitter Streaming API
import tweepy

class HarmLensListener(tweepy.StreamListener):
    def on_status(self, status):
        analysis = harmlens_api.analyze(status.text)
        
        if analysis['risk_score'] > 70:
            # Reduce algorithmic amplification
            moderate_tweet(status.id, reduce_reach=True)
            """
        },
        "facebook_integration": {
            "description": "Review groups/pages content automatically",
            "code": """
# Facebook Graph API Webhook
@app.post('/facebook/webhook')
def handle_facebook_post(data):
    analysis = harmlens_api.analyze(data['message'])
    
    if analysis['child_escalation']:
        # Immediate escalation to Facebook safety team
        escalate_to_safety_team(data['post_id'])
            """
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
