#!/usr/bin/env python3

from crewai import Agent, Task, Crew
from crewai.llm import LLM
from typing import Dict, List, Optional
import boto3
from config import get_bedrock_config
import logging

logger = logging.getLogger(__name__)


class NxtreasuryAgent:
    
    def __init__(self):
        # Get Bedrock configuration
        bedrock_config = get_bedrock_config()
        
        # Initialize AWS Bedrock client
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=bedrock_config['aws_access_key_id'],
            aws_secret_access_key=bedrock_config['aws_secret_access_key'],
            region_name=bedrock_config['region_name']
        )
        
        # Configure CrewAI to use Bedrock
        self.llm = LLM(
            model=f"bedrock/{bedrock_config['model_id']}",
            temperature=bedrock_config['temperature'],
            max_tokens=bedrock_config['max_tokens']
        )
        
        # Initialize the CrewAI agent with Bedrock LLM
        self.agent = Agent(
            role="Assistant",
            goal="Help users with their questions and provide helpful responses.",
            backstory="You are a helpful AI assistant that can answer questions and have conversations with users.",
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            llm=self.llm
        )
        
        logger.info(f"Agent initialized with Bedrock model: {bedrock_config['model_id']}")
    
    def create_task(self, user_message: str) -> Task:
        task_description = f"Respond to this user message: {user_message}"
        expected_output = "A helpful and relevant response to the user's message."
        
        return Task(
            description=task_description,
            expected_output=expected_output,
            agent=self.agent
        )
    
    def chat(self, user_message: str) -> str:
        try:
            task = self.create_task(user_message)
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            result = crew.kickoff()
            return result
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"


def main():
    print("🚀 Basic Agent - Chat Bot (AWS Bedrock)")
    print("="*50)
    
    try:
        agent = NxtreasuryAgent()
        
        print("\n📋 Testing Basic Chat...")
        result = agent.chat("Hello, how are you today?")
        
        print(f"\n✅ Agent Response:")
        print(f"📄 {result}")
        
    except Exception as e:
        print(f"❌ Error initializing agent: {str(e)}")
        print("Please check your AWS credentials and Bedrock configuration.")


if __name__ == "__main__":
    main() 