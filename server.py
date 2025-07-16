#!/usr/bin/env python3

import sys
import os
from pathlib import Path

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

def main():
    print("🚀 Starting Treasury Agent with Excel Analysis Tool...")
    
    # Treasury request parameters with Excel file reference
    inputs = {
        'treasury_request': 'Send $5,000 USD to Alice in France for services. Current account balance is $25,000, minimum balance requirement is $5,000. Please analyze the financial records in data/financial_records.xlsx to understand our payment patterns and available funds before making recommendations.'
    }
    
    try:
        # Create and run the crew
        crew = TreasuryAgent()
        result = crew.crew().kickoff(inputs=inputs)
        
        print("\n✅ Treasury Agent completed successfully!")
        print(f"📄 Result: {result}")
        
    except Exception as e:
        print(f"❌ Error running Treasury Agent: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 