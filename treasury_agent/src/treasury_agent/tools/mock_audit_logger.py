from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from datetime import datetime
import json
import uuid


class AuditLoggerInput(BaseModel):
    """Input schema for AuditLoggerTool."""
    action: str = Field(..., description="Action to log: 'log_transaction', 'log_decision', 'log_compliance_check', or 'retrieve_logs'")
    event_type: str = Field(..., description="Type of event: 'payment_initiated', 'risk_assessment', 'compliance_check', 'decision_made', etc.")
    details: str = Field(..., description="Detailed information about the event")
    transaction_id: str = Field(default="", description="Related transaction ID if applicable")
    user_id: str = Field(default="system", description="User or system that triggered the event")
    severity: str = Field(default="info", description="Log severity: 'info', 'warning', 'error', 'critical'")


class MockAuditLoggerTool(BaseTool):
    name: str = "Audit Logger Tool"
    description: str = (
        "Log all system actions for compliance and audit purposes. "
        "Creates immutable audit trails for regulatory compliance, risk management, and system monitoring. "
        "Supports transaction logging, decision tracking, compliance checks, and log retrieval."
    )
    args_schema: Type[BaseModel] = AuditLoggerInput
    
    # Mock in-memory storage for testing (in real implementation, this would be a database)
    _audit_logs = []

    def _run(self, action: str, event_type: str, details: str, 
             transaction_id: str = "", user_id: str = "system", severity: str = "info") -> str:
        
        if action == "log_transaction":
            return self._log_transaction(event_type, details, transaction_id, user_id, severity)
        elif action == "log_decision":
            return self._log_decision(event_type, details, transaction_id, user_id, severity)
        elif action == "log_compliance_check":
            return self._log_compliance_check(event_type, details, transaction_id, user_id, severity)
        elif action == "retrieve_logs":
            return self._retrieve_logs(transaction_id, event_type)
        else:
            return f"Unknown action: {action}. Available actions: log_transaction, log_decision, log_compliance_check, retrieve_logs"

    def _log_transaction(self, event_type: str, details: str, transaction_id: str, 
                        user_id: str, severity: str) -> str:
        
        log_entry = self._create_log_entry(event_type, details, transaction_id, user_id, severity)
        log_entry["category"] = "TRANSACTION"
        
        # Add transaction-specific fields
        log_entry["compliance_required"] = True
        log_entry["retention_period"] = "7_years"  # Financial records retention
        
        self._audit_logs.append(log_entry)
        
        result = f"✅ Transaction Audit Log Created:\n"
        result += f"Log ID: {log_entry['log_id']}\n"
        result += f"Event: {event_type}\n"
        result += f"Transaction ID: {transaction_id}\n"
        result += f"Timestamp: {log_entry['timestamp']}\n"
        result += f"Severity: {severity.upper()}\n"
        result += f"Compliance Status: LOGGED\n"
        result += f"Retention: {log_entry['retention_period'].replace('_', ' ')}\n"
        
        # Add regulatory compliance note
        if severity in ["warning", "error", "critical"]:
            result += f"\n⚠️  HIGH PRIORITY: This log entry requires immediate regulatory attention."
        
        return result

    def _log_decision(self, event_type: str, details: str, transaction_id: str, 
                     user_id: str, severity: str) -> str:
        
        log_entry = self._create_log_entry(event_type, details, transaction_id, user_id, severity)
        log_entry["category"] = "DECISION"
        
        # Add decision-specific fields
        log_entry["decision_maker"] = user_id
        log_entry["requires_justification"] = severity in ["warning", "error", "critical"]
        
        self._audit_logs.append(log_entry)
        
        result = f"🧠 Decision Audit Log Created:\n"
        result += f"Log ID: {log_entry['log_id']}\n"
        result += f"Decision Type: {event_type}\n"
        result += f"Decision Maker: {user_id}\n"
        result += f"Timestamp: {log_entry['timestamp']}\n"
        result += f"Severity: {severity.upper()}\n"
        
        if log_entry["requires_justification"]:
            result += f"\n📋 JUSTIFICATION REQUIRED: Decision rationale must be documented."
        
        return result

    def _log_compliance_check(self, event_type: str, details: str, transaction_id: str, 
                             user_id: str, severity: str) -> str:
        
        log_entry = self._create_log_entry(event_type, details, transaction_id, user_id, severity)
        log_entry["category"] = "COMPLIANCE"
        
        # Add compliance-specific fields
        log_entry["regulatory_framework"] = "AML/KYC/OFAC"
        log_entry["compliance_officer_review"] = severity in ["error", "critical"]
        
        self._audit_logs.append(log_entry)
        
        result = f"⚖️  Compliance Audit Log Created:\n"
        result += f"Log ID: {log_entry['log_id']}\n"
        result += f"Compliance Check: {event_type}\n"
        result += f"Regulatory Framework: {log_entry['regulatory_framework']}\n"
        result += f"Timestamp: {log_entry['timestamp']}\n"
        result += f"Severity: {severity.upper()}\n"
        
        if log_entry["compliance_officer_review"]:
            result += f"\n🚨 COMPLIANCE ALERT: Requires immediate compliance officer review."
        
        return result

    def _retrieve_logs(self, transaction_id: str = "", event_type: str = "") -> str:
        
        filtered_logs = self._audit_logs.copy()
        
        if transaction_id:
            filtered_logs = [log for log in filtered_logs if log.get("transaction_id") == transaction_id]
        
        if event_type:
            filtered_logs = [log for log in filtered_logs if log.get("event_type") == event_type]
        
        if not filtered_logs:
            return f"No audit logs found matching criteria (Transaction ID: {transaction_id}, Event Type: {event_type})"
        
        result = f"📊 Audit Log Retrieval Results:\n"
        result += f"Found {len(filtered_logs)} matching entries\n"
        result += f"Search Criteria:\n"
        if transaction_id:
            result += f"  - Transaction ID: {transaction_id}\n"
        if event_type:
            result += f"  - Event Type: {event_type}\n"
        result += f"\nLog Entries:\n\n"
        
        for i, log in enumerate(filtered_logs[-10:], 1):  # Show last 10 entries
            result += f"{i}. {log['category']} - {log['event_type']}\n"
            result += f"   ID: {log['log_id']}\n"
            result += f"   Time: {log['timestamp']}\n"
            result += f"   Severity: {log['severity'].upper()}\n"
            result += f"   User: {log['user_id']}\n"
            if log.get("transaction_id"):
                result += f"   TX ID: {log['transaction_id']}\n"
            result += f"   Details: {log['details'][:100]}{'...' if len(log['details']) > 100 else ''}\n\n"
        
        if len(filtered_logs) > 10:
            result += f"... and {len(filtered_logs) - 10} more entries\n"
        
        return result

    def _create_log_entry(self, event_type: str, details: str, transaction_id: str, 
                         user_id: str, severity: str) -> dict:
        
        return {
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "transaction_id": transaction_id,
            "user_id": user_id,
            "severity": severity,
            "system_version": "treasury_agent_v1.0",
            "ip_address": "192.168.1.100",  # Mock IP
            "session_id": f"session_{uuid.uuid4().hex[:8]}",
            "checksum": f"md5_{uuid.uuid4().hex[:16]}"  # Mock checksum for integrity
        } 