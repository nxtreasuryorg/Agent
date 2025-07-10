#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_cors import CORS
from nxtreasury_agent import NxtreasuryAgent
import logging
import traceback
from datetime import datetime

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

nxtreasury_agent = None

def get_agent():
    global nxtreasury_agent
    if nxtreasury_agent is None:
        logger.info("Initializing Agent...")
        nxtreasury_agent = NxtreasuryAgent()
        logger.info("Agent initialized successfully")
    return nxtreasury_agent

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Basic Chat Agent API',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0-basic'
    })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Request must be JSON',
                'status': 'error'
            }), 400
        
        data = request.get_json()
        message = data.get('message')
        
        if not message:
            return jsonify({
                'error': 'Missing message field',
                'status': 'error'
            }), 400
        
        agent = get_agent()
        response = agent.chat(message)
        
        return jsonify({
            'status': 'success',
            'user_message': message,
            'agent_response': response,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'status': 'error',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error',
        'available_endpoints': [
            'GET /health',
            'POST /chat'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500

def main():
    print("🚀 Starting Basic Chat Agent API Server")
    print("="*50)
    
    try:
        get_agent()
        
        print("📡 Available Endpoints:")
        print("   GET  /health  - Health check")
        print("   POST /chat    - Chat with agent")
        print()
        print("🌐 Server starting on http://localhost:5000")
        print("📖 Example request:")
        print("""
   curl -X POST http://localhost:5000/chat \\
     -H "Content-Type: application/json" \\
     -d '{"message": "Hello, how are you?"}'
        """)
        
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        print(f"❌ Server startup failed: {str(e)}")

if __name__ == "__main__":
    main() 