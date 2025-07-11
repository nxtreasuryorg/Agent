from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from datetime import datetime
import random


class RiskAssessmentInput(BaseModel):
    """Input schema for RiskAssessmentTool."""
    recipient: str = Field(..., description="Recipient name or identifier")
    amount: float = Field(..., description="Transaction amount in USD")
    currency: str = Field(default="USD", description="Transaction currency")
    destination_country: str = Field(..., description="Destination country for the payment")
    payment_method: str = Field(default="wire", description="Payment method: 'wire', 'crypto', 'ach', 'swift'")


class MockRiskAssessmentTool(BaseTool):
    name: str = "Risk Assessment Tool"
    description: str = (
        "Perform compliance and risk assessment for payment transactions. "
        "Checks transaction limits, sanctions screening, AML compliance, and country restrictions. "
        "Returns risk score and approval status with detailed explanations."
    )
    args_schema: Type[BaseModel] = RiskAssessmentInput

    def _run(self, recipient: str, amount: float, currency: str = "USD", 
             destination_country: str = "", payment_method: str = "wire") -> str:
        
        # Mock risk assessment logic with realistic scenarios
        risk_factors = []
        risk_score = 0.0
        status = "APPROVED"
        
        # Amount-based risk assessment
        if amount > 50000:
            risk_factors.append("High amount transaction (>$50,000)")
            risk_score += 0.3
        elif amount > 10000:
            risk_factors.append("Medium amount transaction (>$10,000)")
            risk_score += 0.1
        
        # Country-based risk assessment (mock high-risk countries)
        high_risk_countries = ["Iran", "North Korea", "Syria", "Cuba", "Afghanistan"]
        medium_risk_countries = ["Russia", "Belarus", "Myanmar", "Venezuela"]
        
        if destination_country.title() in high_risk_countries:
            risk_factors.append(f"High-risk destination country: {destination_country}")
            risk_score += 0.8
            status = "BLOCKED"
        elif destination_country.title() in medium_risk_countries:
            risk_factors.append(f"Medium-risk destination country: {destination_country}")
            risk_score += 0.4
        
        # Payment method risk
        if payment_method.lower() == "crypto":
            risk_factors.append("Cryptocurrency payment method")
            risk_score += 0.2
        elif payment_method.lower() == "swift":
            risk_factors.append("SWIFT international transfer")
            risk_score += 0.1
        
        # Mock sanctions screening (simulate some blocked entities)
        blocked_entities = ["Evil Corp", "Bad Actor Inc", "Sanctioned Entity", "Blocked Company"]
        if any(blocked in recipient.upper() for blocked in [entity.upper() for entity in blocked_entities]):
            risk_factors.append(f"Recipient matches sanctions list: {recipient}")
            risk_score += 1.0
            status = "BLOCKED"
        
        # Transaction limits check
        daily_limit = 100000
        monthly_limit = 500000
        
        if amount > daily_limit:
            risk_factors.append(f"Exceeds daily limit of ${daily_limit:,.2f}")
            risk_score += 0.5
            status = "REQUIRES_APPROVAL"
        
        # Final risk categorization
        if risk_score >= 0.8:
            status = "BLOCKED"
            risk_level = "HIGH"
        elif risk_score >= 0.4:
            if status != "BLOCKED":
                status = "REQUIRES_APPROVAL"
            risk_level = "MEDIUM"
        elif risk_score >= 0.2:
            if status not in ["BLOCKED", "REQUIRES_APPROVAL"]:
                status = "APPROVED_WITH_MONITORING"
            risk_level = "LOW-MEDIUM"
        else:
            risk_level = "LOW"
        
        # Add some randomness for testing (simulate occasional system flags)
        if random.random() < 0.1 and status == "APPROVED":  # 10% chance of random flag
            risk_factors.append("Flagged by automated screening system")
            status = "REQUIRES_MANUAL_REVIEW"
        
        # Format response
        result = f"""Risk Assessment Results:
Status: {status}
Risk Level: {risk_level}
Risk Score: {risk_score:.2f}/1.0

Transaction Details:
- Recipient: {recipient}
- Amount: ${amount:,.2f} {currency}
- Destination: {destination_country}
- Payment Method: {payment_method.upper()}

Risk Factors Identified:
"""
        
        if risk_factors:
            for i, factor in enumerate(risk_factors, 1):
                result += f"{i}. {factor}\n"
        else:
            result += "None - Low risk transaction\n"
        
        result += f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Add recommendations based on status
        if status == "APPROVED":
            result += "\n\nRecommendation: Transaction approved for processing."
        elif status == "APPROVED_WITH_MONITORING":
            result += "\n\nRecommendation: Transaction approved but requires enhanced monitoring."
        elif status == "REQUIRES_APPROVAL":
            result += "\n\nRecommendation: Transaction requires manual approval before processing."
        elif status == "REQUIRES_MANUAL_REVIEW":
            result += "\n\nRecommendation: Transaction flagged for manual review by compliance team."
        elif status == "BLOCKED":
            result += "\n\nRecommendation: Transaction BLOCKED due to high risk factors. Do not process."
        
        return result 