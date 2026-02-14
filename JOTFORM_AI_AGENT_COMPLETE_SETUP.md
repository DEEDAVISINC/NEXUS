# JotForm AI Agent — Complete Setup Reference

**Last Updated:** February 13, 2026
**Agent Name:** Customer Support AI Agent
**Total Conversations:** 87+
**Phone/SMS:** (313) 825-5877

---

## KNOWLEDGE BASE — 14 Entries

| Entry | Topic |
|-------|-------|
| 1 | Company Identity, VAR Model, DBA Names |
| 2 | Certifications & Credentials |
| 3 | Government Contracts & GPSS |
| 4 | Emergency & Disaster Services |
| 5 | Fingerprinting, Drug Testing, DNA Testing (UPDATED PRICING Feb 13) |
| 6 | Professional Services |
| 7 | NEMT & Healthcare |
| 8 | Logistics & Freight |
| 9 | Technology & Partnerships |
| 10 | Call Handling Rules |
| 11 | Confidentiality Rules |
| 12 | Operations & FAQ |
| 13 | Working With DDI (Contractors/Vendors) |
| 14 | Why DDI & Objection Handling |

Files: `/JOTFORM_ENTRIES/ENTRY_1` through `ENTRY_14`

---

## ACTIONS — 23 Total

| # | Name | Trigger Type |
|---|------|-------------|
| 1 | Greeting | Conversation starts |
| 2 | Emergency | User talks about: emergency, disaster, FEMA, urgent |
| 3 | Contracting Officer | User talks about: contracting officer, solicitation, RFP |
| 4 | Schedule Services | User wants to: schedule, book, make appointment |
| 5 | Become a Subcontractor | User wants to: partner, join network, become vendor |
| 6 | Protect Client Info | User asks about: client names, end buyer, contract details |
| 7 | Pricing Inquiry | User asks about: pricing, cost, rates, quote |
| 8 | DOT Compliance | User talks about: DOT testing, CDL, random pool |
| 9 | DNA Testing | User talks about: DNA test, paternity, immigration DNA |
| 10 | Government Capability | User asks about: what you supply, products, capabilities |
| 11 | NEMT / Medical Transport | User talks about: NEMT, Medicaid ride, Uber Health |
| 12 | Notary / Documents | User talks about: notary, document signing |
| 13 | Freight / Logistics | User talks about: freight, shipping, trucking |
| 14 | Lead / Callback Request | User wants to: speak to someone, get a callback |
| 15 | After-Hours / Weekend | User talks about: after hours, weekend, Saturday |
| 16 | Small Talk / Rapport | User talks about: how are you, good morning |
| 17 | Confused / Unsure | User talks about: I'm not sure, someone told me to call |
| 18 | Wrong Number | User talks about: wrong number, who is this |
| 19 | Thank You / Goodbye | User talks about: thank you, that's all, goodbye |
| 20 | Hold / Delay | User talks about: can you hold, one moment |
| 21 | Complaint / Frustration | User talks about: complaint, frustrated, unhappy |
| 22 | Repeat / Clarification | User talks about: say that again, what was the website |
| 23 | Supplier / Vendor Callback | User talks about: returning your call, calling from Graybar/MSC/etc |

Full action details: `/JOTFORM_AI_AGENT_ACTIONS.md`

---

## TOOLS — Configured

| Tool | Status | Purpose |
|------|--------|---------|
| **Take Note** | ACTIVE | Emails info@ and gpss@ when important calls come in |
| **Ask for Information** | ACTIVE | Collects caller data (name, phone, email, company) |
| **Set Appointment (Google Calendar)** | ACTIVE | Books appointments, syncs to bid.deedavisinc@gmail.com |
| **Find in Website** | ACTIVE | Searches deedavis.biz as backup knowledge source |
| **Escalate to Human** | ACTIVE | Hands off complex calls, sends push + email notification |
| **Send Email** | ACTIVE | Sends confirmation emails to callers after interactions |
| **Send Push Notifications** | ACTIVE | Alerts phone for urgent calls (emergencies, COs, escalations) |
| **Get Consent** | ACTIVE | Collects consent + signature for service bookings |
| **Collect Signature** | ACTIVE | E-signatures for service auth, subcontractor agreements |
| **Set Appointment (Basic)** | DISABLE | Replaced by Google Calendar version |
| **Collect Payments** | DEFERRED | Needs JotForm payment form connected to Square |
| **Connect MCP** | SKIPPED | Not needed now |
| **Shopify** | SKIPPED | Not relevant |
| **Take Photo** | SKIPPED | Not relevant |
| **Send API Request** | SKIPPED | Future — for Airtable/NEXUS integration |
| **Trigger Workflow** | SKIPPED | Future — needs workflows built first |
| **Agent Hub** | SKIPPED | Future — for multiple agents |

---

## CHANNELS

| Channel | Status | Number/Link |
|---------|--------|-------------|
| **Phone** | ACTIVE | (313) 825-5877 |
| **SMS** | ACTIVE | (313) 825-5877 |
| Chatbot | Available | Not yet deployed on website |
| WhatsApp | Available | Not yet configured |
| Email | Available | Not yet configured |

---

## EMAIL ROUTING

| Notification Type | Goes To |
|-------------------|---------|
| Client leads, emergencies, COs | info@deedavis.biz |
| Supplier callbacks | gpss@deedavis.biz |
| Escalations | info@deedavis.biz |
| Push notifications | JotForm mobile app |
| Caller confirmations | Sent from info@deedavis.biz |

---

## PRICING (Current as of Feb 13, 2026)

### Fingerprinting
- Per card: $50
- New customer 2-card minimum: $150 (2 cards + travel)
- Zone 1 (0-15 mi): Free | Zone 2 (15-30 mi): $35 | Zone 3 (30-50 mi): $65 | Zone 4 (50+ mi): $100+
- Volume: 16-50/mo $45/card | 51+/mo $40/card statewide

### Drug Testing — DOT
- 5-panel urine: $125 | Breath alcohol: $85 | Random program: $250/yr
- Post-accident: $150 | Return-to-duty: $150

### Drug Testing — Non-DOT
- 5-panel rapid: $75 | 10-panel rapid: $95
- 5-panel lab: $85 | 10-panel lab: $125
- 5-panel hair: $175 | 10-panel hair: $275
- Breath alcohol: $95 | ETG: $65

### Surcharges
- After-hours/emergency: +$125 | Weekend: +$85 | Express results: +$30

---

## STILL TO DO

- [ ] Set up Collect Payments (connect Square to JotForm payment form)
- [ ] Deploy chatbot on deedavis.biz
- [ ] Build subcontractor application form in JotForm
- [ ] Build service authorization form in JotForm
- [ ] Set up Send API to push leads to Airtable/NEXUS
- [ ] Create separate agent for 3D Ink and Livescan (Agent Hub)
- [ ] Add WhatsApp channel
- [ ] Add Email channel
- [ ] Update deedavis.biz with all services and terms page

---

*JotForm AI Agent Setup Complete — February 13, 2026*
