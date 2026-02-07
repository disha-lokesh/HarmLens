"""
Context sensitivity detection module
Detects high-stakes topics (health, elections, communal tension, disasters)
"""

import json
import os

# LIGHTWEIGHT MODE: Skip heavy ML models to prevent crashes
LIGHTWEIGHT = os.getenv('HARMLENS_LIGHTWEIGHT', '1') == '1'

HAS_EMBEDDINGS = False
if not LIGHTWEIGHT:
    try:
        from sentence_transformers import SentenceTransformer, util
        HAS_EMBEDDINGS = True
    except ImportError:
        HAS_EMBEDDINGS = False


class ContextDetector:
    """Detect sensitive context topics"""
    
    def __init__(self, assets_path=None):
        self.model = None
        self.anchor_embeddings = None
        self.topic_anchors = {
            "health": "public health advice medical treatment vaccine medicine",
            "election": "election voting candidates political campaign ballot results",
            "communal": "communal tension religious conflict ethnic violence riots",
            "disaster": "disaster emergency natural calamity earthquake flood fire"
        }
        
        # Load model if available
        if HAS_EMBEDDINGS:
            try:
                self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                # Pre-compute anchor embeddings
                self.anchor_embeddings = {
                    topic: self.model.encode(text, convert_to_tensor=True)
                    for topic, text in self.topic_anchors.items()
                }
            except Exception as e:
                print(f"Could not load embedding model: {e}")
                self.model = None
        
        # Load sensitive topics from assets
        self.sensitive_keywords = {
            "health": [
                "vaccine", "cure", "treatment", "medicine", "covid", "virus",
                "disease", "pandemic", "health", "doctor", "hospital", "medical",
                "drug", "remedy", "symptom", "infection", "immunity"
            ],
            "election": [
                "vote", "voting", "election", "ballot", "candidate", "polling",
                "evm", "rigged", "fraud", "manipulation", "counting", "results",
                "campaign", "political", "party", "minister", "government"
            ],
            "communal": [
                "riot", "clash", "violence", "attack", "mob", "lynching",
                "tension", "conflict", "religious", "community", "minority",
                "majority", "protest", "demonstration"
            ],
            "disaster": [
                "earthquake", "flood", "fire", "cyclone", "storm", "disaster",
                "emergency", "evacuation", "rescue", "danger", "warning",
                "alert", "calamity", "tragedy", "destruction"
            ]
        }
        
        # Try to load from assets if available
        if assets_path:
            try:
                with open(os.path.join(assets_path, 'sensitive_topics.json'), 'r') as f:
                    loaded = json.load(f)
                    self.sensitive_keywords.update(loaded)
            except:
                pass
    
    def detect(self, text: str) -> dict:
        """
        Detect context sensitivity
        
        Args:
            text: Input text
            
        Returns:
            dict with context_score, context_topic, matched_keywords
        """
        text_lower = text.lower()
        matched_keywords = []
        detected_topics = []
        keyword_scores = {}
        
        # Keyword matching
        for topic, keywords in self.sensitive_keywords.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                keyword_scores[topic] = min(len(matches) * 0.2, 0.8)
                matched_keywords.extend(matches[:3])
                detected_topics.append(topic)
        
        # Embedding similarity (if model available)
        embedding_scores = {}
        if self.model and self.anchor_embeddings:
            try:
                text_embedding = self.model.encode(text[:512], convert_to_tensor=True)
                
                for topic, anchor_emb in self.anchor_embeddings.items():
                    similarity = util.cos_sim(text_embedding, anchor_emb).item()
                    # Convert similarity (-1 to 1) to score (0 to 1)
                    embedding_scores[topic] = max((similarity + 1) / 2 - 0.5, 0) * 2
                    
            except Exception as e:
                print(f"Embedding similarity error: {e}")
        
        # Combine keyword and embedding scores
        combined_scores = {}
        all_topics = set(list(keyword_scores.keys()) + list(embedding_scores.keys()))
        
        for topic in all_topics:
            kw_score = keyword_scores.get(topic, 0)
            emb_score = embedding_scores.get(topic, 0)
            # Weighted average (keywords more reliable)
            combined_scores[topic] = kw_score * 0.7 + emb_score * 0.3
        
        # Get top topic and score
        if combined_scores:
            top_topic = max(combined_scores, key=combined_scores.get)
            context_score = combined_scores[top_topic]
        else:
            top_topic = "none"
            context_score = 0.0
        
        return {
            "context_score": round(context_score, 3),
            "context_topic": top_topic,
            "matched_keywords": list(set(matched_keywords))[:8],
            "all_topics": detected_topics
        }
