# NEXUS CURRENT SESSION STATE

**Purpose:** Persistent record of session findings, active work, and system corrections. Cursor reads this at session start.

**Last Updated:** 2026-07-27

---

## 🧹 CLEANUP — STALE DEADLINES / CALENDAR / ALERTS (Jul 27, 2026)

**Problem:** NEXUS kept resurfacing thousands of past bid deadlines (calendar + alert feed).

**Done:**
- Archived **6,275** past auto-generated BID DEADLINE `.ics` → `calendars/ARCHIVE_EXPIRED/` (gitignored)
- Live `calendars/*.ics` now **~423** (future + protected meetings)
- Pruned `deadline_alerts.json` **24,173 → 156** (expired dropped)
- Fixed regenerators so past Airtable deadlines are **not** rewritten into `calendars/`
- Calendar API (`/calendar/feed.ics`, `/calendar/events`) skips ARCHIVE + past bid events
- Tool: `python3 cleanup_stale_nexus_deadlines.py --apply`

---

## 🔴 ACTIVE — CAQH PROVIDER PORTAL (Jul 27, 2026)

| Field | Value |
|---|---|
| **CAQH Provider ID** | **16876320** |
| **Named** | Dieasha Davis |
| **Status** | INVITED — register / profile / attest incomplete |
| **Portal** | https://proview.caqh.org/pr |
| **Full record** | `CREDENTIALING/CAQH_PROVIDER_PORTAL.md` |
| **Also in** | `COMPANY_INFO_MASTER.md`, `company_info.py`, `PENDING_ACTIONS.md` |

**Next action:** Complete CAQH registration + attestation this week (needed for Humana + MCO credentialing).

---

## 🌐 DDI WEBSITE UPDATE — deedavis.biz

**When Dee says "DDI website update" / "update the website"** → NOT the NEXUS app (`nexus.deedavis.biz`). She means the **marketing site** at **deedavis.biz**.

**Tracker (source of truth):** `WEBSITE/DEEDAVIS_BIZ_WEBSITE_UPDATE_TRACKER.md`

**Summary:** Staged HTML in `WEBSITE/` (VITAL, HAVEN, ARENA, 3D Ink, cwc-proof) — mostly **not deployed** to Netlify yet. Homepage live but needs national TPA copy + SWFT removal. P0: `/cwc-proof` for funder QR.

Also in `PENDING_ACTIONS.md` → section **DDI WEBSITE UPDATE**.

---

## 🔴 ACTIVE THREAD — PHC POSITIONING + LHD OUTREACH (June 4, 2026)

**Full record:** `SESSION_SUMMARY_JUNE_4_2026.md`

### Locked positioning
- **DDI = Contract Management TPA** — NOT a NEMT vendor. PHC framing for LHD/grant/MCO work.
- **One-line identity + banned language:** `NEXUS_LEARNING/DDI_PHC_POSITIONING_LOCKED.md`

### Deliverables ready
| Item | Location |
|---|---|
| Program narrative (live + PDF source) | `nexus-frontend/public/program-narrative.html` · `GRANT_APPLICATION_PACKAGE/DDI_CWC_PHC_Program_Narrative.html` |
| LHD emails (7 counties) | `CLIENT OUTREACH/LHD_DIRECT_OUTREACH_JUN_2026/SEND_TO_LHD/` |
| MCO community investment emails (3) | `CLIENT OUTREACH/MCO_COMMUNITY_INVESTMENT_JUN2026/SEND_TO_MCO/` |
| Outreach workflow | `CLIENT OUTREACH/LHD_DIRECT_OUTREACH_JUN_2026/WORKFLOW_CHECKLIST.md` |
| LHD contacts updated | `CLIENT OUTREACH/LHD_BACKUP_CONTACTS_SIX_COUNTIES.md` |
| Session summary (authoritative) | `DDI_Session_Summary_June2026.md` · `SESSION_SUMMARY_JUNE_4_2026.md` |

### Triggers — do not skip
| Date | Action |
|---|---|
| **Jun 4 (today)** | LinkedIn verify Oakland, Macomb, Genesee, Kent, Muskegon directors |
| **Jun 16** | If Angela/Aimee silent → send Wayne + Detroit LHD emails |
| **Jun 18** | Oakland + Macomb + Genesee |
| **Jun 20** | Kent + Muskegon |
| **End Sep 2026** | Return — begin BCBSM Foundation concept paper (Winter cycle) |
| **Oct 29, 2026** | Submit BCBSM concept paper — forms.office.com/r/wZdDebmJf9 |

### Awaiting (do not chase before trigger)
- **Angela Medina / Aimee Surma (MDHHS)** — until Jun 16
- **Alina Pabin (BCC)** — until Jun 9 one touch max
- **Brian / Dana (HAP CareSource)** — 7-day follow-up if silent

### Corrections applied June 4 import
- CWC MiBridges → **since 2024** · DDI MiBridges → **since May 2020** (separate entities — do not merge dates)
- Detroit contact → **Ali Abazeed** (supersedes Denise Fair Razo on file)
- Genesee → **in Jun 18 wave** (not hold)
- Partner table in public narrative → no Uber/DDC names (internal session list only)

---

## PRIOR THREAD — MEDICARE / MEDICAID DIGITAL NAVIGATION

**Record:** `SESSION_SUMMARY_MAY_30_2026.md` · `NEXUS_LEARNING/DDI_PROGRAM_PACKAGING_STRATEGY.md`

Program priority: 1 Healthcare Access · 2 Family Stability · 3 Substance Use · 4 Housing (future)

---

## CRITICAL REMINDERS

- **Never name fulfillment partners** on LHD/funder docs (`never-name-subvendors-network.mdc`)
- **MDHHS = community partner** — not formal contract
- **Phone on all docs:** 248.376.4550 · **Email:** info@deedavis.biz · **ZIP:** 48084
