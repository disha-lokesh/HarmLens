# HarmLens Blockchain Integration Guide

## Overview

HarmLens now includes **blockchain-based audit trails** and **decentralized storage** for complete transparency and immutability of moderation decisions.

### Key Features

✅ **Immutable Audit Trail**: All moderation decisions recorded on Ethereum blockchain  
✅ **Decentralized Storage**: Full content and analysis data stored on IPFS  
✅ **Cryptographic Verification**: SHA-256 hashing for data integrity  
✅ **Escalation Tracking**: Human review decisions permanently logged  
✅ **Compliance Ready**: Tamper-proof records for regulatory requirements  

---

## Architecture

```
Content Analysis
      ↓
┌─────────────────────────────────────┐
│  1. Store full data to IPFS         │ → Returns IPFS CID (hash)
│  2. Create SHA-256 hash of data     │ → For integrity verification
│  3. Log to blockchain smart contract│ → Immutable record
│  4. Save to local database          │ → Fast queries
└─────────────────────────────────────┘
```

### Data Flow

1. **Content analyzed** → Risk score, categories, action determined
2. **Full data stored on IPFS** → Returns content identifier (CID)
3. **Audit record logged to blockchain** → Includes IPFS CID, risk score, action, timestamp
4. **Local database updated** → For fast queries and dashboard
5. **Webhooks triggered** → Real-time notifications

---

## Smart Contract

The `ModerationAudit.sol` contract provides:

### Core Functions

```solidity
// Log content analysis
function logAnalysis(
    string contentId,
    string ipfsHash,      // IPFS CID
    uint8 riskScore,      // 0-100
    string action,
    bytes32 dataHash      // SHA-256 for integrity
)

// Log escalation/review
function logEscalation(
    string contentId,
    address reviewer,
    string decision,
    string notes
)

// Retrieve audit record
function getAuditRecord(string contentId)
    returns (ipfsHash, riskScore, action, timestamp, auditor)

// Verify data integrity
function verifyIntegrity(string contentId, bytes32 dataHash)
    returns (bool)
```

### Events

```solidity
event AnalysisLogged(string indexed contentId, string ipfsHash, uint8 riskScore, uint256 timestamp)
event EscalationLogged(string indexed contentId, address indexed reviewer, string decision, uint256 timestamp)
```

---

## Setup Instructions

### Prerequisites

1. **Python 3.8+** with pip
2. **Node.js** (for IPFS)
3. **Ethereum wallet** with testnet ETH
4. **IPFS daemon** running locally or remote gateway

### Option 1: Local Development (Recommended for Testing)

#### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 2: Start Local Blockchain (Ganache)

```bash
# Install Ganache
npm install -g ganache

# Start Ganache
ganache --deterministic --accounts 10
```

This gives you 10 accounts with 100 ETH each for testing.

#### Step 3: Start IPFS Daemon

```bash
# Install IPFS
# macOS: brew install ipfs
# Linux: https://docs.ipfs.tech/install/

# Initialize IPFS
ipfs init

# Start daemon
ipfs daemon
```

#### Step 4: Deploy Smart Contract

```bash
python blockchain_setup.py
```

Follow the prompts:
- Select "1" for local network
- Enter private key from Ganache (copy from Ganache UI)
- Contract will be compiled and deployed

#### Step 5: Configure Environment

Update `.env.blockchain` with your settings:

```bash
ETH_PROVIDER_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x... # From deployment output
ETH_PRIVATE_KEY=0x...  # Your private key
IPFS_GATEWAY=http://127.0.0.1:5001
USE_BLOCKCHAIN=true
```

#### Step 6: Run API Server

```bash
python api_server.py
```

---

### Option 2: Testnet Deployment (Polygon Mumbai)

#### Step 1: Get Testnet ETH

1. Create wallet on MetaMask
2. Switch to Polygon Mumbai network
3. Get free testnet MATIC from [Mumbai Faucet](https://faucet.polygon.technology/)

#### Step 2: Get Infura API Key

1. Sign up at [Infura.io](https://infura.io)
2. Create new project
3. Copy API key

#### Step 3: Deploy Contract

```bash
python blockchain_setup.py
```

Select "2" for Polygon Mumbai and enter:
- Your private key
- Update provider URL with your Infura key

#### Step 4: Configure Environment

```bash
ETH_PROVIDER_URL=https://polygon-mumbai.infura.io/v3/YOUR_KEY
CONTRACT_ADDRESS=0x... # From deployment
ETH_PRIVATE_KEY=0x...
IPFS_GATEWAY=https://ipfs.infura.io:5001 # Or local
```

---

### Option 3: Production (Mainnet)

⚠️ **Warning**: Mainnet transactions cost real money!

Use Polygon mainnet for lower gas fees:

```bash
ETH_PROVIDER_URL=https://polygon-mainnet.infura.io/v3/YOUR_KEY
CONTRACT_ADDRESS=0x... # Deploy to mainnet first
ETH_PRIVATE_KEY=0x...  # KEEP THIS SECRET!
```

**Security Best Practices**:
- Never commit private keys to git
- Use hardware wallet for production
- Implement multi-sig for contract ownership
- Regular security audits

---

## Usage Examples

### Python API

```python
from core.blockchain import BlockchainAuditManager
from core.action_executor import ActionExecutor

# Initialize
blockchain = BlockchainAuditManager()
executor = ActionExecutor(blockchain=blockchain)

# Analyze content
analysis = {
    "risk_score": 85,
    "risk_label": "High",
    "action": "Human Review Required",
    "priority": "HIGH",
    "categories": ["Health Misinformation Risk"],
    "reasons": ["High emotional intensity", "Urgent CTAs"]
}

# Execute actions (includes blockchain logging)
result = executor.execute_analysis_actions(
    content_id="post_12345",
    analysis=analysis,
    request_data={"text": "URGENT! Share NOW!", "user_id": "user_789"}
)

print(f"Blockchain TX: {result['tx_hash']}")
print(f"IPFS Hash: {result['ipfs_hash']}")
```

### Verify Audit Integrity

```python
# Retrieve audit record from blockchain
record = blockchain.get_audit_record("post_12345")
print(f"Risk Score: {record['risk_score']}")
print(f"Action: {record['action']}")
print(f"Timestamp: {record['timestamp']}")
print(f"Auditor: {record['auditor']}")

# Verify data hasn't been tampered with
is_valid = blockchain.verify_audit_integrity("post_12345")
print(f"Integrity verified: {is_valid}")
```

### Log Escalation

```python
# When human reviewer makes decision
executor.execute_escalation_actions(
    content_id="post_12345",
    reviewer_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    decision="Approved - False Positive",
    notes="Content is satire, not actual misinformation"
)
```

---

## REST API Integration

### Analyze Content (with blockchain logging)

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "URGENT! Share this NOW!",
    "content_id": "post_001",
    "user_id": "user_123"
  }'
```

Response includes blockchain data:

```json
{
  "content_id": "post_001",
  "risk_score": 75,
  "action": "Human Review Required",
  "blockchain": {
    "tx_hash": "0xabc123...",
    "ipfs_hash": "QmX7Y8Z...",
    "logged": true
  }
}
```

### Get Blockchain Stats

```bash
curl "http://localhost:8000/api/v1/blockchain/stats"
```

```json
{
  "connected": true,
  "network": 80001,
  "account": "0x742d35Cc...",
  "balance": 2.5,
  "contract_deployed": true
}
```

### Verify Audit Record

```bash
curl "http://localhost:8000/api/v1/blockchain/verify/post_001"
```

```json
{
  "content_id": "post_001",
  "verified": true,
  "record": {
    "ipfs_hash": "QmX7Y8Z...",
    "risk_score": 75,
    "action": "Human Review Required",
    "timestamp": 1709856000,
    "auditor": "0x742d35Cc..."
  }
}
```

---

## IPFS Storage

### What Gets Stored on IPFS

Full audit data including:
- Original content text
- Complete analysis results
- Risk scores and categories
- Reasons and explanations
- Timestamp and system version

### Retrieve from IPFS

```python
# Get IPFS hash from blockchain
record = blockchain.get_audit_record("post_12345")
ipfs_hash = record['ipfs_hash']

# Retrieve full data
data = blockchain.retrieve_from_ipfs(ipfs_hash)
print(data['content_text'])
print(data['analysis'])
```

### IPFS Gateways

**Local**: `http://127.0.0.1:5001`  
**Infura**: `https://ipfs.infura.io:5001`  
**Pinata**: `https://api.pinata.cloud`  
**Public**: `https://ipfs.io` (read-only)

---

## Cost Analysis

### Gas Costs (Polygon Mumbai Testnet)

| Operation | Gas Used | Cost (MATIC) | Cost (USD) |
|-----------|----------|--------------|------------|
| Deploy Contract | ~2,000,000 | 0.002 | $0.002 |
| Log Analysis | ~150,000 | 0.00015 | $0.00015 |
| Log Escalation | ~100,000 | 0.0001 | $0.0001 |

**At 1M posts/month**: ~$150 in gas fees (Polygon mainnet)

### IPFS Storage Costs

**Free Options**:
- Local IPFS node (self-hosted)
- Pinata free tier (1GB)

**Paid Options**:
- Pinata: $20/month (100GB)
- Infura: $50/month (5GB)
- Filecoin: ~$0.01/GB/month

---

## Compliance & Regulatory Benefits

### GDPR Compliance

✅ **Right to Audit**: Immutable proof of all moderation decisions  
✅ **Data Integrity**: Cryptographic verification prevents tampering  
✅ **Transparency**: Public blockchain allows independent verification  

### Legal Requirements

✅ **Audit Trail**: Required by EU Digital Services Act  
✅ **Accountability**: Every decision linked to auditor address  
✅ **Dispute Resolution**: Permanent record for appeals  

### Trust & Safety

✅ **Platform Transparency**: Users can verify moderation decisions  
✅ **Regulator Access**: Authorities can audit without platform cooperation  
✅ **Whistleblower Protection**: Immutable evidence of wrongdoing  

---

## Troubleshooting

### "Blockchain not connected"

**Solution**: Check provider URL and network status

```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
print(w3.is_connected())  # Should be True
```

### "IPFS upload failed"

**Solution**: Ensure IPFS daemon is running

```bash
ipfs daemon
# Should see: "Daemon is ready"
```

### "Insufficient funds"

**Solution**: Get testnet ETH from faucet
- Mumbai: https://faucet.polygon.technology/
- Sepolia: https://sepoliafaucet.com/

### "Transaction failed"

**Solution**: Check gas price and account balance

```python
balance = w3.eth.get_balance(account.address)
print(f"Balance: {w3.from_wei(balance, 'ether')} ETH")
```

---

## Development Mode

For testing without blockchain:

```python
from core.blockchain import LocalBlockchainSimulator

# Uses local file-based simulation
blockchain = LocalBlockchainSimulator()

# Same API, no network required
tx_hash = blockchain.log_analysis("post_001", analysis, content)
```

Stores records in `blockchain_sim/audit_chain.json`

---

## Security Considerations

### Private Key Management

❌ **Never** commit private keys to git  
❌ **Never** share private keys  
✅ Use environment variables  
✅ Use hardware wallets for production  
✅ Implement key rotation  

### Smart Contract Security

✅ Access control (only authorized auditors)  
✅ Input validation (risk score 0-100)  
✅ Event logging for transparency  
✅ Upgradeable proxy pattern (future)  

### IPFS Privacy

⚠️ **IPFS is public by default**

For sensitive content:
- Encrypt data before uploading
- Use private IPFS network
- Store only hashes, not content

---

## Roadmap

### Phase 1 (Current)
- ✅ Ethereum integration
- ✅ IPFS storage
- ✅ Basic smart contract
- ✅ Local development mode

### Phase 2 (Q2 2026)
- 🔄 Multi-chain support (Polygon, BSC, Arbitrum)
- 🔄 Filecoin integration for long-term storage
- 🔄 Encrypted IPFS for sensitive content
- 🔄 DAO governance for contract upgrades

### Phase 3 (Q3 2026)
- 📋 Zero-knowledge proofs for privacy
- 📋 Cross-chain audit verification
- 📋 Decentralized moderator network
- 📋 Token incentives for reviewers

---

## Support

**Documentation**: See `README.md` and `API_GUIDE.md`  
**Issues**: GitHub Issues  
**Community**: Discord (coming soon)  

---

## License

MIT License - See LICENSE file

---

**Built with ❤️ for transparent and accountable content moderation**
