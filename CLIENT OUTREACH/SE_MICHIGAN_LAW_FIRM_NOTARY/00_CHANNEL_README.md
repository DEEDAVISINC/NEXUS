# SE Michigan — Law Firm Mobile Notary

**Canonical source:** PRISM module **`prism_law_firm_notary_channel.py`** (not duplicate markdown).

## API (NEXUS backend)

| Endpoint | Returns |
|----------|---------|
| `GET /prism/law-firm-channel` | Full playbook: scheduling SOP, coverage template schema, practice verticals, price summary rows, travel zones, intake JSON schema |
| `GET /prism/law-firm-channel/scheduling` | Scheduling SOP only |
| `GET /prism/law-firm-channel/coverage` | Field schema + **live** counties/agents/capacity from **`uploads/prism/law_firm_coverage.json`** (edit file, no deploy) |
| `GET /prism/law-firm-channel/intake-schema` | Law-firm account field schema (forms / UI) |
| `GET /prism/law-firm-channel/service-menu` | Menu + pricing summary + quote rules |

## Intake → orders

`POST /prism/intake` with:

- `channel`: `law_firm` **or** `service_key`: `notary-law-firm`

Law-firm fields (flat on JSON body or nested under `law_firm_account`) are copied into **`order.details.law_firm_account`** per the intake schema.

## Pricing authority

**`DDI_PROFESSIONAL_SERVICES_PRICING.md`** remains the numeric source of truth; the PRISM bundle mirrors summary rows for UI.

## Docs

- **`PRISM_MASTER.md`** §17 — endpoint list  
- **`STRUCTURED_SETTLEMENT_NOTARY_OUTREACH.md`** — national NSSTA lane (separate from local law-firm list)
