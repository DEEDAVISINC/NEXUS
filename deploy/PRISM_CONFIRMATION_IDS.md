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

---

## Staff exemption codes (per MCO + program)

**Format:** `EX-{CONTRACT#}-{LANE}-{YYYY}Q{Q}-{TYPE}-{RAND6}`

| Segment | Meaning | Example |
|---------|---------|---------|
| **CONTRACT#** | Same sequence as confirmations | `1` = HAP |
| **LANE** | Program lane or `ALL` for MCO-wide | `MOB-A`, `ALL` |
| **YYYYQ{Q}** | Quarter | `2026Q2` |
| **TYPE** | WVR, EXM, EXP, OPS, VIP | `WVR` |
| **RAND6** | Random suffix | `K7M3P9` |

**Examples:**
- HAP NEMT waiver: `EX-1-MOB-A-2026Q2-WVR-K7M3P9`
- HAP all programs billing exempt: `EX-1-ALL-2026Q2-EXM-XXXXXX`
- BCBSM NEMT (when live): `EX-2-MOB-A-2026Q2-WVR-XXXXXX`
- DDI enterprise ops: `EX-0-ALL-2026Q2-OPS-XXXXXX`

**Legacy (migration):** `EX-2026Q2-WVR-XXXXXX` — global, honored until rotated off.

### Exemption types

| Type | Use |
|------|-----|
| **WVR** | Fee waiver — management authorized |
| **EXM** | Billing exempt — contract / MCO / government |
| **EXP** | Expedited / STAT handling |
| **OPS** | Internal ops bypass |
| **VIP** | Priority client handling |

### Scope rules

- Program code (`EX-1-MOB-A-…`) works only for that MCO **and** that lane.
- MCO-wide code (`EX-1-ALL-…`) works for any program under contract **1**.
- Billing validation with an `order_id` auto-resolves contract + lane from the order.
- Wrong MCO/program → rejected even if the code exists.

### First-time rotation (PA)

Set on server `.env`:
```
PRISM_EXEMPTION_PEPPER=<long random secret>
PRISM_EXEMPTION_ADMIN_KEY=<admin bearer token>
```

```bash
curl -s -X POST https://deedavis.pythonanywhere.com/prism/exemptions/rotate \
  -H "Authorization: Bearer YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"setup_defaults": true}'
```

Returns codes for:
1. `1:MOB-A` — HAP Plan NEMT
2. `1:ALL` — HAP all programs
3. `0:ALL` — DDI enterprise

**Store plaintext in 1Password — cannot be retrieved again.**

### Rotate one MCO/program

```bash
curl -s -X POST .../prism/exemptions/rotate \
  -H "Authorization: Bearer ..." \
  -H "Content-Type: application/json" \
  -d '{"contract_payer_id": 2, "lane": "MOB-A", "types": ["WVR","EXM","EXP","OPS","VIP"]}'
```

---

## API

- `GET /prism/confirmations/schema`
- `GET /prism/confirmations/lookup/{ref}?phone_last4=`
- `GET /prism/exemptions/status?contract_payer_id=1&lane=MOB-A`
- `POST /prism/exemptions/rotate` (admin)
- `POST /prism/exemptions/validate`
- `POST /prism/billing/validate-override` (pass `order_id` for auto scope)

---

*Contract # is DDI’s internal sequence — not Availity claims payer ID.*
