# 📱 AMAZON DEVELOPER ACCOUNT & ALEXA SKILL SETUP

## 🎯 **AMAZON DEVELOPER CONSOLE STEP-BY-STEP:**

---

## **STEP 1: Access Amazon Developer Console**

### **1. Navigate to Developer Console**
```
https://developer.amazon.com/alexa/console/ask
```

### **2. Sign In**
- Click **"Sign In"** (top right corner)
- Use your **existing Amazon.com account** OR create new developer account
- If creating new: Click **"Create your Amazon Developer account"**

### **3. Verify Account**
- Check your email for verification link
- Complete any additional verification steps

**✅ You're now in the Alexa Developer Console!**

---

## **STEP 2: Create Your NEXUS Alexa Skill**

### **1. Click "Create Skill"**
- Big blue button on the main dashboard
- Or click the **"+" icon** next to "Your Skills"

### **2. Skill Configuration**
```
Skill name: NEXUS ALEXIS

Default language: English (US)

Choose a model to add to your skill:
  ▶️  Custom  ← SELECT THIS

Choose a method to host your skill's backend resources:
  ▶️  Provision your own  ← SELECT THIS
     (We'll use AWS Lambda)
```

### **3. Click "Create Skill"**
- Wait for skill creation (10-20 seconds)
- You'll be taken to the skill dashboard

---

## **STEP 3: Configure Interaction Model**

### **1. Navigate to Interaction Model**
- In left sidebar: **"Interaction Model"** → **"JSON Editor"**

### **2. Upload Interaction Model**
- Delete all existing JSON content
- Copy entire contents of `interactionModel.json` from your alexa-skill folder
- Paste into the JSON editor

### **3. Save and Build**
- Click **"Save Model"**
- Click **"Build Model"**
- Wait for build to complete (1-2 minutes)
- **Status should show: "Successfully built model"**

---

## **STEP 4: Configure Endpoints**

### **1. Navigate to Endpoints**
- In left sidebar: **"Endpoint"**

### **2. Configure AWS Lambda**
```
Service Endpoint Type:
  ▶️  AWS Lambda ARN  ← SELECT THIS

Default Region:
  ▶️  Your Lambda ARN here (we'll add this after AWS setup)

Note: You'll come back to add the ARN after creating the Lambda function
```

---

## **STEP 5: Configure Account Linking (Optional but Recommended)**

### **1. Navigate to Account Linking**
- In left sidebar: **"Account Linking"**

### **2. Enable Account Linking**
```
Do you allow users to create an account or link to an existing account with you?
  ▶️  Yes  ← SELECT THIS
```

### **3. Authorization Grant Type**
```
Authorization grant type:
  ▶️  Implicit grant  ← SELECT THIS
```

### **4. Authorization URI**
```
Your Authorization URI:
https://your-nexus-backend.onrender.com/auth/alexa
```

### **5. Client ID**
```
Alexa Client ID:
amzn1.application-oa2-client.YOUR_ALEXA_CLIENT_ID
```
*(You'll get this from the Alexa console - copy from URL)*

### **6. Scopes**
```
Add scope: nexus_access
```

---

## **STEP 6: Configure Privacy & Compliance**

### **1. Navigate to Privacy & Compliance**
- In left sidebar: **"Privacy & Compliance"**

### **2. Basic Info**
```
Does this skill allow users to make purchases or engage in digital transactions?
  ▶️  No

Does this Alexa skill collect users' personal information?
  ▶️  No

Is your skill directed to or does it target children under the age of 13?
  ▶️  No

Does this skill contain advertising?
  ▶️  No
```

### **3. Testing Instructions**
```
How can a user test this skill?
"Alexa, open ALEXIS NEXUS" to start managing your government contracting system.
Try commands like "create opportunity" or "add contact".
```

---

## **STEP 7: Get Your Skill ID**

### **1. Find Skill ID**
- Look at the URL in your browser:
  ```
  https://developer.amazon.com/alexa/console/ask/build/amzn1.ask.skill.YOUR_SKILL_ID
  ```
- Copy the **amzn1.ask.skill.YOUR_SKILL_ID** part

### **2. Save for Later**
- You'll need this for:
  - AWS Lambda environment variables
  - NEXUS API environment variables
  - Account linking configuration

---

## **🎯 WHAT YOU'VE ACCOMPLISHED:**

### **✅ Alexa Skill Created:**
- Skill Name: "NEXUS ALEXIS"
- Invocation: "Alexa, open ALEXIS NEXUS"
- Voice Model: Configured with custom intents
- Endpoints: Ready for AWS Lambda connection

### **✅ Voice Commands Ready:**
- "Alexa, tell ALEXIS NEXUS to create opportunity..."
- "Alexa, ask ALEXIS NEXUS to add contact..."
- "Alexa, ask ALEXIS NEXUS what's my status"

### **✅ Next Steps:**
1. ✅ **Amazon Developer account** setup complete
2. ⏳ **AWS account** setup (if not done)
3. ⏳ **AWS Lambda deployment**
4. ⏳ **Connect Lambda to Alexa skill**
5. ⏳ **Testing and certification**

---

## 🔧 **TROUBLESHOOTING:**

### **Can't Access Developer Console?**
- Make sure you're signed into Amazon
- Try incognito/private browsing mode
- Clear browser cache/cookies

### **Skill Creation Fails?**
- Check skill name (must be unique)
- Verify you're in the right region (US)
- Try a different skill name if needed

### **Build Model Fails?**
- Check JSON syntax in interactionModel.json
- Make sure all required fields are present
- Look for error messages in the console

---

## 🎉 **ALEXA SKILL READY!**

**Your Amazon Developer setup is complete!**

The skill interface is ready - now we just need to connect the AWS Lambda brain to make it fully functional.

**Next: Set up your AWS account and deploy the Lambda function!** 🚀