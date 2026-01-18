# 📞 JotForm AI Receptionist Integration Guide

## 🎯 Overview

This guide walks you through integrating JotForm's AI Phone Agent with your NEXUS LBPC system to automatically capture and qualify leads from inbound phone calls, web chat, SMS, and other channels.

---

## 💰 Cost & Value Proposition

**Monthly Cost:** $34/month (JotForm Bronze plan)

**What You Get:**
- 24/7 AI phone receptionist with dedicated phone number
- Unlimited web chat widget
- SMS/text support
- WhatsApp integration
- Native Airtable integration
- Call transcription & recording
- Multi-channel lead capture

**ROI:** If this captures just ONE additional $15K+ surplus recovery lead per month, it pays for itself 400x over.

---

## 📋 Implementation Phases

### **Phase 1: JotForm Setup (1-2 hours)**

#### Step 1: Sign Up for JotForm
1. Go to [jotform.com/pricing](https://www.jotform.com/pricing)
2. Select **Bronze Plan** ($34/month)
3. Sign up with business email

#### Step 2: Create AI Phone Agent
1. Navigate to **AI Agents** in JotForm dashboard
2. Click **Create New Agent**
3. Select **Phone Agent** template
4. Name it: "LBPC Surplus Recovery Receptionist"

#### Step 3: Configure Agent Personality
```
Agent Name: LBPC Assistant
Tone: Professional, empathetic, helpful
Greeting: "Thank you for calling [Your Company Name]. I'm here to help you with surplus property recovery. May I have your name please?"

Core Script:
1. Collect caller's full name
2. Ask: "What county and state is your property located in?"
3. Ask: "Do you know approximately how much surplus funds are available?"
4. Ask: "What's the best phone number to reach you?"
5. Ask: "And your email address?"
6. Confirm: "Great! I've captured your information. A specialist will contact you within 24 hours to discuss your case. Is there anything else I can help you with today?"
```

#### Step 4: Set Up Data Collection Form

**Form Fields to Create:**
- Full Name (required)
- Phone Number (required)
- Email Address (required)
- Property County (required)
- Property State (required)
- Surplus Amount (optional, number)
- Case Number (optional)
- Additional Notes (long text)
- Call Duration (auto-captured)
- Call Recording URL (auto-captured)
- Call Transcript (auto-captured)

#### Step 5: Get Your Phone Number
1. JotForm will assign you a dedicated phone number
2. Note this number - you'll add it to your marketing materials
3. Test by calling yourself

---

### **Phase 2: Direct Airtable Integration (15 minutes)**

#### Step 1: Connect to Airtable
1. In JotForm Agent settings, go to **Integrations**
2. Click **Add Integration** → Select **Airtable**
3. Authorize JotForm to access your Airtable account
4. Select Base: **NEXUS Command Center** (or your LBPC base)
5. Select Table: **LBPC Leads**

#### Step 2: Map Fields
Map JotForm fields to Airtable columns:

| JotForm Field | Airtable Column |
|---------------|-----------------|
| Full Name | Property Owner Name |
| Phone Number | Phone |
| Email Address | Email |
| Property County | County |
| Property State | State |
| Surplus Amount | Surplus Amount |
| Case Number | Case Number |
| Call Transcript | Notes |
| Call Recording URL | Call Recording |

**Special Mappings:**
- Set **Lead Source** to static value: "Phone - AI Receptionist"
- Set **Status** to static value: "New"
- Set **Priority Score** to formula (if available) or leave for backend calculation

#### Step 3: Test Integration
1. Make a test call to your new number
2. Provide sample information
3. Check Airtable - lead should appear within 30 seconds
4. Verify all fields mapped correctly

---

### **Phase 3: NEXUS Backend Webhook (Optional Enhancement)**

While the direct Airtable integration works great, adding a webhook to your NEXUS backend enables:
- Custom lead enrichment
- Priority score calculation
- Automated document generation
- Task creation
- Email notifications

#### Webhook Endpoint Added

The following endpoint has been added to your `api_server.py`:

```python
@app.route('/webhooks/jotform', methods=['POST'])
```

This endpoint:
- ✅ Accepts JotForm submission data
- ✅ Validates and enriches lead information
- ✅ Calculates priority score automatically
- ✅ Creates lead in Airtable via your existing handler
- ✅ Logs call transcript and recording
- ✅ Sends confirmation response

#### Configure Webhook in JotForm

1. **Get Your Webhook URL:**
   - Local dev: `http://localhost:5000/webhooks/jotform`
   - Production: `https://your-nexus-backend.onrender.com/webhooks/jotform`

2. **Add Webhook in JotForm:**
   - Agent settings → Integrations
   - Add **Webhook** integration
   - Paste your webhook URL
   - Select trigger: **On Form Submission**
   - Format: **JSON**

3. **Test Webhook:**
   - Make a test call
   - Check your backend logs (Terminal with api_server.py running)
   - Should see: "JotForm webhook received" in logs
   - Lead should be created in Airtable

---

### **Phase 4: Multi-Channel Expansion (Optional)**

#### Add Web Chat Widget
1. JotForm dashboard → Your AI Agent
2. Click **Get Widget Code**
3. Copy embed code
4. Add to your website/landing page:

```html
<!-- Add before closing </body> tag -->
<script src="https://cdn.jotfor.ms/ai-chat-widget.js"></script>
<script>
  JotFormAI.init({
    agentId: 'YOUR_AGENT_ID',
    position: 'bottom-right',
    theme: 'light'
  });
</script>
```

#### Enable SMS Support
1. Agent settings → Channels
2. Enable **SMS**
3. Get your SMS number (may be same as phone or different)
4. Test by texting yourself

#### Add WhatsApp (Optional)
1. Agent settings → Channels
2. Enable **WhatsApp**
3. Follow WhatsApp Business API setup
4. Connect your WhatsApp Business account

---

## 🧪 Testing Checklist

### Test Scenarios

**Scenario 1: High-Value Lead**
- [ ] Call with $45K surplus, full contact info
- [ ] Verify priority score is 90+
- [ ] Check that lead appears in Airtable
- [ ] Confirm call transcript is captured
- [ ] Verify webhook logged in backend

**Scenario 2: Low-Information Lead**
- [ ] Call with minimal info (name + county only)
- [ ] Verify priority score is lower (30-50)
- [ ] Check that partial lead is still created
- [ ] Confirm AI handles incomplete data gracefully

**Scenario 3: After Hours**
- [ ] Call outside business hours (9 PM)
- [ ] Verify AI still answers and captures info
- [ ] Check that lead is flagged for next-day follow-up

**Scenario 4: Multi-Channel**
- [ ] Submit via web chat
- [ ] Submit via SMS
- [ ] Verify both create leads in Airtable
- [ ] Confirm source is tracked correctly

**Scenario 5: Error Handling**
- [ ] Call with invalid data (bad phone format)
- [ ] Verify AI asks for clarification
- [ ] Check that error doesn't crash system

---

## 📊 Monitoring & Analytics

### JotForm Dashboard
View in JotForm:
- Total calls received
- Average call duration
- Conversion rate (calls → captured leads)
- Busiest call times
- Most common questions

### Airtable Tracking
Monitor in LBPC Leads table:
- Leads by source (filter: "Phone - AI Receptionist")
- Average surplus amount from phone leads
- Conversion rate (phone leads → clients)
- ROI tracking

### NEXUS Backend Logs
Check your api_server logs:
- Webhook hits
- Successfully processed leads
- Any errors or failures

---

## 🎯 Best Practices

### AI Agent Training
- **Weekly Review:** Check call transcripts weekly
- **Refine Questions:** Update qualification questions based on patterns
- **Add FAQs:** Train AI on common questions you hear
- **Tone Adjustment:** Refine greeting and responses

### Response Time
- **Goal:** Contact phone leads within 2-4 hours
- **Setup:** Create Airtable automation to email you when phone lead comes in
- **Priority:** Phone leads are typically warmer than mined leads

### Quality Control
- **Listen to Calls:** Review 5-10 recordings per week
- **Track Satisfaction:** Note any complaints or confusion
- **Iterate:** Continuously improve AI responses

### Marketing Integration
**Where to Display Your New Number:**
1. Business cards
2. Website header
3. Email signatures
4. Outbound document templates (Initial Notice, etc.)
5. Google My Business
6. Social media profiles
7. Direct mail campaigns

---

## 💡 Advanced Features

### Conditional Logic
Set up in JotForm:
- If surplus > $50K → Flag as "Hot Lead"
- If caller mentions attorney → Ask for attorney name
- If out-of-state → Ask if they've relocated

### Smart Routing
- High-value leads ($50K+) → Send SMS alert immediately
- Attorney-represented → Route to specific handler
- Multiple properties → Flag for special attention

### Follow-Up Automation
- Send confirmation email immediately
- Schedule SMS reminder at 24 hours if not contacted
- Auto-generate Initial Notice document
- Create follow-up tasks in Airtable

---

## 🔧 Troubleshooting

### "Lead not appearing in Airtable"
**Check:**
1. JotForm-Airtable integration is active
2. Field mapping is correct
3. No required fields are missing in Airtable
4. Airtable API limits not exceeded

**Solution:** Check JotForm integration logs for errors

### "Webhook not firing"
**Check:**
1. Webhook URL is correct and accessible
2. Backend server is running
3. No firewall blocking JotForm IPs
4. Webhook secret (if configured) matches

**Solution:** Test webhook URL with curl:
```bash
curl -X POST https://your-backend.com/webhooks/jotform \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### "AI not understanding callers"
**Check:**
1. Mic/audio quality on caller's end
2. Background noise during test calls
3. AI training needs more examples
4. Questions are too complex

**Solution:** Simplify questions, add more training data

### "High call volume causing issues"
**Check:**
1. Airtable API rate limits
2. Backend server capacity
3. JotForm plan limits

**Solution:** Upgrade plans if needed, optimize webhook processing

---

## 🚀 Go-Live Checklist

### Pre-Launch
- [ ] JotForm AI Agent configured and tested
- [ ] Airtable integration working
- [ ] Webhook endpoint tested (if using)
- [ ] Test calls completed successfully
- [ ] Call recordings reviewed for quality
- [ ] Phone number noted and ready to distribute

### Launch Day
- [ ] Update all marketing materials with new number
- [ ] Send announcement to existing leads
- [ ] Post on social media
- [ ] Update Google My Business
- [ ] Train team on how to handle phone leads

### Post-Launch (First Week)
- [ ] Monitor calls daily
- [ ] Review transcripts
- [ ] Check lead quality
- [ ] Adjust AI responses as needed
- [ ] Measure conversion rate

### Post-Launch (First Month)
- [ ] Analyze ROI
- [ ] Expand to additional channels if successful
- [ ] Refine qualification criteria
- [ ] Document learnings

---

## 📈 Expected Results

### Week 1
- **Goal:** 5-10 test calls
- **Focus:** Refine AI responses
- **Metric:** 100% lead capture rate

### Month 1
- **Goal:** 20-50 real calls
- **Focus:** Lead quality
- **Metric:** 80%+ conversion to Airtable

### Month 3
- **Goal:** 100+ calls
- **Focus:** ROI optimization
- **Metric:** 1-2 new clients from phone leads

---

## 💰 ROI Calculation

**Investment:** $34/month

**If you capture just 1 additional lead per month:**
- Average surplus: $25,000
- Your fee: 30% = $7,500
- ROI: 22,000% ($7,500 / $34)

**Break-even:** One phone lead every 4-5 months

**Target:** 2-5 phone leads per month = $15-37K additional revenue

---

## 🎉 You're Ready!

Your JotForm AI Receptionist integration is ready to deploy. Follow the phases above, test thoroughly, and launch when ready.

**Remember:** This is about capturing opportunities you'd otherwise miss - after-hours calls, busy periods, or leads who prefer to call rather than fill forms.

**Next Step:** Sign up for JotForm Bronze and start Phase 1!

---

## 📞 Support Resources

- **JotForm Support:** [support.jotform.com](https://support.jotform.com)
- **JotForm AI Agents Docs:** [jotform.com/ai/agents](https://www.jotform.com/ai/agents)
- **NEXUS Backend Docs:** See `LBPC_QUICK_START.md`
- **Airtable Integration:** See `LBPC_AIRTABLE_SCHEMA.md`

---

**Let's turn phone calls into clients!** 📞💰
