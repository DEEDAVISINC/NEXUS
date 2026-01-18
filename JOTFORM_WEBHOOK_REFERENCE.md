# 🔗 JotForm Webhook Integration - Quick Reference

## 📍 Webhook Endpoints

### Production Webhook
```
POST https://your-nexus-backend.onrender.com/webhooks/jotform
```

### Local Development
```
POST http://localhost:5000/webhooks/jotform
```

### Test Endpoint (Get Info)
```
GET http://localhost:5000/webhooks/jotform/test
```

---

## 🧪 Testing the Webhook

### Test with curl (Local)
```bash
curl -X POST http://localhost:5000/webhooks/jotform \
  -H "Content-Type: application/json" \
  -d '{
    "submissionID": "test-123",
    "formTitle": "LBPC Lead Intake",
    "submissionDate": "2026-01-17 10:30:00",
    "rawRequest": {
      "q1_fullName": "John Smith",
      "q2_phoneNumber": "555-123-4567",
      "q3_email": "john@example.com",
      "q4_county": "Wayne",
      "q5_state": "Michigan",
      "q6_surplusAmount": "25000",
      "q7_caseNumber": "2023-CV-12345",
      "q8_additionalNotes": "Test lead from webhook"
    }
  }'
```

### Expected Response (Success)
```json
{
  "success": true,
  "message": "Lead created successfully from JotForm submission",
  "lead_id": "rec1234567890",
  "channel": "Web Form",
  "priority_score": 75
}
```

### Expected Response (Error)
```json
{
  "success": false,
  "error": "Failed to create lead",
  "details": {
    "error": "Missing required field: property_owner_name"
  }
}
```

---

## 📋 JotForm Field Mapping

The webhook accepts flexible field naming. It looks for these patterns:

| Data Needed | Accepted Field Names |
|-------------|---------------------|
| **Full Name** | `q1_fullName`, `fullName`, `name` |
| **Phone** | `q2_phoneNumber`, `phoneNumber`, `phone` |
| **Email** | `q3_email`, `email` |
| **County** | `q4_county`, `county` |
| **State** | `q5_state`, `state` |
| **Surplus Amount** | `q6_surplusAmount`, `surplusAmount`, `surplus_amount` |
| **Case Number** | `q7_caseNumber`, `caseNumber`, `case_number` |
| **Notes** | `q8_additionalNotes`, `additionalNotes`, `notes` |
| **Call Transcript** | `callTranscript` |
| **Call Recording** | `callRecording` |
| **Call Duration** | `callDuration` |

---

## 🎯 How It Works

### 1. JotForm Submission Flow
```
Client calls/chats →
  JotForm AI Agent captures info →
    Form submitted →
      Webhook fired →
        NEXUS receives data →
          Lead created in Airtable →
            Response sent to JotForm
```

### 2. Data Processing

**Step 1:** Webhook receives JSON from JotForm
**Step 2:** Extracts data from `rawRequest` object
**Step 3:** Maps flexible field names to standard format
**Step 4:** Determines channel (Phone, SMS, Web Chat, etc.)
**Step 5:** Builds comprehensive notes (includes transcript if available)
**Step 6:** Calls `handle_lbpc_create_lead()` to create lead
**Step 7:** Returns success/error response

### 3. Channel Detection

The webhook automatically detects the source channel:

- **Phone Call** → If `callRecording` or `callTranscript` exists
- **SMS** → If form title contains "sms"
- **Web Chat** → If form title contains "chat"
- **Web Form** → Default for other submissions

---

## 🔒 Security Considerations

### Current Implementation
- ✅ CORS enabled
- ✅ JSON payload validation
- ✅ Error handling
- ✅ Input sanitization (surplus amount parsing)

### Optional Enhancements
You may want to add:

#### Webhook Secret Verification
```python
# Add to webhook endpoint
JOTFORM_WEBHOOK_SECRET = os.environ.get('JOTFORM_WEBHOOK_SECRET')

# Verify signature
signature = request.headers.get('X-JotForm-Signature')
if signature != JOTFORM_WEBHOOK_SECRET:
    return jsonify({'error': 'Invalid signature'}), 401
```

#### IP Whitelist
```python
# JotForm webhook IPs (example - verify with JotForm docs)
ALLOWED_IPS = ['54.86.50.139', '52.5.218.184', '54.173.33.56']

client_ip = request.remote_addr
if client_ip not in ALLOWED_IPS:
    return jsonify({'error': 'Unauthorized IP'}), 403
```

---

## 📊 Monitoring & Logs

### Console Logs

When a webhook is received, you'll see:
```
================================================================================
JotForm webhook received
================================================================================
Creating LBPC lead from Phone - AI Receptionist:
  Name: John Smith
  Phone: 555-123-4567
  Email: john@example.com
  County: Wayne, Michigan
  Surplus: $25,000.00
  Source: Phone - AI Receptionist
✓ Lead created successfully (ID: rec1234567890)
================================================================================
```

### Error Logs

If something fails:
```
================================================================================
JotForm webhook received
================================================================================
Creating LBPC lead from Web Form:
  Name: John Smith
  Phone: 555-123-4567
  ...
✗ Failed to create lead: Missing required field
================================================================================
```

---

## 🐛 Troubleshooting

### Issue: "Webhook not receiving data"

**Check:**
1. Webhook URL is correct in JotForm
2. Backend server is running
3. Firewall/network allows incoming requests
4. SSL certificate valid (for production)

**Test:**
```bash
# Check if endpoint is reachable
curl http://localhost:5000/webhooks/jotform/test

# Should return endpoint info
```

---

### Issue: "Lead not being created"

**Check:**
1. Backend logs for error messages
2. Airtable API key is valid
3. LBPC Leads table exists in Airtable
4. Required fields in JotForm form

**Debug:**
```bash
# Check backend is running
ps aux | grep api_server

# Check backend logs
tail -f /path/to/logs/api_server.log

# Test with curl (see above)
```

---

### Issue: "Field mapping not working"

**Check:**
1. JotForm field names in webhook payload
2. Field mapping in webhook code matches your form
3. `rawRequest` object structure

**Debug:**
Add temporary logging:
```python
# Add to webhook endpoint
print("Full payload:", json.dumps(data, indent=2))
print("Raw request:", json.dumps(raw_request, indent=2))
```

---

## 🚀 Deployment Steps

### 1. Local Testing
```bash
# Terminal 1: Start backend
cd "NEXUS BACKEND"
python3 api_server.py

# Terminal 2: Test webhook
curl -X POST http://localhost:5000/webhooks/jotform/test
```

### 2. Production Deployment

#### If using Render.com:
1. Push changes to git
2. Render auto-deploys
3. Update JotForm webhook URL to production URL
4. Test with real JotForm submission

#### If using PythonAnywhere:
1. Upload updated `api_server.py`
2. Restart web app
3. Update JotForm webhook URL
4. Test with real submission

### 3. JotForm Configuration

1. **Go to JotForm:** Your AI Agent settings
2. **Navigate to:** Integrations → Add Integration
3. **Select:** Webhook
4. **Configure:**
   - URL: `https://your-backend.com/webhooks/jotform`
   - Method: POST
   - Format: JSON
   - Trigger: On Form Submission
5. **Test:** Submit test form
6. **Verify:** Check Airtable for new lead

---

## 💡 Advanced Features

### Custom Response Handling

You can modify the webhook to return data that JotForm can use:

```python
# In webhook endpoint, modify return
return jsonify({
    'success': True,
    'lead_id': result.get('record_id'),
    'priority_score': priority_score,
    'next_steps': 'A specialist will contact you within 24 hours',
    'confirmation_number': f'LBPC-{result.get("record_id")}'
}), 201
```

Then in JotForm, show this to the caller:
- "Your confirmation number is: LBPC-12345"
- "Priority score: 85/100"

### Conditional Logic

Add custom logic based on lead data:

```python
# High-value lead alert
if surplus_amount > 50000:
    # Send SMS alert to your phone
    send_sms_alert(f"High-value lead: {full_name} - ${surplus_amount:,.2f}")
    
    # Update lead priority
    lead_data['priority_score'] = 100
    lead_data['status'] = 'Hot Lead'

# Attorney-represented leads
if 'attorney' in additional_notes.lower():
    lead_data['notes'] += "\n⚠️ ATTORNEY REPRESENTED - Handle carefully"
    # Notify legal team
```

### Multi-System Integration

Route to different systems based on lead type:

```python
# Determine which system should handle this lead
if surplus_amount > 100000:
    # Route to premium LBPC handler
    result = handle_lbpc_create_lead(lead_data)
    notify_premium_team(lead_data)
elif 'government contract' in additional_notes.lower():
    # Route to GPSS system instead
    result = handle_gpss_create_opportunity(lead_data)
else:
    # Standard LBPC handling
    result = handle_lbpc_create_lead(lead_data)
```

---

## 📈 Analytics

Track webhook performance in Airtable:

### Create View: "JotForm Leads"
- Filter: Lead Source contains "Phone - AI Receptionist" OR "Web Chat" OR "SMS"
- Sort: Created Date (descending)
- Group: Lead Source

### Key Metrics to Monitor
- **Total JotForm leads** (daily/weekly/monthly)
- **Average surplus amount** from phone vs. web vs. SMS
- **Conversion rate** (JotForm leads → clients)
- **Response time** (lead received → first contact)
- **Channel effectiveness** (which channel brings highest-value leads)

---

## ✅ Success Checklist

### Initial Setup
- [x] Webhook endpoint added to `api_server.py`
- [ ] Backend tested locally
- [ ] Test endpoint returns info
- [ ] Test curl command succeeds

### JotForm Integration
- [ ] JotForm AI Agent created
- [ ] Webhook configured in JotForm
- [ ] Field mapping confirmed
- [ ] Test submission successful

### Production Verification
- [ ] Backend deployed to production
- [ ] Production webhook URL updated in JotForm
- [ ] Real test call/submission made
- [ ] Lead appears in Airtable
- [ ] Call transcript captured (if phone call)
- [ ] Logs show successful processing

### Monitoring
- [ ] Webhook logs reviewed
- [ ] Airtable view created for JotForm leads
- [ ] Error alerting configured (optional)
- [ ] Analytics tracking set up

---

## 📞 Support

### Resources
- **Integration Guide:** `JOTFORM_INTEGRATION_GUIDE.md`
- **LBPC Setup:** `LBPC_QUICK_START.md`
- **Backend Docs:** `api_server.py` comments
- **JotForm Docs:** https://www.jotform.com/help/

### Common Questions

**Q: Can I use this webhook for multiple JotForm forms?**
A: Yes! The webhook handles any form submission with the expected fields.

**Q: What happens if a required field is missing?**
A: The `handle_lbpc_create_lead()` function will handle validation and return an error.

**Q: Can I test without creating real leads?**
A: Yes, use the `/webhooks/jotform/test` endpoint or create a test Airtable base.

**Q: How do I see the raw webhook data?**
A: Check backend logs or add `print(data)` to the webhook endpoint.

---

## 🎉 You're All Set!

Your webhook endpoint is ready to receive JotForm submissions and automatically create LBPC leads. 

**Next steps:**
1. Test locally with curl
2. Deploy to production
3. Configure JotForm webhook
4. Make a test call/submission
5. Verify lead creation

**Questions?** Check the logs first, then review the troubleshooting section.

---

**Happy automating!** 🚀📞
