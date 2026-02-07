"""
Test Demo Cases for HarmLens
Verifies all demo scenarios work correctly
"""

from core.signals.enhanced_child_safety import EnhancedChildSafetyDetector
from core.signals.advanced_toxicity import AdvancedToxicityDetector
from core.signals.emotion import EmotionDetector
from core.signals.cta import CTADetector
from core.signals.context import ContextDetector
from core.signals.improved_scoring import calculate_improved_harm_score

# Initialize detectors
child_detector = EnhancedChildSafetyDetector()
tox_detector = AdvancedToxicityDetector()
emotion_detector = EmotionDetector()
cta_detector = CTADetector()
context_detector = ContextDetector('assets')

def analyze_full(text: str) -> dict:
    """Run full analysis pipeline"""
    
    # Run all detectors
    child_result = child_detector.detect(text)
    tox_result = tox_detector.detect(text)
    emotion_result = emotion_detector.detect(text)
    cta_result = cta_detector.detect(text)
    context_result = context_detector.detect(text)
    
    # Create signals dict
    signals = {
        'child_score': child_result['child_score'],
        'child_flag': child_result['child_flag'],
        'child_severity': child_result['severity'],
        'child_exploitation_matches': child_result['exploitation_matches'],
        'child_combination_matches': child_result['combination_matches'],
        
        'tox_score': tox_result['tox_score'],
        'toxicity_severity': tox_result['severity'],
        'requires_immediate_action': tox_result['requires_immediate_action'],
        'toxicity_categories': tox_result['categories'],
        
        'emotion_score': emotion_result['emotion_score'],
        'emotion_labels': emotion_result['emotion_labels'],
        
        'cta_score': cta_result['cta_score'],
        
        'context_score': context_result['context_score'],
        'context_topic': context_result['context_topic']
    }
    
    # Calculate final score
    scoring = calculate_improved_harm_score(signals)
    
    return {
        **scoring,
        'child_result': child_result,
        'tox_result': tox_result,
        'emotion_result': emotion_result,
        'cta_result': cta_result,
        'context_result': context_result
    }


def print_result(title: str, text: str, expected_range: str):
    """Print analysis result"""
    print("\n" + "="*80)
    print(f"TEST: {title}")
    print("="*80)
    print(f"Text: {text}")
    print(f"Expected: {expected_range}")
    print("-"*80)
    
    result = analyze_full(text)
    
    print(f"\n✅ RESULT:")
    print(f"   Risk Score: {result['risk_score']}/100")
    print(f"   Risk Label: {result['risk_label']}")
    print(f"   Child Severity: {result.get('child_severity', 'none')}")
    print(f"   Toxicity Severity: {result.get('toxicity_severity', 'none')}")
    print(f"   Immediate Action: {result.get('immediate_action_required', False)}")
    
    print(f"\n📊 Breakdown:")
    for key, value in result['breakdown'].items():
        print(f"   {key}: {value:.2f}")
    
    print(f"\n🏷️  Categories:")
    if result.get('child_result', {}).get('triggers'):
        print(f"   Child Safety: {result['child_result']['triggers']}")
    if result.get('tox_result', {}).get('categories'):
        print(f"   Toxicity: {result['tox_result']['categories']}")
    
    # Verify expected range
    score = result['risk_score']
    if "85+" in expected_range and score >= 85:
        print(f"\n✅ PASS: Score {score} is in expected range {expected_range}")
    elif "80+" in expected_range and score >= 80:
        print(f"\n✅ PASS: Score {score} is in expected range {expected_range}")
    elif "0-20" in expected_range and score <= 20:
        print(f"\n✅ PASS: Score {score} is in expected range {expected_range}")
    else:
        print(f"\n⚠️  WARNING: Score {score} may not be in expected range {expected_range}")
    
    return result


def main():
    """Run all demo test cases"""
    
    print("\n" + "="*80)
    print("HARMLENS DEMO TEST CASES")
    print("="*80)
    
    # Demo 1: High Risk (Health Panic + CTA)
    print_result(
        "Demo 1: High Risk - Health Panic + CTA",
        "URGENT: New virus spreading fast! Symptoms include fever and cough. "
        "Share this NOW before it's too late! Government is hiding the truth. "
        "Act immediately to protect your family!",
        "85+ (High)"
    )
    
    # Demo 2: Child Safety (CRITICAL)
    print_result(
        "Demo 2: Child Safety - Exploitation/Trafficking",
        "Kids can work to help parents, don't inform parents. "
        "Salary $200 per month. Come to secret location",
        "95+ (High/Critical)"
    )
    
    # Demo 3: Low Risk (Neutral Information)
    print_result(
        "Demo 3: Low Risk - Neutral Information",
        "According to the CDC, washing hands regularly can help prevent the spread of illness. "
        "It's recommended to wash for at least 20 seconds with soap and water.",
        "0-20 (Low)"
    )
    
    # Additional Test: Explicit Threat
    print_result(
        "Additional: Explicit Threat",
        "I hope you die. You deserve to be killed.",
        "90+ (High)"
    )
    
    # Additional Test: Hate Speech
    print_result(
        "Additional: Hate Speech",
        "All Muslims are terrorists and should be removed from this country.",
        "85+ (High)"
    )
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
