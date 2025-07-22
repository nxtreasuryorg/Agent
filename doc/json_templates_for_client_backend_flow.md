# JSON Templates for Client-Backend Treasury Approval Flow

This document defines the JSON contract for each step in the treasury payment approval workflow. Use these templates for both backend and client development to ensure consistent, reliable communication.

---

## 1. Client → Backend: Initial Request

**Purpose:**
User uploads an Excel file and a JSON describing the user and risk configuration.

**JSON Template:**
```json
{
  "user_id": "string",
  "custody_wallet": "string",  // e.g., Ethereum address
  "recipient_wallet": "string",
  "risk_config": {
    "min_balance_usd": 2000.00,
    "transaction_limits": {
      "single": 25000.00,
      "daily": 50000.00,
      "monthly": 200000.00
    }
  },
  "user_notes": "string (optional)"
}
```
**Note:**
- Payment details (amount, currency, purpose, etc.) must be provided in the Excel file, not in the JSON payload.
- The Excel file should be sent as a multipart/form-data upload, with the JSON as a separate field or file.

---

## 2. Backend → Client: Payment Proposal

**Purpose:**
Backend returns a payment proposal for user review/approval.

**JSON Template:**
```json
{
  "proposal_id": "string",  // Unique ID for this proposal
  "user_id": "string",
  "proposed_payments": [
    {
      "recipient_wallet": "string",
      "amount": 1000.00,
      "currency": "USDT",
      "purpose": "string",
      "compliance_status": "APPROVED | REQUIRES_REVIEW | REJECTED",
      "risk_summary": "string",
      "notes": "string (optional)"
    }
    // ... more payments if batch
  ],
  "risk_assessment": {
    "overall_status": "APPROVED | REQUIRES_REVIEW | REJECTED",
    "details": "string"
  },
  "audit_id": "string",  // For traceability
  "simulation_mode": true
}
```
**Note:**
- If you support batch payments, `proposed_payments` can be an array.
- `proposal_id` is critical for matching approvals to proposals.

---

## 3. Client → Backend: User Approval/Modification

**Purpose:**
User reviews the proposal and submits approval, rejection, or partial approval for each payment.

**JSON Template:**
```json
{
  "proposal_id": "string",
  "user_id": "string",
  "approved_payments": [
    {
      "recipient_wallet": "string",
      "amount": 1000.00,
      "currency": "USDT",
      "purpose": "string"
    }
    // ... more if batch
  ],
  "rejected_payments": [
    {
      "recipient_wallet": "string",
      "amount": 500.00,
      "currency": "USDT",
      "purpose": "string",
      "reason": "string (optional)"
    }
    // ... more if batch
  ],
  "partial_modifications": [
    {
      "recipient_wallet": "string",
      "original_amount": 1000.00,
      "approved_amount": 800.00,
      "currency": "USDT",
      "purpose": "string",
      "user_comment": "string (optional)"
    }
    // ... more if batch
  ],
  "user_notes": "string (optional)"
}
```
**Note:**
- You can omit `rejected_payments` or `partial_modifications` if not used.
- This structure allows for full, partial, or no approval.

---

## 4. Backend → Client: Execution Result

**Purpose:**
Backend returns the execution/simulation result for the proposal.

**JSON Template:**
```json
{
  "proposal_id": "string",
  "execution_status": "SUCCESS | PARTIAL_SUCCESS | FAILURE",
  "executed_payments": [
    {
      "recipient_wallet": "string",
      "amount": 800.00,
      "currency": "USDT",
      "purpose": "string",
      "transaction_id": "string (simulated or real)",
      "status": "EXECUTED | SIMULATED | FAILED",
      "notes": "string (optional)"
    }
    // ... more if batch
  ],
  "failed_payments": [
    {
      "recipient_wallet": "string",
      "amount": 200.00,
      "currency": "USDT",
      "purpose": "string",
      "reason": "string"
    }
    // ... more if batch
  ],
  "audit_id": "string",
  "simulation_mode": true,
  "timestamp": "2024-06-01T12:00:00Z"
}
```
**Note:**
- `transaction_id` can be a simulated value in prototype mode.
- `audit_id` links to the audit trail for compliance.

---

## General Recommendations
- Always include a unique `proposal_id` and/or `audit_id` for traceability.
- Use clear status fields (`APPROVED`, `REJECTED`, etc.) for both machine and human readability.
- Document these templates for your client/frontend team and keep them versioned.
- Consider using JSON Schema or Pydantic models to enforce these structures on both backend and frontend. 

---

## Error Responses
- All endpoints return JSON with an `error` field and appropriate HTTP status code on error.
- Example:
```json
{
  "error": "Proposal not found"
}
``` 