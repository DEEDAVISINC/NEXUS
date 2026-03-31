# Federal IDIQ & Contract Vehicles — NEXUS Index

**Purpose:** One place to see **major** multi-agency and high-volume vehicles + **how** to query the real universe (there is no static “all IDIQs” file anywhere — awards and vehicles change daily).

**Related:** `IDIQ_GOVCON_KNOWLEDGE.md` (strategy, task-order math, Coffie framework).

---

## 1. Why “a list of all IDIQs” doesn’t exist as one download

| Reality | Implication |
|--------|-------------|
| **IDIQ** is a *contract type* (FAR 16.504), not one program | Same name covers GSA-wide pools, Army MATOCs, VA lab couriers, etc. |
| **Thousands** of active IDIQs/MACCs/MATOCs/BPAs | Agency- and region-specific (e.g., each USACE district). |
| New vehicles **solicit** on SAM.gov; existing vehicles issue **task orders** often **not** on SAM.gov | You see **vehicle** at competition time; **work** often flows as TOs on agency portals / eBuy. |

**Operational definition:** “List all IDIQs” → pick **(a)** government-wide **GWACs/schedules** you can **apply to**, **(b)** **agency** vehicles in your NAICS, **(c)** **USASpending** / **FPDS** exports filtered by contract type — not one PDF.

---

## 2. Government-wide & multi-agency vehicles (names to know)

*Ceilings are order-of-magnitude public references — verify in current GSA/agency docs before proposals.*

| Vehicle / family | Focus | Notes |
|------------------|-------|--------|
| **GSA MAS** (Multiple Award Schedule) | Products, services, solutions | “Schedule” — massive; task orders via **eBuy** + agency direct. |
| **OASIS+** | Professional services — now **13 domains** (Phase II, Jan 2026 adds five: Business Admin, Human Capital, Financial Services, Marketing & PR, Social Services) | Primary federal lane for **consolidated** professional services per GSA/category-management direction. **SB pools are restricted to certified small businesses** — large primes cannot prime those pools. Strategy write-up: `OASIS_PLUS_FEDERAL_PROFESSIONAL_SERVICES_STRATEGY.md`. Solicitation example: **47QTCH23R0029** (WOSB — `FORECAST_OPPORTUNITIES_TRACKER.md`). |
| **Polaris GWAC** | IT services (GSA) | WOSB and other pools; see `FORECAST_OPPORTUNITIES_TRACKER.md` — **47QTCB22R0003**. |
| **Alliant 3** | Enterprise IT (GSA) | Large IT GWAC family. |
| **CIO-SP4** (NITAAC / NIH) | Health IT, cyber, cloud, etc. | Common for health-adjacent IT. |
| **NASA SEWP** (e.g. SEWP VI) | IT products, software, cloud | Product-heavy; agency task orders. |
| **8(a) STARS III** | 8(a) IT | DDI not 8(a) — team only unless/until certified. |
| **HCaTS** (Human Capital and Training Solutions) | HR, training, organizational development (GSA GWAC family) | **~$5.7B** ceiling — verify current figure on [gsa.gov/hcats](https://www.gsa.gov/hcats). **User intel (Mar 2026):** vehicle reportedly **stops accepting new orders Nov 2026** — confirm dates on GSA master contract / PMO before planning; if accurate, **get on contract or under a HCaTS prime before that window** to compete for task orders. PMO: **hcats@gsa.gov** (per GSA materials). |

---

## 3. Defense, logistics & supply (high dollar — often IDIQ/MACC families)

| Name / family | What it is |
|----------------|------------|
| **LOGCAP V** (and future **LOGCAP VI**) | Army contingency / base ops logistics — very large ceilings. |
| **DLA Troop Support** | Subsistence, medical materiel, Prime Vendor, etc. — often **IDIQ/BPA** style buys. |
| **DLA Energy** | Fuel, energy — regional IDIQ-style contracts. |
| **AFCAP** | Air Force contingency logistics. |
| **NAVFAC** | Navy facilities — **MACC**, **MATOC**, regional construction IDIQs. |
| **USACE** | **MATOC** / **MACC** / district construction IDIQs — **many** separate contract numbers by region. |
| **TRANSCOM** | Transportation / distribution (strategic lift, etc.). |
| **GSA PBS** | Federal buildings — facilities, construction, services (often MACC/JOC). |

*Indo-Pacific and OCONUS MACCs are called out in `IDIQ_GOVCON_KNOWLEDGE.md` — fewer bidders, higher barriers.*

---

## 4. Contract “types” that are often IDIQ-like (search keywords on SAM.gov)

Use these in **Advanced Search** → **Notice Type** / description keywords:

| Keyword / pattern | Meaning |
|-------------------|--------|
| **IDIQ** | Indefinite delivery / indefinite quantity |
| **MACC** | Multiple award construction contract |
| **MATOC** | Multiple award task order contract |
| **JOC** | Job order contract (construction ordering) |
| **BPA** | Blanket purchase agreement (can be multi-award) |
| **GWAC** | Government-wide acquisition contract |
| **OASIS**, **Polaris**, **SEWP** | Specific program names |

---

## 5. How to build *your* exhaustive list (data, not memory)

1. **SAM.gov — Contract Opportunities**  
   - Filter: `IDIQ` or `Multiple Award` in title/description.  
   - Captures **new** IDIQ competitions; not historical awards.

2. **SAM.gov — Contract Data** (beta / contract awards)  
   - Use filters for **contract type**, agency, date — export CSV.

3. **USASpending.gov**  
   - Advanced search → **Award Type** / **Contract Vehicle** style filters (UI evolves).  
   - Export awards; pivot by **recipient**, **awarding agency**, **PSC**, **NAICS**.  
   - Good for “who holds what vehicle” and **recompete** timing.

4. **GSA**  
   - **eLibrary** — MAS contractors; **OASIS+** / **Polaris** public awardee lists on GSA pages.

5. **Agency portals** (examples)  
   - **NASA SEWP**, **NITAAC** (CIO-SP), **DLA** DIBBS — task-order competitions live here once you’re on or team with a holder.

6. **Paid intel** (optional)  
   - GovWin / Deltek, Bloomberg Government — recompete and pipeline tracking; **not** required if you’re disciplined with USASpending + SAM exports.

---

## 6. DDI-relevant slice (don’t boil the ocean)

| Lane | Vehicles / search strategy |
|------|------------------------------|
| **Medical courier, lab, logistics** | NAICS **492210**, **492110** + keyword `courier` / `laboratory` on SAM; VA/DHA hospital **IDIQ** families; task orders under health primes. |
| **Facilities / grounds / janitorial** | USACE / NAVFAC / GSA PBS MACCs; agency-specific IDIQs. |
| **Products / supplies** | GSA MAS; DLA; agency BPAs. |
| **Professional / program mgmt** | OASIS+ pools matching your NAICS; WOSB pool if qualified. |

---

## 7. Repo cross-references

| File | Contents |
|------|----------|
| `IDIQ_GOVCON_KNOWLEDGE.md` | Task-order economics, major names, logistics IDIQs, lesser-known regional MACCs. |
| `FORECAST_OPPORTUNITIES_TRACKER.md` | OASIS+ WOSB, Polaris, other tracked solicitations. |
| `NEW_SOURCES_SOUGHT_PRESOLICITATION_MAR13.md` | Many **IDIQ** notices mined from SAM (examples, not exhaustive). |

---

## 8. Maintenance

- **Owner:** Update this index when NEXUS locks onto a **new** government-wide vehicle (name + link to GSA/agency page).  
- **Do not** paste unverified ceiling values into proposals — always use the **solicitation** or **GSA official** page for the pool you’re bidding.

---

## 9. Automated pull (SAM + USASpending)

Run from repo root (requires `SAM_GOV_API_KEY` in `.env` for SAM rows; USASpending needs no key):

```bash
python3 sam_idiq_pull.py
```

**Writes:**

| File | Contents |
|------|----------|
| `SAM_IDIQ_PULL_LATEST.md` | Summary tables — active SAM title hits + USASpending award keyword matches |
| `data/sam_idiq_sam_gov_pull.json` | Raw SAM `opportunitiesData` |
| `data/sam_idiq_usaspending_pull.json` | Deduped USASpending award rows |

Re-run weekly or when building IDIQ pipeline intel.

---

*This file is an index and methodology, not a claim of a complete government-wide IDIQ census.*
