# AWS Bedrock Setup Guide

## 🔧 AWS Credentials Configuration

### Option 1: Environment Variables
Create a `.env` file in your project root:
```bash
# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_DEFAULT_REGION=us-east-1

# Bedrock Model Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_TEMPERATURE=0.7
BEDROCK_MAX_TOKENS=1000
```

### Option 2: AWS CLI Configuration
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter output format (json)
```

### Option 3: Direct Configuration
Edit `config.py` and replace the default values:
```python
AWS_ACCESS_KEY_ID = 'your_actual_access_key'
AWS_SECRET_ACCESS_KEY = 'your_actual_secret_key'
AWS_DEFAULT_REGION = 'us-east-1'
```

## 🤖 Available Bedrock Models

### Anthropic Claude Models
- **claude-3-haiku**: `anthropic.claude-3-haiku-20240307-v1:0` (Fast, cheap)
- **claude-3-sonnet**: `anthropic.claude-3-sonnet-20240229-v1:0` (Balanced - Default)
- **claude-3-opus**: `anthropic.claude-3-opus-20240229-v1:0` (Most capable, expensive)

### Amazon Titan Models
- **titan-express**: `amazon.titan-text-express-v1` (Amazon's model)

## 🔑 Getting AWS Credentials

1. **Log into AWS Console**
2. **Go to IAM Service**
3. **Create a new user** or use existing user
4. **Attach policies**:
   - `AmazonBedrockFullAccess` (for Bedrock access)
   - Or create custom policy with minimal permissions:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "bedrock:InvokeModel",
                   "bedrock:InvokeModelWithResponseStream"
               ],
               "Resource": "*"
           }
       ]
   }
   ```
5. **Create Access Key** in Security Credentials tab
6. **Copy the Access Key ID and Secret Access Key**

## 🌍 Bedrock Available Regions

Bedrock is available in these regions:
- `us-east-1` (US East - N. Virginia) - **Recommended**
- `us-west-2` (US West - Oregon)
- `eu-west-1` (Europe - Ireland)
- `ap-southeast-1` (Asia Pacific - Singapore)
- `ap-northeast-1` (Asia Pacific - Tokyo)

## ✅ Testing Your Setup

Run the test:
```bash
python nxtreasury_agent.py
```

If successful, you should see:
```
🚀 Basic Agent - Chat Bot (AWS Bedrock)
==================================================
Agent initialized with Bedrock model: anthropic.claude-3-sonnet-20240229-v1:0
...
```

## 🚨 Troubleshooting

### Common Errors:

**1. `NoCredentialsError`**
- Check your AWS credentials are correctly set
- Verify `.env` file exists and has correct values

**2. `AccessDenied`**
- Ensure your user has Bedrock permissions
- Check if Bedrock is enabled in your AWS region

**3. `ValidationException`**
- Verify the model ID is correct
- Check if the model is available in your region

**4. `ThrottlingException`**
- You're hitting rate limits
- Reduce request frequency or upgrade your limits

### Enable Model Access
1. Go to AWS Bedrock Console
2. Click "Model access" in left sidebar
3. Click "Enable specific models"
4. Select the models you want to use
5. Submit request (may take time for approval)

## 💰 Cost Considerations

**Claude 3 Pricing (per 1M tokens):**
- Haiku: ~$0.25 input, ~$1.25 output
- Sonnet: ~$3 input, ~$15 output  
- Opus: ~$15 input, ~$75 output

**Titan Express:**
- ~$0.13 input, ~$0.17 output

Choose model based on your needs vs. cost. 