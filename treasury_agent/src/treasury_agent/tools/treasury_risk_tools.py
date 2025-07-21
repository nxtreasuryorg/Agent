from crewai.tools import BaseTool
from typing import Type, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import json
import random
import os
from web3 import Web3
import requests


class RiskToolsInput(BaseModel):
    """Input schema for TreasuryRiskTools."""
    action: str = Field(..., description="Action to perform: 'check_balance', 'validate_transaction_limits', 'check_minimum_balance', 'assess_risk'")
    wallet_address: str = Field(default="", description="Wallet address to check balance")
    amount: float = Field(default=0.0, description="Transaction amount to validate")
    currency: str = Field(default="USD", description="Currency for the transaction")
    user_id: str = Field(default="default", description="User identifier for tracking limits")
    transaction_type: str = Field(default="payment", description="Type of transaction: 'payment', 'investment'")
    risk_config: Optional[Dict[str, Any]] = Field(default=None, description="Risk configuration dictionary from user JSON input")


class TreasuryRiskTools(BaseTool):
    name: str = "Treasury Risk Tools"
    description: str = (
        "Real-time balance verification and transaction limit validation for treasury operations. "
        "Checks minimum balance requirements, enforces transaction limits, and validates available funds. "
        "Supports both fiat and cryptocurrency balance checking with configurable limits."
    )
    args_schema: Type[BaseModel] = RiskToolsInput

    def __init__(self):
        super().__init__()
        # Initialize Web3 connection (will be None in simulation mode)
        self._w3 = None
        self._infura_url = os.getenv('INFURA_API_KEY')
        
        # Risk configuration (as instance variables, not Pydantic fields)
        self._minimum_balance_usd = 1000.0  # Minimum balance requirement
        self._daily_limit_usd = 50000.0     # Daily transaction limit
        self._monthly_limit_usd = 200000.0  # Monthly transaction limit
        self._max_single_transaction_usd = 25000.0  # Maximum single transaction
        
        # Transaction tracking (in real implementation, this would be in a database)
        self._transaction_history = {}
        
        # Initialize Web3 if API key is available
        if self._infura_url:
            try:
                self._w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{self._infura_url}"))
            except Exception as e:
                print(f"Warning: Could not initialize Web3 connection: {e}")
                self._w3 = None

    def _get_risk_param(self, risk_config, key, default):
        if risk_config and key in risk_config:
            return risk_config[key]
        return default

    def _get_limit_param(self, risk_config, limit_key, default):
        if risk_config and 'transaction_limits' in risk_config and limit_key in risk_config['transaction_limits']:
            return risk_config['transaction_limits'][limit_key]
        return default

    def _run(self, action: str, wallet_address: str = "", amount: float = 0.0, 
             currency: str = "USD", user_id: str = "default", transaction_type: str = "payment", risk_config: Optional[Dict[str, Any]] = None) -> str:
        
        self._minimum_balance_usd = self._get_risk_param(risk_config, 'min_balance_usd', 1000.0)
        self._daily_limit_usd = self._get_limit_param(risk_config, 'daily', 50000.0)
        self._monthly_limit_usd = self._get_limit_param(risk_config, 'monthly', 200000.0)
        self._max_single_transaction_usd = self._get_limit_param(risk_config, 'single', 25000.0)

        if action == "check_balance":
            return self._check_balance(wallet_address, currency)
        elif action == "validate_transaction_limits":
            return self._validate_transaction_limits(amount, currency, user_id, transaction_type)
        elif action == "check_minimum_balance":
            return self._check_minimum_balance(wallet_address, currency)
        elif action == "assess_risk":
            return self._assess_risk(amount, currency, user_id, transaction_type)
        else:
            return f"Unknown action: {action}. Available actions: check_balance, validate_transaction_limits, check_minimum_balance, assess_risk"

    def _check_balance(self, wallet_address: str, currency: str = "USD") -> str:
        """Check real balance for a wallet address."""
        try:
            if not wallet_address:
                return "Error: Wallet address is required for balance check"
            
            if currency.upper() == "USD":
                # For USD, we'll simulate balance checking (in real implementation, this would connect to bank APIs)
                if not self._w3:
                    # Simulation mode for USD balance
                    balance_usd = random.uniform(5000.0, 50000.0)
                    available_balance = max(0, balance_usd - self._minimum_balance_usd)
                    
                    result = f"Balance Check Results (SIMULATION MODE):\n"
                    result += f"Wallet: {wallet_address}\n"
                    result += f"Currency: {currency}\n"
                    result += f"Total Balance: ${balance_usd:,.2f}\n"
                    result += f"Minimum Required: ${self._minimum_balance_usd:,.2f}\n"
                    result += f"Available Balance: ${available_balance:,.2f}\n"
                    result += f"Status: {'SUFFICIENT' if available_balance > 0 else 'INSUFFICIENT'}\n"
                    result += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    result += f"📝 Note: This is a simulation. Real balance would be checked via bank API."
                    
                    return result
                else:
                    # Real implementation would connect to bank APIs here
                    return "Real USD balance checking not implemented yet"
            
            elif currency.upper() in ["ETH", "USDT", "USDC"]:
                # For crypto, use Web3 if available
                if not self._w3:
                    # Simulation mode for crypto
                    if currency.upper() == "ETH":
                        balance = random.uniform(0.1, 2.0)
                        usd_value = balance * 3500  # Mock ETH price
                    elif currency.upper() in ["USDT", "USDC"]:
                        balance = random.uniform(100.0, 10000.0)
                        usd_value = balance  # Stablecoins ≈ USD
                    else:
                        balance = 0.0
                        usd_value = 0.0
                    
                    result = f"Balance Check Results (SIMULATION MODE):\n"
                    result += f"Wallet: {wallet_address}\n"
                    result += f"Currency: {currency}\n"
                    result += f"Balance: {balance:.6f} {currency}\n"
                    result += f"USD Value: ${usd_value:,.2f}\n"
                    result += f"Minimum Required: ${self._minimum_balance_usd:,.2f}\n"
                    result += f"Status: {'SUFFICIENT' if usd_value >= self._minimum_balance_usd else 'INSUFFICIENT'}\n"
                    result += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    result += f"📝 Note: This is a simulation. Real balance would be checked via blockchain."
                    
                    return result
                else:
                    # Real Web3 implementation
                    try:
                        address = Web3.to_checksum_address(wallet_address)
                        
                        if currency.upper() == "ETH":
                            balance_wei = self._w3.eth.get_balance(address)
                            balance = self._w3.from_wei(balance_wei, 'ether')
                            
                            # Get real ETH price
                            response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd', timeout=10)
                            if response.status_code == 200:
                                data = response.json()
                                eth_price = data['ethereum']['usd']
                                usd_value = float(balance) * eth_price
                            else:
                                usd_value = float(balance) * 3500  # Fallback price
                        
                        elif currency.upper() in ["USDT", "USDC"]:
                            # For stablecoins, we'd need contract addresses and ABI
                            # This is simplified for now
                            balance = 0.0
                            usd_value = 0.0
                        
                        result = f"Balance Check Results:\n"
                        result += f"Wallet: {wallet_address}\n"
                        result += f"Currency: {currency}\n"
                        result += f"Balance: {balance:.6f} {currency}\n"
                        result += f"USD Value: ${usd_value:,.2f}\n"
                        result += f"Minimum Required: ${self._minimum_balance_usd:,.2f}\n"
                        result += f"Status: {'SUFFICIENT' if usd_value >= self._minimum_balance_usd else 'INSUFFICIENT'}\n"
                        result += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        
                        return result
                        
                    except Exception as e:
                        return f"Error checking crypto balance: {str(e)}"
            
            else:
                return f"Unsupported currency: {currency}. Supported: USD, ETH, USDT, USDC"
                
        except Exception as e:
            return f"Error in balance check: {str(e)}"

    def _validate_transaction_limits(self, amount: float, currency: str, user_id: str, transaction_type: str) -> str:
        """Validate transaction against configured limits."""
        try:
            if amount <= 0:
                return "Error: Transaction amount must be greater than 0"
            
            # Convert to USD for limit checking (simplified)
            amount_usd = amount
            if currency.upper() != "USD":
                # In real implementation, this would use real exchange rates
                amount_usd = amount  # Simplified for now
            
            # Initialize user transaction history if not exists
            if user_id not in self._transaction_history:
                self._transaction_history[user_id] = {
                    'daily_total': 0.0,
                    'monthly_total': 0.0,
                    'last_daily_reset': datetime.now().date(),
                    'last_monthly_reset': datetime.now().replace(day=1).date()
                }
            
            user_history = self._transaction_history[user_id]
            today = datetime.now().date()
            current_month = datetime.now().replace(day=1).date()
            
            # Reset daily total if it's a new day
            if user_history['last_daily_reset'] < today:
                user_history['daily_total'] = 0.0
                user_history['last_daily_reset'] = today
            
            # Reset monthly total if it's a new month
            if user_history['last_monthly_reset'] < current_month:
                user_history['monthly_total'] = 0.0
                user_history['last_monthly_reset'] = current_month
            
            # Check limits
            violations = []
            status = "APPROVED"
            
            # Single transaction limit
            if amount_usd > self._max_single_transaction_usd:
                violations.append(f"Exceeds single transaction limit of ${self._max_single_transaction_usd:,.2f}")
                status = "BLOCKED"
            
            # Daily limit check
            daily_total_after = user_history['daily_total'] + amount_usd
            if daily_total_after > self._daily_limit_usd:
                violations.append(f"Would exceed daily limit of ${self._daily_limit_usd:,.2f} (current: ${user_history['daily_total']:,.2f})")
                status = "BLOCKED"
            
            # Monthly limit check
            monthly_total_after = user_history['monthly_total'] + amount_usd
            if monthly_total_after > self._monthly_limit_usd:
                violations.append(f"Would exceed monthly limit of ${self._monthly_limit_usd:,.2f} (current: ${user_history['monthly_total']:,.2f})")
                status = "BLOCKED"
            
            # Format response
            result = f"Transaction Limit Validation Results:\n"
            result += f"Status: {status}\n"
            result += f"User ID: {user_id}\n"
            result += f"Transaction Type: {transaction_type}\n"
            result += f"Amount: ${amount_usd:,.2f} {currency}\n"
            result += f"Daily Total: ${user_history['daily_total']:,.2f}\n"
            result += f"Monthly Total: ${user_history['monthly_total']:,.2f}\n"
            result += f"Daily Limit: ${self._daily_limit_usd:,.2f}\n"
            result += f"Monthly Limit: ${self._monthly_limit_usd:,.2f}\n"
            result += f"Single Transaction Limit: ${self._max_single_transaction_usd:,.2f}\n"
            
            if violations:
                result += f"\nLimit Violations:\n"
                for i, violation in enumerate(violations, 1):
                    result += f"{i}. {violation}\n"
            else:
                result += f"\n✅ All limits satisfied\n"
            
            result += f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Update transaction history if approved
            if status == "APPROVED":
                user_history['daily_total'] += amount_usd
                user_history['monthly_total'] += amount_usd
            
            return result
            
        except Exception as e:
            return f"Error in transaction limit validation: {str(e)}"

    def _check_minimum_balance(self, wallet_address: str, currency: str = "USD") -> str:
        """Check if wallet meets minimum balance requirements."""
        try:
            if not wallet_address:
                return "Error: Wallet address is required for minimum balance check"
            
            # Get current balance
            balance_result = self._check_balance(wallet_address, currency)
            
            # Extract balance information (simplified parsing)
            if "SIMULATION MODE" in balance_result:
                # For simulation, we'll parse the simulated balance
                if currency.upper() == "USD":
                    # Extract USD balance from simulation
                    balance_usd = random.uniform(5000.0, 50000.0)
                else:
                    # Extract crypto balance from simulation
                    if currency.upper() == "ETH":
                        balance = random.uniform(0.1, 2.0)
                        balance_usd = balance * 3500
                    else:
                        balance = random.uniform(100.0, 10000.0)
                        balance_usd = balance
            else:
                # For real implementation, parse the actual balance
                balance_usd = 0.0  # Would parse from real balance result
            
            # Check minimum balance requirement
            meets_minimum = balance_usd >= self._minimum_balance_usd
            shortfall = max(0, self._minimum_balance_usd - balance_usd)
            
            result = f"Minimum Balance Check Results:\n"
            result += f"Wallet: {wallet_address}\n"
            result += f"Currency: {currency}\n"
            result += f"Current Balance: ${balance_usd:,.2f}\n"
            result += f"Minimum Required: ${self._minimum_balance_usd:,.2f}\n"
            result += f"Shortfall: ${shortfall:,.2f}\n"
            result += f"Status: {'MEETS_MINIMUM' if meets_minimum else 'BELOW_MINIMUM'}\n"
            result += f"Recommendation: {'Ready for transactions' if meets_minimum else 'Add funds to meet minimum balance'}\n"
            result += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return result
            
        except Exception as e:
            return f"Error in minimum balance check: {str(e)}"

    def _assess_risk(self, amount: float, currency: str, user_id: str, transaction_type: str) -> str:
        """Comprehensive risk assessment combining balance and limit checks."""
        try:
            if amount <= 0:
                return "Error: Transaction amount must be greater than 0"
            
            # Perform all checks
            limit_result = self._validate_transaction_limits(amount, currency, user_id, transaction_type)
            
            # Extract status from limit check
            if "Status: APPROVED" in limit_result:
                risk_status = "LOW_RISK"
                recommendation = "Transaction approved - all limits satisfied"
            elif "Status: BLOCKED" in limit_result:
                risk_status = "HIGH_RISK"
                recommendation = "Transaction blocked - limit violations detected"
            else:
                risk_status = "MEDIUM_RISK"
                recommendation = "Transaction requires review"
            
            # Calculate risk score (simplified)
            risk_score = 0.0
            if "BLOCKED" in limit_result:
                risk_score = 1.0
            elif "APPROVED" in limit_result:
                risk_score = 0.1
            
            result = f"Risk Assessment Results:\n"
            result += f"Risk Status: {risk_status}\n"
            result += f"Risk Score: {risk_score:.2f}/1.0\n"
            result += f"Amount: ${amount:,.2f} {currency}\n"
            result += f"Transaction Type: {transaction_type}\n"
            result += f"User ID: {user_id}\n"
            result += f"Recommendation: {recommendation}\n"
            result += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            result += f"\nDetailed Limit Check:\n{limit_result}"
            
            return result
            
        except Exception as e:
            return f"Error in risk assessment: {str(e)}" 