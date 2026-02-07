# HarmLens Architecture with Blockchain

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HarmLens Platform                            │
│                  Content Moderation with Blockchain                  │
└─────────────────────────────────────────────────────────────────────┘
```

## High-Level Architecture

```
┌──────────────┐
│   Clients    │
│ (Platforms)  │
└──────┬───────┘
       │
       │ HTTP/REST
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         API Layer (FastAPI)                           │
│  • POST /api/v1/analyze                                              │
│  • GET  /api/v1/blockchain/stats                                     │
│  • GET  /api/v1/blockchain/audit/{id}                                │
│  • POST /api/v1/blockchain/escalation                                │
└──────┬───────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      Analysis Engine (Core)                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │  Emotion   │  │    CTA     │  │ Toxicity   │  │  Context   │    │
│  │  Detector  │  │  Detector  │  │  Detector  │  │  Detector  │    │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │
│  ┌────────────┐  ┌────────────┐                                     │
│  │   Child    │  │  Scoring   │                                     │
│  │   Safety   │  │   Engine   │                                     │
│  └────────────┘  └────────────┘                                     │
└──────┬───────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    Action Executor (NEW)                              │
│  • Orchestrates all post-analysis actions                            │
│  • Manages blockchain logging                                        │
│  • Handles IPFS storage                                              │
│  • Triggers webhooks                                                 │
└──────┬───────────────────────────────────────────────────────────────┘
       │
       │ (Parallel Execution)
       │
       ├─────────────────┬─────────────────┬─────────────────┐
       │                 │                 │                 │
       ▼                 ▼                 ▼                 ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   SQLite    │  │ Blockchain  │  │    IPFS     │  │  Webhooks   │
│  Database   │  │  (Ethereum) │  │ (Filecoin)  │  │   (HTTP)    │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
```

## Detailed Component Architecture

### 1. API Layer

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Server                          │
├─────────────────────────────────────────────────────────────┤
│  Endpoints:                                                  │
│  • POST /api/v1/analyze          → Analyze content          │
│  • POST /api/v1/batch            → Batch analysis           │
│  • GET  /api/v1/queue/{name}     → Get queue items          │
│  • POST /api/v1/queue/{id}/review → Review item             │
│  • GET  /api/v1/stats            → Platform stats           │
│                                                              │
│  Blockchain Endpoints (NEW):                                 │
│  • GET  /api/v1/blockchain/stats        → Connection status │
│  • GET  /api/v1/blockchain/audit/{id}   → Get audit record  │
│  • GET  /api/v1/blockchain/verify/{id}  → Verify integrity  │
│  • GET  /api/v1/blockchain/ipfs/{hash}  → Get from IPFS     │
│  • POST /api/v1/blockchain/escalation   → Log escalation    │
└─────────────────────────────────────────────────────────────┘
```

### 2. Analysis Engine

```
┌─────────────────────────────────────────────────────────────┐
│                    Signal Detectors                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Emotion Detector (30% weight)                        │  │
│  │ Model: j-hartmann/emotion-english-distilroberta-base │  │
│  │ Output: emotion_score (0-1)                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ CTA Detector (25% weight)                            │  │
│  │ Method: Rule-based + keywords                        │  │
│  │ Output: cta_score (0-1)                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Toxicity Detector (20% weight)                       │  │
│  │ Model: unitary/toxic-bert                            │  │
│  │ Output: tox_score (0-1)                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Context Detector (15% weight)                        │  │
│  │ Method: Hybrid (keywords + embeddings)               │  │
│  │ Output: context_score (0-1)                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Child Safety Detector (10% weight)                   │  │
│  │ Method: Rule-based guardrail                         │  │
│  │ Output: child_score (0-1), child_flag (bool)        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Scoring Engine                            │
├─────────────────────────────────────────────────────────────┤
│  Formula:                                                    │
│  risk = (0.30 × emotion) + (0.25 × cta) +                  │
│         (0.20 × toxicity) + (0.15 × context) +             │
│         (0.10 × child)                                      │
│                                                              │
│  Override: If child_flag && child_score > 0.6:             │
│    risk = max(risk, 80)                                     │
│                                                              │
│  Output:                                                     │
│  • risk_score (0-100)                                       │
│  • risk_label (Low/Medium/High)                             │
│  • categories (list)                                        │
│  • reasons (list)                                           │
│  • action (string)                                          │
└─────────────────────────────────────────────────────────────┘
```

### 3. Blockchain Integration (NEW)

```
┌─────────────────────────────────────────────────────────────┐
│              Blockchain Audit Manager                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Web3 Connection                                    │    │
│  │ • Provider: Infura/Alchemy/Local                   │    │
│  │ • Network: Ethereum/Polygon/BSC                    │    │
│  │ • Account: From private key                        │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Smart Contract Interface                           │    │
│  │ • Contract: ModerationAudit.sol                    │    │
│  │ • Functions: logAnalysis, logEscalation            │    │
│  │ • Events: AnalysisLogged, EscalationLogged         │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ IPFS Integration                                   │    │
│  │ • Gateway: Local/Infura/Pinata                     │    │
│  │ • Operations: store, retrieve                      │    │
│  │ • Returns: IPFS CID (QmX7Y8Z...)                   │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Cryptographic Hashing                              │    │
│  │ • Algorithm: SHA-256                               │    │
│  │ • Purpose: Data integrity verification             │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4. Data Flow

```
┌─────────────┐
│   Content   │
│  Submitted  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  1. Preprocessing                        │
│     • Clean text                         │
│     • Detect language                    │
│     • Normalize                          │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  2. Signal Extraction                    │
│     • Run all 5 detectors                │
│     • Collect scores                     │
│     • Extract features                   │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  3. Risk Scoring                         │
│     • Weighted combination               │
│     • Apply overrides                    │
│     • Generate categories                │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  4. Explanation Generation               │
│     • Create reasons                     │
│     • Highlight evidence                 │
│     • Build harm pathway                 │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  5. Action Recommendation                │
│     • Determine action                   │
│     • Assign priority                    │
│     • Select queue                       │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  6. Action Execution (NEW)               │
│     ├─→ Store to IPFS                    │
│     │   Returns: QmX7Y8Z...              │
│     │                                     │
│     ├─→ Log to Blockchain                │
│     │   Returns: 0xabc123...             │
│     │                                     │
│     ├─→ Save to Database                 │
│     │   For fast queries                 │
│     │                                     │
│     └─→ Trigger Webhooks                 │
│         Real-time alerts                 │
└─────────────────────────────────────────┘
```

### 5. Storage Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Layer Storage                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: SQLite/PostgreSQL (Fast Queries)                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │ • content_analysis table                           │    │
│  │ • moderation_queue table                           │    │
│  │ • action_log table                                 │    │
│  │ • webhook_log table                                │    │
│  │                                                     │    │
│  │ Purpose: Fast queries, dashboard, queue management │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 2: IPFS (Decentralized Storage) NEW                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │ • Full analysis data                               │    │
│  │ • Original content                                 │    │
│  │ • Complete audit trail                             │    │
│  │                                                     │    │
│  │ Purpose: Decentralized, censorship-resistant       │    │
│  │ Returns: Content-addressed hash (CID)              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 3: Blockchain (Immutable Audit) NEW                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │ • Content ID                                       │    │
│  │ • IPFS hash (pointer to full data)                │    │
│  │ • Risk score                                       │    │
│  │ • Action taken                                     │    │
│  │ • Timestamp                                        │    │
│  │ • Auditor address                                  │    │
│  │ • Data hash (for integrity)                        │    │
│  │                                                     │    │
│  │ Purpose: Immutable, transparent, verifiable        │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6. Smart Contract Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              ModerationAudit.sol (Solidity)                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  State Variables:                                            │
│  • mapping(string => AuditRecord) auditRecords              │
│  • mapping(string => EscalationRecord[]) escalations        │
│  • mapping(address => bool) authorizedAuditors              │
│  • address owner                                             │
│                                                              │
│  Structs:                                                    │
│  • AuditRecord { contentId, ipfsHash, riskScore, ... }      │
│  • EscalationRecord { contentId, reviewer, decision, ... }  │
│                                                              │
│  Functions:                                                  │
│  • logAnalysis(...)           → Write audit record          │
│  • logEscalation(...)         → Write escalation            │
│  • getAuditRecord(...)        → Read audit record           │
│  • verifyIntegrity(...)       → Verify data hash            │
│  • addAuditor(...)            → Add authorized auditor      │
│  • removeAuditor(...)         → Remove auditor              │
│                                                              │
│  Events:                                                     │
│  • AnalysisLogged(contentId, ipfsHash, riskScore, ...)     │
│  • EscalationLogged(contentId, reviewer, decision, ...)    │
│                                                              │
│  Modifiers:                                                  │
│  • onlyOwner                  → Owner-only functions        │
│  • onlyAuthorized             → Auditor-only functions      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Development Environment

```
┌─────────────────────────────────────────────────────────────┐
│                    Local Development                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │    Ganache     │  │  Local IPFS    │  │   SQLite     │ │
│  │  (Blockchain)  │  │    Daemon      │  │  (Database)  │ │
│  │  127.0.0.1:    │  │  127.0.0.1:    │  │   File-      │ │
│  │     8545       │  │     5001       │  │   based      │ │
│  └────────────────┘  └────────────────┘  └──────────────┘ │
│                                                              │
│  Benefits:                                                   │
│  • No cost                                                   │
│  • Instant transactions                                      │
│  • Full control                                              │
│  • Easy debugging                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Production Environment

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Deployment                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │    Polygon     │  │  Pinata IPFS   │  │  PostgreSQL  │ │
│  │   Mainnet      │  │   (Managed)    │  │   (Cloud)    │ │
│  │   (via         │  │                │  │              │ │
│  │   Infura)      │  │                │  │              │ │
│  └────────────────┘  └────────────────┘  └──────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐                    │
│  │   Load         │  │   Monitoring   │                    │
│  │   Balancer     │  │   (Datadog)    │                    │
│  └────────────────┘  └────────────────┘                    │
│                                                              │
│  Benefits:                                                   │
│  • High availability                                         │
│  • Scalable                                                  │
│  • Managed services                                          │
│  • Production-ready                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: API Security                                       │
│  • Authentication (API keys)                                 │
│  • Rate limiting                                             │
│  • CORS configuration                                        │
│  • Input validation                                          │
│                                                              │
│  Layer 2: Smart Contract Security                            │
│  • Access control (onlyOwner, onlyAuthorized)               │
│  • Input validation (risk score 0-100)                      │
│  • Event logging (transparency)                              │
│  • Immutability (records can't be changed)                  │
│                                                              │
│  Layer 3: Private Key Management                             │
│  • Environment variables                                     │
│  • Hardware wallets (production)                             │
│  • Key rotation                                              │
│  • Secrets manager (AWS/GCP)                                 │
│                                                              │
│  Layer 4: Data Security                                      │
│  • Encryption at rest                                        │
│  • Encryption in transit (HTTPS)                             │
│  • IPFS encryption (sensitive data)                          │
│  • Database encryption                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Scalability Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Scaling Strategy                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Horizontal Scaling:                                         │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Load Balancer                                     │    │
│  │       │                                            │    │
│  │       ├─→ API Server 1 ─┐                         │    │
│  │       ├─→ API Server 2 ─┼─→ Shared Database       │    │
│  │       └─→ API Server N ─┘                         │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Vertical Scaling:                                           │
│  • GPU instances for ML models                               │
│  • More RAM for caching                                      │
│  • Faster CPUs for processing                                │
│                                                              │
│  Caching:                                                    │
│  • Redis for frequent queries                                │
│  • Model caching                                             │
│  • IPFS gateway caching                                      │
│                                                              │
│  Async Processing:                                           │
│  • Background tasks for blockchain                           │
│  • Queue-based processing                                    │
│  • Batch operations                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Cost Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Cost Breakdown (1M posts/month)                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Blockchain (Polygon):                                       │
│  • Gas fees: $150/month                                      │
│  • Per post: $0.00015                                        │
│                                                              │
│  IPFS (Pinata):                                              │
│  • Storage: $20/month (100GB)                                │
│  • Per post: $0.00002                                        │
│                                                              │
│  Database (PostgreSQL):                                      │
│  • Hosting: $50/month                                        │
│  • Per post: $0.00005                                        │
│                                                              │
│  Compute (API servers):                                      │
│  • Servers: $200/month                                       │
│  • Per post: $0.0002                                         │
│                                                              │
│  Total: $420/month                                           │
│  Per post: $0.00042                                          │
│                                                              │
│  Compare to ChatGPT API: $0.50/post                          │
│  Savings: 99.9%                                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Application Monitoring:                                     │
│  • API response times                                        │
│  • Error rates                                               │
│  • Request volume                                            │
│  • Queue depths                                              │
│                                                              │
│  Blockchain Monitoring:                                      │
│  • Transaction success rate                                  │
│  • Gas prices                                                │
│  • Confirmation times                                        │
│  • Account balance                                           │
│                                                              │
│  IPFS Monitoring:                                            │
│  • Upload success rate                                       │
│  • Retrieval times                                           │
│  • Storage usage                                             │
│  • Gateway uptime                                            │
│                                                              │
│  Database Monitoring:                                        │
│  • Query performance                                         │
│  • Connection pool                                           │
│  • Storage usage                                             │
│  • Replication lag                                           │
│                                                              │
│  Alerts:                                                     │
│  • High error rate                                           │
│  • Slow response times                                       │
│  • Blockchain transaction failures                           │
│  • Low account balance                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

**Last Updated**: February 2026  
**Version**: 2.0 (with Blockchain)  
**Status**: Production-Ready ✅
