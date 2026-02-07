# HarmLens Escalation System

## Overview
The escalation system allows moderators to escalate critical content issues to specialized teams and track their resolution progress.

## Features

### For Moderators
- **Escalation Queue Dashboard**: Dedicated page to view and manage all escalations
- **Create Escalations**: Escalate content with reason, type, and priority
- **Track Status**: Monitor escalation progress through multiple stages
- **Response Time Estimates**: Automatic estimates based on priority level
- **Action Buttons**: Quick actions to update escalation status

### Escalation Types
1. **Child Safety** - Content involving minors or child exploitation
2. **Legal Issue** - Content with potential legal implications
3. **Urgent Review** - Time-sensitive content requiring immediate attention
4. **Policy Violation** - Severe platform policy violations
5. **Other** - Custom escalation types

### Priority Levels
- **CRITICAL**: < 1 hour response time
- **HIGH**: 2-4 hours response time
- **MEDIUM**: 4-8 hours response time
- **LOW**: 24-48 hours response time

### Status Workflow
1. **Pending** ⏳ - Awaiting review by specialized team
2. **In Progress** 🔄 - Being actively handled
3. **Responded** 💬 - Team has responded, awaiting closure
4. **Resolved** ✅ - Issue fully resolved

## Database Schema

### Escalations Table
```sql
CREATE TABLE escalations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id TEXT NOT NULL,
    escalated_by TEXT NOT NULL,
    escalation_reason TEXT NOT NULL,
    escalation_type TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    assigned_to TEXT,
    response_time_estimate TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    FOREIGN KEY (content_id) REFERENCES content_analysis(content_id)
)
```

## API Methods

### Database Methods

#### Create Escalation
```python
db.create_escalation(
    content_id="abc123",
    escalated_by="moderator",
    reason="Potential child exploitation",
    escalation_type="Child Safety",
    priority="CRITICAL"
)
```

#### Get Escalations
```python
# Get all pending escalations
escalations = db.get_escalations(status="pending")

# Get escalations by specific moderator
escalations = db.get_escalations(escalated_by="moderator")
```

#### Update Escalation Status
```python
# Mark as in-progress
db.update_escalation_status(
    escalation_id=1,
    status="in-progress",
    assigned_to="admin"
)

# Resolve escalation
db.update_escalation_status(
    escalation_id=1,
    status="resolved",
    resolution_notes="Issue resolved - content removed"
)
```

## Dashboard Access

### Admin View
- Full access to all features including content analysis
- Can view all escalations across all moderators
- User management capabilities

### Moderator View
- **Escalation Queue** replaces content analysis
- Can create and track escalations
- View only their own escalations or all pending
- Cannot access user management

## Usage Example

### Creating an Escalation
1. Navigate to **Escalation Queue** from sidebar
2. Click **Create New Escalation** expander
3. Fill in:
   - Content ID (from analyzed content)
   - Escalation Type (e.g., "Child Safety")
   - Priority (e.g., "CRITICAL")
   - Reason (detailed explanation)
4. Click **Create Escalation**

### Managing Escalations
1. View escalations filtered by status/priority/type
2. Click action buttons:
   - **▶️ Start**: Move from pending to in-progress
   - **💬 Respond**: Mark as responded
   - **✅ Resolve**: Close the escalation
   - **👁️ View Details**: See full escalation information

### Tracking Progress
- **Time Elapsed**: Shows how long since escalation was created
- **Response Time Estimate**: Expected response time based on priority
- **Status Badge**: Color-coded status indicator
- **Assigned To**: Shows who is handling the escalation

## Metrics

The dashboard shows:
- **Pending**: Escalations awaiting review
- **In Progress**: Currently being handled
- **Responded**: Team has responded
- **Resolved**: Completed escalations

## Integration with Content Analysis

When content is analyzed:
1. High-risk content is automatically flagged
2. Moderators review flagged content
3. Critical issues are escalated via escalation queue
4. Specialized teams handle escalations
5. Resolution is tracked and logged

## Blockchain Audit Trail

All escalation actions are logged:
- Creation timestamp
- Status changes
- Assignment changes
- Resolution notes
- Complete audit trail for compliance

## Best Practices

### For Moderators
1. **Escalate Early**: Don't wait on critical issues
2. **Provide Context**: Include detailed reasons
3. **Set Correct Priority**: Use CRITICAL sparingly
4. **Follow Up**: Check escalation status regularly
5. **Document Resolution**: Add notes when resolving

### For Admins
1. **Monitor Response Times**: Ensure teams meet SLAs
2. **Review Escalation Patterns**: Identify systemic issues
3. **Assign Appropriately**: Route to correct specialized teams
4. **Track Metrics**: Monitor escalation volume and resolution times
5. **Provide Feedback**: Help moderators improve escalation quality

## Response Time SLAs

| Priority | Response Time | Resolution Time |
|----------|--------------|-----------------|
| CRITICAL | < 1 hour | < 4 hours |
| HIGH | 2-4 hours | < 24 hours |
| MEDIUM | 4-8 hours | < 48 hours |
| LOW | 24-48 hours | < 1 week |

## Notifications (Future Enhancement)

Planned features:
- Email notifications on escalation creation
- Slack/Discord integration for critical escalations
- SMS alerts for CRITICAL priority
- Automated reminders for overdue escalations
- Weekly escalation summary reports

## Reporting

Generate reports on:
- Escalation volume by type
- Average resolution time by priority
- Moderator escalation patterns
- Team performance metrics
- Trend analysis over time

---

**Last Updated**: February 7, 2026
**Version**: 1.0.0
