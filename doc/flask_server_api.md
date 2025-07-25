# Treasury Agent API Documentation

This document describes the REST API endpoints for the Treasury Agent workflow implemented in the Flask server.

---

## 1. POST `/submit_request`
**Description:** Submit an Excel file and a JSON payload to initiate a payment proposal.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Required Fields:
  - `excel`: Excel file (`.xlsx`) containing payment details
  - `json`: JSON string with request metadata (see below)

**JSON Payload Example:**
```json
{
  "user_id": "user_12345",
  "custody_wallet": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "recipient_wallet": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "risk_config": {
    "min_balance_usd": 2000.00,
    "transaction_limits": {
      "single": 25000.00,
      "daily": 50000.00,
      "monthly": 200000.00
    }
  },
  "user_notes": "Urgent payment request for vendor services.",
  "payments": [
    {
      "payment_id": "unique_payment_id_1",
      "amount": 1000.00,
      "currency": "USDT",
      "purpose": "Vendor payment",
      "priority": "high"
    }
  ]
}
```

**Note:**
- Payment details can be provided either in the Excel file or in the JSON payload under the `payments` array.
- If both are provided, the Excel file takes precedence.
- All amounts should be in the specified currency.

**Success Response (200 OK):**
```json
{
  "proposal_id": "unique_proposal_id",
  "status": "processing"
}
```

**Error Responses:**
- 400: Bad Request (missing or invalid parameters)
- 500: Internal Server Error

**Example Error Response:**
```json
{
  "error": "Missing required field: excel file"
}
```

---

## 2. GET `/get_proposal/<proposal_id>`
**Description:** Retrieve the payment proposal for review.

**Request:**
- Method: `GET`
- URL Parameters:
  - `proposal_id`: The unique identifier for the proposal (returned from `/submit_request`)

**Success Response (200 OK):**
```json
{
  "proposal_id": "unique_proposal_id",
  "user_id": "user_12345",
  "status": "ready",
  "proposed_payments": [
    {
      "payment_id": "unique_payment_id_1",
      "recipient_wallet": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "amount": 1000.00,
      "currency": "USDT",
      "purpose": "Vendor payment",
      "priority": "high",
      "estimated_gas_fee": 0.001,
      "compliance_status": "APPROVED",
      "risk_summary": "Within configured limits",
      "agent_recommendation": "Approve payment"
    }
  ],
  "risk_assessment": {
    "overall_status": "APPROVED",
    "details": "All payments within configured risk limits",
    "warnings": []
  },
  "audit_id": "unique_audit_id",
  "simulation_mode": true,
  "created_at": "2024-07-24T12:00:00Z",
  "updated_at": "2024-07-24T12:00:30Z"
}
```

**Status Codes:**
- 200: Success
- 202: Processing (not ready yet)
- 404: Proposal not found
- 500: Internal Server Error

**Notes:**
- The `status` field indicates the current processing state: `processing`, `ready`, or `error`
- `simulation_mode` is always `true` in the current implementation (no real transactions)
- `estimated_gas_fee` is provided in the native blockchain token (e.g., ETH)

---

## 3. POST `/submit_approval`
**Description:** Submit user approval, rejection, or partial approval for a proposal.

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
```json
{
  "proposal_id": "unique_proposal_id",
  "user_id": "user_12345",
  "approval_decision": "approve_all",
  "approved_payments": [
    {
      "payment_id": "unique_payment_id_1",
      "recipient_wallet": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "amount": 1000.00,
      "currency": "USDT",
      "purpose": "Vendor payment"
    }
  ],
  "rejected_payments": [],
  "partial_modifications": [],
  "comments": "Approving all payments as requested",
  "timestamp": "2024-07-24T12:05:00Z",
  "approved_by": "user@example.com"
}
```

**Approval Decision Options:**
- `approve_all`: Approve all payments in the proposal
- `approve_selected`: Approve only the payments listed in `approved_payments`
- `reject_all`: Reject all payments in the proposal
- `modify`: Make partial modifications to the proposal

**Success Response (200 OK):**
```json
{
  "proposal_id": "unique_proposal_id",
  "execution_id": "unique_execution_id",
  "status": "processing",
  "message": "Approval received. Processing payments..."
}
```

**Error Responses:**
- 400: Bad Request (invalid input)
- 404: Proposal not found
- 409: Conflict (proposal already processed)
- 500: Internal Server Error

---

## 4. GET `/execution_result/<proposal_id>`
**Description:** Retrieve the execution/simulation result for a proposal.

**Request:**
- Method: `GET`
- URL Parameters:
  - `proposal_id`: The unique identifier for the proposal

**Success Response (200 OK):**
```json
{
  "proposal_id": "unique_proposal_id",
  "execution_id": "unique_execution_id",
  "execution_status": "SUCCESS",
  "executed_payments": [
    {
      "payment_id": "unique_payment_id_1",
      "recipient_wallet": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
      "amount": 1000.00,
      "currency": "USDT",
      "purpose": "Vendor payment",
      "transaction_id": "simulated_tx_12345",
      "status": "SIMULATED_SUCCESS",
      "gas_used": 21000,
      "gas_price_eth": 0.00000005,
      "timestamp": "2024-07-24T12:05:30Z"
    }
  ],
  "failed_payments": [],
  "audit_id": "unique_audit_id",
  "simulation_mode": true,
  "execution_summary": {
    "total_payments": 1,
    "successful_payments": 1,
    "failed_payments": 0,
    "total_amount_usdt": 1000.00,
    "total_gas_fee_eth": 0.00105,
    "start_time": "2024-07-24T12:05:10Z",
    "end_time": "2024-07-24T12:05:30Z"
  }
}
```

**Status Codes:**
- 200: Success
- 202: Execution still in progress
- 404: Proposal or execution not found
- 500: Internal Server Error

**Execution Status Values:**
- `PENDING`: Execution has been queued
- `PROCESSING`: Execution is in progress
- `SUCCESS`: All payments executed successfully
- `PARTIAL_SUCCESS`: Some payments succeeded, some failed
- `FAILED`: All payments failed
- `CANCELLED`: Execution was cancelled by user

## Health Check Endpoint

### GET `/health`
**Description:** Check if the Treasury Agent service is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-07-24T12:00:00Z"
}
```

## Testing Endpoints

### POST `/test_usdt_tool`
**Description:** Test the USDT payment tool functionality (development use only).

**Response:**
```json
{
  "status": "success",
  "message": "USDT Payment Tool is working correctly",
  "tests": {
    "balance_check": {
      "status": "success",
      "balance": "10000.0 USDT"
    },
    "gas_estimation": {
      "status": "success",
      "gas_price": "50 Gwei",
      "estimated_fee": "0.00105 ETH"
    },
    "address_validation": {
      "status": "success",
      "is_valid": true,
      "checksum_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
    }
  }
}
```

## Error Handling

All API endpoints follow a consistent error response format:

```json
{
  "error": "Descriptive error message",
  "code": "ERROR_CODE",
  "details": {
    "field1": "Additional error details",
    "field2": "More specific information"
  },
  "timestamp": "2024-07-24T12:00:00Z"
}
```

**Common Error Codes:**
- `INVALID_INPUT`: Request validation failed
- `NOT_FOUND`: The requested resource was not found
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `RESOURCE_EXISTS`: Resource already exists
- `RATE_LIMITED`: Too many requests
- `SERVICE_ERROR`: Internal server error