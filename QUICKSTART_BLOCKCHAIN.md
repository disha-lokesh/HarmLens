# Quick Start: Blockchain Integration

Get HarmLens running with blockchain audit trails in 5 minutes.

## Prerequisites

- Python 3.8+
- Node.js (for IPFS)
- 10 minutes

## Option 1: Local Development (Easiest)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start Local Blockchain

```bash
# Install Ganache
npm install -g ganache

# Start Ganache (gives you 10 test accounts with 100 ETH each)
ganache --deterministic
```

Keep this terminal open.

### Step 3: Start IPFS (Optional but Recommended)

```bash
# Install IPFS
# macOS: brew install ipfs
# Linux: wget https://dist.ipfs.tech/kubo/v0.24.0/kubo_v0.24.0_linux-amd64.tar.gz

# Initialize
ipfs init

# Start daemon
ipfs daemon
```

Keep this terminal open.

### Step 4: Deploy Smart Contract

```bash
python blockchain_setup.py
```

- Select "1" for local network
- Copy a private key from Ganache terminal
- Paste when prompted
- Contract will deploy automatically

You'll see output like:
```
✓ Contract deployed successfully!
✓ Contract address: 0x5FbDB2315678afecb367f032d93F642f64180aa3
✓ Transaction hash: 0xabc123...
```

### Step 5: Configure Environment

```bash
cp .env.example .env
```

Update `.env` with values from deployment:
```bash
ETH_PROVIDER_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
ETH_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
IPFS_GATEWAY=http://127.0.0.1:5001
USE_BLOCKCHAIN=true
```

### Step 6: Start API Server

```bash
python api_server.py
```

Server starts at `http://localhost:8000`

### Step 7: Test It!

```bash
# In a new terminal
python examples/blockchain_example.py
```

You'll see:
- Content analyzed
- Risk scores calculated
- Data stored on IPFS
- Audit logged to blockchain
- Transaction hashes returned

**Done!** 🎉

---

## Option 2: Without Blockchain (Simulation Mode)

If you don't want to set up blockchain:

```bash
# Just run the API server
python api_server.py
```

It will automatically use a local blockchain simulator that:
- Stores records in `blockchain_sim/audit_chain.json`
- Provides same API interface
- No network required
- Perfect for development

---

## Option 3: Testnet (Polygon Mumbai)

For testing on a real blockchain:

### Step 1: Get Testnet Tokens

1. Install MetaMask
2. Switch to Polygon Mumbai network
3. Get free MATIC: https://faucet.polygon.technology/

### Step 2: Get Infura API Key

1. Sign up at https://infura.io
2. Create new project
3. Copy API key

### Step 3: Deploy Contract

```bash
python blockchain_setup.py
```

- Select "2" for Mumbai
- Enter your MetaMask private key
- Update provider URL with Infura key

### Step 4: Configure & Run

Update `.env`:
```bash
ETH_PROVIDER_URL=https://polygon-mumbai.infura.io/v3/YOUR_KEY
CONTRACT_ADDRESS=0x... # from deployment
ETH_PRIVATE_KEY=0x...  # your MetaMask key
```

```bash
python api_server.py
```

---

## Testing the API

### Analyze Content

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "URGENT! Share NOW!",
    "content_id": "test_001"
  }'
```

Response includes blockchain data:
```json
{
  "content_id": "test_001",
  "risk_score": 75,
  "action": "Human Review Required",
  "blockchain": {
    "logged": true,
    "tx_hash": "0xabc123...",
    "ipfs_hash": "QmX7Y8Z..."
  }
}
```

### Get Blockchain Stats

```bash
curl "http://localhost:8000/api/v1/blockchain/stats"
```

### Verify Audit Record

```bash
curl "http://localhost:8000/api/v1/blockchain/verify/test_001"
```

---

## What's Happening Behind the Scenes?

1. **Content Analyzed** → Risk score calculated
2. **Data Stored on IPFS** → Returns hash (QmX7Y8Z...)
3. **Blockchain Transaction** → Smart contract logs audit
4. **Database Updated** → Local copy for fast queries
5. **Webhooks Sent** → Real-time notifications

All moderation decisions are now:
- ✅ Immutable (can't be changed)
- ✅ Transparent (publicly verifiable)
- ✅ Decentralized (stored on IPFS)
- ✅ Compliant (audit-ready)

---

## Troubleshooting

### "Blockchain not connected"

**Check Ganache is running:**
```bash
# Should see: Listening on 127.0.0.1:8545
```

### "IPFS upload failed"

**Check IPFS daemon:**
```bash
ipfs daemon
# Should see: Daemon is ready
```

### "Insufficient funds"

**Check account balance:**
```bash
# In Ganache, each account should have 100 ETH
```

### "Contract not deployed"

**Re-run deployment:**
```bash
python blockchain_setup.py
```

---

## Next Steps

- Read `BLOCKCHAIN_GUIDE.md` for detailed documentation
- Check `API_GUIDE.md` for API reference
- See `examples/blockchain_example.py` for code samples
- Deploy to production (see `PRODUCTION_GUIDE.md`)

---

## Cost Estimate

**Local Development**: FREE  
**Testnet (Mumbai)**: FREE (testnet tokens)  
**Production (Polygon)**: ~$0.00015 per analysis  

At 1M posts/month: ~$150/month in gas fees

---

**Questions?** Check the full guide: `BLOCKCHAIN_GUIDE.md`
