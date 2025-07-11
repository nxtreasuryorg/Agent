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
    print("🚀 Starting Treasury Agent...")
    
    # Input parameters
    inputs = {
        'topic': 'AI LLMs',
        'current_year': '2025'
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