# Treasury Agent API Documentation

## Overview

The Treasury Agent API provides a comprehensive 4-step workflow for processing treasury payment requests with USDT payment capabilities. The API enables secure submission, review, approval, and execution of payment proposals through a structured workflow.

**Base URL**: `http://localhost:5001`

**Server**: Flask with CORS enabled
**Port**: 5001
**Host**: 0.0.0.0 (accessible from all interfaces)

## Architecture

The API follows a stateful 4-step workflow:

1. **Submit Request** - Upload Excel file + JSON configuration to generate payment proposals
2. **Review Proposal** - Retrieve and review generated payment proposals
3. **Submit Approval** - Approve, reject, or partially approve payments
4. **Get Execution Result** - Retrieve execution results and transaction details

## Authentication

Currently, no authentication is required. The API uses in-memory storage for proposals and execution results.

## Data Storage

- **Proposals Store**: In-memory storage for payment proposals
- **Execution Results Store**: In-memory storage for execution results
- **Processing Status**: Track async processing status

## API Endpoints

### 1. Health Check

**Endpoint**: `GET /health`

**Description**: Check if the Treasury Agent service is running and healthy.

**Request**: No parameters required

**Response**:
```json
{
  "status": "healthy",
  "message": "Treasury Agent with USDT Payment Tools is running"
}
```

**Status Codes**:
- `200 OK`: Service is healthy

---

### 2. Process Request (Legacy)

**Endpoint**: `POST /process_request`

**Description**: Legacy endpoint for processing treasury requests with USDT payment capabilities.

**Request Body**:
```json
{
  "request": "string - Treasury request description"
}
```

**Response**:
```json
{
  "result": "string - Processing result",
  "status": "success|error"
}
```

**Status Codes**:
- `200 OK`: Request processed successfully
- `400 Bad Request`: Missing request parameter
- `500 Internal Server Error`: Processing error

---

### 3. Test USDT Tool

**Endpoint**: `GET /test_usdt_tool`

**Description**: Test endpoint to verify USDT payment tool functionality.

**Request**: No parameters required

**Response**:
```json
{
  "status": "success",
  "message": "USDT payment tool is functional",
  "test_result": "object - Test execution details"
}
```

**Status Codes**:
- `200 OK`: USDT tool is functional
- `500 Internal Server Error`: Tool test failed

---

### 4. Submit Request (Step 1)

**Endpoint**: `POST /submit_request`

**Description**: Accept Excel file + JSON configuration, process with agent, and return a payment proposal JSON with unique proposal_id.

**Request**: Multipart form data
- **excel** (file): Excel file containing financial data
- **json** (string): JSON configuration string

**JSON Configuration Structure**:
```json
{
  "user_id": "string - User identifier",
  "custody_wallet": "string - Custody wallet address",
  "risk_config": {
    "min_balance_usd": "number - Minimum balance in USD",
    "transaction_limits": {
      "single": "number - Single transaction limit",
      "daily": "number - Daily transaction limit", 
      "monthly": "number - Monthly transaction limit"
    }
  },
  "user_notes": "string - Additional user instructions"
}
```

**Response**:
```json
{
  "success": true,
  "proposal_id": "string - Unique proposal identifier",
  "message": "Proposal generated successfully",
  "next_step": "Get proposal details at GET /get_proposal/{proposal_id}",
  "summary": {
    "total_payments": "number - Total number of payments",
    "total_amount": "number - Total amount across all payments"
  }
}
```

**Status Codes**:
- `200 OK`: Proposal generated successfully
- `400 Bad Request`: Missing or invalid files/JSON
- `500 Internal Server Error`: Processing error

---

### 5. Get Proposal (Step 2)

**Endpoint**: `GET /get_proposal/<proposal_id>`

**Description**: Return the stored proposal JSON for review.

**Path Parameters**:
- **proposal_id** (string): Unique proposal identifier from Step 1

**Response**:
```json
{
  "proposal_id": "string - Proposal identifier",
  "timestamp": "string - ISO timestamp",
  "audit_id": "string - Audit trail identifier",
  "user_request": {
    "user_id": "string",
    "custody_wallet": "string",
    "risk_config": "object",
    "user_notes": "string"
  },
  "agent_analysis": "string - AI agent analysis results",
  "payment_proposals": [
    {
      "payment_id": "string - Unique payment identifier",
      "recipient_wallet": "string - Recipient wallet address",
      "amount": "number - Payment amount",
      "currency": "string - Currency (USDT)",
      "purpose": "string - Payment purpose",
      "priority": "string - Priority level",
      "estimated_gas_fee": "number - Estimated gas fee",
      "status": "string - Payment status",
      "agent_recommendation": "string - AI recommendation"
    }
  ],
  "risk_assessment": {
    "overall_risk": "string - Risk level",
    "total_amount": "number - Total amount",
    "compliance_check": "string - Compliance status"
  },
  "next_step": "Submit approval at POST /submit_approval"
}
```

**Status Codes**:
- `200 OK`: Proposal found and returned
- `404 Not Found`: Proposal not found

---

### 6. Submit Approval (Step 3)

**Endpoint**: `POST /submit_approval`

**Description**: Accept approval/partial approval JSON, validate, and execute (simulate) only the approved payments.

**Request Body**:
```json
{
  "proposal_id": "string - Proposal identifier",
  "approval_decision": "string - approve_all|reject_all|partial",
  "approved_payments": [
    "string - Array of payment_ids to approve (required for partial approval)"
  ],
  "rejected_payments": [
    {
      "payment_id": "string - Payment ID to reject",
      "rejection_reason": "string - Reason for rejection"
    }
  ],
  "comments": "string - Optional approval comments"
}
```

**Approval Decision Options**:
- **approve_all**: Approve all payments in the proposal
- **reject_all**: Reject all payments in the proposal  
- **partial**: Approve only specified payments (requires approved_payments array)

**Response**:
```json
{
  "success": true,
  "execution_status": "string - SUCCESS|PARTIAL_SUCCESS|FAILURE",
  "message": "string - Execution summary",
  "next_step": "Get full results at GET /execution_result/{proposal_id}",
  "summary": {
    "total_executed": "number - Number of executed payments",
    "total_failed": "number - Number of failed payments",
    "total_amount_executed": "number - Total amount executed"
  }
}
```

**Status Codes**:
- `200 OK`: Approval processed and executed
- `400 Bad Request`: Invalid approval data
- `404 Not Found`: Proposal not found
- `500 Internal Server Error`: Execution error

---

### 7. Get Execution Result (Step 4)

**Endpoint**: `GET /execution_result/<proposal_id>`

**Description**: Return the execution/simulation result for the given proposal.

**Path Parameters**:
- **proposal_id** (string): Unique proposal identifier

**Response**:
```json
{
  "proposal_id": "string - Proposal identifier",
  "execution_status": "string - SUCCESS|PARTIAL_SUCCESS|FAILURE",
  "approval_decision": "string - Original approval decision",
  "timestamp": "string - Execution timestamp (ISO format)",
  "audit_id": "string - Audit trail identifier",
  "simulation_mode": "boolean - Whether execution was simulated",
  "user_comments": "string - User approval comments",
  "summary": {
    "total_executed": "number - Number of executed payments",
    "total_failed": "number - Number of failed payments", 
    "total_amount_executed": "number - Total amount executed"
  },
  "executed_payments": [
    {
      "payment_id": "string - Payment identifier",
      "recipient_wallet": "string - Recipient address",
      "amount": "number - Payment amount",
      "currency": "string - Currency",
      "purpose": "string - Payment purpose",
      "transaction_hash": "string - Simulated transaction hash",
      "gas_fee": "number - Gas fee paid",
      "timestamp": "string - Execution timestamp",
      "status": "executed"
    }
  ],
  "failed_payments": [
    {
      "payment_id": "string - Payment identifier",
      "recipient_wallet": "string - Recipient address", 
      "amount": "number - Payment amount",
      "currency": "string - Currency",
      "purpose": "string - Payment purpose",
      "reason": "string - Failure/rejection reason",
      "timestamp": "string - Failure timestamp",
      "status": "failed"
    }
  ]
}
```

**Alternative Responses**:

**Pending Execution** (202 Accepted):
```json
{
  "proposal_id": "string",
  "status": "pending_execution",
  "message": "Proposal exists but has not been executed yet. Submit approval first.",
  "next_step": "Submit approval at POST /submit_approval"
}
```

**Status Codes**:
- `200 OK`: Execution result found and returned
- `202 Accepted`: Proposal exists but not executed yet
- `404 Not Found`: Execution result not found

## Workflow Example

### Complete 4-Step Workflow

```bash
# Step 1: Submit Request
curl -X POST http://localhost:5001/submit_request \
  -F "excel=@financial_data.xlsx" \
  -F "json={\"user_id\":\"test_user\",\"custody_wallet\":\"0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6\",\"risk_config\":{\"min_balance_usd\":2000},\"user_notes\":\"Process vendor payments\"}"

# Response: {"success": true, "proposal_id": "abc123", ...}

# Step 2: Review Proposal  
curl -X GET http://localhost:5001/get_proposal/abc123

# Step 3: Submit Approval
curl -X POST http://localhost:5001/submit_approval \
  -H "Content-Type: application/json" \
  -d '{"proposal_id":"abc123","approval_decision":"approve_all","comments":"Approved"}'

# Step 4: Get Execution Result
curl -X GET http://localhost:5001/execution_result/abc123
```

## Error Handling

### Common Error Responses

**400 Bad Request**:
```json
{
  "error": "string - Error description",
  "success": false
}
```

**404 Not Found**:
```json
{
  "error": "string - Resource not found",
  "proposal_id": "string - Requested ID",
  "available_results": ["array - Available IDs"]
}
```

**500 Internal Server Error**:
```json
{
  "error": "string - Error description", 
  "success": false
}
```

## Data Models

### Payment Structure
```json
{
  "payment_id": "string - Unique identifier",
  "recipient_wallet": "string - Ethereum wallet address",
  "amount": "number - Payment amount (decimal)",
  "currency": "string - Currency code (USDT)",
  "purpose": "string - Payment description",
  "priority": "string - normal|high|low",
  "estimated_gas_fee": "number - Estimated gas cost",
  "status": "string - Payment status",
  "agent_recommendation": "string - AI analysis"
}
```

### Risk Configuration
```json
{
  "min_balance_usd": "number - Minimum balance threshold",
  "transaction_limits": {
    "single": "number - Single transaction limit",
    "daily": "number - Daily limit",
    "monthly": "number - Monthly limit"
  }
}
```

## Excel File Format

The Excel file should contain financial transaction data with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| Date | Date | Transaction date (YYYY-MM-DD) |
| Transaction_Type | String | Type of transaction (Payment, Deposit, etc.) |
| Amount | Number | Transaction amount |
| Currency | String | Currency code (USDT) |
| Recipient | String | Recipient wallet address or identifier |
| Purpose | String | Transaction purpose/description |
| Status | String | Current status (Pending, Completed, etc.) |

### Example Excel Data
```
Date,Transaction_Type,Amount,Currency,Recipient,Purpose,Status
2024-01-15,Payment,150.75,USDT,0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6,Development services,Pending
2024-01-15,Payment,99.75,USDT,0x1234567890123456789012345678901234567890,Marketing services,Pending
```

## Security Considerations

1. **Wallet Addresses**: All wallet addresses are validated for proper Ethereum format
2. **Amount Validation**: Payment amounts are validated for positive values
3. **File Upload**: Excel files are processed securely with filename sanitization
4. **Simulation Mode**: All payments are executed in simulation mode by default
5. **Audit Trail**: All operations include audit_id for tracking

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Monitoring and Logging

The API provides console logging for:
- Request processing status
- Proposal generation
- Approval processing  
- Execution results
- Error conditions

## Testing

Use the provided `test_workflow.py` script to test the complete 4-step workflow:

```bash
python test_workflow.py
```

The test script will:
1. Create dummy Excel and JSON data
2. Test all 4 workflow steps
3. Validate responses and data flow
4. Report success/failure status

## Dependencies

- Flask
- Flask-CORS
- pandas (for Excel processing)
- requests (for testing)
- uuid (for ID generation)
- werkzeug (for file handling)

## Version Information

- **API Version**: 1.0
- **Last Updated**: 2025-01-25
- **Python Version**: 3.x
- **Flask Version**: Latest compatible version
