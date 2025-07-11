from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import random
import string


class PaymentProcessorInput(BaseModel):
    """Input schema for PaymentProcessorTool."""
    action: str = Field(..., description="Action to perform: 'analyze_routes', 'estimate_cost', 'execute_payment', or 'check_status'")
    amount: float = Field(..., description="Payment amount in source currency")
    source_currency: str = Field(default="USD", description="Source currency code")
    target_currency: str = Field(..., description="Target currency code")
    destination_country: str = Field(..., description="Destination country")
    recipient: str = Field(..., description="Recipient name or identifier")
    urgency: str = Field(default="standard", description="Payment urgency: 'urgent', 'standard', 'economy'")
    transaction_id: str = Field(default="", description="Transaction ID for status checks")


class MockPaymentProcessorTool(BaseTool):
    name: str = "Payment Processor Tool"
    description: str = (
        "Analyze payment routes, estimate costs, and execute payments. "
        "Supports multiple payment methods: SWIFT wire, ACH, cryptocurrency, and regional networks. "
        "Can analyze optimal routing, provide cost estimates, execute payments, and track status."
    )
    args_schema: Type[BaseModel] = PaymentProcessorInput

    def _run(self, action: str, amount: float, source_currency: str = "USD", 
             target_currency: str = "", destination_country: str = "", 
             recipient: str = "", urgency: str = "standard", transaction_id: str = "") -> str:
        
        if action == "analyze_routes":
            return self._analyze_routes(amount, source_currency, target_currency, destination_country, urgency)
        elif action == "estimate_cost":
            return self._estimate_cost(amount, source_currency, target_currency, destination_country, urgency)
        elif action == "execute_payment":
            return self._execute_payment(amount, source_currency, target_currency, destination_country, recipient, urgency)
        elif action == "check_status":
            return self._check_status(transaction_id)
        else:
            return f"Unknown action: {action}. Available actions: analyze_routes, estimate_cost, execute_payment, check_status"

    def _analyze_routes(self, amount: float, source_currency: str, target_currency: str, 
                       destination_country: str, urgency: str) -> str:
        
        routes = []
        
        # SWIFT Wire Transfer
        swift_time = "1-3 business days" if urgency == "standard" else "Same day (if before 2 PM)"
        swift_cost = amount * 0.015 + 25  # 1.5% + $25 fixed
        routes.append({
            "method": "SWIFT Wire Transfer",
            "time": swift_time,
            "cost": swift_cost,
            "reliability": "99.8%",
            "pros": "Widely accepted, highly secure",
            "cons": "Higher fees, slower for urgent transfers"
        })
        
        # ACH (for USD transactions to supported countries)
        if source_currency == "USD" and destination_country.lower() in ["usa", "canada", "united states"]:
            ach_cost = amount * 0.008 + 5  # 0.8% + $5
            routes.append({
                "method": "ACH Transfer",
                "time": "2-3 business days",
                "cost": ach_cost,
                "reliability": "99.5%",
                "pros": "Lower cost, good for domestic transfers",
                "cons": "Limited to USD, slower processing"
            })
        
        # Cryptocurrency (for tech-savvy recipients)
        crypto_cost = amount * 0.005 + 10  # 0.5% + $10
        routes.append({
            "method": "Cryptocurrency (USDC/USDT)",
            "time": "5-30 minutes",
            "cost": crypto_cost,
            "reliability": "99.9%",
            "pros": "Very fast, low fees, 24/7 availability",
            "cons": "Requires crypto wallet, regulatory uncertainty"
        })
        
        # Regional networks (SEPA for Europe, etc.)
        if destination_country.lower() in ["germany", "france", "italy", "spain", "netherlands", "belgium"]:
            sepa_cost = amount * 0.002 + 2  # 0.2% + €2
            routes.append({
                "method": "SEPA Transfer",
                "time": "1 business day",
                "cost": sepa_cost,
                "reliability": "99.7%",
                "pros": "Very low cost, fast within EU",
                "cons": "Limited to SEPA countries"
            })
        
        # Sort routes by cost or speed based on urgency
        if urgency == "urgent":
            routes.sort(key=lambda x: self._parse_time(x["time"]))
        else:
            routes.sort(key=lambda x: x["cost"])
        
        result = f"Payment Route Analysis:\n"
        result += f"Amount: {amount} {source_currency} → {target_currency}\n"
        result += f"Destination: {destination_country}\n"
        result += f"Urgency: {urgency.upper()}\n\n"
        result += f"Recommended Routes (sorted by {'speed' if urgency == 'urgent' else 'cost'}):\n\n"
        
        for i, route in enumerate(routes, 1):
            result += f"{i}. {route['method']}\n"
            result += f"   Time: {route['time']}\n"
            result += f"   Cost: ${route['cost']:.2f}\n"
            result += f"   Reliability: {route['reliability']}\n"
            result += f"   Pros: {route['pros']}\n"
            result += f"   Cons: {route['cons']}\n\n"
        
        return result

    def _estimate_cost(self, amount: float, source_currency: str, target_currency: str, 
                      destination_country: str, urgency: str) -> str:
        
        # Base exchange rate (mock)
        exchange_rates = {
            "USD/EUR": 0.92, "USD/GBP": 0.79, "USD/JPY": 148.5,
            "EUR/USD": 1.087, "GBP/USD": 1.266, "JPY/USD": 0.0067
        }
        
        rate_key = f"{source_currency}/{target_currency}"
        exchange_rate = exchange_rates.get(rate_key, 1.0)
        
        # Calculate costs for different methods
        swift_fee = amount * 0.015 + 25
        swift_total = (amount - swift_fee) * exchange_rate
        
        crypto_fee = amount * 0.005 + 10
        crypto_total = (amount - crypto_fee) * exchange_rate
        
        result = f"Cost Estimation:\n"
        result += f"Amount: {amount} {source_currency}\n"
        result += f"Target: {target_currency}\n"
        result += f"Exchange Rate: 1 {source_currency} = {exchange_rate} {target_currency}\n\n"
        
        result += f"Method Comparison:\n"
        result += f"1. SWIFT Wire:\n"
        result += f"   Fee: ${swift_fee:.2f}\n"
        result += f"   Recipient gets: {swift_total:.2f} {target_currency}\n\n"
        
        result += f"2. Cryptocurrency:\n"
        result += f"   Fee: ${crypto_fee:.2f}\n"
        result += f"   Recipient gets: {crypto_total:.2f} {target_currency}\n\n"
        
        if urgency == "urgent":
            result += f"⚡ Urgent transfer surcharge: +$50\n"
        
        return result

    def _execute_payment(self, amount: float, source_currency: str, target_currency: str, 
                        destination_country: str, recipient: str, urgency: str) -> str:
        
        # Generate mock transaction ID
        tx_id = 'TX' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Simulate processing time
        processing_time = random.randint(1, 5)  # 1-5 seconds simulation
        
        # Mock execution with realistic scenarios
        success_rate = 0.95  # 95% success rate
        
        if random.random() < success_rate:
            status = "SUCCESS"
            estimated_completion = datetime.now() + timedelta(
                hours=2 if urgency == "urgent" else 24,
                minutes=random.randint(0, 59)
            )
        else:
            # Simulate various failure scenarios
            failures = [
                "INSUFFICIENT_FUNDS",
                "RECIPIENT_BANK_ERROR", 
                "COMPLIANCE_HOLD",
                "NETWORK_TIMEOUT"
            ]
            status = random.choice(failures)
            estimated_completion = None
        
        result = f"Payment Execution Result:\n"
        result += f"Transaction ID: {tx_id}\n"
        result += f"Status: {status}\n"
        result += f"Amount: {amount} {source_currency}\n"
        result += f"Recipient: {recipient}\n"
        result += f"Destination: {destination_country}\n"
        result += f"Processing Time: {processing_time} seconds\n"
        
        if status == "SUCCESS":
            result += f"Estimated Completion: {estimated_completion.strftime('%Y-%m-%d %H:%M:%S')}\n"
            result += f"Tracking: Payment successfully initiated and will be processed within the estimated timeframe.\n"
        else:
            result += f"Error Details: Payment failed due to {status.replace('_', ' ').lower()}.\n"
            result += f"Recommendation: Please review transaction details and retry, or contact support.\n"
        
        result += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return result

    def _check_status(self, transaction_id: str) -> str:
        if not transaction_id:
            return "Error: Transaction ID is required for status checks."
        
        # Mock status responses
        statuses = [
            ("PROCESSING", "Payment is being processed by the receiving bank"),
            ("COMPLETED", "Payment has been successfully delivered to recipient"),
            ("PENDING_COMPLIANCE", "Payment is under compliance review"),
            ("FAILED", "Payment failed due to technical error"),
            ("CANCELLED", "Payment was cancelled by sender")
        ]
        
        status, description = random.choice(statuses)
        
        result = f"Payment Status Check:\n"
        result += f"Transaction ID: {transaction_id}\n"
        result += f"Current Status: {status}\n"
        result += f"Description: {description}\n"
        result += f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if status == "COMPLETED":
            result += f"✅ Payment successfully delivered!\n"
        elif status == "FAILED":
            result += f"❌ Payment failed. Contact support for assistance.\n"
        elif status == "PROCESSING":
            result += f"⏳ Payment in progress. Check again in a few hours.\n"
        
        return result

    def _parse_time(self, time_str: str) -> int:
        """Convert time string to minutes for sorting purposes"""
        if "minute" in time_str:
            return int(time_str.split("-")[0])
        elif "hour" in time_str:
            return int(time_str.split("-")[0]) * 60
        elif "day" in time_str:
            return int(time_str.split("-")[0]) * 24 * 60
        else:
            return 1440  # Default to 1 day 