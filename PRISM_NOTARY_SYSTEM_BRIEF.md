# PRISM — Notary System (Technical Brief)

**Audience:** Technical or operations contact reviewing how Dee Davis Inc. implements notary-related field services in NEXUS PRISM.  
**Stack:** Python / Flask blueprints, JSON file storage under `uploads/prism/`, REST-style HTTP APIs (registered from `api_server.py`).  
**Date:** April 2026  

---

## 1. What PRISM Is (Context)

PRISM is NEXUS’s **field service delivery layer**: intake → dispatch → execution → QC/scanback → completion. Notary work is **one service type** among others (drug testing, DNA, fingerprinting, etc.), with **dedicated compliance rules** and **optional** law-firm channel packaging.

---

## 2. Core Modules (Notary)


| Module                         | File                               | Role                                                                                                                                                                                                                                                                       |
| ------------------------------ | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Notary compliance API**      | `prism_notary_compliance.py`       | Reference data + helpers: notarial act types, ID rules, RON workflow, journal rules, fatal/correctable errors, state fee caps (incl. MI). Exposes JSON endpoints under `/prism/notary/…`.                                                                                  |
| **Law firm channel**           | `prism_law_firm_notary_channel.py` | SE Michigan **law firm** playbook: scheduling SOP, service menu summary, intake field schema, quote rules. **Live coverage** (counties, agents, capacity) in `uploads/prism/law_firm_coverage.json`. Endpoints under `/prism/law-firm-channel/…`.                          |
| **Orders & intake**            | `prism_orders_api.py`              | **POST `/prism/intake`** creates orders; `service_key` `**notary**` or `**notary-law-firm**` maps to internal type `**notary**`. Law-firm fields merge into `order.details.law_firm_account` when `channel: law_firm`. Persisted in `uploads/prism/orders.json`.           |
| **Inspection engine**          | `prism_inspection_engine.py`       | **31** notary-specific scanback/document rules (PCS CommonErrors–style + multi-state witness/seal checks). Used for **quality inspection** of uploaded work; `service_types` includes `notary`. Apostille section also references **notary validity** for SOS submissions. |
| **Service router (economics)** | `prism_service_router.py`          | Business routing metadata for `**notary_standard`**, `**notary_loan_signing**`, `**notary_ron**`, `**notary_apostille**` (margins, partners, notes — not the compliance engine).                                                                                           |
| **General compliance API**     | `prism_compliance_api.py`          | Broader checklist surface; includes at least one **notary seal** check in shared flows (not the full notary module).                                                                                                                                                       |


---

## 3. Notary Compliance API — Endpoints (`prism_notary_compliance.py`)


| Method | Path                                 | Purpose                                                                |
| ------ | ------------------------------------ | ---------------------------------------------------------------------- |
| GET    | `/prism/notary/acts`                 | All notarial act definitions (acknowledgment, jurat, copy cert, etc.). |
| GET    | `/prism/notary/determine-act`        | Query: suggest act type from `document_type` (+ optional `purpose`).   |
| GET    | `/prism/notary/verify-id`            | Query: ID acceptability.                                               |
| GET    | `/prism/notary/acceptable-ids`       | Primary/secondary ID lists + verification + credible witness rules.    |
| GET    | `/prism/notary/ron-requirements`     | RON requirements, workflow steps, limitations.                         |
| POST   | `/prism/notary/journal-entry`        | Body: journal entry payload (structure per module).                    |
| GET    | `/prism/notary/journal-requirements` | Journal keeping rules.                                                 |
| GET    | `/prism/notary/errors`               | Fatal errors vs correctable issues.                                    |
| GET    | `/prism/notary/fee-limits`           | Optional `?state=MI` — statutory fee caps snapshot.                    |


---

## 4. Law Firm Channel — Endpoints (`prism_law_firm_notary_channel.py`)


| Method | Path                                    | Purpose                                                                                                            |
| ------ | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| GET    | `/prism/law-firm-channel`               | Full playbook (versioned JSON): scheduling, **coverage** (schema + live file), intake schema, menu, travel zones). |
| GET    | `/prism/law-firm-channel/scheduling`    | Scheduling SOP only.                                                                                               |
| GET    | `/prism/law-firm-channel/coverage`      | `field_schema` + `**live`** from JSON file + merged `**hq_effective**`.                                            |
| GET    | `/prism/law-firm-channel/intake-schema` | Law-firm account form fields.                                                                                      |
| GET    | `/prism/law-firm-channel/service-menu`  | Practice verticals + price summary rows + zones (authoritative pricing still in business pricing doc).             |


**Live file:** `uploads/prism/law_firm_coverage.json` — editable without code deploy.

---

## 5. Orders Pipeline — Notary (`prism_orders_api.py`)

- **Routing email** for notary-class keys (notary, apostille, process): `**notary@deedavis.biz`** (configurable per `SERVICE_ROUTING_EMAILS`).
- **QC checklist (type `notary`):** **NOT-1 … NOT-7** — commission, ID, willingness, correct act, journal, seal, certificate wording. **FATAL** items block marking order complete until checked.
- **Workflow gates** for `notary`: identity, willingness, correct act → then journal, seal, scan/upload.
- **Scanback expectation** for notary orders: **2 pages** — *Notarized Document Scan*, *Notary Journal Entry* (see `SCANBACK_EXPECTATIONS` in module).
- **Agents API** sample data includes agents with specialty `**notary`** (and `**ron**` separately where applicable).

**Law firm intake:** `channel: law_firm` or `service_key: notary-law-firm` → `extract_law_firm_account_payload()` → stored under `**order.details.law_firm_account`**.

**Note:** A separate `**ron`** service type exists in QC/workflows (RON-1…RON-7) for orders classified as remote online notarization; default intake maps to `**notary**` unless the client sends a different `service_key`/typing.

---

## 6. Inspection Engine — Notary Rules (`prism_inspection_engine.py`)

- **~31** rules tagged `service_types: ['notary']` covering seal visibility, certificates, dates, witnesses (state-specific notes), Patriot Act notary title, jurat vs acknowledgment, etc.
- Apostille-related rules enforce **valid notarization** before state/federal authentication.
- Inspect API accepts `service_type` `**notary`** (among others) for order-based inspection runs.

---

## 7. Service Router — Notary & Related SKUs (`prism_service_router.py`)

Logical product buckets in `SERVICE_CATALOG` (for margin/partner modeling, not legal compliance):

**Notary / document**

- `notary_standard` — §3 MiLONA general notarization
- `notary_cntda_estate` — §4 CNTDA trust/estate/POA packages
- `notary_loan_signing` — §7 loan signing / NSA
- `notary_ron` — remote online notarization
- `notary_apostille` — apostille coordination (after notarization as needed)

**Adjacent (often paired with notary; separate fulfillment)**

- `legal_courier_filing` — §6 court / SOS / legal runner
- `permit_runner_npr` — §6A NPR / building permit line

---

## 8. Pricing Authority (Outside PRISM Code)

Business **rate card** and statutory notary fee language live in `**DDI_PROFESSIONAL_SERVICES_PRICING.md`** and `**COMPLIANCE_KNOWLEDGE/NOTARY_REFERENCE.md**`. PRISM exposes **summaries** in the law-firm channel API; it does not replace those documents.

---

## 9. Integration Point

Blueprints are registered in `**api_server.py`** (e.g. `prism_notary`, `prism_law_firm_channel`, `prism_orders`, `prism_inspection`). Full PRISM architecture overview: `**PRISM_MASTER.md**`.

---

*This brief describes the codebase as implemented; it is not a legal opinion on notarial practice.*