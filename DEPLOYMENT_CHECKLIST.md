# Blockchain Deployment Checklist

Use this checklist when deploying HarmLens with blockchain to production.

## Pre-Deployment

### 1. Environment Setup
- [ ] Python 3.8+ installed
- [ ] Node.js installed (for IPFS)
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Environment file created: `cp .env.example .env`

### 2. Blockchain Network Selection
- [ ] Network chosen (Polygon recommended for low fees)
- [ ] Wallet created with sufficient funds
- [ ] Provider URL configured (Infura/Alchemy)
- [ ] Private key securely stored (use secrets manager)

### 3. IPFS Setup
- [ ] IPFS daemon installed
- [ ] IPFS gateway configured
- [ ] OR Pinata/Infura account created
- [ ] API keys configured

### 4. Smart Contract
- [ ] Contract compiled: `python blockchain_setup.py`
- [ ] Contract deployed to testnet first
- [ ] Contract address saved
- [ ] ABI file generated

## Security Checklist

### Private Keys
- [ ] Private keys stored in environment variables
- [ ] Private keys NOT committed to git
- [ ] `.env` added to `.gitignore`
- [ ] Production keys use hardware wallet or KMS
- [ ] Key rotation policy defined

### Smart Contract
- [ ] Contract audited by security expert
- [ ] Access control implemented
- [ ] Owner address secured
- [ ] Multi-sig wallet for contract ownership (recommended)
- [ ] Emergency pause function tested

### API Security
- [ ] API authentication enabled
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] HTTPS enabled (production)
- [ ] API keys rotated regularly

### IPFS Security
- [ ] Sensitive data encrypted before upload
- [ ] Private IPFS network for sensitive content
- [ ] Content pinning strategy defined
- [ ] Backup strategy implemented

## Testing Checklist

### Unit Tests
- [ ] Blockchain integration tests pass
- [ ] IPFS storage tests pass
- [ ] Smart contract functions tested
- [ ] Action executor tests pass

### Integration Tests
- [ ] End-to-end analysis with blockchain logging
- [ ] Audit record retrieval works
- [ ] Integrity verification works
- [ ] Escalation logging works

### Load Tests
- [ ] API handles expected load
- [ ] Blockchain transactions don't bottleneck
- [ ] IPFS uploads don't timeout
- [ ] Database queries optimized

### Network Tests
- [ ] Testnet deployment successful
- [ ] Gas estimation accurate
- [ ] Transaction confirmation times acceptable
- [ ] Network failover works

## Deployment Steps

### 1. Testnet Deployment
- [ ] Deploy to Polygon Mumbai testnet
- [ ] Test all functionality
- [ ] Monitor gas costs
- [ ] Verify audit records
- [ ] Test for 24-48 hours

### 2. Production Deployment
- [ ] Deploy smart contract to mainnet
- [ ] Update `.env` with mainnet config
- [ ] Start IPFS daemon/service
- [ ] Start API server
- [ ] Configure monitoring

### 3. Monitoring Setup
- [ ] Blockchain transaction monitoring
- [ ] Gas price alerts
- [ ] IPFS uptime monitoring
- [ ] API error tracking
- [ ] Database performance monitoring

### 4. Backup & Recovery
- [ ] Database backup automated
- [ ] IPFS content pinned to multiple nodes
- [ ] Smart contract address documented
- [ ] Recovery procedures documented
- [ ] Disaster recovery plan tested

## Post-Deployment

### Verification
- [ ] Test analysis endpoint
- [ ] Verify blockchain logging
- [ ] Check IPFS storage
- [ ] Confirm audit retrieval
- [ ] Test integrity verification

### Documentation
- [ ] API documentation updated
- [ ] Deployment guide written
- [ ] Runbook created
- [ ] Contact information updated
- [ ] Support channels established

### Compliance
- [ ] Audit trail verified
- [ ] GDPR compliance checked
- [ ] Data retention policy implemented
- [ ] Privacy policy updated
- [ ] Terms of service updated

## Monitoring & Maintenance

### Daily
- [ ] Check API health
- [ ] Monitor transaction success rate
- [ ] Review error logs
- [ ] Check IPFS uptime

### Weekly
- [ ] Review gas costs
- [ ] Check blockchain sync status
- [ ] Verify backup integrity
- [ ] Review security alerts

### Monthly
- [ ] Audit smart contract events
- [ ] Review access logs
- [ ] Update dependencies
- [ ] Security patch review
- [ ] Cost analysis

## Cost Monitoring

### Blockchain Costs
- [ ] Gas price tracking
- [ ] Transaction volume monitoring
- [ ] Monthly cost projection
- [ ] Budget alerts configured

### IPFS Costs
- [ ] Storage usage tracking
- [ ] Bandwidth monitoring
- [ ] Pinning service costs
- [ ] Optimization opportunities

### Infrastructure Costs
- [ ] Server costs
- [ ] Database costs
- [ ] API gateway costs
- [ ] Total cost of ownership

## Scaling Checklist

### Performance
- [ ] Database indexed properly
- [ ] API response times < 500ms
- [ ] Blockchain transactions batched if needed
- [ ] IPFS uploads optimized
- [ ] Caching implemented

### Capacity
- [ ] Server resources adequate
- [ ] Database size projected
- [ ] IPFS storage capacity planned
- [ ] Network bandwidth sufficient

### Reliability
- [ ] Load balancer configured
- [ ] Auto-scaling enabled
- [ ] Failover tested
- [ ] Backup systems ready
- [ ] SLA defined

## Emergency Procedures

### Blockchain Issues
- [ ] Fallback to simulator mode documented
- [ ] Transaction stuck procedure
- [ ] Gas price spike handling
- [ ] Network congestion plan

### IPFS Issues
- [ ] Fallback storage configured
- [ ] Content recovery procedure
- [ ] Gateway failover plan
- [ ] Pinning service backup

### API Issues
- [ ] Health check endpoint
- [ ] Circuit breaker configured
- [ ] Graceful degradation plan
- [ ] Incident response plan

## Compliance & Legal

### Regulatory
- [ ] GDPR compliance verified
- [ ] Data protection impact assessment
- [ ] Privacy by design implemented
- [ ] Right to erasure handled
- [ ] Data portability supported

### Audit Trail
- [ ] All decisions logged
- [ ] Audit records immutable
- [ ] Verification process documented
- [ ] Retention policy defined
- [ ] Access controls implemented

### Legal
- [ ] Terms of service reviewed
- [ ] Privacy policy updated
- [ ] Data processing agreement
- [ ] Liability limitations clear
- [ ] Jurisdiction defined

## Sign-Off

### Technical Lead
- [ ] Architecture reviewed
- [ ] Security approved
- [ ] Performance validated
- [ ] Documentation complete

### Security Team
- [ ] Penetration testing complete
- [ ] Vulnerability scan passed
- [ ] Access controls verified
- [ ] Incident response ready

### Compliance Team
- [ ] Regulatory requirements met
- [ ] Audit trail verified
- [ ] Privacy controls approved
- [ ] Legal review complete

### Operations Team
- [ ] Monitoring configured
- [ ] Runbooks ready
- [ ] On-call schedule set
- [ ] Escalation path defined

---

## Quick Reference

### Production Environment Variables
```bash
ETH_PROVIDER_URL=https://polygon-mainnet.infura.io/v3/YOUR_KEY
CONTRACT_ADDRESS=0x...
ETH_PRIVATE_KEY=0x... # KEEP SECRET!
IPFS_GATEWAY=https://api.pinata.cloud
USE_BLOCKCHAIN=true
```

### Start Production
```bash
# Start IPFS
ipfs daemon &

# Start API server
python api_server.py
```

### Health Check
```bash
curl http://localhost:8000/api/v1/blockchain/stats
```

### Emergency Contacts
- Technical Lead: [contact]
- Security Team: [contact]
- On-Call: [contact]

---

**Last Updated**: [Date]  
**Reviewed By**: [Name]  
**Next Review**: [Date]
