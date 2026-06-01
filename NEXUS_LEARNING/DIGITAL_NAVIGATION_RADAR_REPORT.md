# DIGITAL NAVIGATION — RADAR Lane Report

**Updated:** May 29, 2026  
**Lane status:** ACTIVE — PROVEN PAST PERFORMANCE (MI Bridges Community Partner since May 15, 2020)  
**SAM cache:** `digital_nav_sam_cache.json` (from `mine_digital_navigation_sam.py`)  
**Intelligence index:** `NEXUS_LEARNING/PRIORITY_TARGETS_INDEX.json` → `digital_navigation_mining_lane`

---

## WHAT RADAR IS (FOR THIS LANE)

**RADAR** = Revenue Acquisition Discovery And Reconnaissance — all NEXUS mining scripts run together via:

```bash
python3 nexus_scheduler.py --radar
```

**Digital navigation was NOT fully wired into RADAR until May 29, 2026:**
- Lane defined in `partner-opportunity-mining.mdc` (Channel 32) and `PRIORITY_TARGETS_INDEX.json`
- **`ddi_opportunity_fit.py` now includes NAICS 624190/624210/561499/541720 + keywords**
- **New miner:** `mine_digital_navigation_sam.py` → `digital_nav_sam_cache.json`

---

## DDI PROOF POINTS (USE ON EVERY BID)

| Proof | Detail |
|-------|--------|
| MDHHS Community Partner | Since **May 15, 2020** (6+ years) |
| Applications facilitated | **200+** (DDI) + **50+** (CWC) = **250+** |
| NAICS | **624190** on SAM.gov |
| Portal | MiLogin **davisd1221** |
| MCO entry | CareSource NEMT contract → SDOH/HRSN path |
| Team model | **DDI prime** (for-profit) + **CWC 501(c)(3)** for grant-funded navigation |

---

## PRIORITY SOURCES — CHECK WEEKLY

| Source | What to search | DDI fit |
|--------|----------------|---------|
| **Michigan SIGMA** | digital equity, navigator, benefits, enrollment | State subcontract prime |
| **SAM.gov** | NAICS 624190 + keywords | Federal grants / ACL pass-through |
| **16 Michigan AAAs** | benefits navigation, SHIP, Medicare counseling | Direct RFPs |
| **NTIA Digital Equity** | grantee subcontract opportunities | Sub to state grantees |
| **ACL / Administration for Community Living** | SHIP, navigator, enrollment | Federal |
| **BidNet / MITN** | digital, navigator, enrollment, senior | Local MI |
| **CareSource** | SDOH / HRSN navigation (Brian Grcevich) | MCO contract |
| **MCOs (Molina, UHC, Meridian, HAP)** | HRSN, community health worker | TPA prime |

---

## IN PIPELINE NOW (NOT FROM SAM — ACTION ITEMS)

| Opportunity | Type | Status | Next action |
|-------------|------|--------|-------------|
| **MVAA Statewide Veteran Service (FY27)** | Grant / state | Inquiry sent Mar 22 — benefits navigation | Watch for FY27 RFP (~April–June 2026) |
| **MDHHS SHIELD** | State program | Proposal to Angela Medina — navigator integration | Follow up if no reply |
| **MDHHS CSBG** | State funding | Inquiry sent | Await response |
| **MDHHS CLPPP / lead navigation** | State partnership | Inquiry | Warm handoff path |
| **CareSource SDOH/HRSN** | MCO procurement | Active NEMT relationship | Ask Brian: navigation contract needs? |
| **Michigan AAAs (16)** | Local RFPs | Not systematically mined | Quarterly RFP check per AAA |
| **SIGMA digital equity** | State NTIA pass-through | Monitor | Search SIGMA quarterly |

---

## SAM SCAN RESULTS (NAICS-only — 60 days, May 29, 2026)

**24 federal notices** in `digital_nav_sam_cache.json` (5 NAICS codes, no keyword pass yet). **No strong digital-navigation fits** — NAICS pulls research, archaeology, EAP, family advocacy, mailroom, and conference support.

| Verdict | Count | Examples |
|---------|-------|----------|
| **Closed / past due** | 6+ | Family Connection Rock Island (May 18), FAP Training (May 19), FY26 Mass Warning (May 29) |
| **Weak fit — social services** | 5 | USACE EAP (Jun 2), DAF FAP Sources Sought (Jun 6), WWCC Support (Jun 15) |
| **Pass — wrong lane** | 10+ | Archaeology/cultural resources (541720), Kyiv conference (561499), DOI contract notices |
| **Review — adjacent** | 1 | **MACPAC Medicaid admin data analysis** (202601, due Jun 30) — research, not navigation delivery |

**Keyword scan still pending** (`digital navigator`, `HRSN`, `SHIP`, etc.) — run when ready:

```bash
python3 nexus_scheduler.py --digital-nav
```

**Takeaway:** Federal SAM NAICS lane alone won't feed digital navigation. **State/local pipeline (MVAA, MDHHS, AAAs, SIGMA, MCOs) remains primary.**

---

## SAM SCAN RESULTS (FULL KEYWORD + NAICS)

See **`digital_nav_sam_cache.json`** for latest federal postings.

---

## REVENUE TIER (TYPICAL)

| Tier | Annual contract value | DDI margin model |
|------|----------------------|------------------|
| AAA / county navigation | $50K–$250K | 40–60% (mostly DDI + CWC labor) |
| State digital equity sub | $250K–$1M+ | 25–40% TPA |
| MCO HRSN / SDOH | $500K–$5M+ | 20–35% TPA |
| ACL / federal navigator grants | Varies | Often CWC prime + DDI admin |

**Win advantage:** EDWOSB on federal; **6-year MI Bridges past performance** on state/local; CWC for 501(c)(3) grant requirements.

---

## RUN COMMANDS

```bash
# Digital navigation SAM scan only
python3 mine_digital_navigation_sam.py

# Full RADAR (all channels)
python3 nexus_scheduler.py --radar
```

---

## GAPS TO CLOSE

- [x] Add `mine_digital_navigation_sam.py` to `nexus_scheduler.py` run_federal_mining() + `--digital-nav` flag (May 29, 2026)
- [x] Add digital navigation rows to `NEXUS_WATCH_LIST.md` (May 29, 2026)
- [x] First NAICS-only SAM cache populate (`digital_nav_sam_cache.json`) — 24 opps, May 29, 2026 (~19 min)
- [ ] Full keyword + NAICS scan via `--digital-nav`
- [ ] SIGMA manual search — "digital equity" / "navigator"
- [ ] AAA outreach list — 16 Michigan AAAs with RFP URLs
- [x] CareSource SDOH email to Brian Grcevich — **sent May 31, 2026** · await reply ~Jun 7
- [ ] MVAA FY27 — check if RFP posted (late May / June 2026)
