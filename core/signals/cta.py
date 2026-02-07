"""
Call-to-action (CTA) detection module
Detects mobilization and urging behavior
"""

import re


class CTADetector:
    """Detect calls to action and mobilization language"""
    
    def __init__(self):
        # Action verbs
        self.action_verbs = [
            "share", "forward", "retweet", "spread", "tell", "inform",
            "boycott", "ban", "stop", "report", "flag", "expose",
            "join", "attend", "gather", "meet", "unite", "organize",
            "fight", "resist", "protest", "demand", "act", "take action",
            "sign", "petition", "call", "contact", "pressure",
            "wake up", "open your eyes", "don't be fooled", "see the truth"
        ]
        
        # Urgency/imperative markers
        self.urgency_terms = [
            "now", "immediately", "today", "tonight", "urgent", "must",
            "need to", "have to", "should", "everyone must",
            "before it's too late", "time is running out", "act fast",
            "don't wait", "hurry"
        ]
        
        # Directive phrases
        self.directive_patterns = [
            r'\bmust\s+\w+',
            r'\bneed\s+to\s+\w+',
            r'\bdon\'?t\s+\w+',
            r'\bstop\s+\w+',
            r'\beveryone\s+should\s+\w+',
            r'\bwe\s+need\s+to\s+\w+',
            r'\blet\'?s\s+\w+',
        ]
    
    def detect(self, text: str) -> dict:
        """
        Detect call-to-action strength
        
        Args:
            text: Input text
            
        Returns:
            dict with cta_score, cta_triggers
        """
        text_lower = text.lower()
        triggers = []
        score_components = []
        
        # Check action verbs
        action_matches = [verb for verb in self.action_verbs if verb in text_lower]
        if action_matches:
            action_score = min(len(action_matches) * 0.2, 0.6)
            score_components.append(action_score)
            triggers.extend(action_matches[:5])  # Limit triggers
        
        # Check urgency terms
        urgency_matches = [term for term in self.urgency_terms if term in text_lower]
        if urgency_matches:
            urgency_score = min(len(urgency_matches) * 0.15, 0.4)
            score_components.append(urgency_score)
            triggers.extend(urgency_matches[:3])
        
        # Check directive patterns (imperative mood)
        directive_matches = []
        for pattern in self.directive_patterns:
            matches = re.findall(pattern, text_lower)
            directive_matches.extend(matches)
        
        if directive_matches:
            directive_score = min(len(directive_matches) * 0.2, 0.5)
            score_components.append(directive_score)
            triggers.extend(directive_matches[:3])
        
        # Check for exclamation marks (intensity indicator)
        exclamation_count = text.count('!')
        if exclamation_count >= 2:
            score_components.append(min(exclamation_count * 0.05, 0.2))
        
        # Calculate final score
        if score_components:
            cta_score = min(sum(score_components), 1.0)
        else:
            cta_score = 0.0
        
        return {
            "cta_score": round(cta_score, 3),
            "cta_triggers": list(set(triggers))[:8]  # Unique, limited
        }
