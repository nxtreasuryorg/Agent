#!/usr/bin/env python3

import sys
import os
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from werkzeug.utils import secure_filename
from flask import send_file

# Add treasury_agent src directory to Python path
current_dir = Path(__file__).parent
treasury_agent_src = current_dir / "treasury_agent" / "src"
sys.path.insert(0, str(treasury_agent_src))

# Load environment variables from treasury_agent/.env
env_file = current_dir / "treasury_agent" / ".env"
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
    print(f"🔧 Loaded environment variables from {env_file}")

from treasury_agent.crew import TreasuryAgent

app = Flask(__name__)
CORS(app)

# In-memory storage for proposals and execution results
proposals_store = {}
execution_results_store = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Treasury Agent with USDT Payment Tools is running'
    })

@app.route('/process_request', methods=['POST'])
def process_request():
    """Process treasury requests with USDT payment capabilities"""
    try:
        data = request.get_json()
        if not data or 'request' not in data:
            return jsonify({
                'error': 'Missing request parameter'
            }), 400
        
        treasury_request = data['request']
        
        print(f"📝 Processing request: {treasury_request}")
        
        # Create and run the crew
        crew = TreasuryAgent()
        result = crew.crew().kickoff(inputs={'treasury_request': treasury_request})
        
        return jsonify({
            'status': 'success',
            'result': result,
            'message': 'Treasury request processed successfully'
        })
        
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to process treasury request'
        }), 500

@app.route('/test_usdt_tool', methods=['GET'])
def test_usdt_tool():
    """Test endpoint to verify USDT payment tool functionality"""
    try:
        from treasury_agent.tools.treasury_usdt_payment_tool import TreasuryUSDTPaymentTool
        
        tool = TreasuryUSDTPaymentTool()
        
        # Test various functions
        balance_result = tool._check_balance('0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6')
        gas_result = tool._estimate_gas()
        validation_result = tool._validate_address('0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6')
        
        return jsonify({
            'status': 'success',
            'message': 'USDT Payment Tool is working correctly',
            'tests': {
                'balance_check': balance_result,
                'gas_estimation': gas_result,
                'address_validation': validation_result
            }
        })
        
    except Exception as e:
        print(f"❌ Error testing USDT tool: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Failed to test USDT payment tool'
        }), 500

@app.route('/submit_request', methods=['POST'])
def submit_request():
    """Accept Excel file + JSON, process, and return a payment proposal JSON with unique proposal_id."""
    try:
        if 'json' not in request.form or 'excel' not in request.files:
            return jsonify({'error': 'Missing required fields: json and excel'}), 400
        
        # Parse JSON
        import json as pyjson
        try:
            user_json = pyjson.loads(request.form['json'])
        except Exception as e:
            return jsonify({'error': f'Invalid JSON: {e}'}), 400
        
        # Save Excel file temporarily (in memory)
        excel_file = request.files['excel']
        filename = secure_filename(excel_file.filename)
        excel_bytes = excel_file.read()
        # For prototype, we do not persist the file
        
        # Trigger the CrewAI agent logic here
        # For now, we simulate by passing the JSON and filename as context
        # In a real implementation, you would save the file and pass its path
        try:
            crew = TreasuryAgent()
            # You may want to pass both the JSON and the Excel file (or its bytes/path) to the agent
            # For now, we pass the JSON as a string and the filename for context
            agent_inputs = {
                'user_json': user_json,
                'excel_filename': filename,
                'excel_bytes': excel_bytes  # Not used in simulation, but available for real agent
            }
            # The agent should return a proposal dict matching the API contract
            # For now, we simulate the agent's output as before
            # result = crew.crew().kickoff(inputs=agent_inputs)
            # Simulate compliance/risk check
            payment = user_json.get('payment', {})
            risk_config = user_json.get('risk_config', {})
            user_id = user_json.get('user_id', '')
            proposal_id = str(uuid.uuid4())
            audit_id = str(uuid.uuid4())
            compliance_status = 'APPROVED' if payment.get('amount', 0) <= risk_config.get('transaction_limits', {}).get('single', 25000) else 'REJECTED'
            risk_summary = 'Within limits' if compliance_status == 'APPROVED' else 'Exceeds single transaction limit'
            proposal = {
                'proposal_id': proposal_id,
                'user_id': user_id,
                'proposed_payments': [
                    {
                        'recipient_wallet': user_json.get('recipient_wallet', ''),
                        'amount': payment.get('amount', 0),
                        'currency': payment.get('currency', ''),
                        'purpose': payment.get('purpose', ''),
                        'compliance_status': compliance_status,
                        'risk_summary': risk_summary,
                        'notes': user_json.get('user_notes', '')
                    }
                ],
                'risk_assessment': {
                    'overall_status': compliance_status,
                    'details': risk_summary
                },
                'audit_id': audit_id,
                'simulation_mode': True
            }
            proposals_store[proposal_id] = proposal
            return jsonify(proposal)
        except Exception as agent_exc:
            return jsonify({'error': f'Agent error: {agent_exc}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_proposal/<proposal_id>', methods=['GET'])
def get_proposal(proposal_id):
    """Return the stored proposal JSON for review."""
    proposal = proposals_store.get(proposal_id)
    if not proposal:
        return jsonify({'error': 'Proposal not found'}), 404
    return jsonify(proposal)

@app.route('/submit_approval', methods=['POST'])
def submit_approval():
    """Accept approval/partial approval JSON, validate, and execute (simulate) only the approved payments."""
    try:
        data = request.get_json()
        if not data or 'proposal_id' not in data:
            return jsonify({'error': 'Missing proposal_id'}), 400
        proposal_id = data['proposal_id']
        proposal = proposals_store.get(proposal_id)
        if not proposal:
            return jsonify({'error': 'Proposal not found'}), 404
        
        # Validate and simulate execution
        approved_payments = data.get('approved_payments', [])
        rejected_payments = data.get('rejected_payments', [])
        partial_modifications = data.get('partial_modifications', [])
        executed_payments = []
        failed_payments = []
        for p in approved_payments:
            executed_payments.append({
                **p,
                'transaction_id': str(uuid.uuid4()),
                'status': 'SIMULATED',
                'notes': 'Simulated execution'
            })
        for p in partial_modifications:
            executed_payments.append({
                'recipient_wallet': p.get('recipient_wallet', ''),
                'amount': p.get('approved_amount', 0),
                'currency': p.get('currency', ''),
                'purpose': p.get('purpose', ''),
                'transaction_id': str(uuid.uuid4()),
                'status': 'SIMULATED',
                'notes': f"Partial approval. Original: {p.get('original_amount', 0)}. {p.get('user_comment', '')}"
            })
        for p in rejected_payments:
            failed_payments.append({
                **p,
                'reason': p.get('reason', 'Rejected by user')
            })
        execution_status = 'SUCCESS' if executed_payments and not failed_payments else (
            'PARTIAL_SUCCESS' if executed_payments and failed_payments else 'FAILURE')
        result = {
            'proposal_id': proposal_id,
            'execution_status': execution_status,
            'executed_payments': executed_payments,
            'failed_payments': failed_payments,
            'audit_id': proposal.get('audit_id'),
            'simulation_mode': True,
            'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z'
        }
        execution_results_store[proposal_id] = result
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/execution_result/<proposal_id>', methods=['GET'])
def execution_result(proposal_id):
    """Return the execution/simulation result for the given proposal."""
    # Debug: print the current keys in the execution_results_store
    print(f"[DEBUG] execution_results_store keys: {list(execution_results_store.keys())}")
    result = execution_results_store.get(proposal_id)
    if not result:
        print(f"[DEBUG] Execution result not found for proposal_id: {proposal_id}")
        return jsonify({'error': 'Execution result not found'}), 404
    return jsonify(result)

if __name__ == '__main__':
    print("🚀 Starting Flask server for Treasury Agent with USDT Payment Tools...")
    print("📡 Server will be available at http://localhost:5001")
    print("🔗 Endpoints:")
    print("   GET  /health - Health check")
    print("   POST /process_request - Process treasury requests")
    print("   GET  /test_usdt_tool - Test USDT payment tool")
    print("   POST /submit_request - Submit new request (Excel + JSON)")
    print("   GET  /get_proposal/<id> - Get proposal by ID")
    print("   POST /submit_approval - Submit approval/partial approval")
    print("   GET  /execution_result/<id> - Get execution result by ID")
    
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False) 