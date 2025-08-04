#!/usr/bin/env python3

import sys
import os
import traceback
import time
import json
from pathlib import Path

# Add treasury_agent src directory to Python path
current_dir = Path(__file__).parent
treasury_agent_src = current_dir / "treasury_agent" / "src"
sys.path.insert(0, str(treasury_agent_src))

def run_stress_test():
    """Run stress tests to identify intermittent issues with risk tools."""
    print("🔍 COMPREHENSIVE RISK TOOLS TROUBLESHOOTING")
    print("=" * 60)
    
    errors = []
    successes = 0
    
    try:
        from treasury_agent.tools.treasury_risk_tools import TreasuryRiskTools
        print("✅ Risk tools import successful")
    except Exception as e:
        print(f"❌ CRITICAL: Cannot import risk tools: {e}")
        traceback.print_exc()
        return
    
    # Initialize tool
    try:
        risk_tool = TreasuryRiskTools()
        print("✅ Risk tools initialization successful")
    except Exception as e:
        print(f"❌ CRITICAL: Cannot initialize risk tools: {e}")
        traceback.print_exc()
        return
    
    # Test scenarios that might cause intermittent failures
    test_scenarios = [
        # Basic functionality
        {
            "name": "Basic Risk Assessment",
            "params": {
                "action": "assess_risk",
                "amount": 1000.0,
                "currency": "USD",
                "user_id": "test_user"
            }
        },
        
        # Edge cases that might cause issues
        {
            "name": "Zero Amount",
            "params": {
                "action": "assess_risk",
                "amount": 0.0,
                "currency": "USD",
                "user_id": "test_user"
            }
        },
        
        {
            "name": "Negative Amount",
            "params": {
                "action": "assess_risk",
                "amount": -100.0,
                "currency": "USD",
                "user_id": "test_user"
            }
        },
        
        {
            "name": "Empty Wallet Address",
            "params": {
                "action": "check_balance",
                "wallet_address": "",
                "currency": "USD"
            }
        },
        
        {
            "name": "None Values",
            "params": {
                "action": "assess_risk",
                "amount": None,
                "currency": None,
                "user_id": None
            }
        },
        
        {
            "name": "Invalid Action",
            "params": {
                "action": "invalid_action",
                "amount": 1000.0
            }
        },
        
        {
            "name": "Missing Required Parameters",
            "params": {
                "action": "check_balance"
                # Missing wallet_address
            }
        },
        
        {
            "name": "Malformed Risk Config",
            "params": {
                "action": "assess_risk",
                "amount": 1000.0,
                "risk_config": "not a dict"
            }
        },
        
        {
            "name": "Complex Risk Config",
            "params": {
                "action": "assess_risk",
                "amount": 5000.0,
                "currency": "USD",
                "user_id": "test_user",
                "risk_config": {
                    "min_balance_usd": 2000.0,
                    "transaction_limits": {
                        "daily": 10000.0,
                        "monthly": 50000.0,
                        "single": 5000.0
                    }
                }
            }
        },
        
        {
            "name": "Treasury Request Format",
            "params": {
                "action": "assess_risk",
                "amount": 2000.0,
                "currency": "USD",
                "user_id": "test_user",
                "treasury_request": 'Process payment request from user test_user. Excel file: /tmp/test.xlsx. Request details: {"user_id": "test_user", "min_balance": 1500.0, "transaction_limits": {"daily": 20000.0, "single": 10000.0}}'
            }
        },
        
        # Stress test with rapid calls
        {
            "name": "Rapid Sequential Calls",
            "params": {
                "action": "validate_transaction_limits",
                "amount": 1000.0,
                "currency": "USD",
                "user_id": "stress_test_user"
            },
            "repeat": 5
        }
    ]
    
    print(f"\n🧪 Running {len(test_scenarios)} test scenarios...")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- Test {i}: {scenario['name']} ---")
        
        repeat_count = scenario.get('repeat', 1)
        for attempt in range(repeat_count):
            try:
                # Handle None values in parameters
                params = scenario['params'].copy()
                cleaned_params = {}
                for key, value in params.items():
                    if value is not None:
                        cleaned_params[key] = value
                    else:
                        # Skip None values to test default handling
                        pass
                
                result = risk_tool._run(**cleaned_params)
                
                if "Error" in result:
                    print(f"  ⚠️  Expected error handled: {result[:100]}...")
                else:
                    print(f"  ✅ Success: {result[:100]}...")
                
                successes += 1
                
                # Small delay for stress test
                if repeat_count > 1:
                    time.sleep(0.1)
                    
            except Exception as e:
                error_info = {
                    "scenario": scenario['name'],
                    "attempt": attempt + 1,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
                errors.append(error_info)
                print(f"  ❌ ERROR: {str(e)}")
                if "CRITICAL" in str(e).upper():
                    print(f"  📋 Full traceback:")
                    traceback.print_exc()
    
    # Summary
    print(f"\n📊 TROUBLESHOOTING SUMMARY")
    print("=" * 60)
    print(f"✅ Successful operations: {successes}")
    print(f"❌ Failed operations: {len(errors)}")
    
    if errors:
        print(f"\n🚨 ERROR ANALYSIS:")
        for error in errors:
            print(f"\n❌ {error['scenario']} (attempt {error['attempt']}):")
            print(f"   Error: {error['error']}")
            if "TypeError" in error['error'] or "AttributeError" in error['error']:
                print(f"   ⚡ This might be causing intermittent failures!")
                print(f"   📋 Traceback preview: {error['traceback'].split('Traceback')[1][:200] if 'Traceback' in error['traceback'] else 'N/A'}...")
    
    # Test potential race conditions or threading issues
    print(f"\n🔄 TESTING CONCURRENT OPERATIONS...")
    try:
        import threading
        import concurrent.futures
        
        def concurrent_test():
            tool = TreasuryRiskTools()
            return tool._run(
                action="assess_risk",
                amount=1000.0,
                currency="USD",
                user_id=f"concurrent_user_{threading.current_thread().ident}"
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(concurrent_test) for _ in range(5)]
            concurrent_results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    concurrent_results.append(result)
                except Exception as e:
                    print(f"❌ Concurrent test error: {e}")
                    errors.append({
                        "scenario": "Concurrent Operations",
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    })
        
        print(f"✅ Concurrent operations completed: {len(concurrent_results)} successful")
        
    except Exception as e:
        print(f"⚠️  Concurrent testing failed: {e}")
    
    print(f"\n🎯 FINAL RESULT:")
    if errors:
        print(f"❌ ISSUES FOUND: {len(errors)} errors detected")
        print("   These might be causing the intermittent failures you're experiencing.")
        return False
    else:
        print("✅ NO ISSUES FOUND: All tests passed successfully")
        print("   Risk tools appear to be functioning correctly.")
        return True

if __name__ == "__main__":
    success = run_stress_test()
    exit(0 if success else 1)
