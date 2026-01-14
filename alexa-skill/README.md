# NEXUS Alexa Skill Setup Guide

This directory contains the Alexa skill configuration for voice control of your NEXUS government contracting system.

## 🚀 Quick Setup (5-10 minutes)

### Step 1: Create Alexa Skill
1. Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Click "Create Skill"
3. Enter skill details:
   - **Skill name**: NEXUS ALEXIS
   - **Default language**: English (US)
   - **Model**: Custom
   - **Hosting**: Provision your own (we'll use AWS Lambda)
   - **Category**: Business & Finance

### Step 2: Configure Interaction Model
1. In the Alexa console, go to "Interaction Model" → "JSON Editor"
2. Copy and paste the contents of `interactionModel.json`
3. Click "Save Model" and "Build Model"

### Step 3: Set Up AWS Lambda
1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
2. Create new function:
   - **Name**: nexus-alexa-skill
   - **Runtime**: Python 3.9
   - **Architecture**: x86_64

3. Upload the Lambda code:
   - Zip the contents of this directory
   - Upload the ZIP file to Lambda

4. Set environment variables:
   ```
   NEXUS_API_URL=https://your-nexus-backend.onrender.com
   ALEXA_SKILL_ID=amzn1.ask.skill.YOUR_SKILL_ID
   ```

### Step 4: Connect Alexa to Lambda
1. In Alexa Developer Console, go to "Endpoint"
2. Select "AWS Lambda ARN"
3. Copy your Lambda function ARN and paste it
4. Save endpoints

### Step 5: Configure Environment Variables
Add these to your Render dashboard for the NEXUS backend:
```
JWT_SECRET=your-secure-jwt-secret-here
ALEXA_SKILL_ID=amzn1.ask.skill.YOUR_SKILL_ID
```

## 🎯 Voice Commands Available

### Opportunity Management
- "Alexa, tell ALEXIS NEXUS to create opportunity Website Redesign"
- "Alexa, tell ALEXIS NEXUS to create opportunity Cloud Migration worth 150,000 dollars for DOD"
- "Alexa, ask ALEXIS NEXUS to add opportunity Mobile App Development"

### Contact Management
- "Alexa, tell ALEXIS NEXUS to add contact John Smith"
- "Alexa, ask ALEXIS NEXUS to add contact Sarah Johnson at sarah@gsa.gov"
- "Alexa, tell ALEXIS NEXUS to create contact Mike Wilson phone 202-555-0123"

### Status & Updates
- "Alexa, ask ALEXIS NEXUS what's my status"
- "Alexa, tell ALEXIS NEXUS to give me a status update"
- "Alexa, ask ALEXIS NEXUS how am I doing"

## 🔧 Technical Architecture

```
Alexa Device → Alexa Service → AWS Lambda → NEXUS API → Airtable Database
       ↑              ↑              ↑              ↑
   Voice Input   Intent Processing  JWT Auth     Data Storage
```

### Security Features
- **JWT Authentication**: Secure token-based auth between Alexa and NEXUS
- **Skill ID Validation**: Only authorized Alexa skills can access your data
- **Token Expiration**: 1-hour token validity for security

### Error Handling
- **Graceful Degradation**: If NEXUS API is down, Alexa provides helpful messages
- **Timeout Protection**: 10-second timeouts prevent hanging requests
- **Fallback Responses**: User-friendly error messages

## 🧪 Testing

### Test in Alexa Developer Console
1. Go to "Test" tab
2. Try voice commands in the text input
3. Check Lambda logs in CloudWatch for debugging

### Test on Real Alexa Device
1. Enable "Developer Mode" on your Alexa app
2. Find the skill in "Your Skills"
3. Test voice commands

## 📋 Files Included

- `lambda_function.py` - AWS Lambda handler code
- `requirements.txt` - Python dependencies for Lambda
- `skill.json` - Alexa skill manifest
- `interactionModel.json` - Voice interaction model
- `README.md` - This setup guide

## 🔧 Customization

### Adding New Voice Commands
1. Add new intents to `interactionModel.json`
2. Add handler functions to `lambda_function.py`
3. Update the NEXUS API if needed

### Modifying Responses
Edit the response text in `lambda_function.py` to customize Alexa's voice and personality.

## 🚨 Important Notes

- **Skill ID**: Replace `YOUR_SKILL_ID` with your actual Alexa skill ID
- **API URL**: Update `NEXUS_API_URL` with your Render deployment URL
- **JWT Secret**: Use a strong, unique secret for production
- **Testing**: Always test in development before publishing

## 🎉 Ready to Go!

Once set up, you can control your entire NEXUS government contracting system with voice commands through Alexa!

**Need help?** Check the Alexa Developer Console documentation or AWS Lambda logs for debugging.