# AIRTABLE ADDITIONS — Incumbent Outreach + GovCon Benchmarks

**Purpose:** Add fields and tables needed for (1) incumbent teaming outreach (Path B from Eric Coffie training) and (2) aspirational woman-owned govcon leaders DDI is modeling after.

---

## PART 1: INCUMBENT OUTREACH INTEGRATION

### 1. GPSS Opportunities (or Federal Forecasts) — ADD THIS FIELD

| Field Name | Type | Description |
|------------|------|-------------|
| **Current Holder** | Single line text | Incumbent company name. Populated when renewal is mined from USAspending. Used for "🤝 Reach Out to Incumbent" button. |

**When it's populated:** Only for records with `[Renewal]` in the Name — mined by `federal_forecasts_system.py` via `POST /gpss/forecasting/mine-renewals`.

---

### 2. Officer Outreach Tracking — ADD TO EXISTING FIELD

**Field:** Outreach Type (Single select)

**Add this option:**
- `Incumbent (Teaming)` — Reaching out to the current prime to offer DDI as sub on their recompete

**Full list of options after update:**
- Forecast (Proactive)
- Closed Opportunity (Reactive)
- **Incumbent (Teaming)** ← NEW

**When used:** When user clicks "🤝 Reach Out to Incumbent" on a renewal forecast. Creates outreach record with:
- Officer Name = incumbent company name (from Current Holder)
- Officer Email = blank or "Research needed" (user finds via research links)
- Letter Content = teaming outreach email draft
- Outreach Type = Incumbent (Teaming)
- Related Forecast = link to the renewal/forecast

---

### 3. Officer Outreach Tracking — OPTIONAL NEW FIELD

| Field Name | Type | Description |
|------------|------|-------------|
| **Research Links** | Long text | URLs to find incumbent contact: SAM.gov search, LinkedIn, Google. Auto-generated when incumbent outreach is created. |

---

### 4. Checklist — Incumbent Outreach Setup

- [ ] Add **Current Holder** to GPSS Opportunities (or Federal Forecasts) table
- [ ] Add **Incumbent (Teaming)** to Outreach Type options in Officer Outreach Tracking
- [ ] (Optional) Add **Research Links** field to Officer Outreach Tracking
- [ ] Add "🤝 Reach Out to Incumbent" button to forecast/opportunity records — show only when Current Holder is not empty
- [ ] Button calls: `POST /api/forecasts/{id}/generate-incumbent-outreach` (to be built)

---

## PART 2: GOVCON BENCHMARKS — Woman-Owned Success Models

**Purpose:** Track woman-owned govcon leaders DDI aspires to match. These are benchmarks for proposal excellence, win rates, and scale.

### 5. NEW TABLE: GovCon Benchmarks (Optional)

| Field Name | Type | Description |
|------------|------|-------------|
| **Name** | Single line text | Expert/company name |
| **Title** | Single line text | Role (e.g., "Proposal Expert", "Enterprise GovCon Expert") |
| **Company** | Single line text | Their company/organization |
| **Certifications** | Single line text | e.g., "CF APMP | Proposal Expert" |
| **Contracts Won** | Single line text | e.g., "$1.7B+", "$45B+" |
| **Win Rate** | Single line text | e.g., "90%+ proposal win rate" |
| **Key Expertise** | Long text | Bullet points (Section M, proposal management, etc.) |
| **Contact** | Single line text | Email or signup (e.g., "govcongiants.org/pb", "hello@govconedu.com") |
| **Source** | Single line text | Where found (e.g., "Govcon Giants Podcast - Feb 2026") |
| **Relevance** | Single line text | Why DDI tracks them (e.g., "Proposal process, Section M training") |
| **Status** | Single select | Tracking, Connected, Learned From |
| **Notes** | Long text | Internal notes |

### 6. Starter Records — Add These

**Record 1: Melissa Palmer**
| Field | Value |
|-------|-------|
| Name | Melissa Palmer |
| Title | CF APMP \| Proposal Expert |
| Company | (Govcon Giants) |
| Certifications | Foundation-certified APMP professional |
| Contracts Won | $1.7B+ in federal contracts won |
| Win Rate | — |
| Key Expertise | • 20+ years proposal management experience<br>• Trained 500+ contractors on proposal writing<br>• Session: Take the Stress Out of Proposals — Build a repeatable proposal process that wins |
| Contact | govcongiants.org/pb |
| Source | Govcon Giants Podcast — Feb 2026 |
| Relevance | Proposal process, repeatable systems, stress reduction |
| Status | Tracking |

**Record 2: Michele Atkinson**
| Field | Value |
|-------|-------|
| Name | Michele Atkinson |
| Title | Enterprise GovCon Expert |
| Company | GovCon Edu |
| Certifications | Section M evaluation expert |
| Contracts Won | $45B+ in federal contracts won |
| Win Rate | 90%+ proposal win rate |
| Key Expertise | • Former evaluator perspective<br>• Section M evaluation expert<br>• Session: Writing to Win — Section M Evaluations (Feb 28, 2026) |
| Contact | email "proposal" to hello@govconedu.com |
| Source | Govcon Giants Podcast — Feb 2026 |
| Relevance | Section M, evaluator mindset, how proposals are scored |
| Status | Tracking |

---

### 7. Checklist — GovCon Benchmarks Setup

- [ ] Create table **GovCon Benchmarks** (optional — can use a simple spreadsheet or Notes if preferred)
- [ ] Add all fields from schema above
- [ ] Add Melissa Palmer and Michele Atkinson as starter records
- [ ] Create view: **By Status** (group by Tracking / Connected / Learned From)
- [ ] Create view: **By Relevance** (filter by proposal, Section M, etc.)

---

## SUMMARY

| Item | Table | Action |
|------|-------|--------|
| Current Holder | GPSS Opportunities | Add field |
| Incumbent (Teaming) | Officer Outreach Tracking | Add to Outreach Type options |
| Research Links | Officer Outreach Tracking | Add field (optional) |
| GovCon Benchmarks | New table | Create + add 2 starter records |

---

*Built for NEXUS — DDI's path to $1B+ in federal contracts. These benchmarks are woman-owned success stories to model.*
