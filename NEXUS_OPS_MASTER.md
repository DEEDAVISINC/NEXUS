# NEXUS OPS — MASTER PLAN
## Employee Work Portal (Sector Desks → NEXUS Systems of Record)

**Created:** July 25, 2026  
**Owner:** Dee Davis Inc.  
**Status:** ARCHITECTURE — Ready for phased build  
**Product name:** **NEXUS OPS**  
**Domain (locked):** `ops.deedavis.biz` · Sister onboarding: `gateway.deedavis.biz` · See `DDI_PORTAL_DOMAINS.md`  
**Related:** `NEXUS_ONBOARDING_SYSTEM.md` (GATEWAY hire/clear) · `PRISM_MASTER.md` (PRISM system of record) · VERTEX / COMPASS module docs

---

## THE RULE

```
GATEWAY hires & clears people
        ↓
NEXUS OPS is where cleared people WORK
        ↓
Each DESK = one NEXUS sector (PRISM, VERTEX, COMPASS, …)
        ↓
Everything writes back to that sector in NEXUS Command Center
```

| Layer | Who | Job |
|---|---|---|
| **NEXUS Command Center** | Dieasha / leadership / HR admin | Full cockpit — strategy, roster, overrides, all sectors |
| **GATEWAY** (`gateway.deedavis.biz`) | New hires / contractors | Hire, policies, training, screening — **not** daily work |
| **NEXUS OPS** (`ops.deedavis.biz`) | Cleared employees (later: FDR-cleared contractors) | Daily work desks — trips, claims entry, etc. |
| **Sector backends** | Systems of record | PRISM, VERTEX, COMPASS, … — OPS never replaces these |

**Do not confuse:**
- GATEWAY ≠ OPS (onboard vs work)
- OPS ≠ NEXUS Command Center (workforce desk vs your cockpit)
- PRISM ≠ OPS (PRISM is **Desk #1 inside OPS**, not the portal name)
- Trip “claim” (pull work from a queue) ≠ billing **claims** (data entry + manager authorize)

---

## VISION MAP

```
                    ┌─────────────────────────────┐
                    │   NEXUS COMMAND CENTER      │
                    │   (admin / audit / control) │
                    └──────────────▲──────────────┘
                                   │ sync / audit
┌──────────────────────────────────┴──────────────────────────────────┐
│                         NEXUS OPS                                   │
│  Login · idle timeout · can-work gate · desk switcher · roles       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  PRISM   │  │ VERTEX / │  │ COMPASS  │  │  Later   │            │
│  │  Desk    │  │ Claims   │  │  Desk    │  │  desks   │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘            │
└───────┼─────────────┼─────────────┼────────────────────────────────┘
        │             │             │
        ▼             ▼             ▼
   prism_* APIs   VERTEX/billing  COMPASS contracts
```

---

## NON-NEGOTIABLE SECURITY (OPS ≠ GATEWAY)

GATEWAY may keep a long browser session for onboarding. **OPS must not.**

| Control | Requirement |
|---|---|
| **Idle timeout** | **15 minutes** no activity → logout |
| **Warning** | Soft warning at **~13 minutes** (“Session ending — stay signed in?”) |
| **Absolute max session** | **12 hours** even if “active” (shift ceiling) |
| **Activity definition** | Keyboard/mouse **and** meaningful API calls (claim, save, submit, approve) |
| **Server enforcement** | Token/session invalid after idle — UI redirect alone is not enough |
| **Auth secret** | **Separate** from GATEWAY (`OPS_AUTH_SECRET` ≠ `GATEWAY_AUTH_SECRET`) |
| **Remember me** | **Forbidden** — no multi-week stay logged in |
| **Login method** | Magic link / OTP (reuse GATEWAY pattern, shorter JWT TTL + idle tracking) |
| **On logout** | Clear local session; optional reason: idle / manual / absolute / admin revoke |
| **PHI hygiene** | No member IDs in URL query strings; mask PHI on list views; optional blur on tab blur |

### Suggested session payload (JWT claims)

- `sub` — GATEWAY onboarding record id (or stable person id)
- `email`
- `role` — `cca` | `claims_entry` | `manager` | `supervisor` | `admin_view` (expand carefully)
- `desks` — e.g. `["prism"]`, later `["prism","claims"]`
- `accounts` — payer/account codes from GATEWAY assignment (e.g. HAP CareSource)
- `iat` / `exp` — absolute expiry
- Idle tracked server-side via `last_activity` (Redis/file/Airtable — decide in Phase A)

---

## IDENTITY BRIDGE (GATEWAY → OPS)

OPS does **not** re-hire people. It reads GATEWAY.

| GATEWAY field | OPS use |
|---|---|
| Status Active | Must be Active |
| `can-work` | **Hard gate** — false → login OK but all desks locked (or login blocked — pick one; prefer login + locked with reason) |
| Division | FDR / desk eligibility hints |
| **Account(s)** | Queue routing (HAP CCA only sees HAP) — from `NEXUS HR ACCOUNT CODES` / assignment |
| **Level** | Manager vs CCA vs supervisor (personnel-number level codes) |
| Worker type | Employee first; contractors only when explicitly entitled |

**Rule:** Any assign/claim/approve in OPS that touches MCO/member work must re-check `GET /nexus/hr/onboarding/<id>/can-work` (or a cached gate with short TTL). If GATEWAY flips red mid-shift, OPS locks.

---

## ROLES (START SMALL)

| Role | Desks | Can |
|---|---|---|
| **CCA / Agent** | PRISM (employed sectors only) | **Mine** + work assigned cases; pool = **Request** only — **cannot self-assign** |
| **Claims entry** | Claims / VERTEX | Draft + submit claims; fix returns |
| **Supervisor** | PRISM (employed sectors) | **Supervisor floor** + **Care desk**: assign / batch / force-unassign / live / agents / request inbox / aging view. Work cases via **Assign to me** → Mine |
| **Manager** | PRISM (+ Claims later) | **Management floor** + Care desk: everything supervisor has + workforce readiness + aging escalate flag; still sector-scoped unless owner |
| **Admin / Owner** | **Ultimate key** — all desks, all sectors | **Owner floor** — Dieasha / `info@deedavis.biz` (+ aliases): all floors + company-wide |
| **NEXUS admin** | All (Command Center) | Not a substitute for OPS — override + audit live in NEXUS |

**Locked (Jul 26, 2026):**
- Same site: `ops.deedavis.biz` — **role floors**, not separate domains
- Supervisors **can** do Care desk work (Assign to me → Mine)
- Owner sits above the supervisor ↔ management split
- Roles still come only from GATEWAY levels

---

## ROUTING ENGINE (TWO LAYERS)

Do **not** overload `prism_service_router.route_order()` (partner/fulfillment). Keep people routing separate.

### Layer 1 — Desk router
Which sector UI? Driven by role/desk entitlements on the session.

### Layer 2 — Account / payer router
Inside a desk, which queue?

```
Trip/order.payer  →  normalize to HR account code  →  filter queue to CCAs with that account
```

**Example:** HAP CareSource trip → PRISM Desk → HAP CareSource queue → only CCAs assigned that account (and `can-work` green) may claim.

| Rule | Behavior |
|---|---|
| Affinity | Payer/account must match CCA assignment |
| Push model (locked) | Orders land in **Unassigned**; **only supervisors/managers assign** (single or batch) to agents |
| Agent network | Supervisors/managers see agents who share **employed sectors** (owner sees all) |
| Queue scope | Supervisors/managers = employed sectors only; **owner/admin** = all accounts |
| Partners | Never name fulfillment brands in OPS UI |

### Sector labels (what people see vs GATEWAY codes)

**Workforce UI shows BUYER-LANE names.** Raw HR codes stay internal for routing only.

| Desk label (show this) | Internal code | Notes |
|---|---|---|
| **HAP-NEMT** | `CSRC` | HAP CareSource NEMT |
| **MOL-NEMT** | `MOLN` | Molina NMT / NEMT dispatch |
| **MOL-CTS** | `CTS` | Molina Community Transition (own lifecycle) |
| **MER-NEMT** | `MER` | Meridian NEMT |
| **HAVN** | `HAVN` | HAVEN continuity |

**Add more as contracts are secured** — extend `SECTOR_DISPLAY` + `PAYER_TO_CODES` in `ops_portal_api.py`, plus GATEWAY account code. Naming pattern: `BUYER-LANE` (e.g. `BCBS-NEMT`, `AETNA-CTS`).

**Molina** = **two product lanes under one PSA** (never treat as NEMT-only):
| Lane | Desk label | HR code | What it is |
|---|---|---|---|
| **NMT / NEMT** | MOL-NEMT | `MOLN` Ⓜ️ | Trip dispatch / transportation |
| **CTS** | MOL-CTS | `CTS` 🏠 | Community Transition Services (Attachment B / T2038) |

GATEWAY assignment of Molina (`MOLN`) also opens the **CTS** queue in OPS. CTS-only assignment stays CTS-scoped. Employees can hold both: `Molina Healthcare of Michigan, CTS` → Ⓜ️🏠.

---

## DESK 1 — PRISM (FIRST BUILD)

**Purpose:** Customer care / coordination work on PRISM trips & related ops — writes back to PRISM.

**Product feel (locked Jul 25, 2026):** Care desk, not gray admin. Emoji status/SLA/actions/empty states. Keep PHI (names/IDs) clean — personality on chips and chrome only.

### Four screens only (resist more nav)
1. **My Queue** — Mine + Pool (grab unassigned)  
2. **Referral Detail** — member + SLA + one next action + activity timeline  
3. **Search** — one bar: name / MCO ID / referral # / phone  
4. **My Day / Team** (supervisor) — **calendar first** (PRISM pickups + callbacks), then counts + by-agent  
   - `GET /ops/prism/calendar` — always derived from PRISM orders (source of record)  
   - `POST …/callback` — writes `ops_callback_at` on the order, then best-effort NEXUS calendar sync  
   - `GET /ops/prism/day` · supervisor `POST …/assign` (agent email)  
   - Rule: **everything falls back to PRISM** — OPS never owns a separate calendar store

### Care status chips
| Chip | Meaning |
|---|---|
| 🆕 New | Unworked / just received |
| 🔧 Working | Claimed / in progress |
| ⏳ Waiting on Auth | Blocked on auth / info |
| ✅ Done | Closed |

### SLA urgency
🟢 On track · 🟡 Tight · 🔴 Overdue — countdown is the #1 desk feature.

### Progress stepper
Received → Assigned → In Progress → Completed

### Backend (new or extend)
- `GET /ops/session` — me + desks + accounts + can-work  
- `GET /ops/prism/queue` — `view=mine|pool|all`, `q=` search  
- `POST /ops/prism/items/<id>/claim` · `/release`  
- `GET|PATCH /ops/prism/items/<id>` — careStatus, **append-only** `activityNote`  
- SLA due from priority (STAT 2h / Same Day 8h / Standard 24h) or `ops_sla_due_at`  
- Existing PRISM/NEMT APIs remain system of record; OPS is a controlled façade  
- **Calendar:** pickup times + `ops_callback_at` on the order → My Day strip; optional write-behind to `/nexus/calendar` with `system=PRISM`  

### Explicit non-goals (PRISM Desk MVP)
- Field agent scanbacks (different portal / later role)  
- Partner dispatch branding  
- Full NEXUS admin chrome  
- React/Supabase rewrite — stay Netlify + Flask until desk UX is boringly solid  

---

## DESK 2 — CLAIMS / VERTEX (DATA ENTRY + AUTHORIZE)

**Purpose:** Claims are **data entry**. Approval requires **management authorization**. Drain times keep submissions moving.

### Lifecycle

```
Draft (entry)
  → Submitted (frozen snapshot for review)
      → Pending manager authorization
          → Approved  → handoff to VERTEX / payer path
          → Rejected / Returned  → back to entry with required reason
```

| Role | Draft | Submit | Approve | Reject/Return |
|---|---|---|---|---|
| Claims entry | ✅ | ✅ | ❌ | ❌ |
| Manager | view | — | ✅ | ✅ |
| Supervisor | ✅* | ✅* | ✅ | ✅ |

\* Supervisor override only when needed — prefer manager as normal path.

### Drain times (defaults — confirm before code)

Use **business hours** unless desk is 24/7.

| Stage | Default drain | On breach |
|---|---|---|
| Draft idle | 48 business hours | Yellow nudge |
| Submitted → manager | **4 business hours** | Yellow on manager queue; red + escalate if still open |
| Returned → entry fix | **1 business day** | Red if ignored |
| Approved → VERTEX handoff | 2 business hours | Red if export/pickup failed |

Manager board sorts **oldest / closest to breach first**, not newest-first.

### Audit (mandatory)
Who created, submitted, approved/rejected, timestamps, reason codes — FDR/MCO defensibility.

---

## SHARED OPS CAPABILITIES

| Capability | Notes |
|---|---|
| Desk switcher | Only desks on session |
| Notifications | Drain breach, can-work lock, unclaimed aging |
| Case notes | Internal CCA ↔ manager (PHI-aware retention) |
| Audit log | Login, idle logout, view, edit, claim, submit, approve |
| Reporting (NEXUS) | Volume, time-to-claim, time-to-approve, drain breaches, can-work blocks |
| QC | OPS must not bypass PRISM QC gates or claims required-field gates |
| Comms later | Member-facing scripts — Phase E+; not MVP |

---

## TIMECLOCK (locked Jul 26, 2026)

**OPS is the employee timeclock — not GATEWAY.**

```
GATEWAY can-work clear → OPS clock in/out (shift hours)
                      → VERTEX HR timesheet / pay run
```

| Layer | Time / pay role |
|---|---|
| **GATEWAY** | Identity + clearance only — **no** punch / hours |
| **OPS** | Clock in / clock out · shift log · (later) suggest hours to VERTEX |
| **VERTEX HR** | Rates · approve hours into pay · Deluxe / tax |

Status: **MVP live** — **OPS sign-in = on shift**; **sign-out / idle = off shift**. Header shows shift time + activity. **→ VERTEX** sends period hours to VERTEX HR.

| Piece | Location |
|---|---|
| Session start | `POST /ops/timeclock/session-start` (on login) |
| Heartbeat / work | `POST /ops/timeclock/heartbeat` (activity + desk actions) |
| Session end | `POST /ops/timeclock/session-end` (sign-out / idle) |
| Data | `uploads/ops/timeclock.json` |
| Netlify | `ops-portal/netlify/functions/ops-timeclock.js` |
| UI | Header “On shift” indicator (no separate Clock in button) |

Requires GATEWAY `can-work` (or OPS relax) to start a shift. Sync employee in VERTEX HR before **→ VERTEX**.

---

## BUILD RULE — ONE PORTAL AT A TIME

1. **Finish OPS** (desks, claim/release, supervisor layer) without stalling on GATEWAY Phase 1 paperwork.
2. **Finish GATEWAY** credentialing for real hires in a dedicated session.
3. **Wire hard** — turn off `OPS_RELAX_CAN_WORK` so desks require true GATEWAY `can-work`.
4. **OPS timeclock** — punch in/out → hours into VERTEX HR (after desks are solid).

Build-time flag: `OPS_RELAX_CAN_WORK=1` on PythonAnywhere unlocks Active employees for OPS smoke tests while GATEWAY still reports incomplete. Banner shows “OPS build mode” + go-live checklist from `/ops/session` (`opsReadiness.toGoLive`). Production = flag off (`OPS_RELAX_CAN_WORK=0` or unset).

**Off-ramp (do not flip until workforce is real):**
1. GATEWAY `can-work` passes for Active staff who need desks
2. Prefer real PRISM orders; use queue **Real only (hide demo)** for live ops
3. Set `OPS_RELAX_CAN_WORK=0` (or unset) on PythonAnywhere and reload webapp
4. Confirm banner shows can-work enforced (not build mode)

### Phase A — OPS shell + security + GATEWAY gate
- [x] Scaffold `ops-portal/` at `ops.deedavis.biz` / `ddi-ops-portal.netlify.app`
- [x] Auth (OTP/magic link) with **15-min sliding JWT + 12-hr absolute** (`OPS_AUTH_SECRET`)
- [x] Client idle watchdog (warn @ 13 min, logout @ 15)
- [x] Flask `ops_portal_api.py` — `GET /ops/session` (can-work, accounts, level→role, desks)
- [x] Netlify functions: `ops-auth-send`, `ops-auth-verify`, `ops-auth-me`, `ops-session`
- [x] PythonAnywhere: `/ops/health` + `/ops/session` live via `prism_pa_app.py`
- [x] Session/health surfaces `relaxCanWork` + `opsReadiness.toGoLive` (UI banner)
- [ ] DNS CNAME `ops` → `ddi-ops-portal.netlify.app`
- [x] Principal/owner `can-work` path (Dieasha / `info@`) — Phase 1 hire checklist N/A; see `GATEWAY_PHASE1_STATUS.md`
- [ ] Turn off `OPS_RELAX_CAN_WORK` after first real employee clears Phase 1 (owner already true without relax)

### Phase B — PRISM Desk MVP
- [x] Queue by account (`GET /ops/prism/queue`) — HAP CareSource ↔ HR CareSource/`CSRC`
- [x] Claim / release (`POST .../claim`, `.../release`) — does **not** reuse field-agent `agent` field
- [x] Notes write-back (`PATCH /ops/prism/items/<id>`)
- [x] Demo queue items in `uploads/ops/prism_demo_queue.json` when real board is thin
- [x] OPS portal PRISM desk UI (claim / release / notes)
- [x] Flask `/ops/prism/*` live on PythonAnywhere
- [x] Supervisor force-release — API `force=true` + UI confirm (Working / Waiting on Auth / In Progress)
- [x] Demo filter — `?demo=all|hide|only` + portal Queue source control + Real/Demo chips

### Phase C — Manager / supervisor ops layer (role floors)
- [x] Same `ops.deedavis.biz` — role floors (`care` / `supervisor` / `management` / `owner`)
- [x] Session `floor` + `capabilities` matrix from GATEWAY level
- [x] Supervisors keep Care desk (`Assign to me`)
- [x] Request inbox (`GET /ops/prism/requests`)
- [x] Aging board (`GET /ops/prism/aging`)
- [x] Workforce readiness — management (`GET /ops/prism/readiness`)
- [ ] Break-glass logout
- [ ] Escalation hooks for unclaimed / drain (PRISM side)

### Phase D — Claims desk + drain timers
- Draft → submit → authorize
- Drain clocks + manager authorize board
- Approved → VERTEX handoff stub

### Phase E — Intake auto-route + reporting
- Voice/intake complete → correct PRISM queue
- NEXUS dashboards for OPS metrics

### Phase F — Next sector desks
- COMPASS, SHIELD, drug-testing coordination, HAVEN — **same shell**, new queues  
- Only after PRISM + Claims patterns are boringly reliable

---

## WHAT WE ARE REUSING

| Existing | Reuse how |
|---|---|
| `gateway-portal` auth pattern | OTP + HMAC JWT — **shorten TTL + add idle** for OPS |
| `hr_onboarding_api.py` `/can-work`, `/assignment`, account codes | Identity + gate + routing keys |
| `prism_nemt.py` / orders APIs | Trip system of record |
| `prism_service_router.route_order` | **Fulfillment only** — not CCA routing |
| `FieldAgentPortal.tsx` | Do **not** bolt CCA onto field scanback UX — separate desk |
| NEXUS frontend PRISM admin | Stays for Dee; OPS is the workforce UI |

---

## OPEN DECISIONS (LOCK BEFORE / DURING PHASE A)

| # | Decision | Recommendation |
|---|---|---|
| 1 | Domain | **LOCKED** `ops.deedavis.biz` (+ `gateway.deedavis.biz` for onboarding) |
| 2 | First live desk | **PRISM only** through Phase B; Claims in Phase D |
| 3 | Contractors in OPS | **Employees only** until can-work is rock solid |
| 4 | Claim model | **Pull-queue** + supervisor override |
| 5 | can-work UX | Allow login, **lock desks** with clear reason |
| 6 | Manager vs supervisor | Separate roles; one person may hold both |
| 7 | Drain defaults | 4 biz hr manager / 1 biz day return (table above) |
| 8 | Idle store | Server `last_activity` (choose Redis vs lightweight file/DB in Phase A) |

---

## SUCCESS CRITERIA (MVP)

- [ ] Cleared HAP CCA signs into OPS, sees only HAP PRISM queue  
- [ ] Uncleared / can-work false cannot act on desk work  
- [ ] 15-minute idle logs them out (server + client)  
- [ ] Claim locks a trip; second CCA cannot double-work it  
- [ ] Status/notes write back into PRISM and show in NEXUS  
- [x] Supervisor can force-release  
- [ ] Audit row for login, claim, update, logout  

Claims MVP (Phase D) adds: submit without self-approve; manager authorize; drain breach visibility.

---

## ANTI-PATTERNS

- ❌ Naming the whole portal “PRISM”  
- ❌ Putting CCA work inside full NEXUS Command Center chrome  
- ❌ Copying GATEWAY’s 30-day session into OPS  
- ❌ Mixing partner fulfillment routing with CCA desk routing  
- ❌ Letting entry staff approve their own claims  
- ❌ Building COMPASS/SHIELD desks before PRISM + Claims patterns work  
- ❌ Showing Uber/Quest/etc. brand names in OPS UI  

---

## DOCUMENT CONTROL

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-07-25 | Initial architecture from NEXUS planning session (OPS shell, PRISM desk, claims/drain, security) |

**Next action after approve:** Phase A scaffold — `ops-portal/` + auth + idle session + GATEWAY bridge.
