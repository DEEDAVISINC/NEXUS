# NEMT State-by-State Profiles — CCAM-TAC Reference

**Last Updated:** June 14, 2026  
**Source:** CCAM-TAC → **NEMT State by State Profiles** (Texas A&M TTI + RLS & Associates; prepared for CTAA/NCMM)  
**URL:** https://www.ccam-tac.org → Resource Central / NEMT State by State Profiles  
**Profile vintages:** Mostly **Sep–Dec 2024**; some **Apr–Feb 2025** (Idaho, Minnesota, Tennessee). **Verify before any bid** — Medicaid NEMT changes fast. Submit updates: info@ccam-tac.org · subject **"NEMT State Profile Update"**

**Status:** Reference library — not a solicitation. Use for **GO/NO-GO**, entry-path selection, and proposal language.

**Related:** `NEXUS_LEARNING/CCAM_FTA_COORDINATION_INTEL.md` · `NEXUS_LEARNING/NEMT_CONTRACT_SLICE_STRATEGY.md` · `NEXUS_LEARNING/MODIVCARE_COMPETITIVE_INTEL.md`

---

## Why this matters to DDI

Federal/CCAM framing matches DDI's model: coordinated human-services transport evolves into **integrated brokerage** — one entity schedules and collects payment for trips performed by several providers.

These profiles answer, per state:
- **Who buys** NEMT (state FFS, state broker, MCO carved-in, county MATP, mixed)
- **Who to call** (member protocol)
- **How providers enroll** (broker network vs county vs MCO)
- **Public transit role** (passes, paratransit integration, broker-as-transit)

**Lane:** **MOB-A** (plan NEMT TPA) only — not HAVEN (MOB-B) or freight (MOB-C).

---

## NEMT model taxonomy (Table 1, Sep 2024)

| Model | # States | Entry implication for DDI |
|---|---|---|
| **Directly operated** (state/county FFS) | 7 | Credential with **state/county** or sub to local provider; no statewide broker RFP |
| **Regional broker — state contract** | 9 | **Regional slice / teaming** with incumbent broker or bid region (Maine, Arkansas, Kentucky, etc.) |
| **Regional broker — MCO contract** | 3 (+ OR split) | **MCO credentialing** path — same as HAP CareSource wedge |
| **Statewide broker — state contract** | 11 | State NET RFP (Nevada, Wisconsin, Missouri, NY, etc.) or **vendor network under broker** |
| **Statewide broker — MCO** | 1 (TN) | MCO broker panel |
| **Mixed** | 21 | Read both FFS/broker **and** MCO paths — Michigan is here |

**National split:** ~41% mixed · ~23% statewide broker · ~22% regional broker · ~14% directly operated (KFF/MCO enrollment ~74% of beneficiaries — MCO path dominates new entry).

**Carved in vs carved out:** Carved **out** = state/broker runs NEMT for all or FFS members. Carved **in** = each MCO contracts its own broker/vendor — **DDI's live HAP path**.

---

## DDI entry path by model (decision matrix)

| If state profile shows… | DDI first move | Prime realistic? |
|---|---|---|
| **MCO carved-in NEMT** | MCO transport credentialing / plan-line vendor (HAP model) | **Yes** as TPA/vendor to plan |
| **State/regional broker** | Slice with broker, regional teaming, or network provider enrollment | **Rarely** sole statewide broker — see slice strategy |
| **County FFS / MATP** (PA, MD, OH JFS) | County RFP or local health dept enrollment | Regional prime or sub |
| **Transit agency as broker** (OR, VT, parts of WA/MA) | Teaming with RTA/CAA — coordination tech angle | Sub / coordination partner |
| **Directly operated + mileage** (WY, parts of AL) | Low-volume — usually skip unless strategic |

**Never name** trip brokers (ModivCare, MTM, etc.) in **cold buyer outreach** — use in internal intel and teaming only (`never-name-subvendors-network.mdc`).

---

## MICHIGAN — profile + NEXUS crosswalk

**Model (profile):** Mixed — **Directly Operated + Regional Transportation Brokers (state contract)**  
**CMS Region:** 5 · **Profile date:** September 2024

| Topic | CCAM-TAC profile | NEXUS current intel (verify at bid time) |
|---|---|---|
| **Administration** | MDHHS — in-house FFS + MCOs for dental/SUD/CMH | Same |
| **NEMT default** | **Carved out** of MCOs — FFS NEMT for most counties | **Oct 2024+ policy:** MCO **carve-in** for plan-managed NEMT accelerating — dual track |
| **Tri-county / statewide FFS broker** | Wayne, Oakland, Macomb — **regional broker** (ModivCare); MDHHS signaling **statewide FFS** expansion | Contract **MA190000000912** expires **Jul 31, 2026** · **RFP 260000002254** anticipated **Aug 2026** · SIGMA **9S301** |
| **Rest of state** | County MDHHS offices — FFS rate schedule by mode | SHIELD/NEMT FFS rates in `SHIELD_REVENUE_MODEL.md` |
| **Member access** | County MDHHS or tri-county broker | **HAP CareSource** = separate **MCO vendor** path (Vendor 100000469269) — do not conflate with state broker |
| **Providers** | MDHHS rate schedule; broker network in tri-county | DDI TPA — fulfillment under contract management |
| **Public transit** | Reimburse public fares | Plan/broker mode assignment |

**DDI strategy (unchanged):**
1. **MCO wedge (live):** HAP + scheduled HIDE SNP MCO outreach — carved-in lane  
2. **State broker slice (watch):** RFP **260000002254** (Aug 2026) — **one vendor on contract**, not ModivCare replacement fantasy · `NEMT_CONTRACT_SLICE_STRATEGY.md`  
3. **Do not merge** state broker narrative with HAP MCO vendor narrative in same email

---

## Active pipeline states — quick profile pull

Use full CCAM-TAC page for detail. Snapshot from profiles:

| State | Model (2024 table) | Broker / buyer notes | NEXUS folder / watch |
|---|---|---|---|
| **MI** | Mixed | Tri-county broker + county FFS; carve-in shift | `MDHHS NEMT BROKERAGE/` · HAP live |
| **ME** | Regional broker (state) | 8 regions; ModivCare statewide award contested | `MAINE NEMT TEAMING/` · 0520260310 |
| **TX** | Mixed | MCO carved-in + HHSC interim broker | `TEXAS MEDICAID DRTS/` · HHS0016482 |
| **NV** | Statewide broker (state) | MTM statewide; dual-eligible paratransit integration | `NEVADA NET BROKER/` |
| **AZ** | Mixed | AHCCCS — MCO regional brokers + state FFS for AIHP | `RADAR HEALTHCARE MCO/AZ_AHCCCS_EXPLORATION.md` |
| **NC** | Mixed | NEMT carved **into** MCOs Jul 2021; DSS for FFS slice | `NC_MEDICAID_EXPLORATION.md` |
| **OH** | Mixed | County JFS + MCE brokers; **ICAM pilot** (SE Ohio regional resource center) | ICAM intel · county JFS RFPs |
| **FL** | Mixed | AHCA + MCO brokers | `FL COMMUNITY CARE PLAN NET DEBRIEF/` |
| **PA** | Mixed | MATP county FFS; Philadelphia ModivCare region | County MATP entry |
| **KY** | Regional broker (state) | HSTD five regions | `LEXINGTON` drug testing lane separate |
| **LA** | Mixed | Verida statewide FFS + MCO brokers | HAVEN geography |
| **WI** | Statewide broker | MTM statewide | MCO + broker dual check |

---

## Incumbent broker concentration (internal intel only)

Profiles reference these brokers repeatedly — **competitors/teaming targets**, not names for outbound copy:

| Broker | Common states (profile sample) |
|---|---|
| **ModivCare** | DE, GA, IN, LA, ME, MS, NJ, OK, PA (Phila), SC, UT, VA FFS, WV, WI mix, MI tri-county |
| **MTM** | CT, DC FFS, ID, IA FFS, MO, NV, RI, WI |
| **Verida** | AR, GA (with ModivCare), IN FFS, LA FFS, TN (with other) |
| **Access2Care** | IA MCO, KS (Aetna), VA MCO |
| **Penquis / Waldo CAP** | ME regions (teaming — DDI path) |

---

## Concepts to cite in proposals (from profile intro)

- **Fee-for-service vs managed care** — who holds risk and who buys transport  
- **Carved in vs carved out** — plan vendor vs state broker  
- **Directly operated vs brokered** — fleet owner vs coordinator  
- **Mixed models** — most states; DDI must classify **which track** per member population  

**Ohio note:** Profile cites active **ICAM grant** for SE Ohio regional transportation resource center — real-world ICAM + NEMT coordination example (`CCAM_FTA_COORDINATION_INTEL.md`).

---

## How NEXUS should use this

1. **Before any new NEMT state bid:** Read that state's CCAM-TAC profile → classify model → pick entry path from matrix above  
2. **Before MCO email:** Confirm carved-in vs carved-out — wrong opener kills credibility  
3. **Quarterly:** Spot-check MI + pipeline states for profile date drift; grep CCAM-TAC news for model changes  
4. **Do not** paste broker names or profile text into buyer-facing docs without tailoring and verification  

---

## Acknowledgment (source)

Sponsored by FTA (5314 TA) via NCMM/CTAA. Authors: Suzie Edrington, Christy Campoll, Ross Peterson (TTI/RLS).

---

*50-state profiles = map, not gospel. Michigan + active pipeline rows above are pre-loaded; full text lives on CCAM-TAC.*
