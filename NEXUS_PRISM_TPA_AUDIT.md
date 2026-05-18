# NEXUS / PRISM TPA SYSTEM AUDIT

**Audit Date:** May 18, 2026
**Purpose:** Verify all DDI TPA sectors have proper NEXUS/PRISM infrastructure

---

## TPA DIVISION STATUS OVERVIEW

| # | TPA Division | Status | PRISM Module | Service Router | Strategy Doc | Gap |
|---|---|---|---|---|---|---|
| 1 | Drug Testing & Compliance | ✅ Active | ✅ `prism_dot_compliance.py` | ✅ 14 services | ✅ C/TPA Strategy | ⚠️ Collection network mgmt |
| 2 | Identity & Biometric (Fingerprinting) | ✅ Active | ✅ `prism_fingerprinting_compliance.py` | ✅ 4 services | — | ✅ Complete |
| 3 | DNA Testing (DePointe) | ✅ Active | ✅ `prism_dna_compliance.py` | ✅ 4 services | — | ✅ Complete |
| 4 | Notary & Documents | ✅ Active | ✅ `prism_notary_compliance.py` | ✅ 7 services | — | ✅ Complete |
| 5 | Healthcare Transportation (NEMT) | ✅ Active | ✅ `prism_nemt.py` | ✅ 4 services | ✅ State Intel | ⚠️ State enrollment automation |
| 6 | Logistics & Fleet (Freight 1st) | ✅ Active | ❌ Missing | ⚠️ 3 courier services | ✅ Search Strategy | ❌ Need `prism_freight.py` |
| 7 | Background Checks (NCS) | ✅ Active | ❌ Missing | ⚠️ In partner directory only | — | ❌ Need `prism_background_checks.py` |
| 8 | Medical Credentialing | 🟡 Building | ❌ Missing | ❌ Not in catalog | — | ❌ Need full module |
| 9 | Workforce Compliance | 🟡 Building | ❌ Missing | ⚠️ Scattered across modules | — | ❌ Need unified module |

---

## PRISM MODULE INVENTORY

### ✅ OPERATIONAL MODULES (26 files)

**Core Infrastructure:**
| Module | Purpose | Status |
|---|---|---|
| `prism_service_router.py` | Master routing engine, service catalog, pricing | ✅ Comprehensive |
| `prism_orders_api.py` | Order management | ✅ Working |
| `prism_compliance_api.py` | Compliance endpoints | ✅ Working |
| `prism_notifications_api.py` | Alert system | ✅ Working |

**Drug Testing Stack:**
| Module | Purpose | Status |
|---|---|---|
| `prism_dot_compliance.py` | DOT 49 CFR Part 40 compliance | ✅ Working |
| `prism_clearinghouse.py` | FMCSA Clearinghouse integration | ✅ Working |
| `prism_random_pool.py` | Random testing pool management | ✅ Working |
| `prism_bat.py` | Breath alcohol testing | ✅ Working |
| `prism_poct.py` | Point of care testing (instant cups) | ✅ Working |

**Other TPA Modules:**
| Module | Purpose | Status |
|---|---|---|
| `prism_dna_compliance.py` | DePointe DNA collection workflow | ✅ Working |
| `prism_fingerprinting_compliance.py` | Biometric services | ✅ Working |
| `prism_notary_compliance.py` | Notary workflow | ✅ Working |
| `prism_nemt.py` | NEMT dispatch | ✅ Working |
| `prism_occupational_health_compliance.py` | DOT physicals, fit tests | ✅ Working |

**Platform Integrations:**
| Module | Purpose | Status |
|---|---|---|
| `prism_uber_health.py` | Uber Health API | ✅ Working |
| `prism_lyft_healthcare.py` | Lyft Healthcare API | ✅ Working |
| `prism_law_firm_notary_channel.py` | Law firm notary pipeline | ✅ Working |

**Quality & AI:**
| Module | Purpose | Status |
|---|---|---|
| `prism_inspection_engine.py` | Scanback/quality inspection | ✅ Working |
| `prism_qc_learning.py` | QC pattern learning | ✅ Working |
| `prism_document_ai.py` | Document processing | ✅ Working |

**VITAL Subsystem:**
| Module | Purpose | Status |
|---|---|---|
| `VITAL/prism/prism_vital_compliance.py` | VITAL compliance | ✅ Working |
| `VITAL/prism/prism_vital_credentials.py` | VITAL credentials | ✅ Working |
| `VITAL/prism/prism_vital_pod.py` | VITAL POD | ✅ Working |
| `VITAL/prism/prism_vital_sla.py` | VITAL SLA tracking | ✅ Working |
| `VITAL/prism/prism_vital_orders.py` | VITAL orders | ✅ Working |

---

## SERVICE ROUTER CATALOG COVERAGE

**14 Service Lines in `prism_service_router.py`:**

| Service Line | Services Count | Coverage |
|---|---|---|
| Drug Testing | 14 | ✅ Complete (DOT, non-DOT, all panels, hair, POCT) |
| DNA Testing | 4 | ✅ Complete (legal, immigration, informational, siblingship) |
| Fingerprinting | 4 | ✅ Complete (livescan, ink, background bundle) |
| Medical Courier | 3 | ✅ Complete (specimen, route, STAT) |
| NEMT | 4 | ✅ Complete (scheduled, wheelchair, stretcher, brokerage) |
| Prescription Delivery | 4 | ✅ Complete (standard, controlled, cold chain, bulk) |
| Occupational Health | 4 | ✅ Complete (DOT physical, non-DOT, phlebotomy, respirator) |
| Notary | 6 | ✅ Complete (standard, CNTDA, loan signing, RON, apostille) |
| Legal Courier | 1 | ⚠️ Basic (filing only) |
| Permit Runner | 1 | ⚠️ Basic |

**Total: 45 service types defined with routing, pricing, and partner assignments**

---

## GAP ANALYSIS

### ❌ CRITICAL GAPS

#### 1. Background Checks TPA — No Dedicated Module
**Current state:** NCS is in partner directory, no workflow automation
**Impact:** Manual order placement, no credential integration
**Needed:**
- `prism_background_checks.py` — NCS order API, status tracking
- Integration with credentialing bundles in service router
- Automated billing reconciliation

#### 2. Collection Network Management — Drug Testing
**Current state:** Strategy doc exists, no operational system
**Impact:** Can't dispatch 1099 collectors or sub companies from PRISM
**Needed:**
- Collection network module in `prism_service_router.py` or separate `prism_collection_dispatch.py`
- Collector credential tracking (already in SERVICE_REQUIRED_CREDENTIALS)
- Geographic routing for local vs network
- Invoice/payment tracking for 1099 contractors

#### 3. Freight/Logistics TPA — No Module
**Current state:** Mentioned in partner directory, no operational workflow
**Impact:** Freight 1st Direct orders are manual
**Needed:**
- `prism_freight.py` — Load management, carrier dispatch
- Integration with MC-1647572 / DOT-4250594 authority
- TMS-lite functionality

### ⚠️ MODERATE GAPS

#### 4. Medical Credentialing TPA — Building
**Current state:** TPA defined in DDI_TPA_DIVISIONS.md, no PRISM module
**Impact:** Cannot operationalize credentialing contracts
**Needed (per TPA 8 build checklist):**
- [ ] CAQH ProView integration
- [ ] State medical board fingerprinting matrix
- [ ] NPDB querying access
- [ ] License monitoring automation
- [ ] `prism_medical_credentialing.py`

#### 5. Workforce Compliance TPA — Building
**Current state:** TPA defined, scattered across modules
**Impact:** No unified employer compliance dashboard
**Needed (per TPA 9 build checklist):**
- [ ] Unified `prism_workforce_compliance.py`
- [ ] DQ file management
- [ ] I-9 / E-Verify automation
- [ ] EAP network integration
- [ ] Bundled compliance dashboard

#### 6. Courier Services — Incomplete
**Current state:** Medical courier in catalog, pharmacy/lab/legal basic
**Impact:** University Health courier contracts need full operational support
**Needed:**
- Expand courier services in SERVICE_CATALOG
- `prism_courier.py` — unified courier dispatch (medical, lab, pharmacy, legal)
- Integration with Roadie, DoorDash Drive, Uber Health

#### 7. NEMT State Enrollment — Manual
**Current state:** Strategy docs exist, no automation
**Impact:** Manual tracking for TX, NC, AZ enrollment
**Needed:**
- NEMT enrollment tracker module
- State MCO credentialing automation
- Deadline monitoring

---

## PARTNER DIRECTORY STATUS

| Partner | Integrated | API | Notes |
|---|---|---|---|
| Quest Diagnostics | ✅ In router | ⏳ Pending | Need formal C/TPA API access |
| eScreen | ✅ In router | ⏳ Pending | Need partner pricing |
| Concentra | ✅ In router | ❌ Manual | Referral only |
| DDC Laboratories | ✅ In router | ✅ Working | DNA testing |
| AMRO | ✅ In router | ⏳ Pending | MRO workflow |
| Lakota | ✅ In router | ⏳ Pending | Fingerprinting overflow |
| IdentoGO | ✅ In router | ❌ Manual | Referral only |
| Uber Health | ✅ Module | ✅ Working | `prism_uber_health.py` |
| Lyft Healthcare | ✅ Module | ✅ Working | `prism_lyft_healthcare.py` |
| Freight 1st Direct | ✅ In router | ❌ Manual | DDI-owned, no module |
| NCS | ✅ In router | ⏳ Pending | Background checks |
| Roadie | ⏳ New | ⏳ Pending | Pharmacy courier |
| DoorDash Drive | ⏳ Pending | ❌ None | Future |
| 12PanelNow | ✅ In router | ✅ Supply chain | POCT cups |

---

## CREDENTIAL BUNDLES STATUS

**In `prism_service_router.py`:**

| Bundle | Fee | Status |
|---|---|---|
| DDI Agent Baseline | $250 | ✅ Defined |
| Medical Courier Ready | $125 | ✅ Defined |
| Rx Delivery Ready | $125 | ✅ Defined |
| NEMT Driver Ready | $250 | ✅ Defined |
| Drug Testing Collector Ready | $200 | ✅ Defined |
| Notary Signing Ready | $150 | ✅ Defined |
| Field Ops Ready | $200 | ✅ Defined |

**Full Packages:**

| Package | Fee | Status |
|---|---|---|
| Full Rx Delivery Agent | $350 | ✅ Defined |
| Full NEMT Driver | $450 | ✅ Defined |
| Full Drug Testing Collector | $400 | ✅ Defined |

---

## REVENUE TARGET BY TPA

| TPA | Status | Annual Target | PRISM Ready |
|---|---|---|---|
| Drug Testing | Active | $500K–$2M | ⚠️ 85% (need collection dispatch) |
| Fingerprinting | Active | $300K–$1M | ✅ 95% |
| DNA Testing | Active | $200K–$750K | ✅ 95% |
| Notary | Active | $200K–$500K | ✅ 95% |
| NEMT | Active | $2M–$10M | ⚠️ 80% (need state automation) |
| Logistics/Freight | Active | $500K–$2M | ❌ 40% (need module) |
| Background Checks | Active | $250K–$1M | ❌ 50% (need module) |
| Medical Credentialing | Building | $500K–$3M | ❌ 10% |
| Workforce Compliance | Building | $750K–$4M | ❌ 20% |
| **TOTAL** | | **$5.2M–$25.25M** | **65% Ready** |

---

## PRIORITY BUILD LIST

### Phase 1: Immediate (Support Active Revenue)

| Priority | Item | Impact | Effort |
|---|---|---|---|
| 1 | Collection network dispatch in `prism_service_router.py` | Drug testing C/TPA contracts | Medium |
| 2 | `prism_background_checks.py` — NCS integration | Background check contracts | Medium |
| 3 | Expand courier services + `prism_courier.py` | University Health fulfillment | Medium |

### Phase 2: Near-Term (Q2 2026)

| Priority | Item | Impact | Effort |
|---|---|---|---|
| 4 | `prism_freight.py` — Freight 1st Direct | Logistics contracts | Medium |
| 5 | NEMT state enrollment automation | HAVEN expansion | Low |
| 6 | Quest/eScreen API integration | Drug testing scale | High |

### Phase 3: Building TPAs (Q3 2026)

| Priority | Item | Impact | Effort |
|---|---|---|---|
| 7 | `prism_medical_credentialing.py` | TPA 8 launch | High |
| 8 | `prism_workforce_compliance.py` | TPA 9 launch | High |
| 9 | CAQH ProView integration | Credentialing scale | High |

---

## SUMMARY

**What's Working (65%):**
- Core service router with 45 service types ✅
- Drug testing compliance (DOT, POCT, random pools) ✅
- DNA, Fingerprinting, Notary workflows ✅
- NEMT dispatch with Uber/Lyft ✅
- Credential gating and bundles ✅
- Quality inspection and learning ✅

**What's Missing (35%):**
- Collection network management for drug testing ❌
- Background checks workflow (NCS) ❌
- Freight/logistics module ❌
- Courier services expansion ❌
- Medical credentialing TPA ❌
- Workforce compliance TPA ❌

**Bottom Line:** NEXUS/PRISM is ~65% ready for full TPA operations. The core drug testing, identity services, and NEMT are solid. Main gaps are:
1. **Collection dispatch** for drug testing C/TPA model
2. **Background checks** workflow for NCS
3. **Courier services** for University Health
4. **Building TPAs** (credentialing, workforce) need modules

---

*Audit complete. System is operational for current contracts but needs expansion for the C/TPA model and building TPAs.*
