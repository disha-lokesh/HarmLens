"""
Blockchain Integration Example
Demonstrates how to use HarmLens with blockchain audit trails
"""

import requests
import json
from datetime import datetime


# API endpoint
API_BASE = "http://localhost:8000"


def analyze_with_blockchain(text: str, content_id: str = None):
    """Analyze content and log to blockchain"""
    
    print(f"\n{'='*60}")
    print(f"Analyzing: {text[:50]}...")
    print(f"{'='*60}\n")
    
    # Call API
    response = requests.post(
        f"{API_BASE}/api/v1/analyze",
        json={
            "text": text,
            "content_id": content_id,
            "user_id": "demo_user_123",
            "platform": "demo"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"✓ Analysis Complete")
        print(f"  Content ID: {result['content_id']}")
        print(f"  Risk Score: {result['risk_score']}/100 ({result['risk_label']})")
        print(f"  Action: {result['action']}")
        print(f"  Priority: {result['priority']}")
        print(f"  Categories: {', '.join(result['categories'])}")
        
        # Blockchain info
        if result.get('blockchain'):
            bc = result['blockchain']
            print(f"\n📦 Blockchain:")
            print(f"  Logged: {bc['logged']}")
            if bc.get('tx_hash'):
                print(f"  TX Hash: {bc['tx_hash']}")
            if bc.get('ipfs_hash'):
                print(f"  IPFS Hash: {bc['ipfs_hash']}")
        
        print(f"\n💡 Reasons:")
        for i, reason in enumerate(result['reasons'], 1):
            print(f"  {i}. {reason}")
        
        return result
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
        return None


def verify_audit_record(content_id: str):
    """Verify audit record from blockchain"""
    
    print(f"\n{'='*60}")
    print(f"Verifying Audit Record: {content_id}")
    print(f"{'='*60}\n")
    
    # Get audit record
    response = requests.get(f"{API_BASE}/api/v1/blockchain/audit/{content_id}")
    
    if response.status_code == 200:
        result = response.json()
        record = result['audit_record']
        
        print(f"✓ Audit Record Found")
        print(f"  IPFS Hash: {record['ipfs_hash']}")
        print(f"  Risk Score: {record['risk_score']}")
        print(f"  Action: {record['action']}")
        print(f"  Timestamp: {datetime.fromtimestamp(record['timestamp'])}")
        print(f"  Auditor: {record['auditor']}")
        
        # Verify integrity
        verify_response = requests.get(
            f"{API_BASE}/api/v1/blockchain/verify/{content_id}"
        )
        
        if verify_response.status_code == 200:
            verify_result = verify_response.json()
            print(f"\n🔒 Integrity Check: {verify_result['message']}")
        
        return result
    else:
        print(f"✗ Error: {response.status_code}")
        return None


def get_blockchain_stats():
    """Get blockchain statistics"""
    
    print(f"\n{'='*60}")
    print(f"Blockchain Statistics")
    print(f"{'='*60}\n")
    
    response = requests.get(f"{API_BASE}/api/v1/blockchain/stats")
    
    if response.status_code == 200:
        stats = response.json()
        
        print(f"Connected: {stats['connected']}")
        print(f"Network: {stats.get('network', 'N/A')}")
        
        if stats.get('account'):
            print(f"Account: {stats['account']}")
            print(f"Balance: {stats.get('balance', 0)} ETH")
        
        print(f"Contract Deployed: {stats.get('contract_deployed', False)}")
        
        if stats.get('total_blocks'):
            print(f"Total Blocks: {stats['total_blocks']}")
        
        return stats
    else:
        print(f"✗ Error: {response.status_code}")
        return None


def log_escalation(content_id: str, decision: str, notes: str):
    """Log human review decision to blockchain"""
    
    print(f"\n{'='*60}")
    print(f"Logging Escalation: {content_id}")
    print(f"{'='*60}\n")
    
    response = requests.post(
        f"{API_BASE}/api/v1/blockchain/escalation",
        params={
            "content_id": content_id,
            "reviewer_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            "decision": decision,
            "notes": notes
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"✓ Escalation Logged")
        print(f"  Blockchain Logged: {result['blockchain_logged']}")
        if result.get('tx_hash'):
            print(f"  TX Hash: {result['tx_hash']}")
        
        return result
    else:
        print(f"✗ Error: {response.status_code}")
        return None


def main():
    """Run demo"""
    
    print("\n" + "="*60)
    print("HarmLens Blockchain Integration Demo")
    print("="*60)
    
    # Check blockchain status
    get_blockchain_stats()
    
    # Example 1: High-risk content
    result1 = analyze_with_blockchain(
        "URGENT! Vaccine contains poison! Share NOW before they remove it!",
        content_id="demo_post_001"
    )
    
    # Example 2: Low-risk content
    result2 = analyze_with_blockchain(
        "Community center opens next month with sports facilities.",
        content_id="demo_post_002"
    )
    
    # Example 3: Child safety concern
    result3 = analyze_with_blockchain(
        "Looking for young kids to join our private group chat.",
        content_id="demo_post_003"
    )
    
    # Verify audit records
    if result1:
        input("\n\nPress Enter to verify audit records...")
        verify_audit_record(result1['content_id'])
    
    # Log escalation (human review)
    if result1:
        input("\n\nPress Enter to log human review decision...")
        log_escalation(
            result1['content_id'],
            decision="Confirmed - Removed",
            notes="Health misinformation with urgent CTA. Removed per policy."
        )
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)
    print("\nAll moderation decisions are now:")
    print("✓ Stored immutably on blockchain")
    print("✓ Backed up on IPFS (decentralized storage)")
    print("✓ Cryptographically verifiable")
    print("✓ Audit-ready for compliance")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
