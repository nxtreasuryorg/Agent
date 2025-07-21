# Flask Server Implementation for Treasury Approval/Payment Workflow

## Overview
This Flask server implements a multi-step, client-backend approval/payment workflow for a treasury automation prototype. It is designed for rapid prototyping, with all state stored in memory and all payment execution simulated for safety.

---

## Architecture & Flow
- **Framework:** Flask (with CORS enabled)
- **State:** All proposals and execution results are stored in Python dictionaries (in-memory, not persisted)
- **Simulation Mode:** All payment executions are simulated; no real funds are moved
- **Integration:** The server is designed to eventually integrate with CrewAI agent logic, but currently simulates proposal and execution logic for demonstration

### Event-Driven Agent Invocation
- **Agent is NOT run at server startup.**
- **Agent is ONLY triggered when the client POSTs Excel + JSON to `/submit_request`.**
- This event-driven design ensures the agent processes each request in response to real client input, not on a schedule or at server boot.
- After the agent processes the request and generates a proposal, the rest of the workflow (proposal review, approval, execution) is handled via API endpoints and in-memory state.
- This matches best practices for agentic API design and is ready for client integration.

### Endpoint Flow
1. **/submit_request** (POST): Accepts an Excel file and a JSON payload. Processes the request (triggers the agent) and returns a payment proposal JSON with a unique `proposal_id`.
2. **/get_proposal/<proposal_id>** (GET): Returns the stored proposal JSON for review.
3. **/submit_approval** (POST): Accepts user approval/partial approval JSON, validates, and simulates execution of only the approved payments. Stores and returns the result.
4. **/execution_result/<proposal_id>** (GET): Returns the execution/simulation result for the given proposal.

### State Management
- **proposals_store:** Dict mapping `proposal_id` to proposal JSON
- **execution_results_store:** Dict mapping `proposal_id` to execution result JSON
- **No files or databases are used**; all data is lost on server restart

### Error Handling
- All endpoints validate input and return clear error messages and HTTP status codes
- Missing or invalid fields, unknown proposal IDs, and internal errors are handled gracefully

### Simulation Mode
- All execution results are clearly marked as simulation
- Transaction IDs are randomly generated UUIDs

### Extending for Production
- Replace in-memory stores with a persistent database (e.g., PostgreSQL, SQLite)
- Integrate real CrewAI agent logic for proposal and execution steps
- Add authentication, authorization, and audit logging
- Implement file storage for Excel uploads if needed
- Harden error handling and input validation

### Limitations
- Not suitable for production as-is (no persistence, no authentication, simulation only)
- All state is lost on server restart
- No concurrency controls for simultaneous requests

---

## How to Run
- Start the server: `python flask_server.py`
- The server will be available at `http://localhost:5001`
- See the API documentation for endpoint details 