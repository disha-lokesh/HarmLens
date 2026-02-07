"""
Toxicity and targeting detection module
Detects harassment, hate-like targeting cues
"""

import os

# LIGHTWEIGHT MODE: Skip heavy ML models to prevent crashes
LIGHTWEIGHT = os.getenv('HARMLENS_LIGHTWEIGHT', '1') == '1'

HAS_TRANSFORMERS = False
if not LIGHTWEIGHT:
    try:
        from transformers import pipeline
        HAS_TRANSFORMERS = True
    except ImportError:
        HAS_TRANSFORMERS = False


class ToxicityDetector:
    """Detect toxicity and targeting behavior"""
    
    def __init__(self):
        self.model = None
        if HAS_TRANSFORMERS:
            try:
                # unitary/toxic-bert or similar
                self.model = pipeline(
                    "text-classification",
                    model="unitary/toxic-bert"
                )
            except Exception as e:
                print(f"Could not load toxicity model: {e}")
                self.model = None
        
        # Group targeting keywords (high-level, non-explicit)
        self.targeting_keywords = [
            # Religious/communal (factual group names, not slurs)
            "community", "group", "minority", "majority",
            # Dehumanizing language
            "they are", "those people", "these people", "them",
            # Hostile framing
            "enemy", "threat", "dangerous", "destroying", "ruining",
            "invasion", "infiltration", "agenda", "conspiracy"
        ]
        
        # Harassment indicators
        self.harassment_terms = [
            "stupid", "idiot", "fool", "moron", "loser", "pathetic",
            "deserve", "karma", "hope you", "shut up", "get out"
        ]
    
    def detect(self, text: str) -> dict:
        """
        Detect toxicity and targeting
        
        Args:
            text: Input text
            
        Returns:
            dict with tox_score, targeted, matched_terms
        """
        text_lower = text.lower()
        matched_terms = []
        targeted = False
        
        # Use model if available
        if self.model:
            try:
                result = self.model(text[:512])[0]
                
                # Get toxicity score
                if result['label'] == 'toxic':
                    tox_score = result['score']
                else:
                    tox_score = 1 - result['score']
                
                # Check for targeting
                targeting_count = sum(1 for kw in self.targeting_keywords if kw in text_lower)
                if targeting_count >= 2:
                    targeted = True
                    matched_terms.extend([kw for kw in self.targeting_keywords if kw in text_lower][:5])
                
                # Boost score if targeted
                if targeted:
                    tox_score = min(tox_score * 1.3, 1.0)
                
                return {
                    "tox_score": round(tox_score, 3),
                    "targeted": targeted,
                    "matched_terms": matched_terms
                }
            except Exception as e:
                print(f"Toxicity detection error: {e}")
                # Fall through to rule-based
        
        # Fallback: rule-based toxicity detection
        harassment_matches = [term for term in self.harassment_terms if term in text_lower]
        targeting_matches = [kw for kw in self.targeting_keywords if kw in text_lower]
        
        harassment_score = min(len(harassment_matches) * 0.25, 0.8)
        targeting_score = min(len(targeting_matches) * 0.15, 0.5)
        
        if len(targeting_matches) >= 2:
            targeted = True
            matched_terms.extend(targeting_matches[:5])
        
        if harassment_matches:
            matched_terms.extend(harassment_matches[:3])
        
        tox_score = min(harassment_score + targeting_score, 1.0)
        
        return {
            "tox_score": round(tox_score, 3),
            "targeted": targeted,
            "matched_terms": list(set(matched_terms))
        }
