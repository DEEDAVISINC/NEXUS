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
| **CCA** | PRISM (account-scoped) | View queue, claim/release, update trip notes/status within policy |
| **Claims entry** | Claims / VERTEX | Draft + submit claims; fix returns |
| **Manager (authorizer)** | Claims (+ optional PRISM) | Approve / reject / return claims; see drain board |
| **Supervisor** | Multi-account / multi-desk | Force-assign, force-release, break-glass logout, overflow |
| **NEXUS admin** | All (Command Center) | Not a substitute for OPS — override + audit live in NEXUS |

Phase A/B may ship **CCA + Supervisor** only; add Claims roles in Phase D.

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
| Pull model (default) | Auto-route to **queue**; human **claims** work item |
| Overflow | Supervisor / multi-account after N minutes unclaimed |
| Force | Supervisor can force-assign / force-release |
| Partners | Never name fulfillment brands in OPS UI |

**HAP CareSource** = one desk/account for routing purposes (align with existing NEMT payer catalog + HR account codes).

---

## DESK 1 — PRISM (FIRST BUILD)

**Purpose:** Customer care / coordination work on PRISM trips & related ops — writes back to PRISM.

### MVP screens
1. **My queue** — account-scoped; oldest / SLA-sensitive first  
2. **Trip / case detail** — eligibility checklist, notes, status, voice/confirmation refs  
3. **Claim / release** — lock so two CCAs don’t work the same member  
4. **Supervisor board** — unclaimed aging, force-assign  

### Backend (new or extend)
- `GET /ops/session` — me + desks + accounts + can-work  
- `GET /ops/prism/queue` — filtered by session accounts  
- `POST /ops/prism/items/<id>/claim`  
- `POST /ops/prism/items/<id>/release`  
- `PATCH /ops/prism/items/<id>` — allowed fields only; audit  
- Existing PRISM/NEMT APIs remain system of record; OPS is a controlled façade  

### Explicit non-goals (PRISM Desk MVP)
- Field agent scanbacks (different portal / later role)  
- Partner dispatch branding  
- Full NEXUS admin chrome  

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

## PHASED BUILD

### Phase A — OPS shell + security + GATEWAY gate
- [x] Scaffold `ops-portal/` at `ops.deedavis.biz` / `ddi-ops-portal.netlify.app`
- [x] Auth (OTP/magic link) with **15-min sliding JWT + 12-hr absolute** (`OPS_AUTH_SECRET`)
- [x] Client idle watchdog (warn @ 13 min, logout @ 15)
- [x] Flask `ops_portal_api.py` — `GET /ops/session` (can-work, accounts, level→role, desks)
- [x] Netlify functions: `ops-auth-send`, `ops-auth-verify`, `ops-auth-me`, `ops-session`
- [ ] Redeploy Flask on PythonAnywhere so `/ops/session` is live (portal falls back to GATEWAY `/self` for OTP eligibility until then)
- [ ] DNS CNAME `ops` → `ddi-ops-portal.netlify.app`

### Phase B — PRISM Desk MVP
- [x] Queue by account (`GET /ops/prism/queue`) — HAP CareSource ↔ HR CareSource/`CSRC`
- [x] Claim / release (`POST .../claim`, `.../release`) — does **not** reuse field-agent `agent` field
- [x] Notes write-back (`PATCH /ops/prism/items/<id>`)
- [x] Demo queue items in `uploads/ops/prism_demo_queue.json` when real board is thin
- [x] OPS portal PRISM desk UI (claim / release / notes)
- [ ] Supervisor force-release UI polish (API supports `force` for supervisor/manager)
- [ ] Redeploy Flask on PythonAnywhere for `/ops/prism/*`

### Phase C — Manager / supervisor ops layer
- Aging boards
- Break-glass logout
- Escalation hooks for unclaimed / drain (PRISM side)

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
- [ ] Supervisor can force-release  
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
