#!/usr/bin/env python3
"""
Test script for Treasury Agent Flask Workflow
Tests the complete 4-step workflow: submit -> review -> approve -> result
"""

import requests
import json
import time
import pandas as pd
from pathlib import Path

# Server configuration
BASE_URL = "http://localhost:5001"
TEST_DATA_DIR = Path("test_data")

def create_dummy_excel():
    """Create a dummy Excel file for testing"""
    data = {
        'Date': ['2024-01-15', '2024-01-15', '2024-01-10', '2024-01-08', '2024-01-05'],
        'Transaction_Type': ['Payment', 'Payment', 'Deposit', 'Payment', 'Payment'],
        'Amount': [150.75, 99.75, 1000.00, 250.00, 75.50],
        'Currency': ['USDT', 'USDT', 'USDT', 'USDT', 'USDT'],
        'Recipient': [
            '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
            '0x1234567890123456789012345678901234567890', 
            'Treasury',
            '0xabcdef1234567890abcdef1234567890abcdef12',
            '0x9876543210987654321098765432109876543210'
        ],
        'Purpose': ['Development services', 'Marketing services', 'Initial funding', 'Consulting fees', 'Software license'],
        'Status': ['Pending', 'Pending', 'Completed', 'Completed', 'Completed']
    }
    
    df = pd.DataFrame(data)
    excel_path = TEST_DATA_DIR / "dummy_financial_data.xlsx"
    df.to_excel(excel_path, index=False)
    print(f"✅ Created Excel file: {excel_path}")
    return excel_path

def test_health_check():
    """Test the health check endpoint"""
    print("\n🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_step1_submit_request():
    """Step 1: Submit request with Excel + JSON"""
    print("\n📝 Step 1: Testing submit_request...")
    
    # Load JSON data
    json_path = TEST_DATA_DIR / "dummy_request.json"
    with open(json_path, 'r') as f:
        json_data = f.read()
    
    # Create Excel file
    excel_path = create_dummy_excel()
    
    # Prepare multipart form data
    files = {
        'excel': ('dummy_financial_data.xlsx', open(excel_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    data = {
        'json': json_data
    }
    
    try:
        response = requests.post(f"{BASE_URL}/submit_request", files=files, data=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and result.get('success'):
            proposal_id = result.get('proposal_id')
            print(f"✅ Step 1 SUCCESS - Proposal ID: {proposal_id}")
            return proposal_id
        else:
            print(f"❌ Step 1 FAILED")
            return None
            
    except Exception as e:
        print(f"❌ Step 1 ERROR: {e}")
        return None
    finally:
        files['excel'][1].close()

def test_step2_get_proposal(proposal_id):
    """Step 2: Get proposal for review"""
    print(f"\n📋 Step 2: Testing get_proposal for {proposal_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/get_proposal/{proposal_id}")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and 'payment_proposals' in result:
            print(f"✅ Step 2 SUCCESS - Found {len(result['payment_proposals'])} payment(s)")
            return result
        else:
            print(f"❌ Step 2 FAILED")
            return None
            
    except Exception as e:
        print(f"❌ Step 2 ERROR: {e}")
        return None

def test_step3_submit_approval(proposal_id, proposal_data):
    """Step 3: Submit approval"""
    print(f"\n✅ Step 3: Testing submit_approval for {proposal_id}...")
    
    # Create approval request (approve all payments)
    approval_data = {
        'proposal_id': proposal_id,
        'approval_decision': 'approve_all',
        'comments': 'Approved via automated test - all payments look good'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/submit_approval", json=approval_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and result.get('success'):
            print(f"✅ Step 3 SUCCESS - Execution: {result.get('execution_status')}")
            return True
        else:
            print(f"❌ Step 3 FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Step 3 ERROR: {e}")
        return False

def test_step4_execution_result(proposal_id):
    """Step 4: Get execution result"""
    print(f"\n📊 Step 4: Testing execution_result for {proposal_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/execution_result/{proposal_id}")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and 'execution_status' in result:
            print(f"✅ Step 4 SUCCESS - Status: {result['execution_status']}")
            print(f"   Executed: {len(result.get('executed_payments', []))}")
            print(f"   Failed: {len(result.get('failed_payments', []))}")
            return True
        else:
            print(f"❌ Step 4 FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Step 4 ERROR: {e}")
        return False

def run_complete_workflow_test():
    """Run the complete 4-step workflow test"""
    print("🚀 Starting Complete Treasury Workflow Test")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("❌ Server not healthy, aborting test")
        return False
    
    # Step 1: Submit request
    proposal_id = test_step1_submit_request()
    if not proposal_id:
        print("❌ Workflow failed at Step 1")
        return False
    
    # Wait a moment for processing
    time.sleep(2)
    
    # Step 2: Get proposal
    proposal_data = test_step2_get_proposal(proposal_id)
    if not proposal_data:
        print("❌ Workflow failed at Step 2")
        return False
    
    # Step 3: Submit approval
    if not test_step3_submit_approval(proposal_id, proposal_data):
        print("❌ Workflow failed at Step 3")
        return False
    
    # Step 4: Get execution result
    if not test_step4_execution_result(proposal_id):
        print("❌ Workflow failed at Step 4")
        return False
    
    print("\n🎉 COMPLETE WORKFLOW TEST PASSED!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    # Create test data directory
    TEST_DATA_DIR.mkdir(exist_ok=True)
    
    # Run the complete test
    success = run_complete_workflow_test()
    
    if success:
        print("\n✅ All tests passed! The Flask workflow is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the server logs for details.")
