#!/usr/bin/env python3
"""
Configuration for AWS Bedrock LLM integration
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'your_aws_access_key_here')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'your_aws_secret_key_here')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

# Bedrock Model Configuration
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

# Model Parameters
BEDROCK_TEMPERATURE = float(os.getenv('BEDROCK_TEMPERATURE', '0.7'))
BEDROCK_MAX_TOKENS = int(os.getenv('BEDROCK_MAX_TOKENS', '1000'))

# Available Bedrock Models
AVAILABLE_MODELS = {
    'claude-3-haiku': 'anthropic.claude-3-haiku-20240307-v1:0',  # Fast, cheap
    'claude-3-sonnet': 'anthropic.claude-3-sonnet-20240229-v1:0',  # Balanced
    'claude-3-opus': 'anthropic.claude-3-opus-20240229-v1:0',  # Most capable
    'titan-express': 'amazon.titan-text-express-v1'  # Amazon's model
}

def get_bedrock_config():
    """Get Bedrock configuration dictionary"""
    return {
        'aws_access_key_id': AWS_ACCESS_KEY_ID,
        'aws_secret_access_key': AWS_SECRET_ACCESS_KEY,
        'region_name': AWS_DEFAULT_REGION,
        'model_id': BEDROCK_MODEL_ID,
        'temperature': BEDROCK_TEMPERATURE,
        'max_tokens': BEDROCK_MAX_TOKENS
    } 