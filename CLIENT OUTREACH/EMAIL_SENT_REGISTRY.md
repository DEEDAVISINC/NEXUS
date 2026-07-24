# Email Sent Registry — DO NOT RE-EMAIL

**Primary log:** `OUTBOUND_EMAIL_LOG.md` — search there first. This file is a dedupe index synced from the master log.

**Rule:** `.cursor/rules/no-re-email-sent-contacts.mdc` · **Log sends:** `.cursor/rules/log-every-send-immediately.mdc` · **CLI:** `python3 log_outbound_email.py`

---

## How to use

```
grep -i "email@domain.com" CLIENT OUTREACH/EMAIL_SENT_REGISTRY.md
```

If found → **SKIP** unless follow-up date has passed AND Dee approved follow-up.

---

## Confirmed sends (do not cold re-pitch)

| Date | To (email) | Contact / Org | Subject / purpose | Source |
|------|------------|---------------|-------------------|--------|
| 2026-03-31 | OhioMedicaidProvider@anthem.com | Shelley Brown / Anthem Ohio | NEMT TPA MyCare D-SNP | Daniel Rivera thread · `PENDING_ACTIONS.md` |
| 2026-03-26 | (Aetna intake form) | Aetna Better Health national/MI | Vendor intake | `AETNA_TPA_VENDOR_OUTREACH.md` |
| ~2026-05-11 | ABHTXcredentialing@aetna.com | Aetna TX (wrong inbox) | PRMS #341819465 closed | `AETNA_TPA_VENDOR_OUTREACH.md` |
| 2026-05-11 19:53 ET | stephanie.logan@medicaid.alabama.gov | Stephanie Logan / AL Medicaid NEMT | NEMT TPA intro | **Dee confirmed** · was ⬜ in file |
| 2026-05-12 | Bennett.Emfinger@medicaid.alabama.gov | Bennett Emfinger / AL Medicaid NET | NET outreach | `PENDING_ACTIONS.md` |
| 2026-05-12 | Natalie.A.Lukaszewicz@CENTENE.COM | Natalie Lukaszewicz / Centene corp | Rick Johnson referral | `OHIO_MCO_OUTREACH_EMAILS.md` |
| 2026-05-13 | (Kristen Halsey email) | Kristen Halsey / CareSource Ohio | Full service pitch | `PENDING_ACTIONS.md` · follow-up May 20 |
| 2026-05-19 | OHMedicaidProviderRelations@humana.com | Humana Ohio (Denise) | Misrouted — awaiting vendor contact | `PENDING_ACTIONS.md` |
| 2026-05-19 | liam.thomas@la.gov | Liam Thomas / LA OGB | TPA supplemental benefits | `PENDING_ACTIONS.md` |
| 2026-05-26 | (multiple LA MCO inboxes) | LA MCO emergency batch | HAVEN / flood — 6 plans | `HAVEN_MCO_OUTREACH_TRACKER.md` |
| 2026-05-29 | Isabelle.Vallejo@uhtx.com | University Health TX | Per-mile rates | `PENDING_ACTIONS.md` |
| 2026-05-30 | apabin@mibluecrosscomplete.com | Alina Pabin / BCC | NEMT follow-up | `ACTIVE_RELATIONSHIP_STATUS.md` |
| 2026-05-30 | MedinaA@michigan.gov, SurmaA@michigan.gov | Angela Medina / Aimee Surma MDHHS | SHIELD follow-up | `ACTIVE_RELATIONSHIP_STATUS.md` |
| 2026-06-07 | Brian.Grcevich@CareSource.com (+ Dana, Michael; CC MI_Network) | Brian / Dana / Michael / HAP CareSource | HIDE SNP NEMT routing vs MTM orientation | `MEMBER_ROUTING_MTM_CONFLICT_EMAIL_READY.md` |
| 2026-05-31 | Brian.Grcevich@CareSource.com | Brian / HAP CareSource | SDOH navigation | `ACTIVE_RELATIONSHIP_STATUS.md` |
| 2026-05-31 | Dana.Drew@CareSource.com | Dana / HAP CareSource | Oakland enrollment | `ACTIVE_RELATIONSHIP_STATUS.md` |
| 2026-05-31 | (Jennifer Eliopoulos) | UH Newark | Debrief on-file | MCO queue #2 |
| 2026-05-31 | beth.rubin@jfs.ohio.gov | Beth Rubin / Greene County CDJFS OH | County NEMT debrief | **ON RFP NOTIFICATION LIST** — Beth Jun 1 confirmed · thread closed |
| 2026-06-01 | beth.rubin@jfs.ohio.gov | Beth Rubin / Greene County OH | Re: thank you | **Do not re-pitch** — wait for RFP notice |
| 2026-05-31 | stephanie.logan@medicaid.alabama.gov | Stephanie Logan | **DUPLICATE — do not send again** | OOO auto-reply |
| 2026-06-03 | stephanie.logan@medicaid.alabama.gov (+ Bennett CC) | Stephanie Logan / Bennett Emfinger | **Reply received** — Bennett to facilitate | DDI short ack same day |
| 2026-06-04 | Bennett.Emfinger@medicaid.alabama.gov (+ Stephanie) | Bennett Emfinger | **Reply received** — internal review; will reach out | DDI ack: “let me know if questions” · **HOLD ~Jun 18–25** |
| 2026-05-31 | jgiombetti@eswa.org | Jason Giombetti / ESWA | Elder Transportation RFP interest | **Next cycle ~2029** — hard LOI May 22 this cycle · not a no · re-outreach when RFP opens |
| 2026-06-01 | jgiombetti@eswa.org | Jason Giombetti / ESWA | Re: thank you / next cycle | Thread closed this cycle · **reach out again ~2029** |
| 2026-06-01 | cushnerm@upstate.edu | Michael Cushner / SUNY Upstate | HMCS052626 home medical courier | **Active bid** · reply received 10:28 AM · full due Jun 17 9 AM |
| 2026-06-02 | cushnerm@upstate.edu | Michael Cushner / SUNY Upstate | HMCS052626 pricing clarifications | **Answered Jun 2 ~2 PM** — Onondaga invoice blocker · NTE hard $1.5M cap · see `CUSHNER_QA_2026-06-02.md` |

---

## LinkedIn / portal (no duplicate email pitch)

| Date | Channel | Contact / Org | Notes |
|------|---------|---------------|-------|
| 2026-03-26 | Aetna intake portal | Aetna Better Health | National/MI intake submitted |
| — | CVS Supplier Portal | CVS/Aetna | Registered |
| — | LinkedIn | Aetna VP Network Dev / LTSS | Message sent · `AETNA_TPA_VENDOR_OUTREACH.md` |

---

## NOT confirmed sent — verify with Dee before emailing

| Email | Contact | Notes |
|-------|---------|-------|
| andrew.hill@adph.state.al.us | Andrew Hill / ADPH AL | May 11 file shows ⬜ — **ask Dee** |
| Natasha.Crusoe@medicaid.alabama.gov | Natasha Crusoe / AL NET | OOO routing May 31 — **never sent** per records |
| GANewContracts@CareSource.com | CareSource GA | Draft only — verify |
| All other `MCO_SEND_ONE_AT_A_TIME.md` NET-NEW rows | Various | **Grep this file + ask Dee before any send** |

---

## Bounced = already emailed (follow-up only with fixed address)

| Date | Email | Notes |
|------|-------|-------|
| ~2026-05-11 | (old BlueCare TN address) | Bounced — use corrected address only on **approved follow-up**, not cold batch |

---

*When in doubt: ask Dee. Never assume net-new from an unchecked ⬜ box.*
