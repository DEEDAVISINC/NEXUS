# JETA — saved naming & usage (NEXUS)

**Status:** Planning / reserved for future implementation. Expand this doc when requirements and compliance scope are defined.

## Names

| Context | Use |
|--------|-----|
| **System name in NEXUS** | **JETA** |
| **Public / email tagline (desk name)** | **JETA Courtiere** — canonical brand spelling (from French *courtière*, broker). Use this org-wide. |

### Do not confuse (permanent)

| Name | What it is |
|------|------------|
| **JETA** | Internal **NEXUS module / system** identifier only. |
| **JETA Courtiere** | **Branding** for the jet fuel brokerage desk—signatures, intros, subject lines. **Not** an ASTM or military fuel specification. |
| **Jet A** / **Jet A-1** | The **actual** kerosene-type aviation turbine fuel names on **contracts, COAs, and uplift tickets** (e.g. per **ASTM D1655**). |

**Rule:** In external fuel or compliance documents, use **Jet A** / **Jet A-1** as the product. Use **JETA Courtiere** only as **who** is contacting or **which** NEXUS program—not as a substitute fuel grade name.

## Email & outbound identity

- Prefer showing **JETA Courtiere** in **From/display names**, signatures, and introductions so recipients understand the program.
- Optional subject prefix: `[JETA Courtiere]` or `[JETA]`.
- Example signature line: `JETA Courtiere — Jet fuel brokerage` (+ company / legal entity as appropriate).
- Optional accented form in formal French contexts: **JETA Courtière** (same brand).

## Product intent (high level)

- Internal **jet fuel brokerage** capability within NEXUS; aligned with **DDI** freight-broker DNA (matchmaking, execution discipline).
- Not implemented in the app yet—no module wiring until product/legal/banking details are settled.

## Related decisions from discussion

- Broker/intermediary model (introduce / fee-on-execution) vs taking title to be decided with counsel when active.
- Counterparty onboarding, KYC/AML, and mandates to be defined before live outreach.

## Knowledge ingestion (learning corpus)

- **Manifest:** `jeta/knowledge/manifest.json` — public RFPs + EIA links for JETA/RAG.
- **How to:** `jeta/knowledge/INGESTION.md` — chunking and guardrails.
- **Fetch PDFs locally:** `bash scripts/fetch_jeta_public_sources.sh` (outputs to `jeta/knowledge/pdfs/`, not committed).

## SAM.gov / NAICS (DDI)

- **Reference:** `jeta/knowledge/NAICS_SAM_GOV.md` — **425120** (petroleum/agents & brokers), **488510** (freight arrangement), **424720** (merchant wholesale if taking title). Confirm with CPA.

---

*Last updated: canonical tagline **JETA Courtiere** (was Courier/Courtier).*
