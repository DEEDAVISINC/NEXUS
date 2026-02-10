# ✅ NEXUS URGENT NOTIFICATIONS ONLY

**Updated:** February 5, 2026 @ 6:45 PM EST  
**Change:** Email notifications now ONLY for urgent/critical bids  

---

## 📧 EMAIL NOTIFICATION POLICY:

### **YOU WILL ONLY RECEIVE EMAILS FOR:**

**🔴 CRITICAL (Day 0):**
- Deadline is TODAY
- Email sent if bid not yet submitted
- Subject: "🔴 CRITICAL: [BID ID] DUE TODAY at 2:30 PM!"

**🔴 URGENT (Day 1):**
- Deadline is TOMORROW
- Email sent to remind final review
- Subject: "🔴 URGENT: [BID ID] Due TOMORROW!"

**🟡 URGENT (Day 2):**
- Deadline is in 2 days
- Email sent to complete bid form
- Subject: "🟡 URGENT: [BID ID] Due in 2 Days!"

**🟡 ALERT (Day 3):**
- Deadline is in 3 days
- Email sent to prepare submission
- Subject: "🟡 ALERT: [BID ID] Due in 3 Days"

### **YOU WILL NOT RECEIVE EMAILS FOR:**

❌ Bids > 3 days away (check NEXUS banner instead)  
❌ Daily "all bids" summary (removed)  
❌ Weekly reminders (removed)  
❌ Status updates (check NEXUS)  

---

## 🖥️ WHERE TO SEE ALL BIDS:

### **NEXUS Frontend Notification Banner**
- Open NEXUS: `http://localhost:3000`
- Banner shows at top of every page
- Displays ALL active bids (not just urgent)
- Real-time countdown (auto-refreshes every 5 min)
- Color-coded: 🔴 Red ≤ 2 days, 🟡 Yellow 3-5 days, 🟢 Green 6+ days

**Use this for:** Daily monitoring, planning, overview

---

## 📧 EMAIL NOTIFICATION SCHEDULE:

### **Day -3 (3 days before):**
```
Subject: 🟡 ALERT: RCOC 7732 Due in 3 Days

ACTION: Prepare for submission
- Request any final quotes
- Review all documents
- Verify pricing calculations
```

### **Day -2 (2 days before):**
```
Subject: 🟡 URGENT: RCOC 7732 Due in 2 Days!

ACTION: Complete bid form today!
- Fill out all bid forms
- Upload to BidNet Direct
- Review for accuracy
```

### **Day -1 (1 day before):**
```
Subject: 🔴 URGENT: RCOC 7732 Due TOMORROW!

ACTION: Final review & submit tomorrow morning!
- Final pricing review
- Test upload to platform
- Submit by 10 AM tomorrow (4.5 hours early)
```

### **Day 0 (deadline day):**
```
Subject: 🔴 CRITICAL: RCOC 7732 DUE TODAY at 2:30 PM!

ACTION: SUBMIT NOW!
- Deadline is TODAY at 2:30 PM EST
- Approximately X hours remaining
- SUBMIT IMMEDIATELY
```

---

## 🔕 NO MORE EMAIL NOISE:

### **What Changed:**
**BEFORE:**
- Daily email with all bids (noisy)
- Weekly summaries (redundant)
- Status updates (check NEXUS instead)
- Calendar invites (use NEXUS banner)

**NOW:**
- ✅ ONLY urgent/critical alerts (≤ 3 days)
- ✅ Action-focused (tells you what to do)
- ✅ Clear urgency levels
- ✅ NEXUS banner shows everything else

---

## 🚀 HOW TO USE THE SYSTEM:

### **Daily Workflow:**

**Morning (9 AM):**
1. Open NEXUS: `http://localhost:3000`
2. Check notification banner at top
3. Review all active bids and deadlines
4. Plan your day

**Throughout Day:**
- Check email for URGENT/CRITICAL alerts only
- NEXUS banner auto-updates (refresh every 5 min)
- No need to check calendar files

**Evening:**
- Quick NEXUS check before end of day
- Urgent emails already alerted you if needed

---

## ⚙️ TO RUN THE SYSTEM:

### **Manual Check (anytime):**
```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 send_bid_notifications.py
```

**Output:**
- If bids ≤ 3 days: Sends urgent emails
- If bids > 3 days: "No urgent bids" (no emails sent)

### **Automatic Daily Check (recommended):**
```bash
crontab -e

# Check every morning at 7 AM
0 7 * * * cd /Users/deedavis/NEXUS\ BACKEND && python3 send_bid_notifications.py

# Check every evening at 5 PM
0 17 * * * cd /Users/deedavis/NEXUS\ BACKEND && python3 send_bid_notifications.py
```

---

## 📊 CURRENT ACTIVE BIDS:

| Bid | Deadline | Days Away | Email Alert? |
|-----|----------|-----------|--------------|
| RCOC 7732 | Feb 10 @ 2:30 PM | 5 days | ❌ Not yet (check NEXUS) |
| RCOC 7842 | Feb 17 @ 2:30 PM | 12 days | ❌ Not yet (check NEXUS) |
| RCOC 7814 | Feb 17 @ 2:30 PM | 12 days | ❌ Not yet (check NEXUS) |
| RCOC 7790 | Feb 17 @ 2:30 PM | 12 days | ❌ Not yet (check NEXUS) |

**As of Feb 5, 6:45 PM:**
- No urgent emails sent (all bids > 3 days away)
- All bids visible in NEXUS banner
- Next email: Feb 7 (RCOC 7732 hits 3-day mark)

---

## 🎯 BENEFITS:

**Email Inbox:**
- ✅ Clean (only urgent alerts)
- ✅ Action-focused (tells you what to do)
- ✅ No noise (no daily summaries)
- ✅ Can't miss critical deadlines

**NEXUS Banner:**
- ✅ Always visible (every page)
- ✅ Shows everything (not just urgent)
- ✅ Real-time countdown
- ✅ Color-coded urgency
- ✅ One place to check daily

---

## 📧 EMAIL SETTINGS:

**From:** NEXUS Notifications <bids.deedavisinc@gmail.com>  
**To:** bids.deedavisinc@gmail.com (or info@deedavis.biz)  
**Frequency:** Only when bid ≤ 3 days away  
**Content:** Urgent action items + deadline info  

**To change email:**
```bash
# Edit .env:
USER_EMAIL=your-email@example.com
```

---

## 📝 REMINDER SCHEDULE EXAMPLE:

**RCOC 7732 Paper Products ($81,478):**
- **Feb 7 @ 7 AM:** 🟡 ALERT (3 days) - "Prepare for submission"
- **Feb 8 @ 7 AM:** 🟡 URGENT (2 days) - "Complete bid form today"
- **Feb 9 @ 7 AM:** 🔴 URGENT (1 day) - "Final review & submit tomorrow"
- **Feb 10 @ 7 AM:** 🔴 CRITICAL (0 days) - "DUE TODAY at 2:30 PM - SUBMIT NOW!"

---

## ✅ SUMMARY:

**Emails:** ONLY urgent/critical (≤ 3 days)  
**NEXUS Banner:** Shows everything (check daily)  
**Result:** Clean inbox + never miss a deadline  

---

*Less noise. More action. Always aware.*
