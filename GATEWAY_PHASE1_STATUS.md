# GATEWAY Phase 1 — Status (Jul 26, 2026)

**Goal:** Real hire/clear so OPS can turn off `OPS_RELAX_CAN_WORK`.

---

## What “Phase 1” means

For **employees**, GATEWAY Phase 1 = **Pre-Boarding** checklist (`preboard`):

1. Offer letter signed and returned ← **portal upload** auto-checks this  
2. Background check initiated ← HR  
3. E-Verify case created ← HR  
4. OIG LEIE (FDR divisions) ← HR / screening log  
5. GSA SAM (FDR divisions) ← HR / screening log  
6. IT ticket (email / NEXUS / PRISM) ← HR  
7. Division/manager assigned ← HR  
8. Start date confirmed in writing ← HR  

`can-work` stays **false** until Phase 1 is complete (plus screening current + no CMS hard-missed training).

---

## Principal / owner exception (locked)

**Dieasha D. Davis / `info@deedavis.biz`** (and aliases) = founding principal.

- Does **not** need a self-hire offer letter or I-9 upload theater  
- Still must be **Active**, exclusion screening current, CMS hard-floor training not missed  
- `can-work` reason: `Compliant (principal / owner — Phase 1 hire checklist N/A)`  
- Portal shows those hire tasks as **N/A — principal**

Regular employees are **not** exempt. They finish the portal + HR checklist.

Override flags on any record (rare): `principalOwner: true` or `canWorkOverride: true`.

---

## Live audit (Jul 26, 2026)

| Person | Status | Blocker before fix | After principal path |
|---|---|---|---|
| Dieasha (`info@`) | Active · Director · Corporate/HR/Admin | Phase 1 — Offer letter unsigned | `can-work` true (principal) |
| Other hires | — | None on roster yet | Full Phase 1 required |

OPS: keep `OPS_RELAX_CAN_WORK=1` until you confirm principal can-work + at least one test employee path, then set `=0` and reload PA.

---

## Real-hire Phase 1 path (next employees)

1. HR creates GATEWAY record with email + division + account + level + start date  
2. NEXUS generates offer + welcome letters  
3. Hire signs in at `gateway.deedavis.biz`  
4. Download offer → sign → upload `offer_letter_signed` (auto-checks Pre-Boarding #1)  
5. Upload I-9 docs · e-sign policies  
6. HR completes remaining Pre-Boarding boxes + screening  
7. `GET .../can-work` → true → OPS desks unlock without relax mode  

---

## Onboarding reminder emails (locked defaults)

Cadence after start date (fallback: training-assignment email date → record created):

| Day | Email |
|---|---|
| **3** | First reminder — open portal tasks listed |
| **7** | Second reminder |
| **14** | Final reminder |

- **Skip:** principal/owner, `can-work` already true, no email, not Active, no yellow/red portal tasks  
- **Gap:** min 48 hours between sends  
- **Manual:** `POST /nexus/hr/onboarding/<id>/remind`  
- **Batch / cron:** `POST /nexus/hr/onboarding/reminders/run` or `python3 nexus_scheduler.py --gateway-reminders`  
- **Preview:** `GET /nexus/hr/onboarding/reminders/preview` or `--gateway-reminders --dry-run`  
- Audit trail: `onboardingReminders[]` on the hire record  

---

## Off-ramp checklist (when ready)

- [ ] `info@` can-work true without relax  
- [ ] One test employee cleared through real Phase 1 (or dry-run documented)  
- [ ] Set `OPS_RELAX_CAN_WORK=0` on PythonAnywhere → Reload  
- [ ] Confirm OPS banner is not “build mode”  
