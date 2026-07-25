# SUBCONTRACTOR ONBOARDING PACKET

**This packet contains every document a subcontractor must complete before beginning work on a Dee Davis Inc. prime contract. Documents are executed in order — do not skip steps.**

---

## EXECUTION ORDER

```
1. NDA → Signed FIRST (before any contract details are shared)
2. NON-COMPETE → Signed SECOND (before contract-specific details are shared)
3. COI → Received and verified THIRD (before work begins)
4. W-9 → Received FOURTH (before any payment)
5. LOI / TEAMING AGREEMENT → Signed LAST (formalizes the engagement)
```

---

## DOCUMENT 1: NON-DISCLOSURE AGREEMENT (NDA)

> **Note:** NEXUS can auto-generate this via API: `POST /gpss/subcontractors/<id>/generate-nda`
> The generated NDA includes mutual confidentiality, govcon protections (no end-run, no client poaching), and a 2-year term.

### Key NDA Provisions (Verify These Are Included):

- [ ] **Mutual confidentiality** — Both parties protect each other's information
- [ ] **Definition of confidential info** — Client names, contract details, pricing, solicitation info, business methods
- [ ] **No end-run clause** — Sub cannot bid directly on the same contract or with the same agency
- [ ] **No client disclosure** — Sub cannot reveal DDI's client to anyone
- [ ] **No supplier/sub poaching** — Sub cannot recruit DDI's other subs or suppliers
- [ ] **Term: 2 years** after contract completion or termination
- [ ] **Remedy: Injunctive relief** — DDI can seek court order to stop violations immediately
- [ ] **Governing law: Michigan**

### After NDA Is Signed:

**NOW you can share:**
- General scope of work
- Service type and general location
- Timeline expectations
- What you're looking for in a subcontractor

**Still DO NOT share:**
- Agency/client name
- Solicitation number
- Contracting officer name
- Specific facility address

---

## DOCUMENT 2: NON-COMPETE AGREEMENT

### Non-Compete Provisions:

**During the contract term AND for 12 months after:**

The Subcontractor agrees NOT to:

1. **Bid directly** on the same contract, follow-on contract, or recompete with the same agency
2. **Solicit or contact** the end client, contracting officer, or any agency personnel identified through this engagement
3. **Solicit DDI's clients, teaming partners, or other subcontractors** for competing work
4. **Use any information** gained through DDI to compete against DDI on the same or similar opportunities
5. **Perform the same services** for the same end client through another prime contractor

**Scope limitations:**
- Geographic: Limited to the contract performance area
- Service type: Limited to the specific services performed under this subcontract
- Duration: Contract period + 12 months

**Remedy:**
- Liquidated damages: $____________ (typically 25-50% of subcontract value)
- Injunctive relief available
- Sub pays DDI's attorney fees if DDI prevails

### After Non-Compete Is Signed:

**NOW you can share (in addition to NDA-level info):**
- Contract-specific details
- Performance location (still use caution with agency name)
- Specific requirements and deliverables
- Timeline and milestones

---

## DOCUMENT 3: CERTIFICATE OF INSURANCE (COI) REQUEST

### COI Request Email Template:

```
Subject: Insurance Certificate Request — Dee Davis Inc. Subcontract

Hi [Sub Contact Name],

Thank you for your interest in partnering with Dee Davis Inc. on this opportunity.

Before we can formalize our agreement, we need a current Certificate of Insurance (COI) showing:

REQUIRED COVERAGE:
- General Liability: Minimum $1,000,000 per occurrence / $2,000,000 aggregate
- Workers' Compensation: Per state requirements for [State]
- [Commercial Auto: Minimum $1,000,000 per occurrence — if driving involved]
- [Professional Liability/E&O: Minimum $1,000,000 — if professional services]

ADDITIONAL REQUIREMENTS:
- DEE DAVIS INC must be listed as ADDITIONAL INSURED
- 30-day written cancellation notice to DDI required
- Policy dates must cover the anticipated contract period: [Start] through [End]

Please send the COI to: gc@deedavis.biz

Certificate Holder:
Dee Davis Inc.
755 W. Big Beaver Rd., Suite 2020
Troy, Michigan 48084

If your current coverage does not meet these minimums, please let us know and we can discuss. Some adjustments may be possible depending on the scope.

Looking forward to working together.

Best regards,
Dee Davis
President & CEO
Dee Davis Inc.
248.376.4550 | info@deedavis.biz
```

### COI Verification Checklist (When Received):

- [ ] General Liability limits meet minimums
- [ ] Workers' Compensation active in correct state
- [ ] Commercial Auto (if required) meets minimums
- [ ] Professional Liability (if required) meets minimums
- [ ] DEE DAVIS INC listed as Additional Insured
- [ ] 30-day cancellation notice included
- [ ] Policy dates cover contract period
- [ ] Insurance carrier is reputable (AM Best A- or better)
- [ ] COI filed in bid folder
- [ ] COI logged in Airtable compliance tracking
- [ ] Calendar reminder set for policy expiration

---

## DOCUMENT 4: W-9 REQUEST

### W-9 Request Email Template:

```
Subject: W-9 Request — Dee Davis Inc.

Hi [Sub Contact Name],

For our records and tax reporting purposes, please provide a completed W-9 form at your earliest convenience.

Please send to: info@deedavis.biz

If you need a blank W-9 form: https://www.irs.gov/pub/irs-pdf/fw9.pdf

Thank you,
Dee Davis
Dee Davis Inc.
248.376.4550 | info@deedavis.biz
```

---

## DOCUMENT 5: LETTER OF INTENT (LOI) / TEAMING AGREEMENT

> **Note:** NEXUS can auto-generate teaming agreements via API: `POST /gpss/subcontractors/<id>/generate-teaming-agreement`

### LOI Template (For Pre-Award — Before Contract Is Won):

```
LETTER OF INTENT TO SUBCONTRACT

Date: [Date]

From: Dee Davis Inc. (Prime Contractor)
      755 W. Big Beaver Rd., Suite 2020
      Troy, Michigan 48084
      CAGE: 8UMX3 | UEI: HJB4KNYJVGZ1

To:   [Subcontractor Company Name]
      [Address]

RE: Intent to Subcontract — [Generic Service Description]

Dear [Sub Contact Name],

Dee Davis Inc. intends to submit a proposal for a [generic description - e.g., "federal 
grounds maintenance contract"] and is pleased to confirm our intent to include 
[Subcontractor Name] as a subcontractor for the following scope of work:

SCOPE:
- [Service 1]
- [Service 2]
- [Service 3]

ESTIMATED SUBCONTRACT VALUE: $____________
CONTRACT PERIOD: [Base year + option years]
PERFORMANCE LOCATION: [General area only]

TERMS:
- Payment: Net 30 after DDI receives government payment
- DDI manages all government reporting and communication
- Sub provides all labor, equipment, and materials for scope above
- Sub maintains required insurance throughout contract period
- Sub complies with all NDA and Non-Compete provisions

This Letter of Intent is non-binding and is contingent upon:
1. DDI receiving the prime contract award
2. Successful negotiation of final subcontract terms
3. Sub maintaining all required licenses, insurance, and certifications

Both parties agree to negotiate in good faith upon contract award.

_______________________________     _______________________________
Dee Davis                           [Sub Representative Name]
President & CEO                     [Title]
Dee Davis Inc.                      [Company Name]
Date: ___________                   Date: ___________
```

---

## ONBOARDING TRACKING

| Step | Document | Status | Date Sent | Date Received | Verified |
|---|---|---|---|---|---|
| 1 | NDA | Pending / Sent / Signed | | | |
| 2 | Non-Compete | Pending / Sent / Signed | | | |
| 3 | COI | Pending / Requested / Received / Verified | | | |
| 4 | W-9 | Pending / Requested / Received | | | |
| 5 | LOI / Teaming Agreement | Pending / Sent / Signed | | | |
| 6 | Staffing Plan | Pending / Requested / Received | | | |
| 7 | Work Plan | Pending / Requested / Received | | | |

**ALL steps must show "Signed" or "Verified" before work begins.**

---

*This packet is the firewall between DDI and subcontractor risk. Every document serves a purpose. Every step is in order. No shortcuts.*
