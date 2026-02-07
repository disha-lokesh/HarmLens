"""
Child safety detection module
Detects content involving minors that needs escalated review
"""

import re


class ChildSafetyDetector:
    """Detect child safety concerns"""
    
    def __init__(self):
        # Minor-related terms (factual, non-explicit)
        self.minor_terms = [
            "child", "children", "kid", "kids", "minor", "minors",
            "boy", "girl", "teen", "teenager", "adolescent",
            "student", "school", "schoolboy", "schoolgirl",
            "underage", "young", "youth", "juvenile"
        ]
        
        # Risky framing indicators (high-level, non-explicit)
        self.risky_framing = [
            "dm", "direct message", "private message", "pm me",
            "meet", "meeting", "contact", "reach out",
            "secret", "don't tell", "keep quiet", "between us",
            "alone", "private", "personal", "one on one",
            "special", "mature", "grown up",
            "send", "share photos", "pictures", "images"
        ]
        
        # Vulnerable context keywords
        self.vulnerable_context = [
            "abuse", "exploitation", "grooming", "predator",
            "harm", "danger", "risk", "threat", "unsafe",
            "missing", "runaway", "lost"
        ]
    
    def detect(self, text: str) -> dict:
        """
        Detect child safety concerns
        
        Args:
            text: Input text
            
        Returns:
            dict with child_score, child_flag, triggers
        """
        text_lower = text.lower()
        triggers = []
        score_components = []
        
        # Check for minor mentions
        minor_matches = [term for term in self.minor_terms if re.search(r'\b' + term + r'\b', text_lower)]
        has_minor_mention = len(minor_matches) > 0
        
        if has_minor_mention:
            triggers.extend(minor_matches[:3])
            score_components.append(0.3)  # Base score for minor mention
        
        # Check for risky framing
        risky_matches = [term for term in self.risky_framing if term in text_lower]
        if risky_matches:
            triggers.extend(risky_matches[:3])
            score_components.append(min(len(risky_matches) * 0.25, 0.6))
        
        # Check for vulnerable context
        vulnerable_matches = [term for term in self.vulnerable_context if term in text_lower]
        if vulnerable_matches:
            triggers.extend(vulnerable_matches[:2])
            score_components.append(min(len(vulnerable_matches) * 0.3, 0.7))
        
        # Calculate score
        if score_components:
            child_score = min(sum(score_components), 1.0)
        else:
            child_score = 0.0
        
        # Flag if minor mention + risky framing
        child_flag = has_minor_mention and (risky_matches or vulnerable_matches)
        
        # Or flag if score is high
        if child_score > 0.6:
            child_flag = True
        
        return {
            "child_score": round(child_score, 3),
            "child_flag": child_flag,
            "triggers": list(set(triggers))[:6]
        }
