# VERTEX HR — MASTER PLAN
## People pay inside VERTEX (receivables / payables / hours / payroll)

**Created:** July 26, 2026  
**Updated:** July 26, 2026  
**Owner:** Dee Davis Inc.  
**Status:** Phase 1 operational API live  
**Related:** `NEXUS_ONBOARDING_SYSTEM.md` (GATEWAY) · `VERTEX_FINANCIAL_SYSTEM_ARCHITECTURE.md` · `NEXUS_OPS_MASTER.md`

---

## THE RULE

```
GATEWAY = who is hired, cleared, role, sector (identity + compliance)
        ↓ sync (personnel number is the join key)
OPS     = timeclock + daily desks (clock in/out, shift hours)
        ↓ suggested / approved hours
VERTEX HR = rates, pay calculations, tax liability, pay runs
        ↓
Pay people     → Deluxe eChecks (net pay)
Deposit taxes  → EFTPS.gov (federal) + Michigan (income / UIA)
        ↓
VERTEX Finance = AP/AR ledger · bank reconcile
```

| Layer | Owns | Does NOT own |
|---|---|---|
| **GATEWAY** | Hire, level, accounts, `can-work`, personnel #, W-2 vs 1099 | Hours, timeclock, rates, net pay |
| **OPS** | Daily work desks **+ timeclock** (clock in/out → shift hours) | Payroll math, tax deposits, Deluxe |
| **VERTEX HR** | Pay rates, timesheet intake from OPS, pay calc, pay runs, stubs | Onboarding checklists, FDR screening, punch UI |
| **Deluxe eChecks** | Paying employees/contractors (net) | Tax calc / tax filing |
| **EFTPS + MI / UIA** | Federal + Michigan tax deposits & filings | Hours / rates |
| **VERTEX Finance** | Invoices (AR), vendor bills (AP), bank, P&L | Creating employees from scratch |

**Locked Jul 26, 2026 — OPS is the timeclock (not GATEWAY).** GATEWAY proves the person; OPS records the hours; VERTEX HR pays them.

**Locked Jul 26, 2026 — no Gusto/Square as pay rail.** VERTEX calculates; Deluxe pays people; EFTPS + Michigan handle taxes.

**Identity join key:** `personnelNumberCore`  
**Ultimate owner key:** `info@deedavis.biz` → admin over all of VERTEX HR

---

## OPERATIONAL ABILITIES (must-have checklist)

| Ability | Status | Endpoint |
|---|---|---|
| Sync roster from GATEWAY | ✅ | `POST /vertex/hr/employees/sync` |
| Re-check can-work before pay | ✅ | Auto on pay-run finalize |
| Set hourly/salary/contractor rates | ✅ | `PUT /employees/<core>/rate` |
| Employee tax / withhold profile | ✅ | `PUT /employees/<core>/tax` |
| Company EIN + MI UIA rate | ✅ | `GET/PUT /vertex/hr/company` |
| Biweekly period helper | ✅ | `GET /vertex/hr/period/current` |
| Timesheets create/edit | ✅ | `POST/PATCH /timesheets` |
| Submit / approve / reject hours | ✅ | `.../submit` `.../approve` `.../reject` |
| Pay preview + finalize | ✅ | `POST /pay-runs/preview` · `POST /pay-runs` |
| Deluxe eCheck register | ✅ | `GET /export/deluxe-pay` |
| Mark Deluxe paid | ✅ | `POST /pay-runs/<id>/mark-deluxe-paid` |
| Pay stub (per person) | ✅ | `GET /pay-runs/<id>/stub/<core>` |
| Tax liability worksheet | ✅ | `GET /tax-liability` |
| Log EFTPS/MI/UIA deposits | ✅ | `GET/POST /tax-deposits` |
| Dashboard + blockers | ✅ | `GET /dashboard` |
| Capabilities / workflow | ✅ | `GET /capabilities` |
| Command Center HR UI | ✅ | VERTEX → **👥 HR Payroll** tab (`VERTEXHRPanel.tsx`) |
| Exact IRS wage-bracket tables | ⏳ later | overrides via withhold % today |
| W-2 / 1099 PDF year-end | ⏳ Phase 3 | — |

---

## PAY CYCLE (how to run payroll)

1. `POST /employees/sync`  
2. Set rates + tax profiles; set company EIN + `miUiaRatePercent`  
3. Enter timesheets → submit → approve  
4. `POST /pay-runs/preview` → `POST /pay-runs`  
5. `GET /export/deluxe-pay` → pay nets in Deluxe  
6. `POST /pay-runs/<id>/mark-deluxe-paid`  
7. `GET /tax-liability?payRunId=...` → deposit in EFTPS + MI/UIA  
8. `POST /tax-deposits` with confirmation numbers  

---

## API SURFACE

```
GET    /vertex/hr/health
GET    /vertex/hr/capabilities
GET    /vertex/hr/dashboard
GET|PUT /vertex/hr/company
GET    /vertex/hr/period/current
POST   /vertex/hr/employees/sync
GET    /vertex/hr/employees
GET    /vertex/hr/employees/<core>
PUT    /vertex/hr/employees/<core>/rate
PUT    /vertex/hr/employees/<core>/tax
POST   /vertex/hr/timesheets
GET    /vertex/hr/timesheets
PATCH  /vertex/hr/timesheets/<id>
POST   /vertex/hr/timesheets/<id>/submit
POST   /vertex/hr/timesheets/<id>/approve
POST   /vertex/hr/timesheets/<id>/reject
POST   /vertex/hr/pay-runs/preview
POST   /vertex/hr/pay-runs
GET    /vertex/hr/pay-runs
GET    /vertex/hr/pay-runs/<id>
POST   /vertex/hr/pay-runs/<id>/mark-deluxe-paid
GET    /vertex/hr/pay-runs/<id>/stub/<core>
GET    /vertex/hr/export/deluxe-pay
GET    /vertex/hr/tax-liability
GET|POST /vertex/hr/tax-deposits
```

---

## DATA

`uploads/vertex_hr/`
- `company_settings.json` — EIN, MI UIA rate, period anchor  
- `employees.json` — synced profiles + rates + tax + YTD  
- `timesheets.json`  
- `pay_runs.json`  
- `tax_deposits.json`  

---

## HARD STOPS

- Do not create employees only in VERTEX — hire in GATEWAY first  
- Do not pay if GATEWAY `can-work` is red  
- Do not finalize the same period twice  
- Do not put member PHI in payroll files  
- Tax withhold amounts are **estimates** until Pub 15 / W-4 tables are wired — use employee withhold % overrides  

---

*VERTEX moves the money. GATEWAY proves the person. Deluxe pays. EFTPS + MI collect the taxes.*
