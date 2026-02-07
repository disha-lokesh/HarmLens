# Moderator Escalation Guide

## What Changed?

### Before
- Moderators had "Analyze Content" feature
- Could analyze new content directly

### After
- Moderators have "Escalation Queue" feature
- Focus on managing escalated issues
- Track response times and resolution status

## Why This Change?

Moderators should focus on:
1. **Reviewing flagged content** from the automated system
2. **Escalating critical issues** to specialized teams
3. **Tracking escalation progress** until resolution
4. **Managing their workload** efficiently

Content analysis is now primarily:
- **Automated** by the AI system
- **Admin-only** for testing and configuration

## How to Use Escalation Queue

### 1. Access the Queue
- Login as moderator: `moderator` / `moderator_001`
- Click **🚨 Escalation Queue** in sidebar
- View all escalations with filters

### 2. Create an Escalation
When you find critical content that needs specialized review:

1. Click **➕ Create New Escalation**
2. Fill in:
   - **Content ID**: From the analyzed content
   - **Escalation Type**: 
     - Child Safety (for minors/exploitation)
     - Legal Issue (copyright, defamation, etc.)
     - Urgent Review (time-sensitive)
     - Policy Violation (severe violations)
     - Other (custom)
   - **Priority**:
     - CRITICAL (< 1 hour response)
     - HIGH (2-4 hours response)
     - MEDIUM (4-8 hours response)
     - LOW (24-48 hours response)
   - **Reason**: Detailed explanation
3. Click **🚨 Create Escalation**

### 3. Track Escalations

Each escalation shows:
- **Status Badge**: Current state (Pending/In Progress/Responded/Resolved)
- **Time Elapsed**: How long since creation
- **Response Time Estimate**: Expected response time
- **Priority**: Color-coded priority level
- **Content Preview**: First 150 characters

### 4. Update Status

Use action buttons:
- **▶️ Start**: Move from pending to in-progress (assigns to you)
- **💬 Respond**: Mark as responded (team has replied)
- **✅ Resolve**: Close the escalation (issue resolved)
- **👁️ View Details**: See full information

### 5. Filter and Search

Use filters to find:
- **Status**: Pending, In Progress, Responded, Resolved
- **Priority**: CRITICAL, HIGH, MEDIUM, LOW
- **Type**: Child Safety, Legal Issue, etc.

## Status Workflow

```
┌─────────┐     ▶️ Start      ┌─────────────┐
│ Pending │ ─────────────────> │ In Progress │
└─────────┘                    └─────────────┘
                                      │
                                      │ 💬 Respond
                                      ▼
                               ┌────────────┐
                               │ Responded  │
                               └────────────┘
                                      │
                                      │ ✅ Resolve
                                      ▼
                               ┌────────────┐
                               │  Resolved  │
                               └────────────┘
```

## Priority Guidelines

### CRITICAL (< 1 hour)
- Child exploitation
- Imminent threats of violence
- Active emergencies
- Legal compliance issues

### HIGH (2-4 hours)
- Hate speech
- Severe harassment
- Copyright violations
- Policy violations

### MEDIUM (4-8 hours)
- Misinformation
- Spam campaigns
- Moderate policy violations
- User reports

### LOW (24-48 hours)
- Minor policy violations
- Content clarifications
- General reviews
- Non-urgent issues

## Best Practices

### DO ✅
- Escalate early on critical issues
- Provide detailed reasons
- Use correct priority levels
- Follow up on your escalations
- Document resolution notes

### DON'T ❌
- Over-escalate minor issues
- Use CRITICAL for non-urgent matters
- Escalate without context
- Forget to update status
- Leave escalations unresolved

## Metrics to Watch

Dashboard shows:
- **⏳ Pending**: Awaiting review
- **🔄 In Progress**: Being handled
- **💬 Responded**: Team replied
- **✅ Resolved**: Completed

## Example Scenarios

### Scenario 1: Child Safety Issue
```
Content: "Kids can work to help parents, don't inform parents. 
         Salary $200 per month. Come to secret location"

Action:
1. Create escalation
2. Type: Child Safety
3. Priority: CRITICAL
4. Reason: "Potential child exploitation/trafficking. 
           Contains danger patterns: child+secret+location+money"
5. Expected: Response < 1 hour
```

### Scenario 2: Hate Speech
```
Content: "All [group] are terrorists and should be removed"

Action:
1. Create escalation
2. Type: Policy Violation
3. Priority: HIGH
4. Reason: "Hate speech targeting protected group. 
           Calls for violence/removal"
5. Expected: Response 2-4 hours
```

### Scenario 3: Misinformation
```
Content: "New virus spreading! Government hiding truth! 
         Share NOW before too late!"

Action:
1. Create escalation
2. Type: Urgent Review
3. Priority: MEDIUM
4. Reason: "Health misinformation with panic-inducing language 
           and call-to-action"
5. Expected: Response 4-8 hours
```

## Integration with Content Analysis

### Workflow
1. **AI analyzes** content automatically
2. **System flags** high-risk content
3. **Moderator reviews** flagged content
4. **Moderator escalates** critical issues
5. **Specialized team** handles escalation
6. **Moderator tracks** until resolution

### Where to Find Content IDs
- From automated analysis results
- From moderation queue
- From audit logs
- From platform webhooks

## Admin vs Moderator

### Admin Can:
- Analyze new content
- View all escalations
- Manage users
- Access blockchain
- View audit logs

### Moderator Can:
- Create escalations
- Track escalations
- Update escalation status
- View audit logs
- Access blockchain verification

### Moderator Cannot:
- Analyze new content (use escalation instead)
- Manage users
- Change system settings
- Delete escalations

## Tips for Efficiency

1. **Use Filters**: Quickly find relevant escalations
2. **Check Pending First**: Address awaiting escalations
3. **Update Status**: Keep escalations current
4. **Add Notes**: Document your actions
5. **Monitor Time**: Watch response time estimates
6. **Batch Similar**: Group similar escalations
7. **Prioritize CRITICAL**: Handle urgent issues first

## Troubleshooting

### Can't Create Escalation
- Check content ID exists
- Ensure all fields filled
- Verify you're logged in as moderator

### Escalation Not Showing
- Check status filter
- Verify priority filter
- Try "All" filters

### Can't Update Status
- Ensure you have permissions
- Check escalation isn't already resolved
- Refresh the page

## Support

For issues or questions:
1. Check this guide
2. View ESCALATION_SYSTEM.md for technical details
3. Contact admin for permissions issues
4. Check audit logs for action history

---

**Last Updated**: February 7, 2026
**Version**: 1.0.0
