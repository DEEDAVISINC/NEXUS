# NEXUS — Master To-Do List

Single in-repo to-do list for outstanding NEXUS work. Add new items at the
bottom of the relevant section. Mark complete by changing `[ ]` → `[x]` and
moving the line under **Completed** (with the date you finished it).

---

## Active

### SAM.gov CO Contact Sync (`sam_co_contact_sync.py`)

- [ ] Retry the sweep with the `ncode` fix to confirm per-NAICS counts are
      now distributed correctly (not the lopsided "144 / 0 / 0 / …" pattern).
      Recommended first run:
      `python3 nexus_scheduler.py --sync-cos --limit-naics 5 --days 7`
- [ ] If the small sweep looks healthy, scale up gradually (e.g.
      `--limit-naics 15`, then `--limit-naics 39` for full coverage).
- [ ] Decide whether to put the full sweep back on a schedule (and if so,
      what cadence — daily? weekly?). Currently it is **manual only**; the
      auto-hook was removed from `run_federal_mining()` on 2026-04-24 to
      stop surprise bandwidth use.
- [ ] Spot-check the 144 CO records that were upserted on 2026-04-24 from
      the partial NAICS 541620 sweep — confirm they look clean in
      `GPSS CONTACTS` (Name / Email / Title / Organization / Notes).

### Other SAM.gov Miners (latent `naics` → `ncode` bug)

- [ ] Audit other miners that hit `api.sam.gov/opportunities/v2/search`
      to confirm they use `ncode` (the canonical NAICS request param), not
      `naics` (which is silently ignored). Already fixed:
      `sam_co_contact_sync.py`, `mine_co_contacts.py`. Worth checking:
      `mine_real_federal_forecasts.py`, `auto_mine_edwosb_wosb_only.py`,
      `federal_forecasts_system.py`, `mine_all_sources_sought.py`,
      `nexus_backend.handle_sam_api_search`.

### Tracked State / Local Opportunities

- [ ] Massachusetts DPH RFR 221931 Courier Services — future outreach
      (no near-term deadline; bid notification only).
- [ ] Maryland MVA ITQ V-HQ-26065-S Courier Services — confirm eMMA
      registration status; pursue if eligible.
- [ ] Illinois IDPH Emergency Purchase Statement 26-482DPH-PREPD-B-51271 —
      track for follow-on solicitations.
- [ ] Contra Costa County RFQ_QUAL_F-Contr-0000000039 (Recovery Residences
      / Employment Vendor Pool) — SOQ deadline **2026-04-27**. Decide
      go / no-go through Cause We Care lens (local preference is the gating
      issue).

---

## Backlog (future work the user has flagged)

- [ ] _add new items here as they come up_

---

## Completed

- [x] **2026-04-24** — Built `sam_co_contact_sync.py` to harvest SAM.gov
      `pointOfContact` (primary + secondary) into `GPSS CONTACTS`
      (idempotent, dedupe by email).
- [x] **2026-04-24** — Wired `--sync-cos` and `--limit-naics N` /
      `--days N` flags into `nexus_scheduler.py`.
- [x] **2026-04-24** — Removed CO sync auto-hook from
      `run_federal_mining()` so cron `--mine` no longer triggers it.
- [x] **2026-04-24** — Rotated invalid `SAM_GOV_API_KEY` in `.env`
      (old `SAM-978ea568…` → new `SAM-2b93241d…`); verified live with a
      200-OK request returning 14,268 NAICS-492110 opportunities.
- [x] **2026-04-24** — Fixed silent SAM.gov `naics` → `ncode` request
      param bug in `sam_co_contact_sync.py` and `mine_co_contacts.py`.
- [x] **2026-04-24** — Added Massachusetts DPH RFR 221931 Courier Services
      to `tracked_state_opportunities.json` and `GPSS OPPORTUNITIES`.
- [x] **2026-04-24** — Added Maryland MVA ITQ V-HQ-26065-S to
      `tracked_state_opportunities.json` and `GPSS OPPORTUNITIES`.
- [x] **2026-04-24** — Added Illinois IDPH Emergency Purchase Statement
      to `tracked_state_opportunities.json`.
- [x] **2026-04-24** — Added Contra Costa County RFQ to tracked state
      opportunities and re-evaluated fit through Cause We Care lens.
