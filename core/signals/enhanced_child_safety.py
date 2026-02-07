"""
Enhanced Child Safety Detection
CRITICAL: Aggressive detection for child exploitation, trafficking, grooming
"""

import re
from typing import Dict, List


class EnhancedChildSafetyDetector:
    """
    Enhanced child safety detector with aggressive pattern matching
    ZERO TOLERANCE for child exploitation content
    """
    
    def __init__(self):
        # Child/minor terms
        self.child_terms = [
            r'\bchild\b', r'\bchildren\b', r'\bkid\b', r'\bkids\b',
            r'\bminor\b', r'\bminors\b', r'\bboy\b', r'\bgirl\b',
            r'\bteen\b', r'\bteenager\b', r'\bteens\b',
            r'\bstudent\b', r'\bstudents\b', r'\bschool\b',
            r'\bunderage\b', r'\byoung\b', r'\byouth\b',
            r'\bjuvenile\b', r'\badolescent\b'
        ]
        
        # CRITICAL: Exploitation indicators
        self.exploitation_patterns = [
            # Work/labor exploitation
            r'\b(work|job|employment|labor|labour)\b.*\b(child|kid|minor|young)\b',
            r'\b(child|kid|minor|young)\b.*\b(work|job|employment|labor|labour)\b',
            r'\bchild\s+labor\b',
            r'\bchild\s+work\b',
            
            # Financial exploitation
            r'\bsalary\b.*\b(child|kid|minor)\b',
            r'\b(child|kid|minor)\b.*\bsalary\b',
            r'\b(pay|paid|payment|money|cash)\b.*\b(child|kid|minor)\b',
            r'\b\$\d+.*\b(child|kid|minor)\b',
            
            # Secrecy/hiding
            r'\bsecret\b.*\b(location|place|meet|contact)\b',
            r'\bdon\'t\s+(tell|inform|let\s+know)\b.*\b(parent|parents|family|guardian)\b',
            r'\bkeep\s+(secret|quiet|hidden)\b',
            r'\bhide\s+from\b.*\b(parent|parents|family)\b',
            
            # Contact/meeting
            r'\bmeet\b.*\b(child|kid|minor|young)\b',
            r'\b(child|kid|minor|young)\b.*\bmeet\b',
            r'\bcome\s+to\b.*\b(location|place|address)\b',
            r'\bprivate\s+(meeting|contact|message)\b',
            
            # Grooming language
            r'\bspecial\s+(friend|relationship)\b',
            r'\bmature\s+for\s+your\s+age\b',
            r'\bdon\'t\s+tell\s+anyone\b',
            r'\bbetween\s+us\b',
            r'\bour\s+secret\b',
            
            # Trafficking indicators
            r'\btravel\b.*\b(child|kid|minor)\b',
            r'\btake\s+you\b.*\b(somewhere|place|location)\b',
            r'\bpick\s+you\s+up\b',
            r'\balone\b.*\b(meet|contact)\b'
        ]
        
        # CRITICAL: Combined danger patterns
        self.danger_combinations = [
            # Child + work + money
            (r'\b(child|kid|minor)\b', r'\b(work|job|labor)\b', r'\b(salary|pay|money|\$)\b'),
            
            # Child + secret + location
            (r'\b(child|kid|minor)\b', r'\bsecret\b', r'\b(location|place|meet)\b'),
            
            # Child + don't tell parents + money
            (r'\b(child|kid|minor)\b', r'\bdon\'t\s+(tell|inform)\b.*\bparent', r'\b(money|pay|salary)\b'),
            
            # Work + secret + location
            (r'\b(work|job)\b', r'\bsecret\b', r'\b(location|place|address)\b'),
        ]
        
        # Vulnerable context
        self.vulnerable_keywords = [
            'abuse', 'exploitation', 'grooming', 'predator', 'trafficking',
            'harm', 'danger', 'unsafe', 'missing', 'runaway',
            'recruit', 'recruiting', 'opportunity', 'easy money'
        ]
    
    def detect(self, text: str) -> Dict:
        """
        Detect child safety concerns with AGGRESSIVE scoring
        
        Args:
            text: Input text
        
        Returns:
            dict with child_score, child_flag, severity, triggers
        """
        text_lower = text.lower()
        triggers = []
        score = 0.0
        severity = 'none'
        matched_patterns = []
        
        # Check for child/minor mentions
        child_mentions = []
        for pattern in self.child_terms:
            if re.search(pattern, text_lower):
                child_mentions.append(pattern.replace(r'\b', '').replace('\\', ''))
        
        has_child_mention = len(child_mentions) > 0
        
        if has_child_mention:
            score += 0.2
            triggers.extend(child_mentions[:2])
        
        # CRITICAL: Check exploitation patterns
        exploitation_matches = 0
        for pattern in self.exploitation_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                exploitation_matches += 1
                matched_patterns.append(pattern[:50])
                score += 0.3  # Each match adds 30%
        
        if exploitation_matches > 0:
            triggers.append(f"{exploitation_matches} exploitation patterns")
        
        # CRITICAL: Check danger combinations
        combination_matches = 0
        for combo in self.danger_combinations:
            if all(re.search(pattern, text_lower, re.IGNORECASE) for pattern in combo):
                combination_matches += 1
                score += 0.4  # Each combination adds 40%
        
        if combination_matches > 0:
            triggers.append(f"{combination_matches} danger combinations")
        
        # Check vulnerable keywords
        vulnerable_matches = [kw for kw in self.vulnerable_keywords if kw in text_lower]
        if vulnerable_matches:
            score += min(len(vulnerable_matches) * 0.15, 0.5)
            triggers.extend(vulnerable_matches[:2])
        
        # Cap score at 1.0
        score = min(score, 1.0)
        
        # Determine severity
        if score >= 0.8 or combination_matches >= 2:
            severity = 'critical'
        elif score >= 0.6 or exploitation_matches >= 2:
            severity = 'high'
        elif score >= 0.4:
            severity = 'medium'
        elif score > 0:
            severity = 'low'
        
        # CRITICAL FLAG CONDITIONS
        child_flag = False
        
        # Flag if ANY of these conditions:
        if combination_matches >= 1:  # Any danger combination
            child_flag = True
        elif exploitation_matches >= 2:  # Multiple exploitation patterns
            child_flag = True
        elif score >= 0.6:  # High score
            child_flag = True
        elif has_child_mention and exploitation_matches >= 1:  # Child + any exploitation
            child_flag = True
        
        return {
            'child_score': round(score, 3),
            'child_flag': child_flag,
            'severity': severity,
            'triggers': list(set(triggers))[:8],
            'exploitation_matches': exploitation_matches,
            'combination_matches': combination_matches,
            'requires_immediate_action': severity in ['critical', 'high']
        }


# Singleton instance
_detector_instance = None

def get_child_safety_detector():
    """Get or create singleton detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = EnhancedChildSafetyDetector()
    return _detector_instance


# Example usage and testing
if __name__ == "__main__":
    detector = EnhancedChildSafetyDetector()
    
    # Test cases
    test_cases = [
        # CRITICAL cases (should be 80-100)
        "Kids can work to help parents, don't inform parents. Salary $200 per month. Come to secret location",
        "Young girls needed for modeling work. Don't tell your parents. Good money. DM for location",
        "Child labor opportunity. $150/month. Secret workplace. Parents don't need to know",
        
        # HIGH risk cases (should be 60-80)
        "Looking for teenagers to work. Contact me privately",
        "Kids welcome to work here. Good pay",
        
        # MEDIUM risk cases (should be 40-60)
        "Children should help their parents with work",
        "Young people can earn money",
        
        # LOW risk cases (should be 0-40)
        "Children's education is important",
        "Kids playing in the park",
        "Normal discussion about children"
    ]
    
    print("=" * 80)
    print("CHILD SAFETY DETECTION TEST")
    print("=" * 80)
    
    for text in test_cases:
        result = detector.detect(text)
        
        print(f"\nText: {text[:80]}...")
        print(f"Score: {result['child_score']*100:.1f}/100")
        print(f"Severity: {result['severity']}")
        print(f"Flag: {result['child_flag']}")
        print(f"Exploitation Patterns: {result['exploitation_matches']}")
        print(f"Danger Combinations: {result['combination_matches']}")
        print(f"Triggers: {result['triggers']}")
        
        # Verify critical case
        if "don't inform parents" in text.lower() and "salary" in text.lower():
            if result['child_score'] < 0.8:
                print("⚠️  WARNING: Critical case not detected properly!")
            else:
                print("✅ Critical case detected correctly")
