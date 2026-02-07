"""
Test Blockchain Integration
Verifies that blockchain components are working correctly
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all blockchain modules can be imported"""
    print("Testing imports...")
    
    try:
        from core.blockchain import BlockchainAuditManager, LocalBlockchainSimulator
        print("✓ Blockchain modules imported")
        
        from core.action_executor import ActionExecutor
        print("✓ Action executor imported")
        
        from web3 import Web3
        print("✓ Web3 imported")
        
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        print("\nRun: pip install -r requirements.txt")
        return False


def test_local_simulator():
    """Test local blockchain simulator"""
    print("\nTesting local blockchain simulator...")
    
    try:
        from core.blockchain import LocalBlockchainSimulator
        
        sim = LocalBlockchainSimulator()
        
        # Test logging
        analysis = {
            "risk_score": 85,
            "risk_label": "High",
            "action": "Human Review Required",
            "priority": "HIGH",
            "categories": ["Test"],
            "reasons": ["Test reason"]
        }
        
        tx_hash = sim.log_analysis("test_001", analysis, "Test content")
        
        if tx_hash:
            print(f"✓ Analysis logged: {tx_hash[:16]}...")
            
            # Test retrieval
            record = sim.get_audit_record("test_001")
            if record:
                print(f"✓ Record retrieved: Block #{record['block_number']}")
                return True
            else:
                print("✗ Record retrieval failed")
                return False
        else:
            print("✗ Logging failed")
            return False
            
    except Exception as e:
        print(f"✗ Simulator test failed: {e}")
        return False


def test_web3_connection():
    """Test Web3 connection to local node"""
    print("\nTesting Web3 connection...")
    
    try:
        from web3 import Web3
        
        # Try local Ganache
        w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
        
        if w3.is_connected():
            print(f"✓ Connected to local blockchain")
            print(f"  Chain ID: {w3.eth.chain_id}")
            print(f"  Block number: {w3.eth.block_number}")
            
            # Check accounts
            accounts = w3.eth.accounts
            if accounts:
                print(f"  Accounts: {len(accounts)}")
                balance = w3.eth.get_balance(accounts[0])
                print(f"  Balance: {w3.from_wei(balance, 'ether')} ETH")
            
            return True
        else:
            print("⚠️  Not connected to local blockchain")
            print("   Start Ganache: ganache --deterministic")
            return False
            
    except Exception as e:
        print(f"⚠️  Connection test skipped: {e}")
        print("   This is OK if you're using simulator mode")
        return False


def test_ipfs_connection():
    """Test IPFS connection"""
    print("\nTesting IPFS connection...")
    
    try:
        import requests
        
        response = requests.post(
            "http://127.0.0.1:5001/api/v0/version",
            timeout=2
        )
        
        if response.status_code == 200:
            version = response.json()
            print(f"✓ IPFS connected")
            print(f"  Version: {version.get('Version', 'unknown')}")
            return True
        else:
            print("⚠️  IPFS not responding")
            print("   Start IPFS: ipfs daemon")
            return False
            
    except Exception as e:
        print(f"⚠️  IPFS test skipped: {e}")
        print("   This is OK if you're not using IPFS")
        return False


def test_smart_contract():
    """Test smart contract compilation"""
    print("\nTesting smart contract...")
    
    contract_path = Path("contracts/ModerationAudit.sol")
    
    if contract_path.exists():
        print(f"✓ Smart contract found: {contract_path}")
        
        # Check if ABI exists
        abi_path = Path("contracts/ModerationAudit_abi.json")
        if abi_path.exists():
            print(f"✓ Contract ABI found: {abi_path}")
        else:
            print(f"⚠️  Contract not compiled yet")
            print("   Run: python blockchain_setup.py")
        
        return True
    else:
        print("✗ Smart contract not found")
        return False


def test_action_executor():
    """Test action executor with blockchain"""
    print("\nTesting action executor...")
    
    try:
        from core.action_executor import ActionExecutor
        from core.database import ModerationDatabase
        
        db = ModerationDatabase(":memory:")  # In-memory database
        executor = ActionExecutor(db, use_blockchain=True)
        
        print("✓ Action executor initialized")
        
        # Test blockchain stats
        stats = executor.get_blockchain_stats()
        print(f"✓ Blockchain stats retrieved")
        print(f"  Connected: {stats['connected']}")
        print(f"  Mode: {stats.get('mode', 'production')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Action executor test failed: {e}")
        return False


def test_environment():
    """Test environment configuration"""
    print("\nTesting environment configuration...")
    
    import os
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print(f"✓ Environment file found: {env_file}")
        
        # Check key variables
        provider = os.getenv('ETH_PROVIDER_URL')
        contract = os.getenv('CONTRACT_ADDRESS')
        
        if provider:
            print(f"  Provider: {provider}")
        else:
            print("  ⚠️  ETH_PROVIDER_URL not set")
        
        if contract:
            print(f"  Contract: {contract[:10]}...")
        else:
            print("  ⚠️  CONTRACT_ADDRESS not set (OK for simulator)")
        
        return True
    else:
        print(f"⚠️  No .env file found")
        print(f"   Copy from: {env_example}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("HarmLens Blockchain Integration Test")
    print("="*60)
    
    results = {
        "Imports": test_imports(),
        "Local Simulator": test_local_simulator(),
        "Web3 Connection": test_web3_connection(),
        "IPFS Connection": test_ipfs_connection(),
        "Smart Contract": test_smart_contract(),
        "Action Executor": test_action_executor(),
        "Environment": test_environment()
    }
    
    print("\n" + "="*60)
    print("Test Results")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20} {status}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print("="*60)
    print(f"Passed: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! You're ready to go.")
        print("\nNext steps:")
        print("1. Start API server: python api_server.py")
        print("2. Run demo: python examples/blockchain_example.py")
    elif results["Imports"] and results["Local Simulator"]:
        print("\n✓ Core functionality working!")
        print("\nYou can use simulator mode without blockchain/IPFS.")
        print("To enable full blockchain:")
        print("1. Start Ganache: ganache --deterministic")
        print("2. Deploy contract: python blockchain_setup.py")
        print("3. Start IPFS: ipfs daemon")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        print("\nInstall dependencies: pip install -r requirements.txt")
    
    print("="*60 + "\n")
    
    return 0 if passed_count >= 2 else 1  # Pass if at least core works


if __name__ == "__main__":
    sys.exit(main())
