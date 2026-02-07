"""
Action Executor - ACTUALLY executes moderation actions
This is what makes it production-ready, not just analysis
"""

import requests
from typing import Dict, Optional
from datetime import datetime
from .database import ModerationDatabase
from .blockchain import BlockchainAuditManager, LocalBlockchainSimulator
import os


class ActionExecutor:
    """
    Executes real moderation actions based on analysis
    - Routes to queues
    - Sends webhooks
    - Logs to database
    - Records to blockchain
    """
    
    def __init__(self, 
                 db: ModerationDatabase = None,
                 blockchain: BlockchainAuditManager = None,
                 use_blockchain: bool = True):
        self.db = db or ModerationDatabase()
        
        # Initialize blockchain
        if use_blockchain:
            try:
                self.blockchain = blockchain or BlockchainAuditManager()
                if not self.blockchain.is_connected():
                    print("⚠️  Blockchain not connected, using local simulator")
                    self.blockchain = LocalBlockchainSimulator()
            except Exception as e:
                print(f"⚠️  Blockchain initialization failed: {e}")
                print("Using local simulator for development")
                self.blockchain = LocalBlockchainSimulator()
        else:
            self.blockchain = None
        
        # Webhook configuration
        self.webhooks = {
            'high_risk': os.getenv('WEBHOOK_HIGH_RISK'),
            'child_safety': os.getenv('WEBHOOK_CHILD_SAFETY'),
            'escalation': os.getenv('WEBHOOK_ESCALATION')
        }
    
    def execute_analysis_actions(self, 
                                 content_id: str,
                                 analysis: dict,
                                 request_data: dict) -> Dict:
        """
        Execute all actions for analyzed content
        
        Args:
            content_id: Unique content identifier
            analysis: Analysis result from scoring
            request_data: Original request data
            
        Returns:
            dict with execution results
        """
        results = {
            "content_id": content_id,
            "database_saved": False,
            "queue_added": False,
            "webhook_sent": False,
            "blockchain_logged": False,
            "ipfs_hash": None,
            "tx_hash": None,
            "errors": []
        }
        
        # 1. Save to database
        try:
            saved = self.db.save_analysis(content_id, analysis, request_data)
            results["database_saved"] = saved
            if saved:
                self.db.log_action(content_id, "analysis_saved", "success")
        except Exception as e:
            results["errors"].append(f"Database save failed: {e}")
        
        # 2. Add to moderation queue if needed
        if analysis['priority'] in ['HIGH', 'CRITICAL', 'MEDIUM']:
            try:
                self.db.add_to_queue(
                    content_id,
                    analysis['queue'],
                    analysis['priority']
                )
                results["queue_added"] = True
                self.db.log_action(content_id, "added_to_queue", analysis['queue'])
            except Exception as e:
                results["errors"].append(f"Queue add failed: {e}")
        
        # 3. Send webhook notifications
        webhook_result = self._send_webhooks(content_id, analysis)
        results["webhook_sent"] = webhook_result['sent']
        if webhook_result.get('error'):
            results["errors"].append(webhook_result['error'])
        
        # 4. Log to blockchain with IPFS storage
        if self.blockchain:
            try:
                tx_hash = self.blockchain.log_analysis_to_blockchain(
                    content_id,
                    analysis,
                    request_data.get('text', '')
                )
                
                if tx_hash:
                    results["blockchain_logged"] = True
                    results["tx_hash"] = tx_hash
                    
                    # Get IPFS hash if available
                    if hasattr(self.blockchain, 'store_to_ipfs'):
                        audit_data = {
                            "content_id": content_id,
                            "analysis": analysis,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        ipfs_hash = self.blockchain.store_to_ipfs(audit_data)
                        results["ipfs_hash"] = ipfs_hash
                    
                    self.db.log_action(
                        content_id,
                        "blockchain_logged",
                        f"tx: {tx_hash}"
                    )
            except Exception as e:
                results["errors"].append(f"Blockchain logging failed: {e}")
        
        return results
    
    def execute_escalation_actions(self,
                                   content_id: str,
                                   reviewer_address: str,
                                   decision: str,
                                   notes: str) -> Dict:
        """
        Execute actions for escalation/review
        
        Args:
            content_id: Content identifier
            reviewer_address: Ethereum address of reviewer
            decision: Review decision
            notes: Review notes
            
        Returns:
            dict with execution results
        """
        results = {
            "content_id": content_id,
            "blockchain_logged": False,
            "tx_hash": None,
            "webhook_sent": False,
            "errors": []
        }
        
        # 1. Log to blockchain
        if self.blockchain:
            try:
                tx_hash = self.blockchain.log_escalation_to_blockchain(
                    content_id,
                    reviewer_address,
                    decision,
                    notes
                )
                
                if tx_hash:
                    results["blockchain_logged"] = True
                    results["tx_hash"] = tx_hash
                    self.db.log_action(
                        content_id,
                        "escalation_logged",
                        f"tx: {tx_hash}"
                    )
            except Exception as e:
                results["errors"].append(f"Blockchain logging failed: {e}")
        
        # 2. Send webhook
        webhook_result = self._send_escalation_webhook(
            content_id,
            decision,
            notes
        )
        results["webhook_sent"] = webhook_result['sent']
        
        return results
    
    def _send_webhooks(self, content_id: str, analysis: dict) -> Dict:
        """Send webhook notifications based on priority"""
        result = {"sent": False, "responses": []}
        
        # Determine which webhooks to trigger
        webhooks_to_send = []
        
        if analysis.get('child_escalation'):
            if self.webhooks['child_safety']:
                webhooks_to_send.append(('child_safety', self.webhooks['child_safety']))
        
        if analysis['priority'] in ['HIGH', 'CRITICAL']:
            if self.webhooks['high_risk']:
                webhooks_to_send.append(('high_risk', self.webhooks['high_risk']))
        
        # Send webhooks
        for webhook_type, webhook_url in webhooks_to_send:
            try:
                payload = {
                    "event": webhook_type,
                    "content_id": content_id,
                    "risk_score": analysis['risk_score'],
                    "risk_label": analysis['risk_label'],
                    "action": analysis['action'],
                    "priority": analysis['priority'],
                    "categories": analysis['categories'],
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                response = requests.post(
                    webhook_url,
                    json=payload,
                    timeout=5
                )
                
                result["responses"].append({
                    "type": webhook_type,
                    "status": response.status_code,
                    "success": response.status_code == 200
                })
                
                # Log webhook delivery
                self.db.log_webhook_delivery(
                    content_id,
                    webhook_url,
                    response.status_code,
                    response.text[:500]
                )
                
                result["sent"] = True
                
            except Exception as e:
                result["error"] = f"Webhook {webhook_type} failed: {e}"
                self.db.log_webhook_delivery(
                    content_id,
                    webhook_url,
                    0,
                    str(e)
                )
        
        return result
    
    def _send_escalation_webhook(self, content_id: str, decision: str, notes: str) -> Dict:
        """Send webhook for escalation"""
        result = {"sent": False}
        
        if not self.webhooks['escalation']:
            return result
        
        try:
            payload = {
                "event": "escalation_reviewed",
                "content_id": content_id,
                "decision": decision,
                "notes": notes,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                self.webhooks['escalation'],
                json=payload,
                timeout=5
            )
            
            result["sent"] = response.status_code == 200
            result["status"] = response.status_code
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_queue_items(self, queue_name: str = None) -> list:
        """Get items from moderation queue"""
        return self.db.get_queue_items(queue_name)
    
    def process_queue_item(self, 
                          queue_id: int,
                          reviewer: str,
                          decision: str,
                          notes: str = None) -> Dict:
        """
        Process a queue item (human review)
        
        Args:
            queue_id: Queue item ID
            reviewer: Reviewer identifier
            decision: Review decision
            notes: Optional notes
            
        Returns:
            dict with processing results
        """
        # Update queue status
        self.db.update_queue_status(
            queue_id,
            'reviewed',
            reviewer,
            decision,
            notes
        )
        
        # Log action
        queue_items = self.db.get_queue_items()
        content_id = None
        for item in queue_items:
            if item['id'] == queue_id:
                content_id = item['content_id']
                break
        
        if content_id:
            self.db.log_action(
                content_id,
                'human_review',
                f"Decision: {decision}"
            )
        
        return {
            "queue_id": queue_id,
            "status": "reviewed",
            "decision": decision
        }
    
    def get_blockchain_stats(self) -> Dict:
        """Get blockchain integration statistics"""
        if self.blockchain:
            return self.blockchain.get_blockchain_stats()
        return {"connected": False, "message": "Blockchain not enabled"}
    
    def verify_audit_integrity(self, content_id: str) -> bool:
        """Verify audit record integrity"""
        if self.blockchain and hasattr(self.blockchain, 'verify_audit_integrity'):
            return self.blockchain.verify_audit_integrity(content_id)
        return False
