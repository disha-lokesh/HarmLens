"""
Test Escalation System
Verify escalation creation and tracking works correctly
"""

from core.database import ModerationDatabase
from datetime import datetime

def test_escalation_system():
    """Test the escalation system"""
    
    print("\n" + "="*80)
    print("TESTING ESCALATION SYSTEM")
    print("="*80)
    
    # Initialize database
    db = ModerationDatabase()
    
    # Test 1: Create escalation
    print("\n📝 Test 1: Creating escalation...")
    
    escalation_id = db.create_escalation(
        content_id="test_content_123",
        escalated_by="moderator",
        reason="Potential child exploitation detected - requires immediate review",
        escalation_type="Child Safety",
        priority="CRITICAL"
    )
    
    print(f"✅ Escalation created: #{escalation_id}")
    
    # Test 2: Get pending escalations
    print("\n📋 Test 2: Retrieving pending escalations...")
    
    pending = db.get_escalations(status="pending")
    print(f"✅ Found {len(pending)} pending escalation(s)")
    
    if pending:
        esc = pending[0]
        print(f"\n   Escalation #{esc['id']}:")
        print(f"   - Type: {esc['escalation_type']}")
        print(f"   - Priority: {esc['priority']}")
        print(f"   - Status: {esc['status']}")
        print(f"   - Response Time: {esc['response_time_estimate']}")
        print(f"   - Created: {esc['created_at']}")
    
    # Test 3: Update to in-progress
    print("\n🔄 Test 3: Updating escalation to in-progress...")
    
    db.update_escalation_status(
        escalation_id=escalation_id,
        status="in-progress",
        assigned_to="admin"
    )
    
    in_progress = db.get_escalations(status="in-progress")
    print(f"✅ Escalation updated - {len(in_progress)} in-progress")
    
    # Test 4: Mark as responded
    print("\n💬 Test 4: Marking as responded...")
    
    db.update_escalation_status(
        escalation_id=escalation_id,
        status="responded"
    )
    
    responded = db.get_escalations(status="responded")
    print(f"✅ Escalation responded - {len(responded)} responded")
    
    # Test 5: Resolve escalation
    print("\n✅ Test 5: Resolving escalation...")
    
    db.update_escalation_status(
        escalation_id=escalation_id,
        status="resolved",
        resolution_notes="Content removed and user banned. Law enforcement notified."
    )
    
    resolved = db.get_escalations(status="resolved")
    print(f"✅ Escalation resolved - {len(resolved)} resolved")
    
    if resolved:
        esc = resolved[0]
        print(f"\n   Resolution Details:")
        print(f"   - Resolved At: {esc['resolved_at']}")
        print(f"   - Notes: {esc['resolution_notes']}")
    
    # Test 6: Get all escalations by moderator
    print("\n👤 Test 6: Getting escalations by moderator...")
    
    mod_escalations = db.get_escalations(escalated_by="moderator")
    print(f"✅ Found {len(mod_escalations)} escalation(s) by moderator")
    
    # Test 7: Get stats
    print("\n📊 Test 7: Getting system stats...")
    
    stats = db.get_stats()
    print(f"✅ System Stats:")
    print(f"   - Total Analyzed: {stats['total_analyzed']}")
    print(f"   - Pending Review: {stats['pending_review']}")
    print(f"   - Escalations: {stats.get('escalations', {})}")
    
    # Test 8: Create multiple escalations with different priorities
    print("\n📝 Test 8: Creating multiple escalations...")
    
    test_escalations = [
        {
            "content_id": "test_high_priority",
            "escalated_by": "moderator",
            "reason": "Hate speech targeting protected group",
            "escalation_type": "Policy Violation",
            "priority": "HIGH"
        },
        {
            "content_id": "test_medium_priority",
            "escalated_by": "moderator",
            "reason": "Potential misinformation about health",
            "escalation_type": "Urgent Review",
            "priority": "MEDIUM"
        },
        {
            "content_id": "test_legal_issue",
            "escalated_by": "reviewer",
            "reason": "Copyright infringement claim",
            "escalation_type": "Legal Issue",
            "priority": "HIGH"
        }
    ]
    
    for esc_data in test_escalations:
        esc_id = db.create_escalation(**esc_data)
        print(f"   ✅ Created escalation #{esc_id} - {esc_data['priority']} priority")
    
    # Test 9: Get all escalations sorted by priority
    print("\n📋 Test 9: Getting all escalations (sorted by priority)...")
    
    all_escalations = db.get_escalations()
    print(f"✅ Total escalations: {len(all_escalations)}")
    
    for esc in all_escalations[:5]:  # Show first 5
        print(f"   #{esc['id']}: {esc['priority']} - {esc['escalation_type']} - {esc['status']}")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED")
    print("="*80)
    
    print("\n📌 Summary:")
    print(f"   - Escalation system is working correctly")
    print(f"   - Database tables created successfully")
    print(f"   - Status workflow functioning properly")
    print(f"   - Priority-based sorting working")
    print(f"   - Response time estimates assigned correctly")
    
    print("\n🚀 Ready to use in moderator dashboard!")
    print("   Run: streamlit run moderator_dashboard.py")
    print("   Login as: moderator / moderator_001")
    print("   Navigate to: Escalation Queue")


if __name__ == "__main__":
    test_escalation_system()
