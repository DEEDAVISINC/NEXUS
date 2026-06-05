# 3D Ink — Loan Originator Rollup (From Scanback / Closing Packages)

**Purpose:** Track **loan officers (MLOs)** extracted from Closing Disclosure **page 5** (Contact Information) on every signing package you scan back — warm outreach for **In-Person Borrower Support**, separate from title-agent rollup.  
**Last Updated:** June 5, 2026  
**Status:** **Wave 0 — build list from scanbacks first, then peer outreach**

---

## WHY THIS EXISTS

`CLOSING_BUYER_ROLLUP.md` indexed **title agents / closers / schedulers** — not the **LO on the CD**.

Every scanback you return to a title company already contains:
- **Loan Originator Organization** + company NMLS  
- **Individual LO name** + **Contact NMLS ID**  
- Often **email and phone** (CD page 5)

Those LOs **already had a file where the borrower needed in-person help at the table.** That is a direct proof point for borrower navigation — warmer than cold ops email.

**You are a licensed MLO (NMLS# 2099291, MI + GA).** Peer-to-peer outreach is legitimate: colleague sharing a pattern, not vendor spam.

---

## EXTRACTION RULE (EVERY SIGNING)

**When:** Before or right after scanback upload — same moment you confirm pen color and ID copies.

**Where on package:** Closing Disclosure **page 5** — section **Contact Information**  
(Also check page 1 for **Lender** name and **Loan Type** / purpose.)

**Capture (no borrower PII in this file):**

| Field | Source |
|-------|--------|
| LO full name | CD Contact line |
| LO NMLS ID | Contact NMLS ID |
| Lender / org name | Lender block + Org NMLS ID |
| Company NMLS | NMLS ID (company) |
| LO email / phone | CD page 5 (verify OCR) |
| Loan product | Refi / HELOC / Purchase / Reverse / FHA / VA |
| Title / settlement co | From rollup cross-ref |
| Signing date | Your tracker |
| Friction note | Internal only — e.g. "borrower needed app/portal help" (no borrower name in outreach) |
| Source PDF | Internal filename only |

**Verify:** Look up Contact NMLS on [NMLS Consumer Access](https://www.nmlsconsumeraccess.org) before first email.

---

## ROLLUP TABLE

| Priority | LO name | NMLS | Lender / org | Co. NMLS | Product | Title co (file) | Email | Phone | Signed | Friction | Outreach |
|----------|---------|------|--------------|----------|---------|-----------------|-------|-------|--------|----------|----------|
| **A** | **Alvin Jabboury** | **1190987** | eMortgage Funding LLC | 1059364 | FHA refi | America's Title (Ortonville) | ⚠️ verify on CD / LinkedIn | ⚠️ verify | 12/2025 | TBD — pull from signing notes | ⬜ Wave 0 peer |
| — | ⚠️ **Extract from Daniel Mies HELOC** (#951754) | — | ⚠️ on First Class package | — | HELOC | — | — | — | 5/16/26 | **Known friction** — proof file | ⬜ **Dee: pull LO from package** |
| — | ⚠️ **Extract from STOWELL** (Finance of America refi) | — | Finance of America | — | Refi | Boston National Title | — | — | — | — | ⬜ OCR batch |
| — | ⚠️ **Extract from Jamison 2** (Mr. Cooper refi) | — | Mr. Cooper | — | Refi | Vylla Title | — | — | — | — | ⬜ OCR batch |
| — | ⚠️ **Extract from STONER** (Mr. Cooper / Title365) | — | Mr. Cooper | — | Refi | Holler / Title365 | — | — | — | — | ⬜ OCR batch |
| — | ⚠️ **Each active signing** (PCS, PSS, JP, First Class…) | — | On CD | — | — | — | — | — | 2026 | — | ⬜ Add on close |

*Increment file count when same LO appears on multiple signings — 3+ touches = ask for ops intro.*

---

## OUTREACH POSTURE

| Audience | Message |
|----------|---------|
| **Individual LO (Wave 0)** | Peer MLO — "I closed a file for your borrower; digital steps were a struggle; do you see this often?" → offer navigation support → ask **who owns fallout/pull-through** if they want a pilot |
| **Title scheduler (existing rollup)** | Relationship — backup signer |
| **Lender ops (Wave 1)** | Enterprise pilot — after you have LO names + proof from the field |

**Do NOT:** Name the borrower in email. **Do NOT:** CC title company on first LO note unless they introduced you.

---

## BATCH QUEUE (OCR BACKLOG)

Same PDFs as `CLOSING_BUYER_ROLLUP.md` — **add LO column**:

| PDF | Lender (known) | LO extracted? |
|-----|----------------|---------------|
| Image_001.pdf | eMortgage Funding LLC | ✅ Alvin Jabboury 1190987 |
| STOWELL.pdf | Finance of America | ⬜ |
| Jamison 2.pdf | Mr. Cooper | ⬜ |
| ISHO.pdf | TBD | ⬜ |
| KLINGER.pdf | TBD | ⬜ |
| STONER.pdf | Mr. Cooper | ⬜ |
| HINES.pdf | TBD | ⬜ |
| First Class #951754 (Mies HELOC) | TBD | ⬜ **priority** |
| All 2026 signings in `NOTARY_SIGNING_TRACKER.md` | On each CD | ⬜ ongoing |

---

## CROSS-REFERENCES

- `CLOSING_BUYER_ROLLUP.md` — title / law firm buyers  
- `LOAN_BORROWER_DIGITAL_NAV_LANE.md` — product strategy  
- `SEND_TO_BUYER/WAVE0_LO_PEER_OUTREACH.md` — copyable peer emails  
- `NOTARY_SIGNING_TRACKER.md` — signing dates + file numbers  
- `PARTNER_ACCOUNT_UPDATES.md` — "Build hit list of LOs from signing history" (pending → **this file**)

---

*One LO who says "yes, my borrowers stall on the portal" is worth ten cold LinkedIn searches.*
