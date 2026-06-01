# Outbound Email Log — Every Email Dee Sends

**Single source of truth for ALL outbound email** (CO, MCO, buyer, supplier, partner, grant).

**Before recommending or drafting ANY email:** grep this file for the TO address.

**When Dee confirms a send:** log here **first** — same chat turn. See `.cursor/rules/log-every-send-immediately.mdc` and `log_outbound_email.py`.

**Federal CO-only history (Mar 2026):** also in `CO_OUTREACH_LOG.md` and `CLIENT OUTREACH/FEDERAL CO OUTREACH PIPELINE/CO_OUTREACH_TRACKER.md`

---

## 2026-05-31

| Time | To | Contact | Organization | Subject | Category | Source file | Status |
|------|-----|---------|--------------|---------|----------|-------------|--------|
| — ET | Brian.Grcevich@CareSource.com | Brian Grcevich | HAP CareSource | HIDE SNP — Benefits & SDOH Navigation TPA | mco | MCO_SEND_ONE_AT_A_TIME.md #1 | SENT |
| — ET | Dana.Drew@CareSource.com | Dana Drew | HAP CareSource | Oakland County — NEMT Vendor 100000469269 | mco | MCO_SEND_ONE_AT_A_TIME.md #1B | SENT |
| — ET | (Jennifer Eliopoulos) | Jennifer Eliopoulos | University Health Newark | Debrief / on-file | mco | MCO_SEND_ONE_AT_A_TIME.md #2 | SENT |
| — ET | (Beth Rubin) | Beth Rubin | Greene County OH | Debrief / on-file | mco | MCO_SEND_ONE_AT_A_TIME.md #3 | SENT |
| — ET | stephanie.logan@medicaid.alabama.gov | Stephanie Logan | Alabama Medicaid NEMT | NEMT TPA (duplicate) | mco | MCO queue #25 | **DUPLICATE — first send 2026-05-11** |

---

## 2026-05-30

| Time | To | Contact | Organization | Subject | Category | Source file | Status |
|------|-----|---------|--------------|---------|----------|-------------|--------|
| — ET | apabin@mibluecrosscomplete.com | Alina Pabin | Blue Cross Complete MI | NEMT & pharmacy TPA follow-up | mco | ACTIVE_RELATIONSHIP_STATUS.md | SENT |
| — ET | MedinaA@michigan.gov | Angela Medina | MDHHS CLPPP | SHIELD follow-up | buyer | ACTIVE_RELATIONSHIP_STATUS.md | SENT |
| — ET | SurmaA@michigan.gov | Aimee Surma | MDHHS CLPPP | SHIELD follow-up (CC) | buyer | ACTIVE_RELATIONSHIP_STATUS.md | SENT |

---

## 2026-05-29

| Time | To | Contact | Organization | Subject | Category | Source file | Status |
|------|-----|---------|--------------|---------|----------|-------------|--------|
| — ET | Isabelle.Vallejo@uhtx.com | Isabelle Vallejo | University Health TX | Per-mile rates | mco | PENDING_ACTIONS.md | SENT |

---

## 2026-05-26

| Time | To | Contact | Organization | Subject | Category | Source file | Status |
|------|-----|---------|--------------|---------|----------|-------------|--------|
| 11:30 ET | (LA MCO batch — multiple inboxes) | LA MCO contacts | LA Medicaid plans | HAVEN emergency / flood | mco | HAVEN_MCO_OUTREACH_TRACKER.md | SENT — 6 plans |

---

## 2026-05-19

| Time | To | Contact | Organization | Subject | Category | Source file | Status |
|------|-----|---------|--------------|---------|----------|-------------|--------|
| — ET | OHMedicaidProviderRelations@humana.com | Denise / Humana OH | Humana Ohio D-SNP | NEMT TPA (misrouted) | mco | PENDING_ACTIONS.md | SENT — awaiting vendor routing |
| — ET | liam.thomas@la.gov | Liam Thomas | Louisiana OGB | TPA supplemental benefits | buyer | PENDING_ACTIONS.md | SENT |

---

## 2026-05-13

| Time | To | Contact | Organization | Subject | Category | Source file | Status |
|------|-----|---------|--------------|---------|----------|-------------|--------|
| — ET | (Kristen Halsey email) | Kristen Halsey | CareSource Ohio | Full service pitch | mco | PENDING_ACTIONS.md | SENT |

---

## 2026-05-12

| Time | To | Contact | Organization | Subject | Category | Source file | Status |
|------|-----|---------|--------------|---------|----------|-------------|--------|
| — ET | Bennett.Emfinger@medicaid.alabama.gov | Bennett Emfinger | Alabama Medicaid NET | NET outreach | mco | PENDING_ACTIONS.md | SENT |
| — ET | Natalie.A.Lukaszewicz@CENTENE.COM | Natalie Lukaszewicz | Centene Corporate | Rick Johnson referral | mco | OHIO_MCO_OUTREACH_EMAILS.md | SENT |

---

## 2026-05-11

| Time | To | Contact | Organization | Subject | Category | Source file | Status |
|------|-----|---------|--------------|---------|----------|-------------|--------|
| 19:53 ET | stephanie.logan@medicaid.alabama.gov | Stephanie Logan | Alabama Medicaid NEMT | NEMT TPA Program Administration — DEE DAVIS INC | Alabama Medicaid | mco | CLIENT OUTREACH/ALABAMA MCO NEMT HAVEN/ALABAMA_HOT_REPLY_EMAILS_MAY11.md | SENT — Dee confirmed |
| 19:53 ET | stephanie.logan@medicaid.alabama.gov | Stephanie Logan | Alabama Medicaid NEMT | NEMT TPA Program Administration | mco | ALABAMA_HOT_REPLY_EMAILS_MAY11.md | SENT — **Dee confirmed** |

---

## 2026-03-31

| Time | To | Contact | Organization | Subject | Category | Source file | Status |
|------|-----|---------|--------------|---------|----------|-------------|--------|
| — ET | OhioMedicaidProvider@anthem.com | Shelley Brown | Anthem Ohio | NEMT TPA MyCare D-SNP | mco | PENDING_ACTIONS.md | SENT — Daniel Rivera thread |

---

## HOW TO ADD A ROW

**In chat:** Dee says "sent" → NEXUS adds row above same turn.

**CLI:**
```bash
python3 log_outbound_email.py \
  --to "email@domain.com" \
  --contact "Full Name" \
  --org "Organization" \
  --subject "Subject line" \
  --date "2026-05-11 19:53" \
  --category mco \
  --source "CLIENT OUTREACH/path/to/draft.md"
```

---

## BACKFILL TODO

Rows marked `(email)` need TO address filled from Sent folder when available. **Do not re-email while backfilling.**

*Last consolidated: 2026-05-31 — merge ongoing sends into this file only.*
