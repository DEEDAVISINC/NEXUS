# PRISM Confirmation & Exemption IDs

**Module:** `prism_confirmation_ids.py`

---

## Member confirmation numbers

**Format:** `{CONTRACT#}-DDI-{LANE}-{YYYYMMDD}-{SEQ4}-{CHK}`

| Segment | Meaning | Example |
|---------|---------|---------|
| **CONTRACT#** | DDI MCO/contract sequence (order secured) | `1` = HAP CareSource, `2` = BCBSM |
| **DDI** | Dee Davis Inc. | fixed |
| **LANE** | Population / program lane | `MOB-A`, `MOB-B`, `TPA-1`, … |
| **YYYYMMDD** | Booking date (ET) | `20260607` |
| **SEQ4** | Daily sequence per contract + lane | `0042` |
| **CHK** | Check digit | `7` |

**Example:** `1-DDI-MOB-A-20260607-0042-7`  
→ Contract **1** (HAP CareSource) · plan NEMT · June 7, 2026 · trip 42 that day.

When BCBSM is secured → contract **2** → `2-DDI-MOB-A-…`

### Contract registry (assign next # when executed)

| # | MCO / contract |
|---|----------------|
| **0** | DDI Direct / non-MCO |
| **1** | HAP CareSource ✅ live |
| **2** | Blue Cross Complete / BCBSM *(when secured)* |
| **3+** | Molina, Priority, UHC CP, Aetna, … *(reserve as signed)* |

### Population lanes

| Lane | Use |
|------|-----|
| **MOB-A** | Plan NEMT |
| **MOB-B** | HAVEN continuity |
| **MOB-C** | Freight & logistics |
| **MOB-E** | Event mobility |
| **TPA-1 … TPA-9** | Non-mobility TPA services |
| **NAV-G** | Navigation / SDOH |

Intake channel (voice/web/portal) is stored on the **order record**, not spoken in the public confirmation string.

---

## Staff exemption codes

Unchanged: `EX-2026Q2-WVR-XXXXXX` — rotating, hashed, quarterly.

See prior sections in this file for setup (`PRISM_EXEMPTION_PEPPER`, `/prism/exemptions/rotate`).

---

## API

- `GET /prism/confirmations/schema`
- `GET /prism/confirmations/lookup/{ref}?phone_last4=`
- `POST /prism/exemptions/validate`

---

*Contract # is DDI’s internal sequence — not Availity claims payer ID.*
