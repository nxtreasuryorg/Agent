# Treasury Approval/Payment API Documentation

This document describes the REST API endpoints for the treasury approval/payment workflow implemented in the Flask server.

---

## 1. POST `/submit_request`
**Description:** Submit an Excel file and a JSON payload to initiate a payment proposal.

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `excel`: Excel file (e.g., `.xlsx`)
  - `json`: JSON string (see below)

**JSON Example:**
```json
{
  "user_id": "user_12345",
  "custody_wallet": "0x...",
  "recipient_wallet": "0x...",
  "risk_config": {
    "min_balance_usd": 2000.00,
    "transaction_limits": {
      "single": 25000.00,
      "daily": 50000.00,
      "monthly": 200000.00
    }
  },
  "user_notes": "Urgent payment."
}
```

**Note:**
- Payment details (amount, currency, purpose, etc.) must be provided in the Excel file, not in the JSON payload.

**Response:**
- 200 OK, JSON proposal (see `/get_proposal`)
- 400/500 on error

---

## 2. GET `/get_proposal/<proposal_id>`
**Description:** Retrieve the payment proposal for review.

**Response:**
- 200 OK, JSON proposal
- 404 if not found

**Example Response:**
```json
{
  "proposal_id": "...",
  "user_id": "...",
  "proposed_payments": [
    {
      "recipient_wallet": "...",
      "amount": 1000.00,
      "currency": "USDT",
      "purpose": "Vendor payment",
      "compliance_status": "APPROVED",
      "risk_summary": "Within limits",
      "notes": "Urgent payment."
    }
  ],
  "risk_assessment": {
    "overall_status": "APPROVED",
    "details": "Within limits"
  },
  "audit_id": "...",
  "simulation_mode": true
}
```

---

## 3. POST `/submit_approval`
**Description:** Submit user approval, rejection, or partial approval for a proposal.

**Request:**
- Content-Type: `application/json`
- Body:
```json
{
  "proposal_id": "...",
  "user_id": "...",
  "approved_payments": [ ... ],
  "rejected_payments": [ ... ],
  "partial_modifications": [ ... ],
  "user_notes": "..."
}
```

**Response:**
- 200 OK, JSON execution result (see `/execution_result`)
- 400/404/500 on error

---

## 4. GET `/execution_result/<proposal_id>`
**Description:** Retrieve the execution/simulation result for a proposal.

**Response:**
- 200 OK, JSON execution result
- 404 if not found

**Example Response:**
```json
{
  "proposal_id": "...",
  "execution_status": "SUCCESS",
  "executed_payments": [
    {
      "recipient_wallet": "...",
      "amount": 1000.00,
      "currency": "USDT",
      "purpose": "Vendor payment",
      "transaction_id": "...",
      "status": "SIMULATED",
      "notes": "Simulated execution"
    }
  ],
  "failed_payments": [],
  "audit_id": "...",
  "simulation_mode": true,
  "timestamp": "2024-06-01T12:00:00Z"
}
```

---

## Error Responses
- All endpoints return JSON with an `error` field and appropriate HTTP status code on error.
- Example:
```json
{
  "error": "Proposal not found"
}
```

---

## Additional Endpoints
- `GET /health`: Health check
- `POST /process_request`, `GET /test_usdt_tool`: Legacy/test endpoints (see code) 