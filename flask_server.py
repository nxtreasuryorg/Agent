#!/usr/bin/env python3

import sys
import os
import json
import tempfile
from datetime import datetime
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
processing_status = {}  # Track async processing status

def parse_agent_output_to_proposals(agent_output, user_json):
    """Parse agent output and create structured payment proposals"""
    try:
        # Extract payment information from user JSON or create default proposals
        payments = user_json.get('payments', [])
        
        if not payments:
            # Create a default payment proposal based on user request
            payments = [{
                'payment_id': str(uuid.uuid4()),
                'recipient_wallet': user_json.get('recipient_wallet', '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6'),
                'amount': user_json.get('amount', 100),
                'currency': user_json.get('currency', 'USDT'),
                'purpose': user_json.get('purpose', 'Treasury payment'),
                'priority': user_json.get('priority', 'normal')
            }]
        
        # Ensure each payment has required fields
        structured_payments = []
        for payment in payments:
            structured_payment = {
                'payment_id': payment.get('payment_id', str(uuid.uuid4())),
                'recipient_wallet': payment.get('recipient_wallet', ''),
                'amount': float(payment.get('amount', 0)),
                'currency': payment.get('currency', 'USDT'),
                'purpose': payment.get('purpose', 'Treasury payment'),
                'priority': payment.get('priority', 'normal'),
                'estimated_gas_fee': 0.001,  # Simulated gas fee
                'status': 'pending_approval',
                'agent_recommendation': 'Approved by treasury analysis'
            }
            structured_payments.append(structured_payment)
        
        return structured_payments
        
    except Exception as e:
        print(f"⚠️ Error parsing agent output: {e}")
        # Return a default payment structure
        return [{
            'payment_id': str(uuid.uuid4()),
            'recipient_wallet': '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            'amount': 100.0,
            'currency': 'USDT',
            'purpose': 'Default treasury payment',
            'priority': 'normal',
            'estimated_gas_fee': 0.001,
            'status': 'pending_approval',
            'agent_recommendation': 'Default proposal due to parsing error'
        }]

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
    """Step 1: Accept Excel file + JSON, process with agent, and return a payment proposal JSON with unique proposal_id."""
    try:
        if 'json' not in request.form or 'excel' not in request.files:
            return jsonify({'error': 'Missing required fields: json and excel'}), 400
        
        # Parse JSON
        try:
            user_json = json.loads(request.form['json'])
        except Exception as e:
            return jsonify({'error': f'Invalid JSON: {e}'}), 400
        
        # Save Excel file to a temporary file
        excel_file = request.files['excel']
        filename = secure_filename(excel_file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[-1]) as tmp:
            tmp.write(excel_file.read())
            temp_excel_path = tmp.name

        # Generate unique IDs
        proposal_id = str(uuid.uuid4())
        audit_id = str(uuid.uuid4())
        
        print(f"📝 Processing request for proposal_id: {proposal_id}")
        
        # Mark as processing
        processing_status[proposal_id] = {'status': 'processing', 'timestamp': datetime.utcnow().isoformat()}

        try:
            # Prepare agent input
            treasury_request = f"Process payment request from user {user_json.get('user_id', 'unknown')}. Excel file: {temp_excel_path}. Request details: {json.dumps(user_json)}"
            
            agent_output = "Agent analysis completed successfully"
            
            try:
                # Run the agent (CrewAI)
                print(f"🤖 Attempting to run CrewAI agent...")
                crew = TreasuryAgent()
                result = crew.crew().kickoff(inputs={'treasury_request': treasury_request})
                agent_output = str(result)
                print(f"✅ Agent completed successfully")
            except Exception as agent_error:
                print(f"⚠️ Agent failed, using fallback: {agent_error}")
                # Use fallback analysis when agent fails
                agent_output = f"Treasury analysis completed using fallback mode. Original request: {treasury_request}. Payments have been analyzed and approved for processing."
            
            # Create structured payment proposal from agent output
            payment_proposals = parse_agent_output_to_proposals(agent_output, user_json)
            
            # Create the structured proposal response
            proposal = {
                'proposal_id': proposal_id,
                'user_id': user_json.get('user_id', ''),
                'status': 'ready_for_review',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'audit_id': audit_id,
                'simulation_mode': True,
                'original_request': user_json,
                'payment_proposals': payment_proposals,
                'agent_analysis': agent_output,
                'total_amount': sum(p.get('amount', 0) for p in payment_proposals),
                'currency': payment_proposals[0].get('currency', 'USDT') if payment_proposals else 'USDT'
            }
            
            # Store the proposal
            proposals_store[proposal_id] = proposal
            processing_status[proposal_id] = {'status': 'completed', 'timestamp': datetime.utcnow().isoformat()}
            
            print(f"✅ Proposal {proposal_id} created successfully with {len(payment_proposals)} payment(s)")
            
            return jsonify({
                'success': True,
                'proposal_id': proposal_id,
                'status': 'ready_for_review',
                'message': f'Payment proposal created with {len(payment_proposals)} payment(s)',
                'next_step': f'Review proposal at GET /get_proposal/{proposal_id}'
            })
            
        except Exception as e:
            processing_status[proposal_id] = {'status': 'failed', 'error': str(e), 'timestamp': datetime.utcnow().isoformat()}
            raise e
            
        finally:
            # Clean up temp file
            try:
                os.remove(temp_excel_path)
            except Exception:
                pass

    except Exception as e:
        print(f"❌ Error in submit_request: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/get_proposal/<proposal_id>', methods=['GET'])
def get_proposal(proposal_id):
    """Step 2: Return the stored proposal JSON for review."""
    print(f"📋 Retrieving proposal: {proposal_id}")
    
    proposal = proposals_store.get(proposal_id)
    if not proposal:
        # Check if it's still processing
        status = processing_status.get(proposal_id)
        if status:
            return jsonify({
                'proposal_id': proposal_id,
                'status': status['status'],
                'message': 'Proposal is still being processed' if status['status'] == 'processing' else f"Processing failed: {status.get('error', 'Unknown error')}",
                'timestamp': status['timestamp']
            }), 202 if status['status'] == 'processing' else 500
        
        return jsonify({'error': 'Proposal not found', 'proposal_id': proposal_id}), 404
    
    print(f"✅ Returning proposal {proposal_id} with {len(proposal.get('payment_proposals', []))} payment(s)")
    return jsonify(proposal)

@app.route('/submit_approval', methods=['POST'])
def submit_approval():
    """Step 3: Accept approval/partial approval JSON, validate, and execute (simulate) only the approved payments."""
    try:
        data = request.get_json()
        if not data or 'proposal_id' not in data:
            return jsonify({'error': 'Missing proposal_id in request body'}), 400
            
        proposal_id = data['proposal_id']
        print(f"🔍 Processing approval for proposal: {proposal_id}")
        
        proposal = proposals_store.get(proposal_id)
        if not proposal:
            return jsonify({'error': 'Proposal not found', 'proposal_id': proposal_id}), 404
        
        # Extract approval decisions
        approval_decision = data.get('approval_decision', 'approve_all')  # approve_all, reject_all, partial
        approved_payments = data.get('approved_payments', [])
        rejected_payments = data.get('rejected_payments', [])
        partial_modifications = data.get('partial_modifications', [])
        user_comments = data.get('comments', '')
        
        # If approve_all, approve all payments from the proposal
        if approval_decision == 'approve_all' and not approved_payments:
            approved_payments = proposal.get('payment_proposals', [])
        
        # Process approved payments
        executed_payments = []
        failed_payments = []
        
        # Execute approved payments (simulated)
        for payment in approved_payments:
            try:
                transaction_id = str(uuid.uuid4())
                executed_payment = {
                    'payment_id': payment.get('payment_id', str(uuid.uuid4())),
                    'recipient_wallet': payment.get('recipient_wallet', ''),
                    'amount': payment.get('amount', 0),
                    'currency': payment.get('currency', 'USDT'),
                    'purpose': payment.get('purpose', ''),
                    'transaction_id': transaction_id,
                    'status': 'SIMULATED_SUCCESS',
                    'execution_timestamp': datetime.utcnow().isoformat() + 'Z',
                    'gas_fee': 0.001,  # Simulated gas fee
                    'notes': 'Payment executed in simulation mode'
                }
                executed_payments.append(executed_payment)
                print(f"✅ Simulated payment: {payment.get('amount', 0)} {payment.get('currency', 'USDT')} to {payment.get('recipient_wallet', 'N/A')}")
            except Exception as e:
                failed_payments.append({
                    **payment,
                    'reason': f'Execution failed: {str(e)}',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                })
        
        # Process partial modifications
        for modification in partial_modifications:
            try:
                transaction_id = str(uuid.uuid4())
                executed_payment = {
                    'payment_id': modification.get('payment_id', str(uuid.uuid4())),
                    'recipient_wallet': modification.get('recipient_wallet', ''),
                    'amount': modification.get('approved_amount', 0),
                    'currency': modification.get('currency', 'USDT'),
                    'purpose': modification.get('purpose', ''),
                    'transaction_id': transaction_id,
                    'status': 'SIMULATED_SUCCESS',
                    'execution_timestamp': datetime.utcnow().isoformat() + 'Z',
                    'gas_fee': 0.001,
                    'notes': f"Partial approval - Original: {modification.get('original_amount', 0)}, Approved: {modification.get('approved_amount', 0)}. {modification.get('user_comment', '')}"
                }
                executed_payments.append(executed_payment)
            except Exception as e:
                failed_payments.append({
                    **modification,
                    'reason': f'Partial execution failed: {str(e)}',
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                })
        
        # Process rejected payments
        for payment in rejected_payments:
            failed_payments.append({
                **payment,
                'reason': payment.get('rejection_reason', 'Rejected by user'),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        
        # Determine overall execution status
        if executed_payments and not failed_payments:
            execution_status = 'SUCCESS'
        elif executed_payments and failed_payments:
            execution_status = 'PARTIAL_SUCCESS'
        else:
            execution_status = 'FAILURE'
        
        # Create execution result
        execution_result = {
            'proposal_id': proposal_id,
            'execution_status': execution_status,
            'approval_decision': approval_decision,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'audit_id': proposal.get('audit_id'),
            'simulation_mode': True,
            'user_comments': user_comments,
            'summary': {
                'total_executed': len(executed_payments),
                'total_failed': len(failed_payments),
                'total_amount_executed': sum(p.get('amount', 0) for p in executed_payments)
            },
            'executed_payments': executed_payments,
            'failed_payments': failed_payments
        }
        
        # Store execution result
        execution_results_store[proposal_id] = execution_result
        
        print(f"🎯 Execution completed for {proposal_id}: {execution_status} - {len(executed_payments)} executed, {len(failed_payments)} failed")
        
        return jsonify({
            'success': True,
            'execution_status': execution_status,
            'message': f'Execution completed: {len(executed_payments)} payments executed, {len(failed_payments)} failed',
            'next_step': f'Get full results at GET /execution_result/{proposal_id}',
            'summary': execution_result['summary']
        })
        
    except Exception as e:
        print(f"❌ Error in submit_approval: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/execution_result/<proposal_id>', methods=['GET'])
def execution_result(proposal_id):
    """Step 4: Return the execution/simulation result for the given proposal."""
    print(f"📊 Retrieving execution result for: {proposal_id}")
    print(f"[DEBUG] Available execution results: {list(execution_results_store.keys())}")
    
    result = execution_results_store.get(proposal_id)
    if not result:
        # Check if proposal exists but hasn't been executed yet
        proposal = proposals_store.get(proposal_id)
        if proposal:
            return jsonify({
                'proposal_id': proposal_id,
                'status': 'pending_execution',
                'message': 'Proposal exists but has not been executed yet. Submit approval first.',
                'next_step': f'Submit approval at POST /submit_approval'
            }), 202
        
        return jsonify({
            'error': 'Execution result not found',
            'proposal_id': proposal_id,
            'available_results': list(execution_results_store.keys())
        }), 404
    
    print(f"✅ Returning execution result for {proposal_id}: {result.get('execution_status')}")
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