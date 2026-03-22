# MICRO-PURCHASE OUTREACH — SESSION LOG — February 28, 2026

---

## SYSTEM SETUP COMPLETED

### Folder Structure Created
```
BIDS:RESOURCES/MICRO-PURCHASE OUTREACH/
├── TEMPLATES/
│   ├── T01_FEDERAL_SECURITY_CREDENTIALING.md
│   ├── T02_DOT_DRUG_ALCOHOL_TPA.md
│   ├── T03_GOVERNMENT_PROCUREMENT_SUPPLY.md
│   ├── T04_NEMT_HEALTHCARE_TRANSPORT.md
│   ├── T05_EMERGENCY_LOGISTICS_COOP.md
│   └── T06_NOTARY_RON_LEGAL_SERVICES.md
├── TRACKING/
│   └── SESSION_LOG_FEB28_2026.md (this file)
├── SEND_TO_BUYER/
│   ├── DDI_Drug_Testing_TPA_Capability_Statement.html (v3, general)
│   └── DDI_Fingerprinting_SWFT_Capability_Statement.html (v3, general)
└── WEEKLY_ACTION_PLAN.md
```

### NEXUS Contacts Imported
- **58 total contacts** from DDI_Micro_Purchase_Tracker.xlsx
- **8 duplicates caught** (SMART, DDOT, ModivCare, Wayne County, VA Ann Arbor, Dingell VAMC — already in system)
- **51 new contacts imported** into NEXUS with sector tags, priority levels, phone numbers, and template assignments
- All tagged with `MICRO-PURCHASE` in Notes for filtering

### Rules Created
- `.cursor/rules/micro-purchase-outreach.mdc` — Master rule for micro-purchase pipeline
- `.cursor/rules/cap-statement-v3-enforcement.mdc` — Detects old cap statements and regenerates as v3

### Templates Rewritten
- All 6 templates (T01-T06) rewritten to remove beggar language
- New tone: DDI is an experienced firm informing COs of availability, not asking for permission
- Positioning: sole-source eligible, active contracts, ready to execute immediately
- No "I would welcome the opportunity" — replaced with "When [Agency] has a need, we're positioned to execute"

### Cap Statements Generated (v3 Engine)
- **Drug Testing TPA** — general (no agency name), purple color scheme
- **Fingerprinting SWFT** — general (no agency name), forest green + gold
- **Fingerprinting SWFT — NSWC Indian Head** — agency-specific, solicitation N0017426Q1009
- Fingerprinting color scheme updated: lime green replaced with gold accent for better readability

### Outreach Strategy Defined
- **Volume:** 50 contacts per week
- **Method:** Email first, call warm leads when they reply
- **Cadence:** Monday = send batch, Tuesday = follow-ups, Wed-Thu = call warm leads, Friday = update NEXUS + prep next batch
- **Cap statements:** One general per sector for cold outreach, agency-specific only for solicitation responses
- **Three parallel revenue channels confirmed:**
  1. Solicitation Response (active RFPs/RFQs)
  2. Presolicitation / Forecasting (early CO relationships)
  3. Micro-Purchase Outreach (vendor list + BPA development)

---

## EMAILS SENT — February 28, 2026

### Email 1: Kevin Wassom — MDOT Office of Passenger Transportation
- **TO:** kevin.wassom@michigan.gov
- **SUBJECT:** FTA-Compliant C/TPA — CAGE 8UMX3 — 5,100+ Collection Sites — EDWOSB
- **TEMPLATE:** T02 (Drug/Alcohol TPA)
- **ATTACHMENT:** DDI Drug Testing TPA Capability Statement (v3, general)
- **SECTOR:** TPA Drug/Alcohol
- **PRIORITY:** 1-URGENT
- **WHY:** FTA Compliance Specialist overseeing all MI transit agency DAPMs — one contact opens every door
- **NEXUS:** Updated ✅
- **FOLLOW-UP DUE:** March 6, 2026

### Email 2: Dean Peterson — MDOT OPT Procurement Compliance
- **TO:** dean.peterson@michigan.gov
- **SUBJECT:** FTA-Compliant C/TPA — CAGE 8UMX3 — 5,100+ Collection Sites — EDWOSB
- **TEMPLATE:** T02 (Drug/Alcohol TPA)
- **ATTACHMENT:** DDI Drug Testing TPA Capability Statement (v3, general)
- **SECTOR:** TPA Drug/Alcohol
- **PRIORITY:** 1-URGENT
- **WHY:** Procurement Compliance Analyst — procurement side of MDOT OPT
- **NEXUS:** Updated ✅
- **FOLLOW-UP DUE:** March 6, 2026

### Email 3: Barbara Grinder — NSWC Indian Head Division
- **TO:** barbara.j.grinder.civ@us.navy.mil
- **SUBJECT:** N0017426Q1009 — SWFT Fingerprint Services — Quote Submission Status
- **TEMPLATE:** Custom (solicitation status inquiry)
- **ATTACHMENT:** None yet — full quote package ready to send if solicitation is still open
- **SECTOR:** Security/SWFT
- **TYPE:** Solicitation response (not micro-purchase)
- **WHY:** Checking if N0017426Q1009 is still accepting quotes after Feb 11 amendment
- **NEXUS:** Updated ✅
- **FOLLOW-UP DUE:** March 6, 2026
- **NOTE:** v3 fingerprinting cap statement regenerated for this solicitation — ready to attach with full quote response if open

---

## PENDING FOR TOMORROW — March 1, 2026

### Priority 1: SWFT Application Resend
- **ISSUE:** Original SWFT application was sent through ImprovMX before switching to Gmail
- **RISK:** ImprovMX lacks proper SPF/DKIM/DMARC — .mil and .gov servers likely rejected it
- **ACTION:** Find original SWFT application, resend from bids.deedavisinc@gmail.com (CC info@deedavis.biz)
- **ALSO CHECK:** Any other critical emails sent through ImprovMX to .mil/.gov addresses that may need resending

### Priority 2: Continue Micro-Purchase Batch 1
Next contacts in queue:
1. MSP/EMHSD Michigan — emhsd@michigan.gov — Emergency/COOP — T05 (needs main cap statement generated)
2. Candice Fowler — cfowler@smartbus.org — TPA Drug/Alcohol — T02 (check if already contacted from solicitation pipeline)
3. Tianna Leapheart — HR@smartbus.org — TPA Drug/Alcohol — T02 (check if already contacted)
4. SMART Procurement — postmaster@smartbus.org — TPA Drug/Alcohol — T02 (check if already contacted)
5. Gabriele Honey — gabriele.honey@detroitmi.gov — TPA Drug/Alcohol — T02 (check if already contacted)

### Priority 3: Generate Remaining Sector Cap Statements
- [ ] Main / Contract Management (navy/gold) — for T03 and T05 emails
- [ ] NEMT (purple/teal) — for T04 emails
- [ ] Notary (sector color) — for T06 emails

### Email Infrastructure Note
- **SENDING FROM:** bids.deedavisinc@gmail.com (primary outbound)
- **CC:** info@deedavis.biz (business inbox copy)
- **REASON:** Gmail has proper authentication. ImprovMX forwarding was unreliable for .mil/.gov delivery.
- **ALL future outreach uses Gmail as sender**

---

## METRICS — Week 1 (Partial)

| Metric | Count |
|---|---|
| Emails sent (micro-purchase) | 2 |
| Emails sent (solicitation) | 1 |
| Total emails today | 3 |
| NEXUS contacts updated | 3 |
| Cap statements generated (v3) | 3 |
| Templates rewritten | 6 |
| New contacts imported to NEXUS | 51 |
| System rules created | 2 |

---

## KEY DECISIONS MADE

1. **Micro-purchase is a parallel pipeline** — does not replace solicitation response or presolicitation forecasting
2. **Email first, call warm leads** — volume approach at 50/week, not phone-first
3. **General cap statements per sector** for cold outreach — agency-specific only for solicitation responses
4. **No beggar language** — DDI positions as experienced firm informing COs of availability
5. **Micro-purchase wins build CPARS** — the real goal is BPAs that generate rated past performance for IDIQs
6. **SWFT and Drug Testing are fastest win sectors** — existing infrastructure, zero ramp-up
7. **ImprovMX is unreliable for .gov/.mil** — all outbound email now through Gmail

---

*Session ended Feb 28, 2026. Resume March 1 with SWFT application resend + micro-purchase batch continuation.*


### Email 4: Joy Nakfoor — Michigan DTMB (NEMT backup contact)
- **TO:** nakfoorj@michigan.gov
- **CC:** govem1@michigan.gov
- **SUBJECT:** RE: NEMT Brokerage Re-Procurement Inquiry — Contract MA190000000912 — EDWOSB
- **TYPE:** NEMT re-procurement follow-up
- **NEXUS:** Updated ✅

### Email 5: SMART Procurement
- **TO:** postmaster@smartbus.org
- **SUBJECT:** FTA-Compliant C/TPA — CAGE 8UMX3 — 5,100+ Collection Sites — EDWOSB
- **TEMPLATE:** T02
- **NEXUS:** Updated ✅

### Email 6: Gabriele Honey — DDOT DAPM
- **TO:** gabriele.honey@detroitmi.gov
- **SUBJECT:** FTA-Compliant C/TPA — CAGE 8UMX3 — 5,100+ Collection Sites — EDWOSB
- **TEMPLATE:** T02
- **NEXUS:** Updated ✅

### Email 7: Tianna Leapheart — SMART HR
- **TO:** HR@smartbus.org
- **SUBJECT:** FTA-Compliant C/TPA — CAGE 8UMX3 — 5,100+ Collection Sites — EDWOSB
- **TEMPLATE:** T02
- **NEXUS:** Updated ✅


### Email 8: RTA of Southeast Michigan
- **TO:** info@rtamichigan.org
- **SUBJECT:** FTA-Compliant C/TPA — CAGE 8UMX3 — 5,100+ Collection Sites — EDWOSB
- **TEMPLATE:** T02
- **NEXUS:** Updated ✅


### Email 9: Marie Stewart — MTA Flint
- **TO:** mstewart@mtaflint.org
- **SUBJECT:** FTA-Compliant C/TPA — CAGE 8UMX3 — 5,100+ Collection Sites — EDWOSB
- **TEMPLATE:** T02
- **NEXUS:** Updated ✅


### Email 10: The Rapid (Grand Rapids) — Title VI Coordinator
- **TO:** TitleVI@ridetherapid.org
- **SUBJECT:** FTA-Compliant C/TPA — CAGE 8UMX3 — 5,100+ Collection Sites — EDWOSB
- **TEMPLATE:** T02
- **NEXUS:** Updated ✅


### Email 11: CATA Lansing
- **TO:** info@cata.org
- **SUBJECT:** FTA-Compliant C/TPA — CAGE 8UMX3 — 5,100+ Collection Sites — EDWOSB
- **TEMPLATE:** T02
- **NEXUS:** Updated ✅


### Email 12: DTE Energy
- **TO:** supplierdiversity@dteenergy.com
- **CC:** procurement@dteenergy.com
- **SUBJECT:** DOT-Compliant C/TPA Services — CAGE 8UMX3 — EDWOSB
- **TEMPLATE:** T02
- **NEXUS:** Updated ✅


### Email 13: DTE Energy Named Buyers
- **TO:** matthew.brunette@dteenergy.com
- **CC:** corey.moore@dteenergy.com; jamie.evans@dteenergy.com
- **SUBJECT:** DOT-Compliant C/TPA Services — CAGE 8UMX3 — EDWOSB
- **TEMPLATE:** T02
- **NEXUS:** Updated ✅


### Email 14: Selfridge ANGB — 127th Wing Public Affairs (Routing)
- **TO:** 127.wg.127.wg.pa.org@us.af.mil
- **SUBJECT:** Routing Request — SWFT Credentialing & Compliance Support — CAGE 8UMX3
- **TYPE:** Routing follow-up (requesting Personnel Security/Provost Marshal POC)
- **NEXUS:** Updated ✅
