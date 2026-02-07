"""
Improved Harm Risk Scoring
More aggressive scoring that properly flags problematic content
"""


def calculate_improved_harm_score(signals: dict) -> dict:
    """
    Calculate weighted harm risk score with aggressive thresholds
    
    Args:
        signals: dict containing all signal scores
            - emotion_score
            - cta_score
            - tox_score (from advanced detector)
            - context_score
            - child_score
            - child_flag
            - toxicity_severity (optional)
            - requires_immediate_action (optional)
            - child_severity (optional) - NEW
            - child_exploitation_matches (optional) - NEW
    
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
    
    # NEW: Get advanced toxicity info
    toxicity_severity = signals.get('toxicity_severity', 'low')
    requires_immediate_action = signals.get('requires_immediate_action', False)
    toxicity_categories = signals.get('toxicity_categories', [])
    
    # NEW: Get enhanced child safety info
    child_severity = signals.get('child_severity', 'none')
    child_exploitation_matches = signals.get('child_exploitation_matches', 0)
    child_combination_matches = signals.get('child_combination_matches', 0)
    
    # IMPROVED WEIGHTS: Child safety is now most important
    # 35% Child Safety, 30% Toxicity, 20% Emotion, 10% CTA, 5% Context
    base_score = (
        0.35 * child +
        0.30 * tox +
        0.20 * emotion +
        0.10 * cta +
        0.05 * context
    )
    
    # Convert to 0-100 scale
    risk_score = base_score * 100
    
    # ===== CRITICAL OVERRIDES - CHILD SAFETY =====
    
    # Override 1: CRITICAL child safety (exploitation/trafficking)
    if child_severity == 'critical' or child_combination_matches >= 1:
        risk_score = max(risk_score, 95)
        requires_immediate_action = True
    
    # Override 2: HIGH child safety (multiple exploitation patterns)
    elif child_severity == 'high' or child_exploitation_matches >= 2:
        risk_score = max(risk_score, 85)
        requires_immediate_action = True
    
    # Override 3: Child flag with high score
    elif child_flag and child > 0.6:
        risk_score = max(risk_score, 80)
    
    # Override 4: Child flag with any exploitation
    elif child_flag and child_exploitation_matches >= 1:
        risk_score = max(risk_score, 85)
        requires_immediate_action = True
    
    # ===== TOXICITY OVERRIDES =====
    
    # Override 5: Immediate action required (threats, violence, etc.)
    if requires_immediate_action and not child_flag:
        risk_score = max(risk_score, 85)
    
    # Override 6: Critical toxicity severity
    if toxicity_severity == 'critical':
        risk_score = max(risk_score, 90)
    elif toxicity_severity == 'high':
        risk_score = max(risk_score, 75)
    
    # Override 7: Multiple severe categories
    severe_categories = [
        'Threats/Violence', 'Hate Speech', 'Sexual Harassment',
        'Extremist Content', 'Slurs/Derogatory Language'
    ]
    severe_count = sum(1 for cat in toxicity_categories if cat in severe_categories)
    if severe_count >= 2:
        risk_score = max(risk_score, 85)
    elif severe_count >= 1:
        risk_score = max(risk_score, 70)
    
    # ===== COMBINATION MULTIPLIERS =====
    
    # Override 8: High toxicity + high emotion = very dangerous
    if tox > 0.7 and emotion > 0.6:
        risk_score = min(risk_score * 1.2, 100)
    
    # Override 9: High toxicity + CTA = mobilization for harm
    if tox > 0.7 and cta > 0.6:
        risk_score = min(risk_score * 1.25, 100)
    
    # Override 10: Child safety + any other high signal
    if child_flag and (tox > 0.6 or emotion > 0.6):
        risk_score = min(risk_score * 1.3, 100)
    
    # Cap at 100
    risk_score = min(int(round(risk_score)), 100)
    
    # IMPROVED THRESHOLDS: More aggressive
    # Low: 0-49 (was 0-39)
    # Medium: 50-74 (was 40-69)
    # High: 75-100 (was 70-100)
    if risk_score <= 49:
        risk_label = "Low"
    elif risk_score <= 74:
        risk_label = "Medium"
    else:
        risk_label = "High"
    
    # Score breakdown for visualization
    breakdown = {
        "Child Safety": child,
        "Toxicity": tox,
        "Emotion": emotion,
        "Call-to-Action": cta,
        "Context Sensitivity": context
    }
    
    return {
        "risk_score": risk_score,
        "risk_label": risk_label,
        "breakdown": breakdown,
        "child_escalation": child_flag and child > 0.5,
        "immediate_action_required": requires_immediate_action or child_severity in ['critical', 'high'],
        "toxicity_severity": toxicity_severity,
        "child_severity": child_severity
    }


def get_improved_harm_categories(signals: dict, threshold: float = 0.3) -> list:
    """
    Get multi-label harm categories with lower threshold
    
    Args:
        signals: dict containing all signal data
        threshold: minimum score to include category (lowered from 0.4 to 0.3)
    
    Returns:
        list of harm category strings
    """
    categories = []
    
    # Add toxicity categories first (from advanced detector)
    toxicity_categories = signals.get('toxicity_categories', [])
    if toxicity_categories and toxicity_categories != ['Safe']:
        categories.extend(toxicity_categories)
    
    # Check emotion
    if signals.get('emotion_score', 0) >= threshold:
        emotion_labels = signals.get('emotion_labels', [])
        if 'fear' in emotion_labels or 'anger' in emotion_labels:
            categories.append("Panic/Fear-mongering")
        elif 'sadness' in emotion_labels:
            categories.append("High Emotional Intensity")
    
    # Check CTA
    if signals.get('cta_score', 0) >= threshold:
        categories.append("Mobilization/Call-to-Action")
    
    # Check context
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
    
    # Check child safety
    if signals.get('child_flag', False):
        if 'Child Safety' not in categories:
            categories.append("Child Safety Concern")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_categories = []
    for cat in categories:
        if cat not in seen:
            seen.add(cat)
            unique_categories.append(cat)
    
    # Default if no categories
    if not unique_categories:
        unique_categories.append("General Content")
    
    return unique_categories


# Compatibility function for existing code
def calculate_harm_score(signals: dict) -> dict:
    """Wrapper for backward compatibility"""
    return calculate_improved_harm_score(signals)


def get_harm_categories(signals: dict, threshold: float = 0.3) -> list:
    """Wrapper for backward compatibility"""
    return get_improved_harm_categories(signals, threshold)
