#!/usr/bin/env python3

import sys
import os
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

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

if __name__ == '__main__':
    print("🚀 Starting Flask server for Treasury Agent with USDT Payment Tools...")
    print("📡 Server will be available at http://localhost:5000")
    print("🔗 Endpoints:")
    print("   GET  /health - Health check")
    print("   POST /process_request - Process treasury requests")
    print("   GET  /test_usdt_tool - Test USDT payment tool")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 