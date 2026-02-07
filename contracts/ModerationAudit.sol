// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ModerationAudit
 * @dev Smart contract for immutable content moderation audit trails
 * Stores audit records on-chain with IPFS references for full data
 */
contract ModerationAudit {
    
    struct AuditRecord {
        string contentId;
        string ipfsHash;        // IPFS CID for full data
        uint8 riskScore;        // 0-100
        string action;          // Action taken
        uint256 timestamp;
        address auditor;        // Address that logged the audit
        bytes32 dataHash;       // Hash of data for integrity verification
    }
    
    struct EscalationRecord {
        string contentId;
        address reviewer;
        string decision;
        string notes;
        uint256 timestamp;
    }
    
    // Mappings
    mapping(string => AuditRecord) public auditRecords;
    mapping(string => EscalationRecord[]) public escalations;
    mapping(string => bool) public exists;
    
    // Events
    event AnalysisLogged(
        string indexed contentId,
        string ipfsHash,
        uint8 riskScore,
        uint256 timestamp
    );
    
    event EscalationLogged(
        string indexed contentId,
        address indexed reviewer,
        string decision,
        uint256 timestamp
    );
    
    // Owner for access control
    address public owner;
    mapping(address => bool) public authorizedAuditors;
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }
    
    modifier onlyAuthorized() {
        require(
            msg.sender == owner || authorizedAuditors[msg.sender],
            "Not authorized"
        );
        _;
    }
    
    constructor() {
        owner = msg.sender;
        authorizedAuditors[msg.sender] = true;
    }
    
    /**
     * @dev Add authorized auditor
     */
    function addAuditor(address auditor) external onlyOwner {
        authorizedAuditors[auditor] = true;
    }
    
    /**
     * @dev Remove authorized auditor
     */
    function removeAuditor(address auditor) external onlyOwner {
        authorizedAuditors[auditor] = false;
    }
    
    /**
     * @dev Log content analysis to blockchain
     * @param contentId Unique content identifier
     * @param ipfsHash IPFS CID where full data is stored
     * @param riskScore Risk score (0-100)
     * @param action Action taken
     * @param dataHash SHA-256 hash of data for integrity
     */
    function logAnalysis(
        string memory contentId,
        string memory ipfsHash,
        uint8 riskScore,
        string memory action,
        bytes32 dataHash
    ) external onlyAuthorized {
        require(riskScore <= 100, "Risk score must be 0-100");
        require(!exists[contentId], "Content already audited");
        
        auditRecords[contentId] = AuditRecord({
            contentId: contentId,
            ipfsHash: ipfsHash,
            riskScore: riskScore,
            action: action,
            timestamp: block.timestamp,
            auditor: msg.sender,
            dataHash: dataHash
        });
        
        exists[contentId] = true;
        
        emit AnalysisLogged(contentId, ipfsHash, riskScore, block.timestamp);
    }
    
    /**
     * @dev Log escalation/review decision
     * @param contentId Content identifier
     * @param reviewer Address of reviewer
     * @param decision Review decision
     * @param notes Review notes
     */
    function logEscalation(
        string memory contentId,
        address reviewer,
        string memory decision,
        string memory notes
    ) external onlyAuthorized {
        require(exists[contentId], "Content not found");
        
        escalations[contentId].push(EscalationRecord({
            contentId: contentId,
            reviewer: reviewer,
            decision: decision,
            notes: notes,
            timestamp: block.timestamp
        }));
        
        emit EscalationLogged(contentId, reviewer, decision, block.timestamp);
    }
    
    /**
     * @dev Get audit record for content
     * @param contentId Content identifier
     * @return ipfsHash IPFS CID
     * @return riskScore Risk score
     * @return action Action taken
     * @return timestamp When logged
     * @return auditor Who logged it
     */
    function getAuditRecord(string memory contentId)
        external
        view
        returns (
            string memory ipfsHash,
            uint8 riskScore,
            string memory action,
            uint256 timestamp,
            address auditor
        )
    {
        require(exists[contentId], "Content not found");
        
        AuditRecord memory record = auditRecords[contentId];
        return (
            record.ipfsHash,
            record.riskScore,
            record.action,
            record.timestamp,
            record.auditor
        );
    }
    
    /**
     * @dev Get escalation count for content
     * @param contentId Content identifier
     * @return count Number of escalations
     */
    function getEscalationCount(string memory contentId)
        external
        view
        returns (uint256 count)
    {
        return escalations[contentId].length;
    }
    
    /**
     * @dev Get specific escalation record
     * @param contentId Content identifier
     * @param index Escalation index
     * @return reviewer Reviewer address
     * @return decision Decision made
     * @return notes Review notes
     * @return timestamp When reviewed
     */
    function getEscalation(string memory contentId, uint256 index)
        external
        view
        returns (
            address reviewer,
            string memory decision,
            string memory notes,
            uint256 timestamp
        )
    {
        require(index < escalations[contentId].length, "Invalid index");
        
        EscalationRecord memory record = escalations[contentId][index];
        return (
            record.reviewer,
            record.decision,
            record.notes,
            record.timestamp
        );
    }
    
    /**
     * @dev Verify data integrity
     * @param contentId Content identifier
     * @param dataHash Hash to verify
     * @return bool True if hash matches
     */
    function verifyIntegrity(string memory contentId, bytes32 dataHash)
        external
        view
        returns (bool)
    {
        require(exists[contentId], "Content not found");
        return auditRecords[contentId].dataHash == dataHash;
    }
}
