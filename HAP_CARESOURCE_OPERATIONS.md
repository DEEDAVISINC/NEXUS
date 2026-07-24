# CARESOURCE NEMT OPERATIONS — DEE DAVIS INC.

**Contracting party:** **CareSource** (HAP CareSource + Affiliates — per executed agreement, collectively “CareSource”)  
**Plan / brand name:** HAP CareSource MI Coordinated Health (HIDE SNP) — joint venture marketing name on member/provider materials  
**Contract type:** CareSource Provider Agreement + Michigan LTSS Comp Schedule (MA_SNP) — NEMT credentialed service line  
**Vendor ID:** 100000469269 (issued Apr 28, 2026 after CareSource credentialing)  
**Fully executed:** Mar 29, 2026 (DDI) · Mar 31, 2026 (CareSource — Michael Fantoni, National Network & Strategic Sourcing)  
**Executed PDF:** `BIDS:RESOURCES/HAP CARESOURCE NEMT NETWORK/CONTRACTS/CareSource_Michigan_LTSS_MA_SNP_Fully_Executed_2026-03-31.pdf`  
**Go-Live:** Activate in portal — READY NOW  
**Orientation Completed:** May 6, 2026 (Brian Grcevich)  
**Orientation deck (archived):** `BIDS:RESOURCES/HAP CARESOURCE NEMT NETWORK/ORIENTATION/Michigan_Combined_Provider_Orientation_2026_v2.pdf` (125 slides, Jun 2026 v2)

---

## SERVICE AREA

**Source of truth:** `BIDS:RESOURCES/HAP CARESOURCE NEMT NETWORK/CARESOURCE_CONTRACT_SCOPE.md`

| County | Status |
|--------|--------|
| **Wayne County** | ✅ Active (executed contract) |
| **Macomb County** | ✅ Active (executed contract) |
| **Oakland County** | ⏳ Not active — expansion expected soon (confirm with Brian/Dana before claiming live) |

**Not the same contract as MDHHS ModivCare broker MA190000000912** (state tri-county broker — separate opportunity).

**Pharmacy / Rx home delivery:** **Not covered under HIDE SNP / MICH program** — confirmed Brian Grcevich (Jun 2026). Drug benefit = PBM/mail-order (Express Scripts, etc.), separate from LTSS. **VITAL lane is a different MCO contract path** — do not pitch pharmacy courier on HAP HIDE SNP calls.

**Member Population:** ~4,500 members in program (Wayne + Macomb service area per orientation)  
**Ride Benefit:** Unlimited rides (no trip cap)

---

## RATES

**Source:** CareSource call — Jun 2026 ✅ **Confirmed:** ambulatory $28 base, WAV $35 base, **$1.85/mi loaded mileage all trip types**

**HAP pays DDI:** base trip **+ loaded mileage**

| Component | DDI Rate |
|-----------|----------|
| **Standard ride / ambulatory (base)** | **$28.00** |
| **Wheelchair / WAV (base)** | **$35.00** |
| **Loaded mileage (all trip types)** | **$1.85 per mile** |

**Invoice formula:** `Base + (loaded miles × $1.85)`

| Example | Calculation | HAP pays DDI |
|---------|-------------|--------------|
| Ambulatory, 3 mi | $28 + (3 × $1.85) | **$33.55** |
| Ambulatory, 8 mi | $28 + (8 × $1.85) | **$42.80** |
| Ambulatory, 15 mi | $28 + (15 × $1.85) | **$55.75** |
| Wheelchair, 8 mi | $35 + (8 × $1.85) | **$49.80** |
| Wheelchair, 15 mi | $35 + (15 × $1.85) | **$62.75** |

**VERTEX / NEXUS billing:** `nemt_billing.compute_trip_claim()` — base HCPCS (T2002 / A0130) + mileage line (T2003 / A0425) at **$1.85/mi**. Ops must enter **actual loaded mileage** on Mark Complete.

### Fulfillment vs margin (Uber Health — update with mileage)

| | HAP pays DDI | Uber fulfillment (est.) | DDI gross |
|--|--------------|-------------------------|-----------|
| 3 mi ambulatory | ~$33.55 | ~$5–$10 | ~$23–$28 |
| 8 mi ambulatory | ~$42.80 | ~$12–$20 | ~$22–$30 |
| 15 mi ambulatory | ~$55.75 | up to ~$24 | ~$31–$32 |
| Wheelchair, 8 mi | ~$49.80 | Lyft WAV / sub — TBD | TBD |
| Wheelchair, 15 mi | ~$62.75 | Lyft WAV / sub — TBD | TBD |

---

## HOW TRIPS COME TO DDI — TWO-LANE MODEL (Brian Grcevich, Jun 7, 2026)

CareSource confirmed **two transportation categories** for HIDE SNP / Wayne + Macomb:

| Category | Vendor | Routing |
|----------|--------|---------|
| **Medical transport** | **MTM** | Member/provider scheduling — **1-866-733-8997** (orientation deck) |
| **Non-medical transport** | **DDI** (Vendor 100000469269) | **Care manager** creates **service plan** → authorizes trips |
| **Pharmacy / Rx home delivery** | **Not in HIDE SNP** | Brian confirmed — not covered; PBM/mail-order only for drugs |

**Pharmaceutical delivery is out of scope for this program.** Do not bundle VITAL into HAP HIDE SNP positioning.

### DDI intake channels (confirm on Jun 8 call)

1. **Care manager service plan authorization** — primary path per Brian  
2. **Portal queue** — Trip requests in CareSource provider portal (if used for non-medical)  
3. **Direct member/caregiver contact** — **855-773-0035** (PRISM Voice Intake + SMS) — ✅ **LIVE**

**Call scheduled:** Wed **Jun 10, 2026 · 1:00 PM ET** · Brian 317-296-0519 · Prep: `BIDS:RESOURCES/HAP CARESOURCE NEMT NETWORK/BRIAN_ROUTING_CALL_PREP_2026-06-08.md` · `.ics`: `calendars/CARESOURCE_BRIAN_ROUTING_CALL_2026-06-10.ics`

---

## MEMBER CARE LINE — STATUS

| Item | Status |
|------|--------|
| **855-773-0035** (Twilio voice + SMS) | ✅ **LIVE** — tested |
| Inbound → `/prism/voice/inbound` on PA | ✅ |
| Voice agent → PRISM order + NEMT queue | ✅ |
| Post-trip grade SMS from 855 | ✅ |
| QC / MCO audit exports | ✅ |
| **Caller ID (CNAM)** — “DDI” on outbound | ⬜ **ONLY REMAINING** |

**248.376.4550** = President & CEO **personal cell** — email/CO correspondence only; **not** member call center.  
Human handoff (optional): `PRISM_VOICE_TRANSFER_NUMBER` → Google Voice / ops mobile.  
Full setup: `deploy/PRISM_VOICE_INTAKE.md`

### Care Management Contact
| Plan | Phone |
|------|-------|
| Medicaid | 1-844-217-1357 |
| MI Coordinated Health (D-SNP) | 1-833-230-2057 |

---

## FULFILLMENT

DDI dispatches rides through:
- **Uber Health** — Standard rides, ambulatory (**~$5–$24/trip fulfillment cost per Jeff Metz Jun 2, 2026**)
- **Lyft Healthcare** — **Primary for wheelchair (WAV)** — Uber 3P/WAV sparse in Detroit metro (Jun 2, 2026)
- **Wheelchair-accessible partners** — TBD / local vendors as needed

---

## BILLING & PAYMENT

### Claims Submission
- **Method:** Availity clearinghouse or portal upload
- **Payer ID (Medicaid):** MIMCDCS1
- **Payer ID (MI Coordinated Health):** MIMCRCS1
- **Timely Filing:** 365 days from date of service

### Payment
- **First payment:** Paper check
- **After first payment:** Enroll in ECHO EFT
- **ECHO Enrollment:** 1-888-834-3511
- **Payment Frequency:** Twice weekly (Tuesday & Saturday)

### Claim Address (if mailing)
```
HAP CareSource
Attn: Claims Department
P.O. Box 1186
Dayton, OH 45401
```

---

## PORTAL ACCESS

- **Login URL (PRISM Live Portals / daily ops):** https://providerportal.caresource.com/MI/User/Login.aspx?ReturnUrl=%2fMI%2fLogout.aspx
- **HAP provider resources hub:** https://www.hap.org/providers (forms, policies — portal login linked from there)
- **Login:** Set up May 6, 2026 ✅
- **Capabilities:**
  - Check member eligibility
  - View/submit claims
  - View trip requests
  - Track payment history
  - Download EOPs (Explanation of Payment)

---

## KEY CONTACTS

| Department | Medicaid | MI Coordinated Health |
|------------|----------|----------------------|
| **Provider Services** | 1-833-230-2102 | 1-833-230-2159 |
| **Care Management** | 1-844-217-1357 | 1-833-230-2057 |
| **UM Fax** | 1-844-432-8931 | 1-844-633-0399 |
| **Member Services** | 1-833-230-2053 | 1-833-230-2057 |

### ECHO (Payments)
- **Enrollment:** 1-888-834-3511
- **Customer Service:** 1-833-629-9725
- **Fax:** 440-835-5656

---

## REQUIRED TRAINING

| Training | Status | Where |
|----------|--------|-------|
| Provider Orientation | ✅ Completed May 6, 2026 | |
| Model of Care (MI Coordinated Health) | ✅ Attested Jun 7, 2026 | secureforms.caresource.com/ProviderTraining |
| Fraud, Waste & Abuse | ✅ Attested Jun 7, 2026 | secureforms.caresource.com/ProviderTraining |

---

## REVENUE PROJECTIONS

**Member base:** 4,500 members with unlimited rides

| Scenario | DDI Trips/Month | Monthly Revenue | Annual Revenue |
|----------|-----------------|-----------------|----------------|
| Conservative (10% capture) | 180 | $5,000-$6,300 | $60K-$75K |
| Moderate (15% capture) | 810 | $22,700-$28,400 | $270K-$340K |
| Aggressive (20% capture) | 2,160 | $60,500-$75,600 | $725K-$900K |

**High-value recurring members:**
- Dialysis patients (3x/week)
- Chemotherapy patients
- Physical therapy patients
- Behavioral health appointments

---

## IMMEDIATE NEXT STEPS

- [ ] **Walkthrough readiness** — Complete gates in `HAP_CARESOURCE_WALKTHROUGH_READY.md` before scheduling call with CareSource
- [x] **Complete Model of Care training** — ✅ Attested Jun 7, 2026 (secureforms)
- [x] **Complete FWA attestation** — ✅ Attested Jun 7, 2026 (secureforms)
- [x] **Twilio + 855 voice/SMS** — ✅ Live, tested (inbound voice intake + outbound member SMS)
- [x] **PRISM voice → NEMT queue** — ✅ Live on PythonAnywhere
- [x] **Member trip grades + QC MCO packets** — ✅ Live on PA
- [ ] **Caller ID (CNAM)** — ⬜ **ONLY REMAINING** for member care line — register **DDI** display on **855-773-0035** outbound (see `deploy/PRISM_VOICE_INTAKE.md`)
- [ ] **Activate in portal** — Turn on DDI's availability to receive trips
- [ ] **First trip → First claim → First payment**
- [ ] **Enroll in ECHO EFT** after first paper check received

**Walkthrough package:** `HAP_CARESOURCE_WALKTHROUGH_READY.md` · One-pager: `SEND_TO_BUYER/HAP_NEMT_OPERATIONAL_READINESS_ONE_PAGER.md`

---

## ORIENTATION 2026 v2 — KEY INTEL (Jun 2026 deck)

### MICH plan facts (slides 6–7)
- **Counties:** Wayne and Macomb only (Oakland not in deck geography — aligns with Oakland still pending)
- **Population:** 21+, full Medicaid + Medicare enrolled
- **Benefits:** LTSS, behavioral health, no in-network copays/deductibles (Part D exclusions apply)
- **Branded as:** "Next Generation MyCare" internally

### Member-facing NEMT vs DDI contract path (slides 90–91) — READ THIS
HAP's **published vendor** for Medicaid + MICH transportation is **MTM (Medical Transportation Management)**:
- **Member/provider scheduling line:** 1-866-733-8997
- Routine trips: **48 hours** advance (Mon–Fri 7 AM–8 PM ET)
- Urgent/discharge: **24/7/365**
- Deck also cites 30 one-way / 15 round trips under 30 miles annually, then states **no trip limits for covered benefits** — confirm with Brian/Dana which applies to HIDE SNP NEMT line

**Operational meaning (updated Jun 7):** MTM is **correct** for **medical** transport. DDI is **non-medical** under **CM service plan** authorization — not a conflict to escalate; a **lane to operationalize**. Still need written SOP, CM directory, rates/codes for non-medical, and one validation trip.

### Waiver / LTSS (slides 42–51) — separate from NEMT TPA
- Waiver claims via portal (custom fee schedule, ECHO payment, payer of last resort)
- **Provider Sourcing** in portal — waiver service opportunities; case manager creates service plan after "interested"
- **EVV:** HHAeXchange mandatory Jan 1, 2026 for home health / personal care (T1019, etc.) — not DDI NEMT lane unless expanding into PCA

### SDOH / care coordination wedges (slides 104–105, 119–120)
- **Care Managers** connect members to **community support services** — referral path for CWC Digital Navigation
- **Community of Innovation (COI)** — complex members (SDOH, SUD, LTSS, child welfare) — ask Provider Services to connect; aligns with Brian SDOH thread (Vendor 100000469269)
- **Care Management referral:** Portal → refer patient; same phone 1-833-230-2057 (MICH)

### Credentialing / contracting (slide 17)
- **Email:** providernetwork@hap.org
- **Subject must include:** "Credentialing Status" or "Contracting Status"
- **Include:** Type 1 + Type 2 NPI, TIN, provider name, address, phone, preferred email

### Training & compliance (slides 14, 117, 129–130)
| Item | Where |
|------|--------|
| Model of Care (MICH) | hap.org → HAP CareSource → Users → Provider Training → LMS → HealthPlanResources.com — **attest after viewing** |
| Fraud/Waste/Abuse | HealthPlanResources.com — attest in portal |
| Prior auth lookup | procedurelookup.caresource.com → MI MICH |

### Other vendors on deck (slide 90) — not DDI lanes unless expanded
CSS Health (MTM pharmacy), Delta Dental, NationsHearing, EyeMed, **MTM (transport)**, Express Scripts (PBM)

---

## OPERATIONS WORKFLOW

### When a trip request comes in:

1. **Verify member eligibility** — Check portal or call Provider Services
2. **Confirm trip details** — Pickup, destination, date/time, assistance level
3. **Dispatch via Uber Health or Lyft Healthcare** — Book ride through platform
4. **Track ride completion** — Confirm pickup and dropoff
5. **Document trip** — Member ID, date, pickup/dropoff, trip type, driver info
6. **Submit claim** — Via Availity (Payer ID: MIMCDCS1 or MIMCRCS1)
7. **Track payment** — Portal or ECHO

### Trip Documentation Required:
- Member name and HAP CareSource ID
- Date of service
- Pickup and dropoff addresses
- Trip type (standard/ambulatory/wheelchair)
- Confirmation of ride completion

### Member Trip Grade — SMS-First (Audit / Performance Record)

**No phone-call surveys.** After each completed trip, DDI sends a **text from 855-773-0035** with a mobile link to **grade** the ride. Portal is backup only if they log in before grading.

| Grade | Meaning | Numeric (audit export) |
|-------|---------|------------------------|
| **A** | Excellent | 5 |
| **B** | Good | 4 |
| **C** | Fair | 3 |
| **D** | Poor | 2 |
| **F** | Unacceptable | 1 |

Member grades three categories (tap A–F on phone):

| Category | What they grade |
|----------|-----------------|
| **DDI overall** | Program / service experience |
| **Driver / travel companion** | Courtesy, professionalism, assistance |
| **Trip / travel** | Comfort, timeliness, ride quality |

**SMS flow (won't be missed):**
1. **Initial text** ~60 min after dropoff — "Grade your trip (A–F)" + link (~30 sec)
2. **Reminder text** 24h later if no grade submitted (configurable)
3. **Portal gate** — if they open portal before grading, modal blocks next schedule until each ride is graded

- **Grade link:** SMS from **855-773-0035** → mobile form at `/member/survey/{token}`
- **Portal gate:** blocking modal on portal.deedavis.biz before rebook / new NEMT
- **Pending API:** `GET /prism/nemt/satisfaction/pending?email=&order_ids=`
- **Submit API:** `POST /prism/nemt/satisfaction/submit` (JSON grades: `ddi_grade`, `driver_grade`, `trip_grade`)

### Where survey audit records live (PRISM — not VERTEX or COMPASS)

| Store | Path / API | What's in it |
|-------|------------|--------------|
| **Master log** | `uploads/member_satisfaction/survey_log.json` | Every trip grade — pending + completed, full detail |
| **Per-trip archive** | `uploads/member_satisfaction/audit/YYYY/YYYY-MM-DD_{nemt_order_id}.json` | Immutable JSON written when member submits grade |
| **Single trip (HTML)** | `GET /prism/nemt/satisfaction/trip/{nemt_order_id}.html` | Beautiful one-page scorecard — print to PDF |
| **MCO packet (HTML)** | `GET /prism/nemt/satisfaction/mco-packet.html?payer=HAP%20CareSource` | Full summary + trip log — print to PDF for CareSource |
| **Per-trip archive (HTML)** | `uploads/member_satisfaction/audit/YYYY/*.html` | Auto-saved when member grades (matches JSON) |
| **Bulk export (CSV)** | `GET /prism/nemt/satisfaction/export.csv?payer=HAP%20CareSource` | Spreadsheet backup |

Each detailed record includes: member name, payer, trip purpose, driver, grades (A–F + numeric), SMS sent/reminder timestamps, response channel, comments, and **trip_snapshot** (pickup/dropoff, times, mileage, transport type, VERTEX trip ID).

**Billing audits** stay in **VERTEX**. **Contract CO reports** stay in **COMPASS**. **Member trip grade audits** stay in **PRISM** at the paths above.

Include quarterly grade averages + A–F distribution in **MCO audit packets** (open `mco-packet.html` in Chrome → Print → Save as PDF).

**How to build the quality section of an MCO packet:**
1. Open `https://deedavis.pythonanywhere.com/prism/nemt/satisfaction/mco-packet.html?payer=HAP%20CareSource`
2. Click **Save as PDF / Print** — summary stats, grade distribution chart, full trip table
3. Attach individual trip HTML files from `uploads/member_satisfaction/audit/` if requested

**Env:** `MEMBER_SURVEY_DELAY_MINUTES=60` · `MEMBER_SURVEY_REMINDER_HOURS=24` (0=off) · `NEXUS_CONFIRM_BASE_URL` or `PRISM_VOICE_BASE_URL` for links

### Full quality control (not grades alone)

Member trip grades = **Pillar 4** of nine (HAP) / universal framework (all contracts).

**System-wide QC master:** `NEXUS_QUALITY_CONTROL_FRAMEWORK.md`  
**HAP instance:** `BIDS:RESOURCES/HAP CARESOURCE NEMT NETWORK/HAP_QUALITY_CONTROL_PLAN.md`

**Still open for “full QC”:** Mark Complete → VERTEX billing wired in UI, formal grievance log (all lanes), OTP dashboard — see gap tables in both docs.

---

*DDI's first direct MCO NEMT contract — Wayne & Macomb counties, Michigan*
*Created: May 6, 2026*
