"""
Advanced Toxicity Detection
Uses multiple pretrained models + ensemble for better accuracy
"""

import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    pipeline
)
import re
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')


class AdvancedToxicityDetector:
    """
    Multi-model ensemble for toxicity detection
    Much more aggressive and accurate than single model
    """
    
    def __init__(self, device: str = None):
        """
        Initialize multiple toxicity models
        
        Args:
            device: 'cuda', 'mps', or 'cpu'
        """
        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device
        
        print(f"🔍 Loading advanced toxicity models on {self.device}...")
        
        # Load multiple models for ensemble
        self._load_models()
        
        # Comprehensive harmful patterns
        self._load_patterns()
        
        print("✅ Advanced toxicity detection ready")
    
    def _load_models(self):
        """Load multiple toxicity detection models"""
        self.models = {}
        
        # Model 1: Toxic-BERT (Unitary)
        try:
            self.models['toxic_bert'] = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                device=0 if self.device == "cuda" else -1,
                top_k=None
            )
            print("  ✓ Toxic-BERT loaded")
        except Exception as e:
            print(f"  ⚠️  Toxic-BERT failed: {e}")
        
        # Model 2: Hate Speech Detection
        try:
            self.models['hate_speech'] = pipeline(
                "text-classification",
                model="facebook/roberta-hate-speech-dynabench-r4-target",
                device=0 if self.device == "cuda" else -1
            )
            print("  ✓ Hate Speech model loaded")
        except Exception as e:
            print(f"  ⚠️  Hate Speech model failed: {e}")
        
        # Model 3: Detoxify (multi-label)
        try:
            from detoxify import Detoxify
            self.models['detoxify'] = Detoxify('original', device=self.device)
            print("  ✓ Detoxify loaded")
        except Exception as e:
            print(f"  ⚠️  Detoxify failed: {e}")
    
    def _load_patterns(self):
        """Load comprehensive harmful patterns"""
        
        # Explicit threats and violence
        self.threat_patterns = [
            r'\b(kill|murder|shoot|stab|attack|assault|beat|hurt|harm)\b.*\b(you|them|him|her)\b',
            r'\b(going to|gonna|will)\b.*\b(kill|hurt|attack|destroy)\b',
            r'\bshould (die|be killed|be shot|be hurt)\b',
            r'\bdeserve(s)? to (die|suffer|be hurt)\b',
            r'\bhope (you|they) (die|get hurt|suffer)\b'
        ]
        
        # Hate speech patterns
        self.hate_patterns = [
            r'\ball \w+ (are|is) (bad|evil|stupid|dangerous|criminals|terrorists)',
            r'\b(these|those) \w+ (are|is) (destroying|ruining|invading)',
            r'\bget rid of (all|the) \w+',
            r'\b(they|them) should (leave|go back|be removed)',
            r'\b(inferior|subhuman|animals|vermin|parasites)\b'
        ]
        
        # Harassment patterns
        self.harassment_patterns = [
            r'\b(you are|you\'re|ur) (stupid|idiot|moron|dumb|pathetic|worthless|trash)',
            r'\bshut (up|the fuck up)\b',
            r'\bkill yourself\b',
            r'\bgo die\b',
            r'\bnobody likes you\b',
            r'\byou should (die|leave|disappear)\b'
        ]
        
        # Sexual harassment
        self.sexual_harassment_patterns = [
            r'\b(rape|molest|grope|assault)\b',
            r'\bsexual (assault|harassment|abuse)\b',
            r'\b(send|show) (nudes|pics|pictures)\b'
        ]
        
        # Slurs and derogatory terms (partial list - add more as needed)
        self.slur_patterns = [
            r'\bn+i+g+[aer]+\b',  # N-word variants
            r'\bf+a+g+[ots]*\b',  # F-slur variants
            r'\br+e+t+a+r+d+\b',  # R-slur
            # Add more patterns as needed
        ]
        
        # Extremist content
        self.extremist_patterns = [
            r'\b(white|black|jewish|muslim) (supremacy|power|genocide)\b',
            r'\b(race|holy) war\b',
            r'\b(ethnic|racial) cleansing\b',
            r'\b(nazi|hitler|holocaust) (was right|did nothing wrong)\b'
        ]
        
        # Self-harm
        self.self_harm_patterns = [
            r'\b(want to|going to|gonna) (kill myself|commit suicide|end it all)\b',
            r'\b(cutting|self harm|self-harm)\b',
            r'\bsuicide (plan|method|note)\b'
        ]
    
    def detect(self, text: str) -> Dict:
        """
        Comprehensive toxicity detection
        
        Args:
            text: Input text
        
        Returns:
            Dictionary with detailed toxicity scores
        """
        text_lower = text.lower()
        
        results = {
            'tox_score': 0.0,
            'risk_level': 'low',
            'categories': [],
            'model_scores': {},
            'pattern_matches': {},
            'severity': 'low',
            'targeted': False,
            'requires_immediate_action': False
        }
        
        # Run all models
        model_scores = []
        
        # Model 1: Toxic-BERT
        if 'toxic_bert' in self.models:
            try:
                result = self.models['toxic_bert'](text[:512])
                if isinstance(result[0], list):
                    toxic_score = next((r['score'] for r in result[0] if r['label'] == 'toxic'), 0)
                else:
                    toxic_score = result[0]['score'] if result[0]['label'] == 'toxic' else 1 - result[0]['score']
                
                results['model_scores']['toxic_bert'] = toxic_score
                model_scores.append(toxic_score)
            except Exception as e:
                print(f"Toxic-BERT error: {e}")
        
        # Model 2: Hate Speech
        if 'hate_speech' in self.models:
            try:
                result = self.models['hate_speech'](text[:512])
                hate_score = result[0]['score'] if result[0]['label'] == 'hate' else 0
                results['model_scores']['hate_speech'] = hate_score
                model_scores.append(hate_score)
            except Exception as e:
                print(f"Hate Speech error: {e}")
        
        # Model 3: Detoxify
        if 'detoxify' in self.models:
            try:
                detox_result = self.models['detoxify'].predict(text)
                detox_score = max(
                    detox_result['toxicity'],
                    detox_result['severe_toxicity'],
                    detox_result['obscene'],
                    detox_result['threat'],
                    detox_result['insult'],
                    detox_result['identity_attack']
                )
                results['model_scores']['detoxify'] = detox_score
                results['model_scores']['detoxify_breakdown'] = detox_result
                model_scores.append(detox_score)
            except Exception as e:
                print(f"Detoxify error: {e}")
        
        # Pattern matching (rule-based boost)
        pattern_score = 0.0
        
        # Check threats
        threat_matches = sum(1 for pattern in self.threat_patterns if re.search(pattern, text_lower, re.IGNORECASE))
        if threat_matches > 0:
            results['categories'].append('Threats/Violence')
            results['pattern_matches']['threats'] = threat_matches
            pattern_score = max(pattern_score, 0.9)
            results['requires_immediate_action'] = True
        
        # Check hate speech
        hate_matches = sum(1 for pattern in self.hate_patterns if re.search(pattern, text_lower, re.IGNORECASE))
        if hate_matches > 0:
            results['categories'].append('Hate Speech')
            results['pattern_matches']['hate'] = hate_matches
            results['targeted'] = True
            pattern_score = max(pattern_score, 0.85)
        
        # Check harassment
        harassment_matches = sum(1 for pattern in self.harassment_patterns if re.search(pattern, text_lower, re.IGNORECASE))
        if harassment_matches > 0:
            results['categories'].append('Harassment')
            results['pattern_matches']['harassment'] = harassment_matches
            results['targeted'] = True
            pattern_score = max(pattern_score, 0.8)
        
        # Check sexual harassment
        sexual_matches = sum(1 for pattern in self.sexual_harassment_patterns if re.search(pattern, text_lower, re.IGNORECASE))
        if sexual_matches > 0:
            results['categories'].append('Sexual Harassment')
            results['pattern_matches']['sexual_harassment'] = sexual_matches
            pattern_score = max(pattern_score, 0.95)
            results['requires_immediate_action'] = True
        
        # Check slurs
        slur_matches = sum(1 for pattern in self.slur_patterns if re.search(pattern, text_lower, re.IGNORECASE))
        if slur_matches > 0:
            results['categories'].append('Slurs/Derogatory Language')
            results['pattern_matches']['slurs'] = slur_matches
            pattern_score = max(pattern_score, 0.9)
        
        # Check extremist content
        extremist_matches = sum(1 for pattern in self.extremist_patterns if re.search(pattern, text_lower, re.IGNORECASE))
        if extremist_matches > 0:
            results['categories'].append('Extremist Content')
            results['pattern_matches']['extremist'] = extremist_matches
            pattern_score = max(pattern_score, 0.95)
            results['requires_immediate_action'] = True
        
        # Check self-harm
        self_harm_matches = sum(1 for pattern in self.self_harm_patterns if re.search(pattern, text_lower, re.IGNORECASE))
        if self_harm_matches > 0:
            results['categories'].append('Self-Harm')
            results['pattern_matches']['self_harm'] = self_harm_matches
            pattern_score = max(pattern_score, 0.85)
            results['requires_immediate_action'] = True
        
        # Ensemble scoring: Take max of (average model score, pattern score)
        if model_scores:
            avg_model_score = sum(model_scores) / len(model_scores)
            max_model_score = max(model_scores)
            
            # Weighted: 60% max model, 40% average
            ensemble_model_score = 0.6 * max_model_score + 0.4 * avg_model_score
        else:
            ensemble_model_score = 0.0
        
        # Final score: Take max of ensemble and pattern score
        final_score = max(ensemble_model_score, pattern_score)
        
        # Boost if multiple categories detected
        if len(results['categories']) > 1:
            final_score = min(final_score * 1.2, 1.0)
        
        results['tox_score'] = round(final_score, 3)
        
        # Determine severity
        if final_score >= 0.8:
            results['severity'] = 'critical'
            results['risk_level'] = 'critical'
        elif final_score >= 0.6:
            results['severity'] = 'high'
            results['risk_level'] = 'high'
        elif final_score >= 0.4:
            results['severity'] = 'medium'
            results['risk_level'] = 'medium'
        else:
            results['severity'] = 'low'
            results['risk_level'] = 'low'
        
        if not results['categories']:
            results['categories'] = ['Safe']
        
        return results


# Singleton instance
_detector_instance = None

def get_toxicity_detector():
    """Get or create singleton detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = AdvancedToxicityDetector()
    return _detector_instance


# Example usage
if __name__ == "__main__":
    detector = AdvancedToxicityDetector()
    
    # Test cases
    test_texts = [
        "I hope you die",
        "All Muslims are terrorists",
        "You're an idiot, kill yourself",
        "This is a normal message",
        "I'm going to shoot up the school"
    ]
    
    for text in test_texts:
        result = detector.detect(text)
        print(f"\nText: {text}")
        print(f"Score: {result['tox_score']}")
        print(f"Severity: {result['severity']}")
        print(f"Categories: {result['categories']}")
