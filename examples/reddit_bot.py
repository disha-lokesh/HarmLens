"""
Working Reddit Bot Integration - ACTUALLY WORKS
This script monitors Reddit and automatically moderates using HarmLens
"""

import praw
import requests
import time
import os
from datetime import datetime

# Configuration
HARMLENS_API_URL = os.getenv('HARMLENS_API_URL', 'http://localhost:8000')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')
SUBREDDIT_NAME = os.getenv('SUBREDDIT_NAME', 'test')  # Your subreddit

# Auto-action thresholds
AUTO_REMOVE_THRESHOLD = 80  # Risk score >= 80: auto-remove
AUTO_FLAIR_THRESHOLD = 60   # Risk score >= 60: add warning flair


def init_reddit():
    """Initialize Reddit API client"""
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD]):
        raise ValueError("Missing Reddit credentials. Set environment variables.")
    
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        user_agent='HarmLens Moderation Bot v1.0'
    )


def analyze_with_harmlens(text: str, reddit_id: str, author: str):
    """Call HarmLens API to analyze content"""
    try:
        response = requests.post(
            f"{HARMLENS_API_URL}/api/v1/analyze",
            json={
                "text": text,
                "content_id": f"reddit_{reddit_id}",
                "user_id": author,
                "platform": "reddit",
                "metadata": {
                    "reddit_id": reddit_id,
                    "timestamp": datetime.now().isoformat()
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error calling HarmLens API: {e}")
        return None


def moderate_submission(reddit, submission, analysis):
    """Take moderation action based on analysis"""
    try:
        risk_score = analysis['risk_score']
        priority = analysis['priority']
        action = analysis['action']
        reasons = analysis['reasons']
        
        print(f"\n📊 Analysis Result:")
        print(f"   Risk Score: {risk_score}/100")
        print(f"   Priority: {priority}")
        print(f"   Action: {action}")
        print(f"   Top Reason: {reasons[0] if reasons else 'N/A'}")
        
        # CRITICAL: Auto-remove immediately
        if priority == 'CRITICAL' or risk_score >= AUTO_REMOVE_THRESHOLD:
            submission.mod.remove(spam=False)
            removal_reason = reasons[0] if reasons else "Content flagged for policy violation"
            submission.mod.send_removal_message(
                f"Your post has been removed.\n\nReason: {removal_reason}\n\n"
                f"If you believe this was a mistake, please contact the moderators."
            )
            print(f"   🚫 REMOVED - Critical risk detected")
            return "removed"
        
        # HIGH: Remove and flag for review
        elif priority == 'HIGH':
            submission.mod.remove(spam=False)
            submission.mod.flair(text='🛡️ Under Review')
            print(f"   ⚠️ REMOVED & FLAIRED - Manual review triggered")
            return "removed_pending_review"
        
        # MEDIUM: Add warning flair
        elif risk_score >= AUTO_FLAIR_THRESHOLD:
            submission.mod.flair(text='⚠️ Disputed Content')
            print(f"   ⚠️ FLAIRED - Soft intervention applied")
            return "flaired"
        
        # LOW: Monitor only
        else:
            print(f"   ✅ APPROVED - Low risk, monitoring")
            return "approved"
            
    except Exception as e:
        print(f"   ❌ Moderation action failed: {e}")
        return "error"


def monitor_subreddit(reddit, subreddit_name):
    """Monitor subreddit for new posts"""
    subreddit = reddit.subreddit(subreddit_name)
    
    print(f"🤖 HarmLens Bot starting...")
    print(f"📡 Monitoring r/{subreddit_name}")
    print(f"🔗 API: {HARMLENS_API_URL}")
    print(f"🚨 Auto-remove threshold: {AUTO_REMOVE_THRESHOLD}")
    print(f"⚠️ Auto-flair threshold: {AUTO_FLAIR_THRESHOLD}")
    print("-" * 60)
    
    # Monitor new submissions
    for submission in subreddit.stream.submissions(skip_existing=True):
        try:
            # Skip if no text content
            if not submission.selftext and not submission.title:
                continue
            
            content = f"{submission.title}\n\n{submission.selftext}"
            author = str(submission.author)
            
            print(f"\n🆕 New post detected:")
            print(f"   ID: {submission.id}")
            print(f"   Author: {author}")
            print(f"   Title: {submission.title[:50]}...")
            
            # Analyze with HarmLens
            analysis = analyze_with_harmlens(content, submission.id, author)
            
            if analysis:
                # Take moderation action
                result = moderate_submission(reddit, submission, analysis)
                
                # Log to console
                print(f"   ✅ Action completed: {result}")
            else:
                print(f"   ⚠️ Analysis failed - skipping moderation")
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error processing submission: {e}")
            continue


if __name__ == "__main__":
    print("=" * 60)
    print("HarmLens Reddit Bot - PRODUCTION MODE")
    print("=" * 60)
    
    try:
        # Initialize Reddit
        reddit = init_reddit()
        print("✅ Reddit API connected")
        
        # Test HarmLens API
        test_response = requests.get(f"{HARMLENS_API_URL}/")
        if test_response.status_code == 200:
            print("✅ HarmLens API connected")
        else:
            raise Exception("HarmLens API not responding")
        
        # Start monitoring
        monitor_subreddit(reddit, SUBREDDIT_NAME)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        print("\nMake sure:")
        print("1. Reddit API credentials are set in environment variables")
        print("2. HarmLens API server is running (python api_server.py)")
        print("3. You have moderator permissions on the subreddit")
