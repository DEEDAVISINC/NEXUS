# Session Context — March 17, 2026
## Read this first in any new chat to get caught up instantly.

---

## WHAT WE DISCUSSED TODAY

### Topic 1: Simplified Acquisitions
- Covered the most common SAP categories (drug testing, MRO, grounds, courier, janitorial, IT, etc.)
- DDI's strongest SAP lanes: drug testing, courier/transport, MRO/supplies, janitorial, grounds

### Topic 2: Corporate / Enterprise Expansion
- Dee wants to go DIRECT to corporate, not just federal contracting
- DDCSS was already built for this — but most of it was non-functional (display only)
- Key insight: corporate is harder than federal because there's no public bid board
- Three real entry points identified: job posting signals, WBENC supplier profiles, corporate supplier portals

### Topic 3: DDCSS Mining — What Was Built Today
We built and deployed `DDCSSProspectMiner` and `DDCSSPortalTracker` into `nexus_backend.py` and `api_server.py`.

**Original mistake caught and corrected:**
- First version used SAM.gov federal prime mining inside DDCSS — WRONG
- SAM.gov finds government contractors, not corporate clients DDI can serve directly
- Dee caught this: "why would DDCSS mine corporate primes on SAM.gov?"
- Removed SAM.gov mining from DDCSS entirely

**Correct DDCSS mining sources (now live):**
1. **Corporate HR Signals** — Google News RSS monitoring for healthcare systems, staffing agencies, manufacturers, logistics companies expanding in Michigan
2. **Job Posting Mining** — Indeed RSS watching for companies hiring notaries, drug testing coordinators, fingerprint techs (budget approved = warm lead)
3. **Diversity News** — Google News RSS for companies announcing supplier diversity initiatives (hot leads)

**Why these work for DDI:** All three target companies DDI can serve DIRECTLY with no government contract and no sub needed. Drug testing via Quest/CRL, fingerprinting via SWFT, notary via signing agent network.

---

## DDCSS CORPORATE PORTAL TRACKER — Built Today

`DDCSSPortalTracker` class added to `nexus_backend.py`.
20 pre-researched corporate supplier portals loaded and ready to seed into Airtable.

**To initialize:** `POST /ddcss/portals/seed`
**To view all portals:** `GET /ddcss/portals`
**To update status:** `PUT /ddcss/portals/<id>`

### Priority Portal List (HIGH priority, register these first):

| Company | Why It's Priority | Services |
|---|---|---|
| **Kelly Services** | Troy, MI — same city as DDI. Drug tests every placed employee. | Drug Testing, Background Screening |
| **General Motors** | WBENC member, mandated WBE spend | Drug Testing, Background Screening, Courier |
| **Ford Motor Company** | WBENC supporter, WBE goals published | Drug Testing, Background Screening |
| **DTE Energy** | Michigan utility, DOT workforce | Drug Testing, Background Screening, Courier |
| **Consumers Energy** | Michigan utility, regulated workforce | Drug Testing, Background Screening |
| **Corewell Health** | Largest Michigan health system (60K+ employees) | Drug Testing, Fingerprinting, Courier |
| **Henry Ford Health** | Detroit-based, all clinical staff tested | Drug Testing, Fingerprinting |
| **Blue Cross Blue Shield MI** | WBENC corporate member, actively seeks WBE vendors | Drug Testing, Background Screening, Notary |
| **Rocket Companies** | Detroit HQ — notary angle for mortgage closings | Drug Testing, Mobile Notary |

---

## KELLY SERVICES — SPECIFIC CONTEXT

**What Dee has tried:** Previously emailed Kelly Services. Got ghosted. No response.

**Why it got ghosted:** Almost certainly hit a general inbox or wrong person, or used a vendor pitch format that gets filtered.

**Correct approach going forward:**
- Find a NAMED person: VP HR, Director Talent Acquisition, or Troy Branch Manager
- Search LinkedIn: "Kelly Services" + "Troy" + "HR" or "Talent"
- Use a one-question email format, NOT a capability statement or vendor pitch

**Draft email ready to use:**
```
Subject: Drug Testing for Your Michigan Placements — Quick Question

Hi [Name],

I'm Dee Davis, President of Dee Davis Inc. — we're also based in Troy and 
provide drug testing and background screening for Michigan employers.

Quick question: are you currently happy with your drug testing vendor for 
placed employees, or is that something you'd be open to a conversation about?

We're EDWOSB and WBENC certified, work with Quest Diagnostics, and can handle 
collections across Michigan without you changing a thing operationally.

Worth a 10-minute call?

Dee Davis
President & CEO, Dee Davis Inc.
Troy, MI | 248.376.4550
```

**Follow-up sequence:** Send initial → follow up at day 4 → follow up at day 11. Most responses come on follow-up 2.

---

## WBENC PORTAL — What Dee Learned Today

- WBENC portal does NOT have a directory for finding corporate clients
- WBENC works in REVERSE: corporations search for DDI, not the other way around
- The value of WBENC is: (1) profile completeness so corps CAN find DDI, (2) WBEC Great Lakes events with corporate buyers, (3) the certified seal for credibility
- **Action needed:** Verify DDI's WBENC profile is 100% complete with all services and NAICS codes listed

**Michigan regional affiliate:** WBEC Great Lakes — this is where corporate buyer matchmaking events happen, not the national portal.

---

## MODEL CLARITY — Three Revenue Models for DDI

This came up today and is important context for any conversation:

**Model 1: GPSS — DDI primes government contract, sub delivers**
DDI wins the federal/state/local contract. DDI manages it. A subcontractor does the physical work. Sub-management framework applies. This is DDI's main current model.

**Model 2: DDCSS Corporate — DDI sells directly to corporate clients**
A corporation's HR pays DDI for drug testing, notary, fingerprinting, or background screening. DDI delivers via its network (Quest/CRL, SWFT, signing agents). NO sub needed. NO government contract. This is what DDCSS is for.

**Model 3: Teaming/Sub — DDI subs to a large federal prime**
Large contractors (Leidos, Boeing, SAIC) need EDWOSB subs to hit diversity goals. DDI slots in to provide a specific service. DDI is the sub. Only works for service lines DDI can deliver directly. NOT the same as SAM.gov prime mining.

---

## NEW API ENDPOINTS ADDED TODAY

All in `api_server.py`:

```
POST /ddcss/run-mining              — runs all 3 mining sources
POST /ddcss/mine-corporate-hr       — healthcare/staffing/manufacturing signals
POST /ddcss/mine-jobs               — job posting mining (Indeed RSS)
POST /ddcss/mine-diversity-news     — diversity initiative news
GET  /ddcss/portals                 — get all corporate portals
POST /ddcss/portals/seed            — initialize portal list in Airtable
PUT  /ddcss/portals/<id>            — update portal status/contacts
GET  /ddcss/portals/dashboard       — registration progress summary
```

---

## IMMEDIATE NEXT ACTIONS

1. **Seed the portal tracker:** `POST /ddcss/portals/seed` — loads 20 portals into Airtable
2. **Kelly Services:** Find a named contact on LinkedIn (Troy, MI office), send the one-question email above
3. **WBENC profile:** Audit completeness — all services, all NAICS codes, current logo, current description
4. **WBEC Great Lakes:** Register for next matchmaking or networking event with corporate buyers
5. **Corewell Health:** Second-highest priority after Kelly — 60K employees, drug tests every hire

---

## FILES MODIFIED TODAY

- `/Users/deedavis/NEXUS BACKEND/nexus_backend.py` — Added `DDCSSProspectMiner` and `DDCSSPortalTracker` classes
- `/Users/deedavis/NEXUS BACKEND/api_server.py` — Added 8 new DDCSS endpoints

---

*Written at end of session March 17, 2026. Any new chat: read this file first.*
