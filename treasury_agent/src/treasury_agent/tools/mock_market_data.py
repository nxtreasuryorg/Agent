from crewai.tools import BaseTool
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
import random
from datetime import datetime


class MarketDataInput(BaseModel):
    """Input schema for MarketDataTool."""
    currency_pair: str = Field(..., description="Currency pair to get data for (e.g., 'USD/EUR', 'USD/GBP', 'BTC/USD')")
    data_type: str = Field(default="rate", description="Type of data: 'rate', 'volatility', 'spread', or 'all'")


class MockMarketDataTool(BaseTool):
    name: str = "Market Data Tool"
    description: str = (
        "Get current exchange rates, volatility, and market data for currency pairs. "
        "Supports fiat currencies (USD, EUR, GBP, JPY) and cryptocurrencies (BTC, ETH). "
        "Use this tool to make informed decisions about payment routing and timing."
    )
    args_schema: Type[BaseModel] = MarketDataInput

    def _run(self, currency_pair: str, data_type: str = "rate") -> str:
        # Mock market data with realistic but predictable values for testing
        mock_data = {
            "USD/EUR": {
                "rate": 0.92,
                "volatility": "low",
                "spread": 0.002,
                "trend": "stable",
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "USD/GBP": {
                "rate": 0.79,
                "volatility": "medium",
                "spread": 0.003,
                "trend": "declining",
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "USD/JPY": {
                "rate": 148.50,
                "volatility": "high",
                "spread": 0.005,
                "trend": "volatile",
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "BTC/USD": {
                "rate": 43250.00,
                "volatility": "very_high",
                "spread": 0.008,
                "trend": "bullish",
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "ETH/USD": {
                "rate": 2580.00,
                "volatility": "high",
                "spread": 0.006,
                "trend": "stable",
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        # Add some randomness to simulate market movement (±2%)
        pair_upper = currency_pair.upper()
        if pair_upper in mock_data:
            data = mock_data[pair_upper].copy()
            base_rate = data["rate"]
            variation = random.uniform(-0.02, 0.02)  # ±2% variation
            data["rate"] = round(base_rate * (1 + variation), 4)
            
            if data_type == "rate":
                return f"Current {currency_pair} rate: {data['rate']}"
            elif data_type == "volatility":
                return f"{currency_pair} volatility: {data['volatility']} (spread: {data['spread']})"
            elif data_type == "spread":
                return f"{currency_pair} bid-ask spread: {data['spread']}"
            elif data_type == "all":
                return (f"Market Data for {currency_pair}:\n"
                       f"- Rate: {data['rate']}\n"
                       f"- Volatility: {data['volatility']}\n"
                       f"- Spread: {data['spread']}\n"
                       f"- Trend: {data['trend']}\n"
                       f"- Last Update: {data['last_update']}")
        else:
            return f"Currency pair {currency_pair} not supported. Available pairs: USD/EUR, USD/GBP, USD/JPY, BTC/USD, ETH/USD" 