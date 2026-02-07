# 🤖 HarmLens Reddit Extension Guide

## Overview

HarmLens can be integrated with Reddit in **3 ways**:

1. **Reddit Bot** - Automated moderation bot (Python)
2. **Browser Extension** - Manual analysis tool for moderators (Chrome/Firefox)
3. **API Integration** - Custom integration with Reddit's API

---

## 1️⃣ Reddit Bot (Automated Moderation)

### What It Does

- ✅ Monitors subreddit in real-time
- ✅ Analyzes every new post and comment
- ✅ Auto-removes high-risk content
- ✅ Flags medium-risk content for review
- ✅ Notifies moderators via modmail
- ✅ Logs all actions to blockchain
- ✅ Escalates child safety issues

### Setup Instructions

#### Step 1: Install Dependencies

```bash
pip install praw requests
```

#### Step 2: Create Reddit App

1. Go to https://www.reddit.com/prefs/apps
2. Click **"Create App"** or **"Create Another App"**
3. Fill in details:
   - **Name**: HarmLens Moderation Bot
   - **Type**: Select **"script"**
   - **Description**: AI-powered content moderation
   - **Redirect URI**: `http://localhost:8080`
4. Click **"Create app"**
5. Copy your **client_id** (under app name) and **client_secret**

#### Step 3: Configure Bot

Edit `examples/reddit_extension.py`:

```python
REDDIT_CONFIG = {
    'client_id': 'YOUR_CLIENT_ID_HERE',
    'client_secret': 'YOUR_CLIENT_SECRET_HERE',
    'user_agent': 'HarmLens Moderation Bot v1.0',
    'username': 'YOUR_BOT_USERNAME',
    'password': 'YOUR_BOT_PASSWORD'
}

# Subreddit to monitor
SUBREDDIT_NAME = 'your_subreddit_name'  # Without r/

# Moderation Settings
MODERATION_SETTINGS = {
    'auto_remove_threshold': 80,  # Auto-remove if risk >= 80
    'auto_flag_threshold': 60,    # Flag for review if risk >= 60
    'notify_moderators': True,
    'add_removal_reason': True,
    'log_to_blockchain': True
}
```

#### Step 4: Run Bot

```bash
# Make sure HarmLens API is running
python api_server.py

# In another terminal, run the bot
python examples/reddit_extension.py
```

### Bot Output Example

```
✅ Connected to Reddit as: YourBotUsername
✅ Monitoring r/your_subreddit
✅ HarmLens API: http://localhost:8000

🚀 HarmLens Reddit Bot Started
📡 Monitoring r/your_subreddit
⚙️  Auto-remove threshold: 80
⚙️  Auto-flag threshold: 60

============================================================

📊 Post Analysis: u/username123
   Risk Score: 85/100 (High)
   Action: REMOVE
   Categories: Toxicity, Harassment
   ✅ Removed post: abc123
   📧 Moderators notified

💬 Comment Analysis: u/username456
   Risk Score: 65/100 (Medium)
   🚩 Flagged for review: def456
```

---

## 2️⃣ Browser Extension (Manual Tool)

### What It Does

- ✅ Adds "Analyze with HarmLens" button to Reddit posts/comments
- ✅ Shows risk score overlay on content
- ✅ Quick actions: Remove, Flag, Approve
- ✅ Works directly in Reddit's interface
- ✅ Perfect for manual moderation

### Setup Instructions

#### Step 1: Create Extension Files

Create a folder `harmlens-reddit-extension/` with these files:

**manifest.json**:
```json
{
  "manifest_version": 3,
  "name": "HarmLens for Reddit",
  "version": "1.0.0",
  "description": "AI-powered content moderation for Reddit",
  "permissions": ["activeTab", "storage"],
  "host_permissions": ["https://*.reddit.com/*"],
  "action": {
    "default_popup": "popup.html",
    "default_icon": "icon.png"
  },
  "content_scripts": [{
    "matches": ["https://*.reddit.com/*"],
    "js": ["content.js"]
  }]
}
```

**content.js**:
```javascript
// Add "Analyze" button to every post/comment
function addAnalyzeButtons() {
  const posts = document.querySelectorAll('[data-testid="post-container"]');
  
  posts.forEach(post => {
    if (post.querySelector('.harmlens-button')) return;
    
    const button = document.createElement('button');
    button.className = 'harmlens-button';
    button.textContent = '🛡️ Analyze';
    button.onclick = () => analyzeContent(post);
    
    const toolbar = post.querySelector('[data-click-id="timestamp"]')?.parentElement;
    if (toolbar) toolbar.appendChild(button);
  });
}

async function analyzeContent(post) {
  const text = post.querySelector('[data-click-id="text"]')?.textContent || '';
  
  // Call HarmLens API
  const response = await fetch('http://localhost:8000/api/v1/analyze', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      text: text,
      platform: 'reddit'
    })
  });
  
  const result = await response.json();
  
  // Show risk score overlay
  showRiskOverlay(post, result);
}

function showRiskOverlay(post, result) {
  const overlay = document.createElement('div');
  overlay.className = 'harmlens-overlay';
  overlay.innerHTML = `
    <div class="risk-badge risk-${result.risk_label.toLowerCase()}">
      Risk: ${result.risk_score}/100 (${result.risk_label})
    </div>
    <div class="categories">${result.categories.join(', ')}</div>
    <div class="actions">
      <button onclick="removePost()">Remove</button>
      <button onclick="flagPost()">Flag</button>
      <button onclick="approvePost()">Approve</button>
    </div>
  `;
  post.appendChild(overlay);
}

// Run on page load and when new content loads
addAnalyzeButtons();
setInterval(addAnalyzeButtons, 2000);
```

**popup.html**:
```html
<!DOCTYPE html>
<html>
<head>
  <title>HarmLens for Reddit</title>
  <style>
    body { width: 300px; padding: 15px; font-family: Arial; }
    .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
    .connected { background: #e8f5e9; color: #2e7d32; }
    .disconnected { background: #ffebee; color: #c62828; }
  </style>
</head>
<body>
  <h2>🛡️ HarmLens</h2>
  <div id="status" class="status">Checking connection...</div>
  <button id="settings">Settings</button>
  <script src="popup.js"></script>
</body>
</html>
```

#### Step 2: Install Extension

**Chrome**:
1. Go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `harmlens-reddit-extension/` folder

**Firefox**:
1. Go to `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select `manifest.json` from folder

#### Step 3: Use Extension

1. Go to any Reddit page
2. You'll see "🛡️ Analyze" button on posts
3. Click to analyze content
4. View risk score and take action

---

## 3️⃣ API Integration (Custom)

### Direct API Calls

```python
import praw
import requests

reddit = praw.Reddit(...)

# Monitor new submissions
for submission in reddit.subreddit('all').stream.submissions():
    # Analyze with HarmLens
    response = requests.post('http://localhost:8000/api/v1/analyze', json={
        'text': submission.selftext,
        'content_id': submission.id,
        'user_id': str(submission.author),
        'platform': 'reddit'
    })
    
    result = response.json()
    
    # Take action based on risk
    if result['risk_score'] >= 80:
        submission.mod.remove()
        print(f"Removed: {submission.id} (Risk: {result['risk_score']})")
    
    elif result['risk_score'] >= 60:
        submission.report(f"HarmLens: {result['risk_label']} Risk")
        print(f"Flagged: {submission.id}")
```

---

## Configuration Options

### Moderation Thresholds

```python
MODERATION_SETTINGS = {
    'auto_remove_threshold': 80,   # 80-100: Auto-remove
    'auto_flag_threshold': 60,     # 60-79: Flag for review
    'notify_moderators': True,     # Send modmail notifications
    'add_removal_reason': True,    # Explain removal to users
    'log_to_blockchain': True      # Blockchain audit trail
}
```

### Risk Score Guidelines

| Score | Label | Action | Example |
|-------|-------|--------|---------|
| 0-39 | Low | Allow | Normal discussion |
| 40-59 | Medium | Monitor | Heated debate |
| 60-79 | High | Flag for review | Insults, mild toxicity |
| 80-100 | Critical | Auto-remove | Harassment, threats |

---

## Features

### ✅ Automated Actions

- **Auto-remove**: High-risk content removed instantly
- **Auto-flag**: Medium-risk content sent to mod queue
- **User notification**: Removal reasons sent to users
- **Mod alerts**: Modmail for critical issues

### ✅ Blockchain Audit Trail

Every action is logged to blockchain:
- What was removed/flagged
- Why (risk score, categories)
- When (timestamp)
- Who (moderator/bot)
- Immutable proof for appeals

### ✅ Child Safety Escalation

- Automatic detection of child safety concerns
- Immediate escalation to moderators
- Logged separately for compliance
- Can integrate with Reddit's safety team

---

## Use Cases

### 1. Large Subreddit Moderation

**Problem**: 1000+ posts/day, can't review everything

**Solution**: Bot auto-removes obvious violations, flags borderline cases

```python
MODERATION_SETTINGS = {
    'auto_remove_threshold': 85,  # Only remove very high risk
    'auto_flag_threshold': 65,    # Flag more for human review
}
```

### 2. Small Community Protection

**Problem**: Limited mod team, need to catch everything

**Solution**: Lower thresholds, more aggressive moderation

```python
MODERATION_SETTINGS = {
    'auto_remove_threshold': 75,  # More aggressive
    'auto_flag_threshold': 50,    # Flag more content
    'notify_moderators': True     # Alert on everything
}
```

### 3. Manual Moderation Enhancement

**Problem**: Want AI assistance but keep human control

**Solution**: Use browser extension for manual analysis

- Moderator reviews content normally
- Clicks "Analyze" for suspicious posts
- Gets AI recommendation
- Makes final decision

---

## Deployment Options

### Option 1: Local Development

```bash
# Run on your computer
python api_server.py
python examples/reddit_extension.py
```

**Pros**: Free, full control
**Cons**: Must keep computer running

### Option 2: Cloud Hosting

```bash
# Deploy to Heroku/Railway/Render
git push heroku main

# Update bot config
HARMLENS_API = 'https://your-app.herokuapp.com'
```

**Pros**: Always running, scalable
**Cons**: Hosting costs (~$7/month)

### Option 3: Reddit Hosting

Run bot on Reddit's servers (if you have access):
- No external hosting needed
- Lowest latency
- Best for large subreddits

---

## Monitoring & Analytics

### View Bot Activity

Dashboard: http://localhost:8501

- Total content analyzed
- Removal rate
- Risk score distribution
- Blockchain audit logs
- Moderator actions

### Export Reports

```python
# Get moderation statistics
response = requests.get('http://localhost:8000/api/v1/stats')
stats = response.json()

print(f"Total analyzed: {stats['total_analyzed']}")
print(f"High risk: {stats['by_risk_level']['High']}")
print(f"Removed: {stats['actions']['removed']}")
```

---

## Troubleshooting

### Bot Not Starting

```
❌ Cannot connect to HarmLens API
```

**Fix**: Make sure API server is running:
```bash
python api_server.py
```

### Reddit Authentication Failed

```
❌ Invalid credentials
```

**Fix**: Check Reddit app credentials:
1. Verify client_id and client_secret
2. Make sure bot account has mod permissions
3. Check username/password are correct

### Content Not Being Analyzed

```
❌ API Error: 500
```

**Fix**: Check API logs for errors:
```bash
# View API server output
tail -f api_server.log
```

---

## Best Practices

### 1. Start Conservative

Begin with high thresholds, lower gradually:
```python
'auto_remove_threshold': 90,  # Very conservative
'auto_flag_threshold': 75,
```

### 2. Monitor First Week

- Review all bot actions
- Adjust thresholds based on results
- Check for false positives

### 3. Communicate with Community

Post announcement:
```
We've added an AI moderation assistant to help keep our community safe.
It will flag potentially harmful content for review. Human moderators
make all final decisions. Questions? Ask below!
```

### 4. Regular Audits

- Weekly review of removed content
- Check blockchain logs for transparency
- Adjust settings as community evolves

---

## Legal & Compliance

### Data Privacy

- Content analyzed in real-time
- Not stored permanently (unless flagged)
- Blockchain logs are anonymized
- GDPR/CCPA compliant

### Transparency

- All actions logged to blockchain
- Users can appeal removals
- Moderators can verify decisions
- Audit trail for Reddit admins

### Reddit TOS Compliance

- Bot follows Reddit's API rules
- Rate limits respected
- No vote manipulation
- Proper mod permissions required

---

## Support

- **Documentation**: See `COMPLETE_SYSTEM_GUIDE.md`
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501
- **Issues**: Check logs in `logs/` folder

---

## Next Steps

1. ✅ Set up Reddit app credentials
2. ✅ Configure bot settings
3. ✅ Test on small subreddit first
4. ✅ Monitor for 1 week
5. ✅ Adjust thresholds
6. ✅ Deploy to production
7. ✅ Announce to community

---

**Ready to moderate smarter, not harder! 🛡️**
