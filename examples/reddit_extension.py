"""
HarmLens Reddit Extension
Real-time content moderation bot for Reddit communities

INSTALLATION:
1. pip install praw
2. Create Reddit app at https://www.reddit.com/prefs/apps
3. Set environment variables or update config below
4. Run: python reddit_extension.py

FEATURES:
- Real-time monitoring of new posts and comments
- Automatic flagging/removal of high-risk content
- Moderator notifications for escalations
- Blockchain audit trail for all actions
- Dashboard integration for manual review
"""

import praw
import requests
import time
import os
from datetime import datetime
from typing import Dict, Optional
import json


# ===== CONFIGURATION =====

# Reddit API Credentials
REDDIT_CONFIG = {
    'client_id': os.getenv('REDDIT_CLIENT_ID', 'YOUR_CLIENT_ID'),
    'client_secret': os.getenv('REDDIT_CLIENT_SECRET', 'YOUR_CLIENT_SECRET'),
    'user_agent': 'HarmLens Moderation Bot v1.0',
    'username': os.getenv('REDDIT_USERNAME', 'YOUR_BOT_USERNAME'),
    'password': os.getenv('REDDIT_PASSWORD', 'YOUR_BOT_PASSWORD')
}

# HarmLens API Configuration
HARMLENS_API = os.getenv('HARMLENS_API', 'http://localhost:8000')

# Subreddit to monitor
SUBREDDIT_NAME = os.getenv('SUBREDDIT', 'test')  # Change to your subreddit

# Moderation Settings
MODERATION_SETTINGS = {
    'auto_remove_threshold': 80,  # Auto-remove if risk_score >= 80
    'auto_flag_threshold': 60,    # Flag for review if risk_score >= 60
    'notify_moderators': True,     # Send modmail for high-risk content
    'add_removal_reason': True,    # Add removal reason to removed posts
    'log_to_blockchain': True      # Log all actions to blockchain
}


# ===== HARMLENS INTEGRATION =====

class HarmLensClient:
    """Client for HarmLens API"""
    
    def __init__(self, api_base: str):
        self.api_base = api_base
        self.session = requests.Session()
    
    def analyze_content(self, text: str, content_id: str, 
                       user_id: str, metadata: Dict = None) -> Optional[Dict]:
        """Analyze content using HarmLens API"""
        try:
            response = self.session.post(
                f"{self.api_base}/api/v1/analyze",
                json={
                    "text": text,
                    "content_id": content_id,
                    "user_id": user_id,
                    "platform": "reddit",
                    "metadata": metadata or {}
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return None


# ===== REDDIT BOT =====

class HarmLensRedditBot:
    """Reddit moderation bot powered by HarmLens"""
    
    def __init__(self, reddit_config: Dict, harmlens_api: str, 
                 subreddit: str, settings: Dict):
        self.reddit = praw.Reddit(**reddit_config)
        self.subreddit = self.reddit.subreddit(subreddit)
        self.harmlens = HarmLensClient(harmlens_api)
        self.settings = settings
        
        print(f"✅ Connected to Reddit as: {self.reddit.user.me()}")
        print(f"✅ Monitoring r/{subreddit}")
        print(f"✅ HarmLens API: {harmlens_api}")
    
    def moderate_submission(self, submission):
        """Moderate a Reddit submission (post)"""
        try:
            # Skip if already removed
            if submission.removed:
                return
            
            # Analyze content
            text = f"{submission.title}\n\n{submission.selftext}"
            
            analysis = self.harmlens.analyze_content(
                text=text,
                content_id=submission.id,
                user_id=str(submission.author),
                metadata={
                    "type": "submission",
                    "subreddit": str(submission.subreddit),
                    "url": submission.url,
                    "score": submission.score,
                    "num_comments": submission.num_comments
                }
            )
            
            if not analysis:
                return
            
            risk_score = analysis['risk_score']
            risk_label = analysis['risk_label']
            action = analysis['action']
            
            print(f"\n📊 Post Analysis: u/{submission.author}")
            print(f"   Risk Score: {risk_score}/100 ({risk_label})")
            print(f"   Action: {action}")
            print(f"   Categories: {', '.join(analysis['categories'])}")
            
            # Take action based on risk score
            if risk_score >= self.settings['auto_remove_threshold']:
                self._remove_submission(submission, analysis)
            
            elif risk_score >= self.settings['auto_flag_threshold']:
                self._flag_submission(submission, analysis)
            
            # Child safety escalation
            if analysis.get('child_escalation'):
                self._escalate_to_admins(submission, analysis)
            
        except Exception as e:
            print(f"❌ Error moderating submission: {e}")
    
    def moderate_comment(self, comment):
        """Moderate a Reddit comment"""
        try:
            # Skip if already removed
            if comment.removed:
                return
            
            # Analyze content
            analysis = self.harmlens.analyze_content(
                text=comment.body,
                content_id=comment.id,
                user_id=str(comment.author),
                metadata={
                    "type": "comment",
                    "subreddit": str(comment.subreddit),
                    "parent_id": comment.parent_id,
                    "score": comment.score
                }
            )
            
            if not analysis:
                return
            
            risk_score = analysis['risk_score']
            risk_label = analysis['risk_label']
            
            print(f"\n💬 Comment Analysis: u/{comment.author}")
            print(f"   Risk Score: {risk_score}/100 ({risk_label})")
            
            # Take action based on risk score
            if risk_score >= self.settings['auto_remove_threshold']:
                self._remove_comment(comment, analysis)
            
            elif risk_score >= self.settings['auto_flag_threshold']:
                self._flag_comment(comment, analysis)
            
            # Child safety escalation
            if analysis.get('child_escalation'):
                self._escalate_to_admins(comment, analysis)
            
        except Exception as e:
            print(f"❌ Error moderating comment: {e}")
    
    def _remove_submission(self, submission, analysis: Dict):
        """Remove submission and notify user"""
        try:
            submission.mod.remove()
            
            if self.settings['add_removal_reason']:
                reasons = "\n".join([f"- {r}" for r in analysis['reasons'][:3]])
                removal_message = f"""
Your post has been removed by our automated moderation system.

**Risk Assessment**: {analysis['risk_label']} Risk ({analysis['risk_score']}/100)

**Reasons**:
{reasons}

If you believe this was a mistake, please contact the moderators.

*This action was logged on blockchain for transparency.*
                """
                submission.mod.send_removal_message(removal_message)
            
            print(f"   ✅ Removed post: {submission.id}")
            
            # Notify moderators
            if self.settings['notify_moderators']:
                self._notify_moderators(submission, analysis, "removed")
            
        except Exception as e:
            print(f"   ❌ Failed to remove: {e}")
    
    def _remove_comment(self, comment, analysis: Dict):
        """Remove comment"""
        try:
            comment.mod.remove()
            print(f"   ✅ Removed comment: {comment.id}")
            
            if self.settings['notify_moderators'] and analysis['risk_score'] >= 85:
                self._notify_moderators(comment, analysis, "removed")
            
        except Exception as e:
            print(f"   ❌ Failed to remove: {e}")
    
    def _flag_submission(self, submission, analysis: Dict):
        """Flag submission for manual review"""
        try:
            # Report to mod queue
            submission.report(f"HarmLens: {analysis['risk_label']} Risk ({analysis['risk_score']}/100)")
            print(f"   🚩 Flagged for review: {submission.id}")
            
        except Exception as e:
            print(f"   ❌ Failed to flag: {e}")
    
    def _flag_comment(self, comment, analysis: Dict):
        """Flag comment for manual review"""
        try:
            comment.report(f"HarmLens: {analysis['risk_label']} Risk ({analysis['risk_score']}/100)")
            print(f"   🚩 Flagged for review: {comment.id}")
            
        except Exception as e:
            print(f"   ❌ Failed to flag: {e}")
    
    def _escalate_to_admins(self, item, analysis: Dict):
        """Escalate to Reddit admins for child safety issues"""
        try:
            print(f"   🚨 CHILD SAFETY ESCALATION: {item.id}")
            
            # Send modmail
            self.subreddit.message(
                subject="🚨 URGENT: Child Safety Escalation",
                message=f"""
HarmLens has detected potential child safety concerns.

**Content ID**: {item.id}
**Author**: u/{item.author}
**Risk Score**: {analysis['risk_score']}/100
**Categories**: {', '.join(analysis['categories'])}

**Immediate action required.**

View in dashboard: http://localhost:8501
Blockchain record: {analysis.get('blockchain', {}).get('tx_hash', 'N/A')}
                """
            )
            
        except Exception as e:
            print(f"   ❌ Failed to escalate: {e}")
    
    def _notify_moderators(self, item, analysis: Dict, action: str):
        """Send modmail notification to moderators"""
        try:
            item_type = "Post" if hasattr(item, 'title') else "Comment"
            
            self.subreddit.message(
                subject=f"HarmLens: {analysis['risk_label']} Risk Content {action.title()}",
                message=f"""
**{item_type} {action}** by automated moderation.

**Author**: u/{item.author}
**Content ID**: {item.id}
**Risk Score**: {analysis['risk_score']}/100
**Action**: {analysis['action']}
**Priority**: {analysis['priority']}

**Categories**: {', '.join(analysis['categories'])}

**Reasons**:
{chr(10).join([f"- {r}" for r in analysis['reasons']])}

**Review in dashboard**: http://localhost:8501
**Blockchain audit**: {analysis.get('blockchain', {}).get('tx_hash', 'N/A')}
                """
            )
            
        except Exception as e:
            print(f"   ❌ Failed to notify: {e}")
    
    def run(self):
        """Start monitoring subreddit"""
        print(f"\n🚀 HarmLens Reddit Bot Started")
        print(f"📡 Monitoring r/{self.subreddit.display_name}")
        print(f"⚙️  Auto-remove threshold: {self.settings['auto_remove_threshold']}")
        print(f"⚙️  Auto-flag threshold: {self.settings['auto_flag_threshold']}")
        print(f"\n{'='*60}\n")
        
        # Monitor both submissions and comments
        try:
            for item in self.subreddit.stream.submissions(skip_existing=True):
                self.moderate_submission(item)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
        except Exception as e:
            print(f"\n❌ Bot error: {e}")


# ===== BROWSER EXTENSION INTEGRATION =====

def create_browser_extension_manifest():
    """
    Create manifest for Chrome/Firefox extension
    This would allow moderators to analyze content directly from Reddit
    """
    manifest = {
        "manifest_version": 3,
        "name": "HarmLens for Reddit",
        "version": "1.0.0",
        "description": "Real-time content moderation powered by HarmLens AI",
        "permissions": [
            "activeTab",
            "storage"
        ],
        "host_permissions": [
            "https://*.reddit.com/*"
        ],
        "action": {
            "default_popup": "popup.html",
            "default_icon": {
                "16": "icons/icon16.png",
                "48": "icons/icon48.png",
                "128": "icons/icon128.png"
            }
        },
        "content_scripts": [
            {
                "matches": ["https://*.reddit.com/*"],
                "js": ["content.js"],
                "css": ["styles.css"]
            }
        ],
        "background": {
            "service_worker": "background.js"
        }
    }
    
    return json.dumps(manifest, indent=2)


# ===== MAIN =====

def main():
    """Run the Reddit bot"""
    
    # Check configuration
    if REDDIT_CONFIG['client_id'] == 'YOUR_CLIENT_ID':
        print("❌ Please configure Reddit API credentials")
        print("\n📝 Setup Instructions:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Click 'Create App' or 'Create Another App'")
        print("3. Choose 'script' type")
        print("4. Set redirect URI to http://localhost:8080")
        print("5. Copy client_id and client_secret")
        print("6. Update REDDIT_CONFIG in this file or set environment variables")
        return
    
    # Test HarmLens API connection
    try:
        response = requests.get(f"{HARMLENS_API}/", timeout=5)
        if response.status_code != 200:
            print(f"❌ Cannot connect to HarmLens API at {HARMLENS_API}")
            print("   Make sure the API server is running: python api_server.py")
            return
    except Exception as e:
        print(f"❌ Cannot connect to HarmLens API: {e}")
        return
    
    # Start bot
    bot = HarmLensRedditBot(
        reddit_config=REDDIT_CONFIG,
        harmlens_api=HARMLENS_API,
        subreddit=SUBREDDIT_NAME,
        settings=MODERATION_SETTINGS
    )
    
    bot.run()


if __name__ == "__main__":
    main()
