# Quick Start: Escalation System

## 🚀 Start the System

```bash
# Terminal 1: API Server
python api_server.py

# Terminal 2: Dashboard
streamlit run moderator_dashboard.py
```

## 🔐 Login

**Moderator Account:**
- Username: `moderator`
- User ID: `moderator_001`

**Admin Account:**
- Username: `admin`
- User ID: `admin_001`

## 📋 Moderator Workflow

### 1. View Dashboard
- See pending escalations count
- Check priority queue stats
- View recent flagged content

### 2. Access Escalation Queue
- Click **🚨 Escalation Queue** in sidebar
- View all escalations with filters

### 3. Create Escalation
```
➕ Create New Escalation
├─ Content ID: abc123
├─ Type: Child Safety
├─ Priority: CRITICAL
└─ Reason: "Potential exploitation..."
```

### 4. Manage Escalations
- **▶️ Start**: Begin handling
- **💬 Respond**: Mark as responded
- **✅ Resolve**: Close escalation
- **👁️ View**: See full details

## 🎯 Priority Guide

| Priority | Response Time | Use For |
|----------|--------------|---------|
| CRITICAL | < 1 hour | Child exploitation, imminent threats |
| HIGH | 2-4 hours | Hate speech, severe harassment |
| MEDIUM | 4-8 hours | Misinformation, spam campaigns |
| LOW | 24-48 hours | Minor violations, general reviews |

## 🔄 Status Flow

```
Pending → In Progress → Responded → Resolved
```

## 📊 Key Metrics

Dashboard shows:
- ⏳ **Pending**: Awaiting review
- 🔄 **In Progress**: Being handled
- 💬 **Responded**: Team replied
- ✅ **Resolved**: Completed

## 🎨 Color Codes

**Status:**
- 🟡 Pending (Orange)
- 🔵 In Progress (Blue)
- 🟣 Responded (Purple)
- 🟢 Resolved (Green)

**Priority:**
- 🔴 CRITICAL (Red)
- 🟠 HIGH (Orange)
- 🔵 MEDIUM (Blue)
- ⚪ LOW (Gray)

## ⚡ Quick Actions

### Create Escalation
1. Click "Create New Escalation"
2. Fill form
3. Click "Create Escalation"

### Update Status
1. Find escalation
2. Click action button
3. Status updates automatically

### View Details
1. Click "View Details"
2. See full information
3. Click "Close Details"

## 🔍 Filters

- **Status**: All, Pending, In Progress, Responded, Resolved
- **Priority**: All, CRITICAL, HIGH, MEDIUM, LOW
- **Type**: All, Child Safety, Legal Issue, etc.

## 📝 Example Escalation

```
Content ID: post_12345
Type: Child Safety
Priority: CRITICAL
Reason: "Content contains child exploitation indicators:
- Work + child + money combination
- Secret location mention
- Don't tell parents instruction
Requires immediate review and potential law enforcement notification."
```

## ✅ Best Practices

**DO:**
- ✅ Escalate early on critical issues
- ✅ Provide detailed reasons
- ✅ Use correct priority
- ✅ Update status promptly
- ✅ Document resolution

**DON'T:**
- ❌ Over-escalate minor issues
- ❌ Use CRITICAL for non-urgent
- ❌ Escalate without context
- ❌ Forget to follow up
- ❌ Leave unresolved

## 🆘 Troubleshooting

**Can't see Escalation Queue?**
- Check you're logged in as moderator
- Refresh the page
- Check sidebar navigation

**Can't create escalation?**
- Verify content ID exists
- Fill all required fields
- Check you have permissions

**Escalation not showing?**
- Check status filter
- Try "All" filters
- Refresh the page

## 📚 Documentation

- **MODERATOR_ESCALATION_GUIDE.md** - Full user guide
- **ESCALATION_SYSTEM.md** - Technical documentation
- **ESCALATION_UPDATE_SUMMARY.md** - Implementation details

## 🧪 Test the System

```bash
python test_escalation_system.py
```

Expected: ✅ All tests pass

---

**Quick Reference** | **Version 1.0.0** | **February 7, 2026**
