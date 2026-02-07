# Smart Contracts

This directory contains the Solidity smart contracts for HarmLens blockchain integration.

## ModerationAudit.sol

The main smart contract for logging content moderation decisions to the blockchain.

### Features

- **Immutable Audit Trail**: All moderation decisions permanently recorded
- **IPFS Integration**: Links to full data stored on IPFS
- **Access Control**: Only authorized auditors can log records
- **Event Emission**: Transparent logging via blockchain events
- **Integrity Verification**: Cryptographic hash verification

### Contract Structure

```solidity
struct AuditRecord {
    string contentId;      // Unique content identifier
    string ipfsHash;       // IPFS CID for full data
    uint8 riskScore;       // Risk score (0-100)
    string action;         // Action taken
    uint256 timestamp;     // When logged
    address auditor;       // Who logged it
    bytes32 dataHash;      // SHA-256 for integrity
}

struct EscalationRecord {
    string contentId;      // Content identifier
    address reviewer;      // Reviewer address
    string decision;       // Review decision
    string notes;          // Review notes
    uint256 timestamp;     // When reviewed
}
```

### Key Functions

#### logAnalysis
```solidity
function logAnalysis(
    string memory contentId,
    string memory ipfsHash,
    uint8 riskScore,
    string memory action,
    bytes32 dataHash
) external onlyAuthorized
```

Logs a content analysis to the blockchain.

**Parameters:**
- `contentId`: Unique identifier for the content
- `ipfsHash`: IPFS CID where full data is stored
- `riskScore`: Risk score (0-100)
- `action`: Action taken (e.g., "Human Review Required")
- `dataHash`: SHA-256 hash of data for integrity verification

**Emits:** `AnalysisLogged(contentId, ipfsHash, riskScore, timestamp)`

#### logEscalation
```solidity
function logEscalation(
    string memory contentId,
    address reviewer,
    string memory decision,
    string memory notes
) external onlyAuthorized
```

Logs a human review decision to the blockchain.

**Parameters:**
- `contentId`: Content identifier
- `reviewer`: Ethereum address of reviewer
- `decision`: Review decision
- `notes`: Review notes

**Emits:** `EscalationLogged(contentId, reviewer, decision, timestamp)`

#### getAuditRecord
```solidity
function getAuditRecord(string memory contentId)
    external view
    returns (
        string memory ipfsHash,
        uint8 riskScore,
        string memory action,
        uint256 timestamp,
        address auditor
    )
```

Retrieves an audit record from the blockchain.

**Parameters:**
- `contentId`: Content identifier

**Returns:** Audit record details

#### verifyIntegrity
```solidity
function verifyIntegrity(string memory contentId, bytes32 dataHash)
    external view
    returns (bool)
```

Verifies data integrity by comparing hashes.

**Parameters:**
- `contentId`: Content identifier
- `dataHash`: Hash to verify

**Returns:** `true` if hash matches, `false` otherwise

### Access Control

The contract implements role-based access control:

- **Owner**: Can add/remove authorized auditors
- **Authorized Auditors**: Can log analysis and escalations
- **Public**: Can read audit records and verify integrity

#### Managing Auditors

```solidity
function addAuditor(address auditor) external onlyOwner
function removeAuditor(address auditor) external onlyOwner
```

### Events

```solidity
event AnalysisLogged(
    string indexed contentId,
    string ipfsHash,
    uint8 riskScore,
    uint256 timestamp
)

event EscalationLogged(
    string indexed contentId,
    address indexed reviewer,
    string decision,
    uint256 timestamp
)
```

## Deployment

### Prerequisites

- Solidity compiler (solc) 0.8.0+
- Python 3.8+
- Web3.py
- py-solc-x

### Compile Contract

```bash
python3 blockchain_setup.py
```

This will:
1. Install Solidity compiler
2. Compile the contract
3. Generate ABI file (`ModerationAudit_abi.json`)
4. Deploy to chosen network

### Deploy to Local Network

```bash
# Start Ganache
ganache --deterministic

# Deploy contract
python3 blockchain_setup.py
# Select option 1 (Local)
```

### Deploy to Testnet

```bash
# Deploy to Polygon Mumbai
python3 blockchain_setup.py
# Select option 2 (Mumbai)
# Enter your private key
```

### Deploy to Mainnet

```bash
# Deploy to Polygon Mainnet
python3 blockchain_setup.py
# Select option 3 (Mainnet)
# Enter your private key (KEEP SECRET!)
```

## Gas Costs

Estimated gas costs on Polygon:

| Operation | Gas Used | Cost (MATIC) | Cost (USD) |
|-----------|----------|--------------|------------|
| Deploy Contract | ~2,000,000 | 0.002 | $0.002 |
| Log Analysis | ~150,000 | 0.00015 | $0.00015 |
| Log Escalation | ~100,000 | 0.0001 | $0.0001 |
| Get Audit Record | 0 (read) | 0 | $0 |
| Verify Integrity | 0 (read) | 0 | $0 |

## Security Considerations

### Implemented

✅ **Access Control**: Only authorized auditors can write  
✅ **Input Validation**: Risk score must be 0-100  
✅ **Event Logging**: All actions emit events  
✅ **Immutability**: Records cannot be modified  
✅ **Integrity Verification**: Cryptographic hash checking  

### Recommended for Production

⚠️ **Smart Contract Audit**: Have contract audited by security firm  
⚠️ **Multi-sig Wallet**: Use multi-sig for contract ownership  
⚠️ **Upgradeable Proxy**: Consider proxy pattern for upgrades  
⚠️ **Rate Limiting**: Implement rate limiting in application layer  
⚠️ **Emergency Pause**: Add pause functionality for emergencies  

## Testing

### Unit Tests

```bash
# Run contract tests
python3 test_blockchain_integration.py
```

### Manual Testing

```python
from web3 import Web3
from core.blockchain import BlockchainAuditManager

# Initialize
blockchain = BlockchainAuditManager()

# Log analysis
tx_hash = blockchain.log_analysis_to_blockchain(
    "test_001",
    {"risk_score": 85, "action": "Review"},
    "Test content"
)

# Get record
record = blockchain.get_audit_record("test_001")
print(record)

# Verify integrity
is_valid = blockchain.verify_audit_integrity("test_001")
print(f"Valid: {is_valid}")
```

## Upgrading

The current contract is not upgradeable. For production, consider:

1. **Proxy Pattern**: Use OpenZeppelin's upgradeable contracts
2. **Migration**: Deploy new contract and migrate data
3. **Versioning**: Track contract versions in events

## ABI File

After compilation, the ABI is saved to `ModerationAudit_abi.json`.

This file is used by Web3.py to interact with the contract:

```python
import json
from web3 import Web3

# Load ABI
with open('contracts/ModerationAudit_abi.json') as f:
    abi = json.load(f)

# Create contract instance
contract = w3.eth.contract(address=contract_address, abi=abi)

# Call functions
result = contract.functions.getAuditRecord("content_001").call()
```

## Network Configuration

### Local (Ganache)
```
Provider: http://127.0.0.1:8545
Chain ID: 1337
Gas Price: 20 gwei
```

### Polygon Mumbai (Testnet)
```
Provider: https://polygon-mumbai.infura.io/v3/YOUR_KEY
Chain ID: 80001
Gas Price: 1 gwei
Explorer: https://mumbai.polygonscan.com/
```

### Polygon Mainnet
```
Provider: https://polygon-mainnet.infura.io/v3/YOUR_KEY
Chain ID: 137
Gas Price: 30 gwei
Explorer: https://polygonscan.com/
```

## Troubleshooting

### "Insufficient funds"
- Check account balance: `w3.eth.get_balance(address)`
- Get testnet tokens from faucet

### "Transaction failed"
- Check gas price: `w3.eth.gas_price`
- Increase gas limit in transaction

### "Contract not found"
- Verify contract address
- Check network connection
- Ensure contract is deployed

### "Not authorized"
- Check if address is added as auditor
- Verify private key matches authorized address

## Support

- **Documentation**: See `BLOCKCHAIN_GUIDE.md`
- **Examples**: See `examples/blockchain_example.py`
- **API Reference**: See `API_GUIDE.md`

## License

MIT License - See LICENSE file
