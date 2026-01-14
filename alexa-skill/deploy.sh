#!/bin/bash

# NEXUS Alexa Skill Deployment Script

echo "🚀 NEXUS Alexa Skill Deployment"
echo "==============================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first:"
    echo "   https://aws.amazon.com/cli/"
    exit 1
fi

# Check if ZIP is available
if ! command -v zip &> /dev/null; then
    echo "❌ ZIP utility not found. Please install it."
    exit 1
fi

echo "📦 Creating deployment package..."

# Create deployment directory
mkdir -p lambda

# Copy files to lambda directory
cp lambda_function.py lambda/
cp requirements.txt lambda/

# Install dependencies
cd lambda
pip install -r requirements.txt -t .

# Create ZIP file
zip -r ../nexus-alexa-skill.zip .

cd ..
rm -rf lambda

echo "✅ Deployment package created: nexus-alexa-skill.zip"

echo ""
echo "📤 Next steps:"
echo "1. Go to AWS Lambda Console: https://console.aws.amazon.com/lambda/"
echo "2. Create new function: nexus-alexa-skill (Python 3.9)"
echo "3. Upload nexus-alexa-skill.zip"
echo "4. Set environment variables:"
echo "   - NEXUS_API_URL: https://your-nexus-backend.onrender.com"
echo "   - ALEXA_SKILL_ID: amzn1.ask.skill.YOUR_SKILL_ID"
echo "5. Copy the Lambda ARN to Alexa Developer Console"

echo ""
echo "🎉 Ready to deploy!"