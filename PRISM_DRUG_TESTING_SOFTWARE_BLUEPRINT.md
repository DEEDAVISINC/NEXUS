 # PRISM Drug Testing Software Blueprint
 ## Replicate + Improve + Integrate
 
 **Created:** March 9, 2026  
 **System:** PRISM (NEXUS Module #8)  
 **Goal:** Build a PRISM-native drug/alcohol testing platform that matches market leaders and outperforms on compliance, failover, and govcon readiness.
 
 ---
 
 ## 1) Product Goal
 
 Build a single PRISM module for:
 - Employer onboarding
 - Test ordering
 - Collection site routing
 - Random program management (DOT + non-DOT)
 - eCCF / chain-of-custody workflows
 - MRO workflow
 - Results ingestion and reporting
 - Contract-grade compliance exports
 
 This becomes the operating core for DDI's drug testing lane.
 
 ---
 
 ## 2) What To Replicate (Baseline Features)
 
 ### A. Account Setup
 - Employer account onboarding
 - Service selection (DOT, non-DOT, occ health)
 - Volume and location profile
 
 ### B. Collection Network Access
 - Nationwide site lookup by ZIP/city
 - Service availability by site (urine, hair, BAT, oral fluid)
 - Hours and after-hours flags
 
 ### C. Test Ordering
 - Single order
 - Batch order upload
 - Policy-based test panel defaults
 - Donor registration and appointment scheduling
 
 ### D. Program Management
 - Random draw automation
 - DER dashboard
 - Consortium logic
 - Event-driven tests (post-accident, reasonable suspicion, return-to-duty)
 
 ### E. Results + MRO
 - Result status lifecycle
 - MRO review queue
 - Negative/positive disposition
 - Audit history
 
 ### F. Reporting
 - Client reports
 - DOT logs
 - Program compliance reports
 - Downloadable records for bids/audits
 
 ---
 
 ## 3) What To Perfect (PRISM Differentiators)
 
 ### 1. Multi-Lab Failover (Critical)
 Do not hardwire to one vendor.
 
 Add a **Lab Abstraction Layer**:
 - Primary vendor by account
 - Secondary vendor fallback
 - Site-level fallback if service unavailable
 - SLA tracker (response time, result turnaround, exception rate)
 
 ### 2. Government Contract Mode
 Add "GovCon Profile" per client/contract:
 - Required panel (for example: 15-panel)
 - Confirmation rules (both positive and negative if required)
 - Site radius requirements
 - Required documentation packet
 - Submission deadlines + reminders
 
 ### 3. Compliance Packet Generator
 One-click export bundle:
 - Certifications
 - SOP summaries
 - Chain-of-custody documentation
 - MRO credentials
 - Site list and distances
 - Turnaround SLA evidence
 
 ### 4. Rules Engine by Opportunity
 Attach bid-specific rules to each order stream:
 - "All results confirmed"
 - "RBT-IV required"
 - "Within 20 miles of facility"
 
 ### 5. Vendor Performance Scorecard
 Score each vendor monthly:
 - Responsiveness
 - Fill-rate
 - Error rate
 - Cost variance
 - Turnaround time
 
 Auto-demote underperformers.

### 6. BioChain QA Engine (Drug + DNA Error Prevention)
PRISM needs a notary-grade (or better) prevention layer for clinical workflows.

**Quality gates before order can close:**
- `SITE_READY` gate (facility/equipment/compliance readiness)
- `COLLECTOR_READY` gate (credentials, proficiency, expiration checks)
- `COLLECTION_COMPLETE` gate (required fields/documents complete)
- `CHAIN_COMPLETE` gate (full chain-of-custody timeline intact)
- `RESULTS_COMPLETE` gate (confirmations/MRO status meet contract rules)
- `RELEASE_APPROVED` gate (all contract-specific requirements satisfied)

**Hard-stop errors (cannot close order):**
- Missing donor/signer identity verification
- Missing collector signature/date/time
- Missing specimen seal ID or mismatch across forms
- Missing transfer custody event (collector -> courier -> lab)
- Missing or invalid panel mapping to contract rule
- Missing confirmation where required (including all-negative confirmation contracts)
- Missing MRO disposition where required
- Missing DNA COC witness/collector attestations

**DNA-specific controls:**
- Chain-of-custody form completeness score
- Photo evidence required at each custody handoff (if contract/client requires)
- Swab kit lot/expiration tracking
- Related-party conflict attestation (collector relationship disclosure)
- Specimen tamper flag workflow

**Drug-testing-specific controls:**
- CCF/eCCF field validation (DOT vs non-DOT logic)
- BAT flow validation (RBT-IV / confirmation path when threshold met)
- Random draw integrity logs (selection proof + notification timestamps)
- Collection site radius compliance check (for bid-specific location constraints)
- Turnaround SLA breach alerts
 
 ---
 
 ## 4) PRISM Data Model Extensions
 
 Add these tables (or equivalent models):
 
 1. `PRISM_DRUG_PROGRAMS`
 - Client, DOT/non-DOT, random cadence, panel policy, MRO policy
 
 2. `PRISM_TEST_PANELS`
 - Panel code, analytes, DOT flag, confirmation policy, pricing bands
 
 3. `PRISM_COLLECTION_SITES`
 - Site details, services, hours, emergency flag, vendor source
 
 4. `PRISM_VENDOR_CONNECTORS`
 - Vendor name, API status, auth, SLA, fallback priority
 
 5. `PRISM_DRUG_ORDERS`
 - Order intent, panel, reason, donor, appointment, current status
 
 6. `PRISM_CHAIN_OF_CUSTODY`
 - CCF/eCCF IDs, specimen IDs, custody timestamps, photo evidence
 
 7. `PRISM_MRO_CASES`
 - Result review, physician notes, disposition audit trail
 
 8. `PRISM_RANDOM_POOLS`
 - Pool roster, draw history, selected/notified/collected flow
 
 9. `PRISM_COMPLIANCE_EXPORTS`
 - Generated package history by contract/opportunity

10. `PRISM_SITE_READINESS`
- Site audit checklist, equipment readiness, hours verification, emergency capability, policy docs

11. `PRISM_COLLECTOR_CREDENTIALS`
- DOT collector qualification, BAT cert, DNA collector training, expiration tracking, proficiency checks

12. `PRISM_QA_EVENTS`
- Validation events, rule failures, severity, remediation owner, timestamps, closure evidence
 
 ---
 
 ## 5) API Layer (Suggested Endpoints)
 
 - `POST /prism/drug-programs`
 - `POST /prism/drug-orders`
 - `POST /prism/drug-orders/batch`
 - `GET /prism/collection-sites/search`
 - `POST /prism/random-pools/{id}/draw`
 - `POST /prism/coc/upload`
- `POST /prism/site-readiness/verify`
- `POST /prism/collector-readiness/verify`
- `POST /prism/qa/validate-order/{order_id}`
 - `POST /prism/results/ingest`
 - `POST /prism/mro/{id}/disposition`
- `POST /prism/release-gate/{order_id}/approve`
 - `GET /prism/compliance/export/{contract_id}`
 - `GET /prism/vendor-scorecards`
 
 ---
 
 ## 6) UI/UX Inside PRISM
 
 Add a **Drug Testing Workspace** under PRISM:
 
 Tabs:
 1. Programs
 2. Orders
 3. Random Draws
 4. Collection Sites
 5. MRO Queue
 6. Compliance Exports
 7. Vendor Health
8. QA Gates
9. Site Readiness
10. Collector Credentials
 
 Key widgets:
 - Today collections
 - Awaiting MRO
 - Overdue confirmations
 - Site coverage gaps
 - Vendor SLA alerts
- Orders blocked by QA gate
- Expiring collector certifications
- Chain-of-custody exceptions
 
 ---
 
 ## 7) Build Plan (Phased)
 
 ### Phase 1 (2 weeks) - Core Operations
 - Program setup
 - Order entry
 - Site search
 - Manual results tracking
 - Basic reporting
 
 ### Phase 2 (2-3 weeks) - Compliance + Random
 - Random pool engine
 - Chain-of-custody records
 - GovCon rules
 - Compliance export v1
- BioChain QA gates (site/collector/collection/chain/release)
 
 ### Phase 3 (2-3 weeks) - Integrations
 - Vendor connectors (Quest/Labcorp/eScreen/CRL or aggregator)
 - Result ingestion automation
 - MRO queue workflow
 - Fallback routing
 
 ### Phase 4 (ongoing) - Optimization
 - Vendor scorecards
 - SLA alerting
 - Predictive coverage gaps
 - Margin optimization by panel/vendor
- QA false-positive tuning + adaptive rule confidence scoring
 
 ---
 
 ## 8) Operating Policy
 
 - Never depend on one vendor for all panels.
 - Every active contract must have primary + fallback path.
 - Every opportunity must have registration timing decision logged:
   - Register now / after award / subcontract route.
 - Every order flow must be auditable end-to-end.
- No order closes unless all QA release gates pass.
- DNA and drug workflows use separate validation templates with shared audit logging.
 
 ---
 
 ## 9) Immediate Next Actions
 
 1. Add PRISM drug data tables.
 2. Build order + site lookup UI.
 3. Implement GovCon rules profile per opportunity.
 4. Stand up compliance packet generator for active bids.
 5. Activate vendor scorecard tracking from day 1.
6. Implement BioChain QA release gates before automation scale-up.
 
 ---
 
 ## Bottom Line
 
 Replicate the market baseline, but win on:
 - multi-vendor resilience,
 - govcon-grade compliance exports,
 - and PRISM-native execution speed.
 
 That's how DDI turns vendor chaos into a controlled operating system.
