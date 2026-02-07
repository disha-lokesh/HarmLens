"""
Harm risk scoring module
Combines signal scores into final risk score with overrides
"""


def calculate_harm_score(signals: dict) -> dict:
    """
    Calculate weighted harm risk score
    
    Args:
        signals: dict containing all signal scores
            - emotion_score
            - cta_score
            - tox_score
            - context_score
            - child_score
            - child_flag
    
    Returns:
        dict with risk_score (0-100), risk_label, breakdown
    """
    # Extract signal scores
    emotion = signals.get('emotion_score', 0)
    cta = signals.get('cta_score', 0)
    tox = signals.get('tox_score', 0)
    context = signals.get('context_score', 0)
    child = signals.get('child_score', 0)
    child_flag = signals.get('child_flag', False)
    
    # Weighted scoring
    # 30% Emotion, 25% CTA, 20% Toxicity, 15% Context, 10% Child Safety
    raw = (
        0.30 * emotion +
        0.25 * cta +
        0.20 * tox +
        0.15 * context +
        0.10 * child
    )
    
    # Convert to 0-100 scale
    risk_score = int(round(raw * 100))
    
    # Override: Child safety escalation
    if child_flag and child > 0.6:
        risk_score = max(risk_score, 80)
    
    # Determine risk label
    if risk_score <= 39:
        risk_label = "Low"
    elif risk_score <= 69:
        risk_label = "Medium"
    else:
        risk_label = "High"
    
    # Score breakdown for visualization
    breakdown = {
        "Emotion": emotion,
        "Call-to-Action": cta,
        "Toxicity/Targeting": tox,
        "Context Sensitivity": context,
        "Child Safety": child
    }
    
    return {
        "risk_score": risk_score,
        "risk_label": risk_label,
        "breakdown": breakdown,
        "child_escalation": child_flag and child > 0.6
    }


def get_harm_categories(signals: dict, threshold: float = 0.4) -> list:
    """
    Get multi-label harm categories based on signals
    
    Args:
        signals: dict containing all signal data
        threshold: minimum score to include category
    
    Returns:
        list of harm category strings
    """
    categories = []
    
    # Check each signal type
    if signals.get('emotion_score', 0) >= threshold:
        emotion_labels = signals.get('emotion_labels', [])
        if 'fear' in emotion_labels or 'anger' in emotion_labels:
            categories.append("Panic/Fear-mongering")
        else:
            categories.append("High Emotional Intensity")
    
    if signals.get('cta_score', 0) >= threshold:
        categories.append("Mobilization/Call-to-Action")
    
    if signals.get('tox_score', 0) >= threshold:
        if signals.get('targeted', False):
            categories.append("Targeted Harassment/Hate")
        else:
            categories.append("Toxicity")
    
    if signals.get('context_score', 0) >= threshold:
        context_topic = signals.get('context_topic', 'none')
        if context_topic != 'none':
            category_map = {
                'health': 'Health Misinformation Risk',
                'election': 'Election Misinformation Risk',
                'communal': 'Communal Tension Risk',
                'disaster': 'Disaster/Emergency Misinformation'
            }
            categories.append(category_map.get(context_topic, 'Sensitive Context'))
    
    if signals.get('child_flag', False):
        categories.append("Child Safety Concern")
    
    # Default if no categories
    if not categories:
        categories.append("General Content")
    
    return categories
