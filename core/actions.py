"""
Action recommendation module
Routes content to appropriate moderation action
"""


def recommend_action(scoring_result: dict, signals: dict) -> dict:
    """
    Recommend moderation action based on risk score
    
    Args:
        scoring_result: dict from calculate_harm_score
        signals: dict containing all signal data
    
    Returns:
        dict with action, queue, priority, rationale
    """
    risk_score = scoring_result['risk_score']
    risk_label = scoring_result['risk_label']
    child_escalation = scoring_result.get('child_escalation', False)
    
    # Child safety override
    if child_escalation:
        return {
            "action": "ESCALATE IMMEDIATELY",
            "queue": "Child Safety",
            "priority": "CRITICAL",
            "rationale": "Child safety concern requires immediate human review by specialized team.",
            "recommended_steps": [
                "Route to Child Safety specialists",
                "Preserve all evidence",
                "Immediate review required (SLA: <15 min)",
                "Consider account investigation"
            ]
        }
    
    # Action based on risk score
    if risk_score <= 39:  # Low risk
        return {
            "action": "Monitor",
            "queue": "Automated Monitoring",
            "priority": "LOW",
            "rationale": "Low harm risk. Continue automated monitoring for patterns.",
            "recommended_steps": [
                "Log for pattern analysis",
                "No immediate action required",
                "Track engagement metrics",
                "Re-evaluate if viral spread detected"
            ]
        }
    
    elif risk_score <= 69:  # Medium risk
        return {
            "action": "Add Warning / Reduce Reach",
            "queue": "Automated + Sampling Review",
            "priority": "MEDIUM",
            "rationale": "Moderate harm risk. Apply soft interventions to reduce potential spread.",
            "recommended_steps": [
                "Append context/fact-check label if available",
                "Reduce algorithmic amplification",
                "Flag for random sampling review",
                "Monitor user reports"
            ]
        }
    
    else:  # High risk (70-100)
        return {
            "action": "Human Review Required",
            "queue": "Priority Review Queue",
            "priority": "HIGH",
            "rationale": "High harm risk. Requires human judgment before further action.",
            "recommended_steps": [
                "Route to human moderators immediately",
                "Temporarily reduce reach pending review",
                "Review account history",
                "Prepare for potential removal/suspension"
            ]
        }


def get_guardrails_notice() -> str:
    """
    Return standard guardrails disclaimer
    
    Returns:
        string with guardrails notice
    """
    return """
**⚠️ Decision-Support Tool Notice:**
- This is a risk assessment tool, not a truth/falsity determiner
- Human review required for all high-risk and removal decisions
- Tool output must not be sole basis for account actions
- Regular audits for bias and accuracy required
- Appeals process must be available to users
    """.strip()


def format_action_card(action_result: dict) -> dict:
    """
    Format action recommendation as UI card data
    
    Args:
        action_result: dict from recommend_action
    
    Returns:
        dict formatted for UI display
    """
    # Color coding
    priority_colors = {
        "CRITICAL": "#dc2626",  # Red
        "HIGH": "#ea580c",      # Orange
        "MEDIUM": "#f59e0b",    # Amber
        "LOW": "#10b981"        # Green
    }
    
    return {
        "title": action_result['action'],
        "queue": action_result['queue'],
        "priority": action_result['priority'],
        "priority_color": priority_colors.get(action_result['priority'], "#6b7280"),
        "rationale": action_result['rationale'],
        "steps": action_result['recommended_steps']
    }
