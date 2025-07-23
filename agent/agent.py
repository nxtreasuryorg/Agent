from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_required, current_user
from .models import User
import requests
import json
from datetime import datetime
import pandas as pd
import io
import tempfile
import os

agent = Blueprint('agent', __name__, template_folder='templates', static_folder='static')

# Treasury Agent Backend URL
TREASURY_AGENT_URL = "http://localhost:5001"

@agent.route('/agent/', methods=['GET', 'POST'])
@login_required
def ai_agent():
    """
    Treasury Agent - Complete 4-step workflow interface
    Step 1: Submit Request (Excel + JSON)
    Step 2: Review Proposal 
    Step 3: Submit Approval
    Step 4: View Execution Results
    """
    # Initialize workflow state
    workflow_state = session.get('treasury_workflow', {
        'step': 1,
        'proposal_id': None,
        'proposal_data': None,
        'execution_result': None,
        'error_message': None
    })
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'submit_request':
            # Step 1: Submit Treasury Request
            result = handle_submit_request(request)
            if result['success']:
                workflow_state.update({
                    'step': 2,
                    'proposal_id': result['proposal_id'],
                    'error_message': None
                })
                flash(f'Treasury request submitted successfully! Proposal ID: {result["proposal_id"]}', 'success')
            else:
                workflow_state['error_message'] = result['error']
                flash(f'Error submitting request: {result["error"]}', 'danger')
        
        elif action == 'review_proposal':
            # Step 2: Get and Review Proposal
            result = handle_review_proposal(workflow_state['proposal_id'])
            if result['success']:
                workflow_state.update({
                    'step': 3,
                    'proposal_data': result['data'],
                    'error_message': None
                })
                flash('Proposal loaded successfully! Please review and approve/reject payments.', 'info')
            else:
                workflow_state['error_message'] = result['error']
                flash(f'Error loading proposal: {result["error"]}', 'danger')
        
        elif action == 'submit_approval':
            # Step 3: Submit Approval Decision
            result = handle_submit_approval(request, workflow_state['proposal_id'])
            if result['success']:
                workflow_state.update({
                    'step': 4,
                    'error_message': None
                })
                flash(f'Approval submitted successfully! Status: {result["execution_status"]}', 'success')
            else:
                workflow_state['error_message'] = result['error']
                flash(f'Error submitting approval: {result["error"]}', 'danger')
        
        elif action == 'view_results':
            # Step 4: View Execution Results
            result = handle_view_results(workflow_state['proposal_id'])
            if result['success']:
                workflow_state.update({
                    'execution_result': result['data'],
                    'error_message': None
                })
                flash('Execution results loaded successfully!', 'success')
            else:
                workflow_state['error_message'] = result['error']
                flash(f'Error loading results: {result["error"]}', 'danger')
        
        elif action == 'reset_workflow':
            # Reset workflow to start over
            workflow_state = {
                'step': 1,
                'proposal_id': None,
                'proposal_data': None,
                'execution_result': None,
                'error_message': None
            }
            flash('Workflow reset. You can start a new treasury request.', 'info')
    
    # Save workflow state to session
    session['treasury_workflow'] = workflow_state
    
    return render_template(
        'agent/ai_agent.html',
        user=current_user if isinstance(current_user._get_current_object(), User) else None,
        workflow_state=workflow_state
    )

def handle_submit_request(request):
    """Step 1: Handle treasury request submission"""
    try:
        # Get form data
        user_id = request.form.get('user_id', current_user.email)
        amount = float(request.form.get('amount', 0))
        currency = request.form.get('currency', 'USDT')
        purpose = request.form.get('purpose', '')
        recipient_wallet = request.form.get('recipient_wallet', '')
        priority = request.form.get('priority', 'normal')
        
        # Get uploaded Excel file
        uploaded_file = request.files.get('excel_file')
        if not uploaded_file or uploaded_file.filename == '':
            return {'success': False, 'error': 'Please upload an Excel file'}
        
        # Validate Excel file
        if not uploaded_file.filename.lower().endswith(('.xlsx', '.xls')):
            return {'success': False, 'error': 'Please upload a valid Excel file (.xlsx or .xls)'}
        
        # Create JSON payload
        json_payload = {
            'user_id': user_id,
            'request_type': 'payment',
            'amount': amount,
            'currency': currency,
            'purpose': purpose,
            'recipient_wallet': recipient_wallet,
            'priority': priority,
            'approval_required': True,
            'timestamp': datetime.now().isoformat(),
            'notes': f'Treasury request submitted via web interface by {user_id}'
        }
        
        # Prepare multipart form data
        files = {
            'excel': (uploaded_file.filename, uploaded_file.stream, uploaded_file.content_type)
        }
        data = {
            'json': json.dumps(json_payload)
        }
        
        # Submit to treasury agent
        response = requests.post(
            f"{TREASURY_AGENT_URL}/submit_request",
            files=files,
            data=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return {
                    'success': True,
                    'proposal_id': result['proposal_id'],
                    'message': result.get('message', 'Request submitted successfully')
                }
            else:
                return {'success': False, 'error': result.get('error', 'Unknown error')}
        else:
            return {'success': False, 'error': f'Server error: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': f'Error submitting request: {str(e)}'}

def handle_review_proposal(proposal_id):
    """Step 2: Handle proposal review"""
    try:
        response = requests.get(
            f"{TREASURY_AGENT_URL}/get_proposal/{proposal_id}",
            timeout=30
        )
        
        if response.status_code == 200:
            proposal_data = response.json()
            return {'success': True, 'data': proposal_data}
        elif response.status_code == 202:
            # Still processing
            return {'success': False, 'error': 'Proposal is still being processed. Please wait and try again.'}
        else:
            return {'success': False, 'error': f'Error loading proposal: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': f'Error loading proposal: {str(e)}'}

def handle_submit_approval(request, proposal_id):
    """Step 3: Handle approval submission"""
    try:
        approval_decision = request.form.get('approval_decision', 'approve_all')
        comments = request.form.get('comments', '')
        
        # Create approval payload
        approval_payload = {
            'proposal_id': proposal_id,
            'approval_decision': approval_decision,
            'comments': comments,
            'timestamp': datetime.now().isoformat(),
            'approved_by': current_user.email
        }
        
        # Handle partial approvals if needed
        if approval_decision == 'partial':
            # Get partial approval data from form
            approved_payments = []
            rejected_payments = []
            
            # Process each payment decision
            payment_decisions = request.form.getlist('payment_decision')
            for i, decision in enumerate(payment_decisions):
                payment_id = request.form.get(f'payment_id_{i}')
                if decision == 'approve':
                    approved_payments.append({'payment_id': payment_id})
                elif decision == 'reject':
                    rejected_payments.append({
                        'payment_id': payment_id,
                        'rejection_reason': request.form.get(f'rejection_reason_{i}', 'Rejected by user')
                    })
            
            approval_payload.update({
                'approved_payments': approved_payments,
                'rejected_payments': rejected_payments
            })
        
        # Submit approval
        response = requests.post(
            f"{TREASURY_AGENT_URL}/submit_approval",
            json=approval_payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return {
                    'success': True,
                    'execution_status': result.get('execution_status'),
                    'message': result.get('message')
                }
            else:
                return {'success': False, 'error': result.get('error', 'Unknown error')}
        else:
            return {'success': False, 'error': f'Server error: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': f'Error submitting approval: {str(e)}'}

def handle_view_results(proposal_id):
    """Step 4: Handle viewing execution results"""
    try:
        response = requests.get(
            f"{TREASURY_AGENT_URL}/execution_result/{proposal_id}",
            timeout=30
        )
        
        if response.status_code == 200:
            result_data = response.json()
            return {'success': True, 'data': result_data}
        elif response.status_code == 202:
            return {'success': False, 'error': 'Execution not completed yet. Please submit approval first.'}
        else:
            return {'success': False, 'error': f'Error loading results: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': f'Error loading results: {str(e)}'}

@agent.route('/agent/test_connection', methods=['POST'])
@login_required
def test_agent_connection():
    """
    Test connection to Treasury Agent backend
    """
    try:
        response = requests.get(
            f"{TREASURY_AGENT_URL}/health",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True, 
                'message': 'Treasury Agent connection successful!',
                'status': result.get('status', 'healthy')
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'Treasury Agent returned status: {response.status_code}'
            })
            
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'message': 'Connection timed out'})
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'message': 'Could not connect to Treasury Agent service'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})