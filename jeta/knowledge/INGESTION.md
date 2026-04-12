# JETA knowledge ingestion

## Purpose

Feed **JETA** (and any RAG / copilot) with **structured, cited** chunks from **public** documents—primarily **airport/municipal aviation fuel RFPs** and **EIA** data—not as legal truth, but as **pattern libraries** (specs, pricing forms, evaluation criteria).

## What gets ingested

| Layer | Source | Action |
|-------|--------|--------|
| **Manifest** | `manifest.json` | Single source of truth for URLs and topics. |
| **PDFs** | Run `scripts/fetch_jeta_public_sources.sh` | Downloads into `pdfs/` (gitignored). |
| **Future** | Airtable or vector DB | Chunk + embed with metadata from manifest. |

## Chunking (for RAG)

1. Split PDFs by **logical sections** (Purpose, Specifications, Pricing, Insurance, Evaluation, Attachments).
2. Store with metadata: `source_id`, `page_range`, `doc_type: airport_rfp`, `jurisdiction`.
3. Tag **unverified_training** vs **internal_policy** when mixing with NEXUS-owned content.

## Guardrails

- Do **not** treat RFP text as **regulatory** or **universal** contract law.
- **Refresh** manifest when links rot; EIA URLs are stable; city PDFs may move.
- Optional: add **Buildofarm** or other **paid course** material only if **license allows** and tagged **third_party_training**.

## Next implementation steps (when building JETA module)

1. Ingest pipeline: PDF → text extract → chunk → embed.
2. UI: show **citations** to `source_id` + section.
3. Human review queue for **first** 50 chunks from new solicitations.
