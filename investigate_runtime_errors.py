#!/usr/bin/env python3

import sys
import os
import json
import traceback
from pathlib import Path

# Add treasury_agent src directory to Python path
current_dir = Path(__file__).parent
treasury_agent_src = current_dir / "treasury_agent" / "src"
sys.path.insert(0, str(treasury_agent_src))

def investigate_runtime_environment():
    """Investigate potential runtime issues that might cause intermittent failures."""
    print("🔍 RUNTIME ENVIRONMENT INVESTIGATION")
    print("=" * 60)
    
    # Check Python environment
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path[:3]}...")  # Show first few paths
    
    # Check memory and resource constraints
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"Available memory: {memory.available / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB")
        print(f"Memory usage: {memory.percent}%")
    except ImportError:
        print("psutil not available - cannot check memory usage")
    
    # Check import paths and potential conflicts
    print(f"\n📦 CHECKING IMPORTS AND DEPENDENCIES")
    critical_imports = [
        'crewai.tools',
        'pydantic',
        'web3',
        'requests',
        'json',
        'datetime',
        'typing'
    ]
    
    for module in critical_imports:
        try:
            __import__(module)
            print(f"✅ {module}: Available")
        except ImportError as e:
            print(f"❌ {module}: MISSING - {e}")
    
    # Test actual CrewAI integration
    print(f"\n🤖 TESTING CREWAI INTEGRATION")
    try:
        from crewai.tools import BaseTool
        from treasury_agent.tools.treasury_risk_tools import TreasuryRiskTools
        
        # Test if the tool can be instantiated the way CrewAI does it
        risk_tool = TreasuryRiskTools()
        print(f"✅ Tool instantiation: SUCCESS")
        print(f"   Tool name: {risk_tool.name}")
        print(f"   Tool description length: {len(risk_tool.description)} chars")
        print(f"   Args schema: {risk_tool.args_schema.__name__}")
        
        # Test BaseTool methods that CrewAI might use
        if hasattr(risk_tool, 'run'):
            print(f"✅ Tool.run method: Available")
        if hasattr(risk_tool, '_run'):
            print(f"✅ Tool._run method: Available")
        if hasattr(risk_tool, 'args_schema'):
            print(f"✅ Tool.args_schema: Available")
            
    except Exception as e:
        print(f"❌ CrewAI integration test failed: {e}")
        traceback.print_exc()
    
    # Test potential input format issues
    print(f"\n📝 TESTING POTENTIAL INPUT FORMAT ISSUES")
    
    # Test with actual CrewAI-style input formats
    test_inputs = [
        # How CrewAI might pass arguments
        {
            "name": "CrewAI Dict Format",
            "input": {
                "action": "assess_risk",
                "amount": 1000.0,
                "currency": "USD",
                "user_id": "test_user"
            }
        },
        
        # With string numbers (common in web/JSON)
        {
            "name": "String Numbers",
            "input": {
                "action": "assess_risk",
                "amount": "1000.0",
                "currency": "USD",
                "user_id": "test_user"
            }
        },
        
        # With nested complex data
        {
            "name": "Complex Nested Input",
            "input": {
                "action": "assess_risk",
                "amount": 5000.0,
                "currency": "USD",
                "user_id": "test_user",
                "risk_config": {
                    "min_balance_usd": "2000.0",  # String number
                    "transaction_limits": {
                        "daily": "10000.0",
                        "monthly": "50000.0",
                        "single": "5000.0"
                    }
                }
            }
        }
    ]
    
    risk_tool = TreasuryRiskTools()
    
    for test in test_inputs:
        try:
            print(f"Testing {test['name']}...")
            
            # Try different ways CrewAI might call the tool
            # Method 1: Direct _run call
            result1 = risk_tool._run(**test['input'])
            print(f"  ✅ Direct _run: OK")
            
            # Method 2: Using the run method if available
            if hasattr(risk_tool, 'run'):
                try:
                    result2 = risk_tool.run(test['input'])
                    print(f"  ✅ run() method: OK")
                except Exception as e:
                    print(f"  ⚠️  run() method failed: {e}")
            
        except Exception as e:
            print(f"  ❌ {test['name']} failed: {e}")
            if "TypeError" in str(e) or "ValueError" in str(e):
                print(f"     This could cause intermittent failures!")
                traceback.print_exc()
    
    # Check for potential threading/async issues
    print(f"\n🔄 TESTING THREADING/ASYNC SCENARIOS")
    try:
        import threading
        import time
        
        errors = []
        results = []
        
        def worker_test(worker_id):
            try:
                tool = TreasuryRiskTools()
                result = tool._run(
                    action="assess_risk",
                    amount=1000.0 + worker_id,  # Slightly different amounts
                    currency="USD",
                    user_id=f"worker_{worker_id}"
                )
                results.append(f"Worker {worker_id}: SUCCESS")
                time.sleep(0.1)  # Simulate some processing time
            except Exception as e:
                errors.append(f"Worker {worker_id}: {str(e)}")
        
        # Create multiple threads
        threads = []
        for i in range(3):
            t = threading.Thread(target=worker_test, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        print(f"  Threading results: {len(results)} success, {len(errors)} errors")
        if errors:
            print(f"  Threading errors: {errors}")
            
    except Exception as e:
        print(f"  Threading test failed: {e}")
    
    # Check environment variables that might affect behavior
    print(f"\n🌍 ENVIRONMENT VARIABLES")
    env_vars = ['INFURA_API_KEY', 'PYTHONPATH', 'PATH']
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        if var == 'INFURA_API_KEY' and value != 'Not set':
            print(f"  {var}: {'*' * 10} (hidden)")
        else:
            print(f"  {var}: {value}")
    
    print(f"\n💡 RECOMMENDATIONS")
    print("If intermittent errors are still occurring:")
    print("1. Check the actual error messages when they happen")
    print("2. Look for memory constraints during peak usage")
    print("3. Verify all dependencies are properly installed")
    print("4. Check if errors happen with specific input patterns")
    print("5. Monitor concurrent tool usage in production")

def simulate_crew_environment():
    """Simulate how CrewAI actually calls the risk tools."""
    print(f"\n🎭 SIMULATING CREW ENVIRONMENT")
    print("=" * 60)
    
    try:
        from treasury_agent.crew import TreasuryAgent
        from treasury_agent.tools.treasury_risk_tools import TreasuryRiskTools
        
        # Test how the tool is configured in the crew
        crew_agent = TreasuryAgent()
        crew = crew_agent.crew()
        
        print(f"Crew agents: {len(crew.agents)}")
        
        # Find the risk assessor agent
        risk_assessor = None
        for agent in crew.agents:
            if hasattr(agent, 'role') and 'risk' in agent.role.lower():
                risk_assessor = agent
                break
        
        if risk_assessor:
            print(f"✅ Found risk assessor agent")
            print(f"   Tools: {len(risk_assessor.tools)}")
            
            # Find the risk tool
            risk_tool = None
            for tool in risk_assessor.tools:
                if isinstance(tool, TreasuryRiskTools):
                    risk_tool = tool
                    break
            
            if risk_tool:
                print(f"✅ Found risk tool in agent")
                
                # Test the tool as it would be called by the agent
                test_result = risk_tool._run(
                    action="assess_risk",
                    amount=1000.0,
                    currency="USD",
                    user_id="crew_test"
                )
                print(f"✅ Crew context test successful")
            else:
                print(f"❌ Risk tool not found in agent tools")
        else:
            print(f"❌ Risk assessor agent not found")
            
    except Exception as e:
        print(f"❌ Crew environment simulation failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    investigate_runtime_environment()
    simulate_crew_environment()
    print(f"\n🎯 Investigation complete. Check output for potential issues.")
