# NEXUS COMMAND REFERENCE

**How to make NEXUS execute automated workflows without friction.**

---

## MAGIC PHRASES (Say These to Trigger Auto-Execution)

### 🔥 OPPORTUNITY INTAKE (Full Auto Sequence)
Say any of these and NEXUS will:
- Score the opportunity
- Create folder structure
- Generate cap statement + buyer email
- Generate RFQ (if products)
- Generate sub outreach (if services)
- Update Airtable
- Present complete package

**Phrases:**
- "I found a solicitation"
- "New opportunity"
- "Bid on this"
- "Respond to this"
- "This RFP/RFQ"
- "Sources sought notice"
- "Presolicitation"
- Upload any solicitation file

---

### 🔄 FOLLOW-UP & STATUS
- "What's the status of [bid name]?"
- "Follow up on [bid]"
- "Next steps for [bid]"
- "Where are we with [solicitation #]?"

**Result:** NEXUS checks state, finds last action, generates follow-up document.

---

### 📋 SUPPLIER RFQ GENERATION
- "Generate RFQ"
- "Create quote request"
- "Send to suppliers"
- "Get pricing"

**Result:** RFQ generated in SEND_TO_SUPPLIER/ with buyer protection applied.

---

### 📄 PROPOSAL GENERATION
- "Generate proposal"
- "Create quote response"
- "Prepare bid submission"
- "Write technical approach"
- "Build compliance matrix"

**Result:** Full quote response with compliance matrix, pricing, ProposalBio applied.

---

### 👥 SUBCONTRACTOR MANAGEMENT
- "Find subcontractor"
- "Sub outreach"
- "Need a sub for [service]"
- "Generate NDA"
- "Generate teaming agreement"

**Result:** Vetting checklist, outreach email, agreements generated.

---

### 🎯 HIT LIST & PRIORITIES
- "What's my hit list?"
- "Show opportunities"
- "What should I bid on?"
- "Find me contracts"
- "Agency targets"

**Result:** Prioritized report of BID NOW opportunities + upcoming deadlines.

---

### 💾 SAVE / REMEMBER
- "Remember this"
- "Save this"
- "Track this"
- "Don't forget"
- "Add to my list"
- "Note this"

**Result:** Written to CURRENT_SESSION_STATE.md and tracked.

---

## WHAT NEXUS DOES AUTOMATICALLY (No Need to Ask)

| If You... | NEXUS Automatically... |
|-----------|----------------------|
| Upload a solicitation | Creates folder, generates cap statement + email, scores opportunity |
| Mention a deadline | Calculates action deadline (minus 5 days), adds to tracking |
| Say "products" | Generates RFQ with buyer protection |
| Say "services" | Generates subcontractor outreach |
| Reference a bid name | Checks status, continues workflow |
| Say "follow up" | Drafts follow-up email based on last action |
| Say "remember" | Saves to session state for next time |

---

## WHAT YOU DON'T NEED TO SAY ANYMORE

❌ "Can you generate a capability statement?"  
✅ Upload the solicitation. It's automatic.

❌ "Create a folder for this bid"  
✅ Say "I found a solicitation." Folder auto-creates.

❌ "Make sure to include the logo"  
✅ Cap statement auto-extracts base64 logo from existing files.

❌ "Don't reveal the buyer name"  
✅ RFQs auto-run protection checklists.

❌ "Use the right phone number"  
✅ All docs auto-use 248.376.4550 per company-info-verification.mdc.

---

## SESSION START

At the beginning of each chat, NEXUS will:
1. Read CURRENT_SESSION_STATE.md
2. Report: "[X] active bids, [Y] upcoming deadlines, [Z] open loops"
3. Ask: "Continue with existing work or new opportunity?"

---

## THE NEW RULE

**NEXUS doesn't ask "Do you want me to...?"**

**NEXUS executes.**

You say: "I found a solicitation."  
NEXUS does: Score → Folder → Cap Statement → Email → RFQ/Sub → Airtable → Report.

One phrase. Full sequence. No friction.

---

*Keep this reference handy. The more you use the magic phrases, the more NEXUS feels like the cohesive automated system it's meant to be.*
