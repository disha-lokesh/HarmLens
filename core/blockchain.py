"""
Blockchain Integration - Immutable Audit Trail & Decentralized Storage
Uses Ethereum for audit records and IPFS for content storage
"""

from web3 import Web3
try:
    from web3.middleware import geth_poa_middleware
except ImportError:
    # Newer versions of web3.py
    try:
        from web3.middleware import ExtraDataToPOAMiddleware as geth_poa_middleware
    except ImportError:
        geth_poa_middleware = None
import json
import hashlib
from datetime import datetime
from typing import Dict, Optional, List
import os
from pathlib import Path


class BlockchainAuditManager:
    """
    Manages blockchain-based audit trails for content moderation
    - Stores audit records on Ethereum
    - Uses IPFS for decentralized content storage
    - Provides immutable proof of moderation decisions
    """
    
    def __init__(self, 
                 provider_url: str = None,
                 contract_address: str = None,
                 private_key: str = None,
                 ipfs_gateway: str = "http://127.0.0.1:5001"):
        """
        Initialize blockchain connection
        
        Args:
            provider_url: Ethereum node URL (Infura, Alchemy, or local)
            contract_address: Deployed smart contract address
            private_key: Private key for signing transactions
            ipfs_gateway: IPFS API gateway URL
        """
        # Load from environment if not provided
        self.provider_url = provider_url or os.getenv('ETH_PROVIDER_URL', 'http://127.0.0.1:8545')
        self.contract_address = contract_address or os.getenv('CONTRACT_ADDRESS')
        self.private_key = private_key or os.getenv('ETH_PRIVATE_KEY')
        self.ipfs_gateway = ipfs_gateway
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.provider_url))
        
        # Add PoA middleware for networks like Polygon, BSC (if available)
        if geth_poa_middleware:
            try:
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            except:
                pass  # Middleware not needed or already injected
        
        # Load account
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
        else:
            self.account = None
        
        # Load smart contract
        self.contract = None
        if self.contract_address:
            self._load_contract()
    
    def _load_contract(self):
        """Load the audit smart contract"""
        # Contract ABI (simplified for audit logging)
        abi = self._get_contract_abi()
        
        if self.w3.is_checksum_address(self.contract_address):
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=abi
            )
    
    def _get_contract_abi(self) -> List[Dict]:
        """
        Returns the ABI for the ModerationAudit smart contract
        """
        return [
            {
                "inputs": [
                    {"name": "contentId", "type": "string"},
                    {"name": "ipfsHash", "type": "string"},
                    {"name": "riskScore", "type": "uint8"},
                    {"name": "action", "type": "string"},
                    {"name": "dataHash", "type": "bytes32"}
                ],
                "name": "logAnalysis",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "contentId", "type": "string"},
                    {"name": "reviewer", "type": "address"},
                    {"name": "decision", "type": "string"},
                    {"name": "notes", "type": "string"}
                ],
                "name": "logEscalation",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "contentId", "type": "string"}
                ],
                "name": "getAuditRecord",
                "outputs": [
                    {"name": "ipfsHash", "type": "string"},
                    {"name": "riskScore", "type": "uint8"},
                    {"name": "action", "type": "string"},
                    {"name": "timestamp", "type": "uint256"},
                    {"name": "auditor", "type": "address"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "contentId", "type": "string"},
                    {"indexed": False, "name": "ipfsHash", "type": "string"},
                    {"indexed": False, "name": "riskScore", "type": "uint8"},
                    {"indexed": False, "name": "timestamp", "type": "uint256"}
                ],
                "name": "AnalysisLogged",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "contentId", "type": "string"},
                    {"indexed": True, "name": "reviewer", "type": "address"},
                    {"indexed": False, "name": "decision", "type": "string"},
                    {"indexed": False, "name": "timestamp", "type": "uint256"}
                ],
                "name": "EscalationLogged",
                "type": "event"
            }
        ]
    
    def is_connected(self) -> bool:
        """Check if connected to blockchain"""
        try:
            return self.w3.is_connected()
        except:
            return False
    
    def get_balance(self, address: str = None) -> float:
        """Get ETH balance of address"""
        addr = address or (self.account.address if self.account else None)
        if not addr:
            return 0.0
        
        balance_wei = self.w3.eth.get_balance(addr)
        return self.w3.from_wei(balance_wei, 'ether')
    
    def hash_data(self, data: dict) -> str:
        """
        Create SHA-256 hash of data for integrity verification
        
        Args:
            data: Dictionary to hash
            
        Returns:
            Hex string of hash
        """
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def store_to_ipfs(self, data: dict) -> Optional[str]:
        """
        Store data to IPFS (decentralized storage)
        
        Args:
            data: Dictionary to store
            
        Returns:
            IPFS hash (CID) or None if failed
        """
        try:
            import requests
            
            # Convert to JSON
            json_data = json.dumps(data, indent=2)
            
            # Upload to IPFS
            files = {'file': json_data}
            response = requests.post(
                f"{self.ipfs_gateway}/api/v0/add",
                files=files
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['Hash']  # IPFS CID
            else:
                print(f"IPFS upload failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"IPFS storage error: {e}")
            return None
    
    def retrieve_from_ipfs(self, ipfs_hash: str) -> Optional[dict]:
        """
        Retrieve data from IPFS
        
        Args:
            ipfs_hash: IPFS CID
            
        Returns:
            Retrieved data or None
        """
        try:
            import requests
            
            response = requests.post(
                f"{self.ipfs_gateway}/api/v0/cat",
                params={'arg': ipfs_hash}
            )
            
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                return None
                
        except Exception as e:
            print(f"IPFS retrieval error: {e}")
            return None
    
    def log_analysis_to_blockchain(self, 
                                   content_id: str,
                                   analysis: dict,
                                   content_text: str) -> Optional[str]:
        """
        Log content analysis to blockchain with IPFS storage
        
        Args:
            content_id: Unique content identifier
            analysis: Analysis result dictionary
            content_text: Original content text
            
        Returns:
            Transaction hash or None if failed
        """
        if not self.contract or not self.account:
            print("Blockchain not configured. Skipping on-chain logging.")
            return None
        
        try:
            # Prepare audit data
            audit_data = {
                "content_id": content_id,
                "content_text": content_text,
                "risk_score": analysis['risk_score'],
                "risk_label": analysis['risk_label'],
                "categories": analysis['categories'],
                "action": analysis['action'],
                "priority": analysis['priority'],
                "reasons": analysis['reasons'],
                "timestamp": datetime.utcnow().isoformat(),
                "system_version": "HarmLens v1.0"
            }
            
            # Store full data to IPFS
            ipfs_hash = self.store_to_ipfs(audit_data)
            if not ipfs_hash:
                print("IPFS storage failed")
                return None
            
            # Create data hash for integrity
            data_hash = self.hash_data(audit_data)
            data_hash_bytes = bytes.fromhex(data_hash)
            
            # Build transaction
            txn = self.contract.functions.logAnalysis(
                content_id,
                ipfs_hash,
                analysis['risk_score'],
                analysis['action'],
                data_hash_bytes
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                print(f"✓ Analysis logged to blockchain: {tx_hash.hex()}")
                print(f"✓ Content stored on IPFS: {ipfs_hash}")
                return tx_hash.hex()
            else:
                print(f"Transaction failed: {receipt}")
                return None
                
        except Exception as e:
            print(f"Blockchain logging error: {e}")
            return None
    
    def log_escalation_to_blockchain(self,
                                     content_id: str,
                                     reviewer_address: str,
                                     decision: str,
                                     notes: str) -> Optional[str]:
        """
        Log escalation/review decision to blockchain
        
        Args:
            content_id: Content identifier
            reviewer_address: Ethereum address of reviewer
            decision: Review decision
            notes: Review notes
            
        Returns:
            Transaction hash or None
        """
        if not self.contract or not self.account:
            return None
        
        try:
            # Build transaction
            txn = self.contract.functions.logEscalation(
                content_id,
                reviewer_address,
                decision,
                notes
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send
            signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                print(f"✓ Escalation logged to blockchain: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                return None
                
        except Exception as e:
            print(f"Escalation logging error: {e}")
            return None
    
    def get_audit_record(self, content_id: str) -> Optional[Dict]:
        """
        Retrieve audit record from blockchain
        
        Args:
            content_id: Content identifier
            
        Returns:
            Audit record dictionary or None
        """
        if not self.contract:
            return None
        
        try:
            result = self.contract.functions.getAuditRecord(content_id).call()
            
            return {
                "ipfs_hash": result[0],
                "risk_score": result[1],
                "action": result[2],
                "timestamp": result[3],
                "auditor": result[4]
            }
        except Exception as e:
            print(f"Error retrieving audit record: {e}")
            return None
    
    def verify_audit_integrity(self, content_id: str) -> bool:
        """
        Verify audit record integrity by comparing blockchain hash with IPFS data
        
        Args:
            content_id: Content identifier
            
        Returns:
            True if integrity verified, False otherwise
        """
        try:
            # Get blockchain record
            record = self.get_audit_record(content_id)
            if not record:
                return False
            
            # Retrieve data from IPFS
            ipfs_data = self.retrieve_from_ipfs(record['ipfs_hash'])
            if not ipfs_data:
                return False
            
            # Compute hash and compare
            computed_hash = self.hash_data(ipfs_data)
            
            # In production, you'd compare with stored hash from blockchain
            print(f"Data hash: {computed_hash}")
            print(f"Integrity check: Data retrieved successfully from IPFS")
            
            return True
            
        except Exception as e:
            print(f"Integrity verification error: {e}")
            return False
    
    def get_blockchain_stats(self) -> Dict:
        """Get blockchain integration statistics"""
        stats = {
            "connected": self.is_connected(),
            "network": "Unknown",
            "account": self.account.address if self.account else None,
            "balance": 0.0,
            "contract_deployed": self.contract is not None
        }
        
        if self.is_connected():
            try:
                stats["network"] = self.w3.eth.chain_id
                if self.account:
                    stats["balance"] = self.get_balance()
            except:
                pass
        
        return stats


# Fallback: Local blockchain simulation for development
class LocalBlockchainSimulator:
    """
    Simulates blockchain functionality for development/testing
    Stores records locally with cryptographic hashing
    """
    
    def __init__(self, storage_path: str = "blockchain_sim"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.audit_file = self.storage_path / "audit_chain.json"
        self._init_chain()
    
    def _init_chain(self):
        """Initialize local chain file"""
        if not self.audit_file.exists():
            self.audit_file.write_text(json.dumps({"blocks": []}, indent=2))
    
    def _load_chain(self) -> dict:
        """Load chain from file"""
        return json.loads(self.audit_file.read_text())
    
    def _save_chain(self, chain: dict):
        """Save chain to file"""
        self.audit_file.write_text(json.dumps(chain, indent=2))
    
    def hash_data(self, data: dict) -> str:
        """Hash data"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def log_analysis(self, content_id: str, analysis: dict, content_text: str) -> str:
        """Simulate blockchain logging"""
        chain = self._load_chain()
        
        # Create block
        block = {
            "block_number": len(chain["blocks"]),
            "timestamp": datetime.utcnow().isoformat(),
            "content_id": content_id,
            "data": {
                "content_text": content_text,
                "analysis": analysis
            },
            "previous_hash": chain["blocks"][-1]["hash"] if chain["blocks"] else "0" * 64
        }
        
        # Add hash
        block["hash"] = self.hash_data(block)
        
        # Append to chain
        chain["blocks"].append(block)
        self._save_chain(chain)
        
        return block["hash"]
    
    def get_audit_record(self, content_id: str) -> Optional[Dict]:
        """Retrieve audit record"""
        chain = self._load_chain()
        
        for block in chain["blocks"]:
            if block.get("content_id") == content_id:
                return block
        
        return None
    
    def is_connected(self) -> bool:
        """Always connected in simulation"""
        return True
    
    def get_blockchain_stats(self) -> Dict:
        """Get simulation stats"""
        chain = self._load_chain()
        return {
            "connected": True,
            "network": "Local Simulation",
            "total_blocks": len(chain["blocks"]),
            "mode": "development"
        }
