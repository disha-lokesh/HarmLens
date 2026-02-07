"""
Database Manager - ACTUAL storage of moderation data
This is what makes it REAL, not just console logs
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os


class ModerationDatabase:
    """Real database for storing all moderation decisions"""
    
    def __init__(self, db_path: str = "harmlens_production.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Content analysis results
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id TEXT UNIQUE NOT NULL,
            user_id TEXT,
            platform TEXT,
            content_text TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_label TEXT NOT NULL,
            categories TEXT,
            action TEXT NOT NULL,
            priority TEXT NOT NULL,
            queue TEXT NOT NULL,
            reasons TEXT,
            child_escalation BOOLEAN,
            processing_time_ms REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
        """)
        
        # Moderation queue - ACTUAL queue system
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS moderation_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id TEXT NOT NULL,
            queue_name TEXT NOT NULL,
            priority TEXT NOT NULL,
            assigned_to TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            reviewer_decision TEXT,
            reviewer_notes TEXT,
            FOREIGN KEY (content_id) REFERENCES content_analysis(content_id)
        )
        """)
        
        # Action log - ACTUAL action tracking
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS action_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            action_result TEXT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error TEXT,
            FOREIGN KEY (content_id) REFERENCES content_analysis(content_id)
        )
        """)
        
        # Webhook delivery log
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS webhook_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id TEXT NOT NULL,
            webhook_url TEXT NOT NULL,
            status_code INTEGER,
            response TEXT,
            delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (content_id) REFERENCES content_analysis(content_id)
        )
        """)
        
        # Escalation tracking - for moderator escalations
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS escalations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id TEXT NOT NULL,
            escalated_by TEXT NOT NULL,
            escalation_reason TEXT NOT NULL,
            escalation_type TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            assigned_to TEXT,
            response_time_estimate TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            responded_at TIMESTAMP,
            resolved_at TIMESTAMP,
            resolution_notes TEXT,
            FOREIGN KEY (content_id) REFERENCES content_analysis(content_id)
        )
        """)
        
        conn.commit()
        conn.close()
    
    def save_analysis(self, content_id: str, analysis: dict, request_data: dict):
        """Store analysis result - THIS IS PERMANENT STORAGE"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO content_analysis 
            (content_id, user_id, platform, content_text, risk_score, risk_label, 
             categories, action, priority, queue, reasons, child_escalation, 
             processing_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content_id,
                request_data.get('user_id'),
                request_data.get('platform'),
                request_data.get('text'),
                analysis['risk_score'],
                analysis['risk_label'],
                json.dumps(analysis['categories']),
                analysis['action'],
                analysis['priority'],
                analysis['queue'],
                json.dumps(analysis['reasons']),
                analysis.get('child_escalation', False),
                analysis.get('processing_time_ms', 0)
            ))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Content already analyzed
            return False
        finally:
            conn.close()
    
    def add_to_queue(self, content_id: str, queue_name: str, priority: str):
        """Add to moderation queue - REAL queue management"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO moderation_queue (content_id, queue_name, priority)
        VALUES (?, ?, ?)
        """, (content_id, queue_name, priority))
        
        conn.commit()
        conn.close()
    
    def get_queue_items(self, queue_name: str = None, status: str = 'pending') -> List[Dict]:
        """Get items from queue - REAL queue retrieval"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if queue_name:
            cursor.execute("""
            SELECT q.*, c.content_text, c.risk_score, c.reasons
            FROM moderation_queue q
            JOIN content_analysis c ON q.content_id = c.content_id
            WHERE q.queue_name = ? AND q.status = ?
            ORDER BY 
                CASE q.priority
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    ELSE 4
                END,
                q.created_at ASC
            """, (queue_name, status))
        else:
            cursor.execute("""
            SELECT q.*, c.content_text, c.risk_score, c.reasons
            FROM moderation_queue q
            JOIN content_analysis c ON q.content_id = c.content_id
            WHERE q.status = ?
            ORDER BY 
                CASE q.priority
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    ELSE 4
                END,
                q.created_at ASC
            """, (status,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_queue_status(self, queue_id: int, status: str, reviewer: str = None, 
                           decision: str = None, notes: str = None):
        """Update queue item - REAL moderator action tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        UPDATE moderation_queue
        SET status = ?, 
            reviewed_at = CURRENT_TIMESTAMP,
            assigned_to = COALESCE(?, assigned_to),
            reviewer_decision = COALESCE(?, reviewer_decision),
            reviewer_notes = COALESCE(?, reviewer_notes)
        WHERE id = ?
        """, (status, reviewer, decision, notes, queue_id))
        
        conn.commit()
        conn.close()
    
    def log_action(self, content_id: str, action_type: str, result: str = None, error: str = None):
        """Log executed action - AUDIT TRAIL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO action_log (content_id, action_type, action_result, error)
        VALUES (?, ?, ?, ?)
        """, (content_id, action_type, result, error))
        
        conn.commit()
        conn.close()
    
    def log_webhook_delivery(self, content_id: str, webhook_url: str, 
                             status_code: int, response: str):
        """Log webhook delivery - REAL webhook tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO webhook_log (content_id, webhook_url, status_code, response)
        VALUES (?, ?, ?, ?)
        """, (content_id, webhook_url, status_code, response))
        
        conn.commit()
        conn.close()
    
    def create_escalation(self, content_id: str, escalated_by: str, reason: str, 
                         escalation_type: str, priority: str) -> int:
        """Create new escalation - for moderator escalations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Determine response time estimate based on priority
        time_estimates = {
            'CRITICAL': '< 1 hour',
            'HIGH': '2-4 hours',
            'MEDIUM': '4-8 hours',
            'LOW': '24-48 hours'
        }
        
        cursor.execute("""
        INSERT INTO escalations 
        (content_id, escalated_by, escalation_reason, escalation_type, priority, response_time_estimate)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (content_id, escalated_by, reason, escalation_type, priority, 
              time_estimates.get(priority, '24-48 hours')))
        
        escalation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return escalation_id
    
    def get_escalations(self, status: str = None, escalated_by: str = None) -> List[Dict]:
        """Get escalations with optional filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
        SELECT e.*, c.content_text, c.risk_score, c.risk_label, c.categories
        FROM escalations e
        LEFT JOIN content_analysis c ON e.content_id = c.content_id
        WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND e.status = ?"
            params.append(status)
        
        if escalated_by:
            query += " AND e.escalated_by = ?"
            params.append(escalated_by)
        
        query += """
        ORDER BY 
            CASE e.priority
                WHEN 'CRITICAL' THEN 1
                WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3
                ELSE 4
            END,
            e.created_at DESC
        """
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_escalation_status(self, escalation_id: int, status: str, 
                                 assigned_to: str = None, resolution_notes: str = None):
        """Update escalation status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        update_fields = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        params = [status]
        
        if assigned_to:
            update_fields.append("assigned_to = ?")
            params.append(assigned_to)
        
        if status == 'responded' and resolution_notes is None:
            update_fields.append("responded_at = CURRENT_TIMESTAMP")
        
        if status == 'resolved':
            update_fields.append("resolved_at = CURRENT_TIMESTAMP")
            if resolution_notes:
                update_fields.append("resolution_notes = ?")
                params.append(resolution_notes)
        
        params.append(escalation_id)
        
        query = f"UPDATE escalations SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Get platform statistics - REAL metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total analyzed
        cursor.execute("SELECT COUNT(*) FROM content_analysis")
        total = cursor.fetchone()[0]
        
        # By risk label
        cursor.execute("""
        SELECT risk_label, COUNT(*) as count
        FROM content_analysis
        GROUP BY risk_label
        """)
        by_risk = dict(cursor.fetchall())
        
        # Pending queue items
        cursor.execute("""
        SELECT COUNT(*) FROM moderation_queue WHERE status = 'pending'
        """)
        pending_count = cursor.fetchone()[0]
        
        # Average processing time
        cursor.execute("SELECT AVG(processing_time_ms) FROM content_analysis")
        avg_time = cursor.fetchone()[0] or 0
        
        # Escalation stats
        cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM escalations
        GROUP BY status
        """)
        escalation_stats = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_analyzed": total,
            "by_risk_level": by_risk,
            "pending_review": pending_count,
            "avg_processing_time_ms": round(avg_time, 2),
            "escalations": escalation_stats
        }
