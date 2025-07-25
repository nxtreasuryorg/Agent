# Treasury Agent - JSON Contract

This document defines the JSON schemas for the Treasury Agent API.

## 1. Initial Request (`POST /submit_request`)

**Request (multipart/form-data):**
- `excel`: Payment details file
- `json`: Metadata (see below)

```json
{
  "user_id": "user_12345",
  "custody_wallet": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "risk_config": {
    "min_balance_usd": 2000.00,
    "transaction_limits": {
      "single": 25000.00,
      "daily": 50000.00,
      "monthly": 200000.00
    },
    "allowed_currencies": ["USDT", "USDC"]
  },
  "payments": [
    {
      "payment_id": "pay_1",
      "recipient_wallet": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "amount": 1000.00,
      "currency": "USDT",
      "purpose": "Vendor payment"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "proposal_id": "prop_123",
  "status": "processing"
}
```

## 2. Payment Proposal (`GET /get_proposal/{id}`)

**Response (200 OK):**
```json
{
  "proposal_id": "prop_123",
  "status": "ready",
  "proposed_payments": [
    {
      "payment_id": "pay_1",
      "recipient_wallet": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "amount": 1000.00,
      "currency": "USDT",
      "purpose": "Vendor payment",
      "compliance_status": "APPROVED",
      "estimated_gas_fee": 0.001
    }
  ],
  "risk_assessment": {
    "overall_status": "APPROVED",
    "details": "Within limits"
  },
  "simulation_mode": true
}
```
**Note:**
- If you support batch payments, `proposed_payments` can be an array.
- `proposal_id` is critical for matching approvals to proposals.

---

## 3. Approval Submission (`POST /submit_approval`)

**Request:**
```json
{
  "proposal_id": "prop_123",
  "user_id": "user_12345",
  "approval_decision": "approve_all",
  "approved_payments": [
    {
      "payment_id": "pay_1",
      "recipient_wallet": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "amount": 1000.00,
      "currency": "USDT"
    }
  ],
  "rejected_payments": [],
  "partial_modifications": [],
  "comments": "Approving all payments"
}
```

**Response (200 OK):**
```json
{
  "proposal_id": "prop_123",
  "execution_id": "exec_456",
  "status": "processing"
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