"""
Upgrade Text Moderation Models
Replaces old models with improved, more aggressive detection
"""

import os
import shutil
from datetime import datetime


def backup_old_files():
    """Backup old model files"""
    print("📦 Backing up old files...")
    
    backup_dir = f"backups/models_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        'core/scoring.py',
        'core/signals/toxicity.py'
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            backup_path = os.path.join(backup_dir, os.path.basename(file))
            shutil.copy2(file, backup_path)
            print(f"  ✓ Backed up {file}")
    
    print(f"✅ Backup complete: {backup_dir}")


def update_scoring():
    """Update scoring.py to use improved version"""
    print("\n🔄 Updating scoring system...")
    
    # Replace scoring.py with improved version
    if os.path.exists('core/signals/improved_scoring.py'):
        shutil.copy2('core/signals/improved_scoring.py', 'core/scoring.py')
        print("  ✓ Updated core/scoring.py")
    else:
        print("  ⚠️  improved_scoring.py not found")


def update_toxicity():
    """Update toxicity.py to use advanced version"""
    print("\n🔄 Updating toxicity detection...")
    
    # Replace toxicity.py with advanced version
    if os.path.exists('core/signals/advanced_toxicity.py'):
        shutil.copy2('core/signals/advanced_toxicity.py', 'core/signals/toxicity.py')
        print("  ✓ Updated core/signals/toxicity.py")
    else:
        print("  ⚠️  advanced_toxicity.py not found")


def install_dependencies():
    """Install required dependencies"""
    print("\n📥 Installing dependencies...")
    
    dependencies = [
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "detoxify>=0.5.0"
    ]
    
    print("Run the following command:")
    print(f"pip install {' '.join(dependencies)}")


def test_new_models():
    """Test the new models"""
    print("\n🧪 Testing new models...")
    
    try:
        from core.signals.advanced_toxicity import AdvancedToxicityDetector
        from core.signals.improved_scoring import calculate_improved_harm_score
        
        print("  ✓ Imports successful")
        
        # Test detector
        detector = AdvancedToxicityDetector()
        
        # Test cases
        test_cases = [
            ("I hope you die", "Should be HIGH risk"),
            ("All Muslims are terrorists", "Should be HIGH risk"),
            ("You're stupid, kill yourself", "Should be HIGH risk"),
            ("This is a normal message", "Should be LOW risk"),
            ("I disagree with your opinion", "Should be LOW risk")
        ]
        
        print("\n  Testing detection:")
        for text, expected in test_cases:
            result = detector.detect(text)
            
            # Create signals dict for scoring
            signals = {
                'tox_score': result['tox_score'],
                'toxicity_severity': result['severity'],
                'requires_immediate_action': result['requires_immediate_action'],
                'toxicity_categories': result['categories'],
                'emotion_score': 0.5,
                'cta_score': 0.3,
                'context_score': 0.2,
                'child_score': 0.1,
                'child_flag': False
            }
            
            scoring = calculate_improved_harm_score(signals)
            
            print(f"\n  Text: '{text[:50]}...'")
            print(f"  Expected: {expected}")
            print(f"  Result: {scoring['risk_label']} risk ({scoring['risk_score']}/100)")
            print(f"  Categories: {result['categories']}")
            
            # Verify
            if "HIGH" in expected and scoring['risk_label'] != 'High':
                print(f"  ⚠️  WARNING: Expected HIGH but got {scoring['risk_label']}")
            elif "LOW" in expected and scoring['risk_label'] == 'High':
                print(f"  ⚠️  WARNING: Expected LOW but got {scoring['risk_label']}")
            else:
                print(f"  ✓ Correct")
        
        print("\n✅ Testing complete!")
        
    except Exception as e:
        print(f"  ❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main upgrade process"""
    print("=" * 60)
    print("🚀 HarmLens Text Model Upgrade")
    print("=" * 60)
    
    print("\nThis will upgrade your text moderation models to:")
    print("  • Advanced multi-model toxicity detection")
    print("  • More aggressive scoring thresholds")
    print("  • Better pattern matching")
    print("  • Improved accuracy on harmful content")
    
    response = input("\nContinue? (y/n): ")
    
    if response.lower() != 'y':
        print("Upgrade cancelled")
        return
    
    # Step 1: Backup
    backup_old_files()
    
    # Step 2: Update files
    update_scoring()
    update_toxicity()
    
    # Step 3: Dependencies
    install_dependencies()
    
    # Step 4: Test
    print("\n" + "=" * 60)
    print("After installing dependencies, run:")
    print("  python upgrade_text_models.py --test")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if '--test' in sys.argv:
        test_new_models()
    else:
        main()
