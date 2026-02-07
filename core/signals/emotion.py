"""
Emotion intensity detection module
Uses emotion classification to detect fear/anger/urgency
"""

import os
import re

# LIGHTWEIGHT MODE: Skip heavy ML models to prevent crashes
# Set HARMLENS_LIGHTWEIGHT=0 to use ML models (needs ~2GB RAM)
LIGHTWEIGHT = os.getenv('HARMLENS_LIGHTWEIGHT', '1') == '1'

HAS_TRANSFORMERS = False
if not LIGHTWEIGHT:
    try:
        from transformers import pipeline
        HAS_TRANSFORMERS = True
    except ImportError:
        HAS_TRANSFORMERS = False


class EmotionDetector:
    """Detect emotional intensity in text"""
    
    def __init__(self):
        self.model = None
        if HAS_TRANSFORMERS:
            try:
                # j-hartmann/emotion-english-distilroberta-base
                self.model = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    top_k=None
                )
            except Exception as e:
                print(f"Could not load emotion model: {e}")
                self.model = None
        
        # Urgency keywords
        self.urgency_keywords = [
            "now", "immediately", "urgent", "hurry", "quick", "fast",
            "asap", "right now", "today", "tonight", "must act",
            "time is running out", "before it's too late", "act now"
        ]
    
    def detect(self, text: str) -> dict:
        """
        Detect emotion intensity
        
        Args:
            text: Input text
            
        Returns:
            dict with emotion_score, emotion_labels, trigger_words
        """
        text_lower = text.lower()
        
        # Detect urgency bonus
        urgency_count = sum(1 for kw in self.urgency_keywords if kw in text_lower)
        urgency_bonus = min(urgency_count * 0.15, 0.5)  # Cap at 0.5
        
        urgency_triggers = [kw for kw in self.urgency_keywords if kw in text_lower]
        
        # If model available, use it
        if self.model:
            try:
                results = self.model(text[:512])[0]  # Truncate to model limit
                
                # Extract scores
                emotion_dict = {r['label']: r['score'] for r in results}
                
                # Focus on fear, anger, sadness (high-intensity emotions)
                fear_score = emotion_dict.get('fear', 0)
                anger_score = emotion_dict.get('anger', 0)
                sadness_score = emotion_dict.get('sadness', 0)
                
                base_score = max(fear_score, anger_score, sadness_score * 0.7)
                emotion_score = min(base_score * (1 + urgency_bonus), 1.0)
                
                # Get top emotions
                sorted_emotions = sorted(results, key=lambda x: x['score'], reverse=True)
                top_emotions = [e['label'] for e in sorted_emotions[:3] if e['score'] > 0.1]
                
                return {
                    "emotion_score": round(emotion_score, 3),
                    "emotion_labels": top_emotions,
                    "trigger_words": urgency_triggers,
                    "raw_emotions": emotion_dict
                }
            except Exception as e:
                print(f"Emotion detection error: {e}")
                # Fall through to rule-based
        
        # Fallback: rule-based emotion detection
        emotion_keywords = {
            'fear': ['afraid', 'scared', 'terrified', 'panic', 'fear', 'worry', 'danger', 'threat', 'risk'],
            'anger': ['angry', 'furious', 'outrage', 'hate', 'rage', 'mad', 'disgusting', 'unacceptable'],
            'sadness': ['sad', 'tragic', 'devastated', 'heartbroken', 'awful', 'terrible']
        }
        
        emotion_scores = {}
        detected_labels = []
        
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            if count > 0:
                emotion_scores[emotion] = min(count * 0.25, 1.0)
                detected_labels.append(emotion)
        
        base_score = max(emotion_scores.values()) if emotion_scores else 0.2
        emotion_score = min(base_score * (1 + urgency_bonus), 1.0)
        
        return {
            "emotion_score": round(emotion_score, 3),
            "emotion_labels": detected_labels[:3] if detected_labels else ['neutral'],
            "trigger_words": urgency_triggers,
            "raw_emotions": emotion_scores
        }
