# VERTEX Phase 6 — Contract Volume Monitor (thin design)
**Date:** July 28, 2026  
**Status:** Design only — build after payer profiles are approved  
**Depends on:** `VERTEX_PAYER_PROFILES_HAP_MOLINA.md` / `VERTEX_PAYER_PROFILES.json`

---

## Purpose

Flag **technically active** payer contracts that produce **zero or near-zero** billable encounters — the HAP “Vendor ID live / trips never arrive” pattern — within **weeks**, not months.

This is a **monitor**, not a second billing system. It reads PRISM/VERTEX encounter + claim counts and writes alerts.

---

## Inputs (per payer profile)

| Input | Source |
|---|---|
| Profile `volume_monitor.alert_if_zero_trips_days` | JSON profile |
| Profile `volume_monitor.active_when` | gates / credentialed |
| Completed trips / CTS cases | `prism_nemt_data.json` / VERTEX trips |
| Claims generated / paid / denied | VERTEX INVOICES (Source System = NEMT) |
| Hard gates | `MOLINA_LTSS_*` flags |

## Rules (v1)

1. **HAP (`hap_caresource`):** If Vendor credentialed AND zero completed NEMT trips in Wayne/Macomb for **≥14 days** → YELLOW alert. ≥30 days → RED.
2. **Molina (`molina_mi_ltss`):** Only evaluate when **both** hard gates are True. Then same 14/30 day zero-volume rules statewide.
3. **Never alert** on Molina while attestation or Availity is False (expected zero).
4. **Oakland (HAP):** Any trip with Oakland county before pending county activated → RED config error.
5. **Denial spike:** If denial rate on last 20 claims > 5% → YELLOW (QC target ≤2%).

## Outputs

- Append to `logs/vertex_volume_monitor_last_run.json`
- Optional line in `PENDING_ACTIONS.md` / morning briefing
- No auto-email to payer without Dee approval

## Non-goals (v1)

- No automatic contract termination language
- No GBIS grant math
- No 837 generation

## Build estimate

Small cron/task in `nexus_scheduler.py` or `nexus_autonomous.py` — 1 focused session after profiles signed off.
