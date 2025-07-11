#!/usr/bin/env python3
"""
Test script for mock treasury tools
This script tests all mock tools to ensure they work correctly
before integrating them with the treasury agents.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from treasury_agent.tools import (
    MockMarketDataTool,
    MockRiskAssessmentTool,
    MockPaymentProcessorTool,
    MockAuditLoggerTool
)

def test_market_data_tool():
    print("=" * 60)
    print("🔍 TESTING MARKET DATA TOOL")
    print("=" * 60)
    
    tool = MockMarketDataTool()
    
    # Test 1: Get USD/EUR rate
    print("\n📊 Test 1: USD/EUR Exchange Rate")
    result = tool._run("USD/EUR", "rate")
    print(result)
    
    # Test 2: Get all market data for BTC/USD
    print("\n📊 Test 2: Complete BTC/USD Market Data")
    result = tool._run("BTC/USD", "all")
    print(result)
    
    # Test 3: Get volatility for unsupported pair
    print("\n📊 Test 3: Unsupported Currency Pair")
    result = tool._run("ABC/XYZ", "volatility")
    print(result)

def test_risk_assessment_tool():
    print("\n" + "=" * 60)
    print("⚖️  TESTING RISK ASSESSMENT TOOL")
    print("=" * 60)
    
    tool = MockRiskAssessmentTool()
    
    # Test 1: Low risk transaction
    print("\n🟢 Test 1: Low Risk Transaction")
    result = tool._run("Alice Johnson", 5000, "USD", "France", "wire")
    print(result)
    
    # Test 2: High risk - blocked country
    print("\n🔴 Test 2: High Risk - Blocked Country")
    result = tool._run("Bob Smith", 10000, "USD", "Iran", "swift")
    print(result)
    
    # Test 3: Medium risk - high amount
    print("\n🟡 Test 3: Medium Risk - High Amount")
    result = tool._run("Carol Williams", 75000, "USD", "Germany", "crypto")
    print(result)
    
    # Test 4: Blocked entity
    print("\n🔴 Test 4: Blocked Entity")
    result = tool._run("Evil Corp", 1000, "USD", "USA", "wire")
    print(result)

def test_payment_processor_tool():
    print("\n" + "=" * 60)
    print("💳 TESTING PAYMENT PROCESSOR TOOL")
    print("=" * 60)
    
    tool = MockPaymentProcessorTool()
    
    # Test 1: Analyze routes for urgent transfer
    print("\n🚀 Test 1: Route Analysis - Urgent Transfer")
    result = tool._run("analyze_routes", 10000, "USD", "EUR", "Germany", "Alice Corp", "urgent")
    print(result)
    
    # Test 2: Cost estimation
    print("\n💰 Test 2: Cost Estimation")
    result = tool._run("estimate_cost", 5000, "USD", "GBP", "UK", "", "standard")
    print(result)
    
    # Test 3: Execute payment
    print("\n⚡ Test 3: Execute Payment")
    result = tool._run("execute_payment", 2500, "USD", "EUR", "France", "Jean Dupont", "standard")
    print(result)
    
    # Test 4: Check status (with mock transaction ID)
    print("\n📋 Test 4: Check Payment Status")
    result = tool._run("check_status", 0, "", "", "", "", "", "TX12345ABC")
    print(result)

def test_audit_logger_tool():
    print("\n" + "=" * 60)
    print("📝 TESTING AUDIT LOGGER TOOL")
    print("=" * 60)
    
    tool = MockAuditLoggerTool()
    
    # Test 1: Log a transaction
    print("\n📊 Test 1: Log Transaction")
    result = tool._run("log_transaction", "payment_initiated", 
                      "Payment of $5000 to Alice Johnson in France", 
                      "TX12345", "treasury_agent", "info")
    print(result)
    
    # Test 2: Log a decision
    print("\n🧠 Test 2: Log Decision")
    result = tool._run("log_decision", "route_selection", 
                      "Selected SWIFT wire transfer due to reliability requirements", 
                      "TX12345", "treasury_agent", "info")
    print(result)
    
    # Test 3: Log compliance check (high severity)
    print("\n⚖️  Test 3: Log Compliance Check")
    result = tool._run("log_compliance_check", "sanctions_screening", 
                      "High-risk country detected: Iran", 
                      "TX12346", "treasury_agent", "critical")
    print(result)
    
    # Test 4: Retrieve logs
    print("\n📋 Test 4: Retrieve Logs")
    result = tool._run("retrieve_logs", "", "", "TX12345", "", "")
    print(result)

def run_all_tests():
    print("🏛️  TREASURY AGENT MOCK TOOLS TEST SUITE")
    print("Testing all mock tools for decision-making capabilities...")
    print()
    
    try:
        test_market_data_tool()
        test_risk_assessment_tool()
        test_payment_processor_tool()
        test_audit_logger_tool()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("🎯 The treasury agents now have access to:")
        print("   • Market data for routing decisions")
        print("   • Risk assessment for compliance")
        print("   • Payment processing capabilities")
        print("   • Audit logging for regulatory compliance")
        print()
        print("🚀 Ready to integrate with CrewAI treasury agents!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print("Please check the tool implementations.")

if __name__ == "__main__":
    run_all_tests() 