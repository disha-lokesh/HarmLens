"""
Explainability module
Generates human-readable explanations for harm scores
"""

import re


def generate_reasons(signals: dict, scoring_result: dict) -> list:
    """
    Generate top reasons for the harm score
    
    Args:
        signals: dict containing all signal data
        scoring_result: dict from calculate_harm_score
    
    Returns:
        list of reason strings (3-5 bullets)
    """
    reasons = []
    breakdown = scoring_result['breakdown']
    
    # Sort signals by contribution
    sorted_signals = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
    
    # Generate reasons for top signals
    for signal_name, score in sorted_signals[:5]:
        if score < 0.3:  # Skip low signals
            continue
        
        if signal_name == "Emotion":
            emotion_labels = signals.get('emotion_labels', [])
            if emotion_labels and emotion_labels[0] != 'neutral':
                reason = f"High emotional intensity detected ({', '.join(emotion_labels[:2])}), which increases likelihood of impulsive sharing and emotional reactions."
            else:
                reason = "Elevated emotional tone that may influence reader response."
            reasons.append(reason)
        
        elif signal_name == "Call-to-Action":
            cta_triggers = signals.get('cta_triggers', [])
            if cta_triggers:
                examples = ', '.join([f'"{t}"' for t in cta_triggers[:3]])
                reason = f"Contains mobilizing calls-to-action ({examples}) encouraging people to act or share quickly, amplifying potential spread."
            else:
                reason = "Contains language urging immediate action or sharing."
            reasons.append(reason)
        
        elif signal_name == "Toxicity/Targeting":
            if signals.get('targeted', False):
                reason = "Includes targeting or dehumanizing framing toward groups, which can inflame hostility and trigger harassment."
            else:
                reason = "Contains toxic or hostile language that may escalate conflict."
            reasons.append(reason)
        
        elif signal_name == "Context Sensitivity":
            context_topic = signals.get('context_topic', 'none')
            if context_topic != 'none':
                topic_map = {
                    'health': 'public health',
                    'election': 'elections',
                    'communal': 'communal/religious tension',
                    'disaster': 'emergency/disaster'
                }
                topic_name = topic_map.get(context_topic, 'sensitive context')
                reason = f"Addresses {topic_name}, a high-stakes context where misinformation can escalate real-world harm."
            else:
                reason = "Touches on context-sensitive topics requiring extra scrutiny."
            reasons.append(reason)
        
        elif signal_name == "Child Safety":
            if signals.get('child_flag', False):
                reason = "References minors with potentially risky framing; requires immediate review under child-safety policy to ensure protection."
            else:
                reason = "Contains child-related content that warrants review."
            reasons.append(reason)
    
    # Add child safety override reason if applicable
    if scoring_result.get('child_escalation', False):
        if not any('child' in r.lower() for r in reasons):
            reasons.insert(0, "CRITICAL: Child safety concern detected. Automatic escalation triggered for immediate human review.")
    
    # Ensure we have at least 2 reasons
    if len(reasons) < 2:
        reasons.append("Content flagged for precautionary review based on combined risk factors.")
    
    return reasons[:5]  # Return top 5


def generate_evidence_highlights(text: str, signals: dict) -> list:
    """
    Extract and highlight specific text spans that triggered signals
    
    Args:
        text: Original text
        signals: dict containing all signal data with triggers
    
    Returns:
        list of dicts with 'text' and 'reason' for each highlight
    """
    highlights = []
    text_lower = text.lower()
    
    # Collect all triggers
    all_triggers = []
    
    # Emotion triggers
    emotion_triggers = signals.get('trigger_words', [])
    for trigger in emotion_triggers[:3]:
        all_triggers.append({"phrase": trigger, "reason": "Urgency/emotional trigger"})
    
    # CTA triggers
    cta_triggers = signals.get('cta_triggers', [])
    for trigger in cta_triggers[:4]:
        all_triggers.append({"phrase": trigger, "reason": "Call-to-action"})
    
    # Toxicity triggers
    tox_triggers = signals.get('matched_terms', [])
    for trigger in tox_triggers[:3]:
        all_triggers.append({"phrase": trigger, "reason": "Targeting/toxicity indicator"})
    
    # Context triggers
    context_triggers = signals.get('matched_keywords', [])
    for trigger in context_triggers[:4]:
        all_triggers.append({"phrase": trigger, "reason": "Sensitive context keyword"})
    
    # Child safety triggers
    child_triggers = signals.get('child_triggers', [])
    for trigger in child_triggers[:3]:
        all_triggers.append({"phrase": trigger, "reason": "Child safety concern"})
    
    # Find and extract highlights from text
    for item in all_triggers[:10]:  # Limit to top 10
        phrase = item['phrase'].lower()
        reason = item['reason']
        
        # Find the phrase in text
        pattern = r'\b' + re.escape(phrase) + r'\b'
        match = re.search(pattern, text_lower)
        
        if match:
            # Extract with context (up to 60 chars)
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            snippet = text[start:end].strip()
            
            # Add ellipsis if truncated
            if start > 0:
                snippet = "..." + snippet
            if end < len(text):
                snippet = snippet + "..."
            
            highlights.append({
                "text": snippet,
                "reason": reason,
                "trigger": phrase
            })
    
    # Remove duplicates
    seen = set()
    unique_highlights = []
    for h in highlights:
        key = h['text']
        if key not in seen:
            seen.add(key)
            unique_highlights.append(h)
    
    return unique_highlights[:8]  # Return top 8


def generate_causal_chain(signals: dict, scoring_result: dict) -> str:
    """
    Generate a causal explanation of potential harm pathway
    
    Args:
        signals: dict containing all signal data
        scoring_result: dict from calculate_harm_score
    
    Returns:
        string explaining the harm pathway
    """
    risk_label = scoring_result['risk_label']
    
    # Build causal chain based on dominant signals
    breakdown = scoring_result['breakdown']
    top_signal = max(breakdown, key=breakdown.get)
    
    chains = {
        "Emotion": "If believed → triggers fear/anger → emotional sharing → amplified spread → potential panic or conflict",
        "Call-to-Action": "If believed → mobilizes coordinated action → rapid viral spread → potential real-world mobilization",
        "Toxicity/Targeting": "If believed → reinforces hostile attitudes → targete harassment → escalated inter-group conflict",
        "Context Sensitivity": "If believed → influences critical decisions (health/voting/safety) → direct real-world harm",
        "Child Safety": "If acted upon → potential exploitation or harm to minors → critical safety risk"
    }
    
    causal_chain = chains.get(top_signal, "If believed → influences behavior → potential harm")
    
    return f"**Harm Pathway ({risk_label} Risk):** {causal_chain}"
