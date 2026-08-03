# Humana Dual Integrated (MI) — Credentialing Playbook

**Last Updated:** August 1, 2026  
**Plan:** Humana Medical Plan of Michigan, Inc. — Humana Dual Integrated (HMO D-SNP) / Midwest contracting  
**Official join page:** https://provider.humana.com/medicaid/michigandsnp/join-our-network  
**Status:** 🟡 **IN PROGRESS** — Humana Contracting invited DDI into Quickbase (Abby Davidson, Aug 1, 2026)

> **Portal / network request ≠ contract.** Completing these steps gets DDI into Humana’s credentialing/contracting queue. Award still requires their paperwork + committee.

---

## ACTIVE PATH — Humana Contracting invitation (FOLLOW THIS)

| Field | Value |
|---|---|
| **Contact** | **Abby Davidson** — Supervisor IN & MI, Provider Network Operations, Contracting Negotiations – Midwest Region |
| **Invite received** | August 1, 2026 |
| **Portal** | https://humana-6853.quickbase.com/nav/app/buwr742wd |
| **Tutorial** | https://provider.humana.com/working-with-us/making-it-easier#skip-header |
| **Rule from Abby** | They **will not proceed** until required documents for provider type are **uploaded** |
| **After submit** | Email confirmation with **Inquiry ID #** — Contracting Team follows up |
| **Form note (Aug 1)** | Red Taxonomy Warning = **MI market + transportation/LTSS taxonomy not available for online Quickbase submit**. Do **not** keep changing taxonomies to clear it. **Reply to Abby** with screenshot: `CREDENTIALING/REPLY_ABBY_DAVIDSON_TAXONOMY_WARNING.md`. Parallel: DAAA if she confirms LTSS path. |
| **Address on forms** | Always **Troy, MI 48084** (not 48083) |

### Abby path checklist

1. [ ] Open portal → **download** required documents for provider type
2. [ ] Complete packet (W-9, ownership, insurance, roster, etc. as listed)
3. [ ] **Upload** all required docs + supporting paperwork
4. [ ] Submit → save **Inquiry ID #** here: _______________
5. [ ] Reply to Abby only if upload/submit fails or market warning blocks after correct docs
6. [ ] CAQH **16876320** — still complete/attest + authorize Humana in parallel
7. [ ] Log Inquiry ID + status in `PENDING_ACTIONS.md` + `COMPANY_INFO_MASTER.md`

---

## DDI Identity (use on every form / email)

| Field | Value |
|---|---|
| **Legal name** | Dee Davis Inc. |
| **NPI** | 1538939111 |
| **CHAMPS Provider ID** | 6309049 (Atypical Agency / NEMT — ACTIVE) |
| **CAQH Provider ID** | 16876320 (Dieasha Davis) — **attest first** |
| **Taxonomy** | 347E00000X (Transportation Broker) |
| **Address** | 755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084 |
| **Phone** | 248.376.4550 |
| **Email** | info@deedavis.biz |
| **EIN / TIN** | (from W-9 — do not store in this file) |
| **Proof contracts** | HAP CareSource Vendor **100000469269** · Molina LTSS Vendor **214337479** (NMT + CTS) |

---

## Pick the RIGHT Humana lane (do not mix)

Humana Dual Integrated splits networks. DDI’s Molina win was **LTSS / HCBS** (Non-Medical Transportation + Community Transition Services) — **not** medical NEMT under a trip broker.

| Lane | When to use | Where to apply |
|---|---|---|
| **✅ LTSS / HCBS (PRIMARY for DDI)** | NMT, CTS, HCBS waiver-style services — same model as Molina | **Wayne / Macomb (+ contiguous):** Detroit Area Agency on Aging (DAAA) → `contractmgt@daaa1a.org` · **Other MI counties:** `LTSSContracting@humana.com` |
| ⚠️ Transportation (medical NEMT broker) | Only if pursuing trip-level medical NEMT under Humana’s broker | **SafeRide Health** (per Humana join page) — different game; do **not** lead with this if goal is Molina-style LTSS |
| ❌ Physical / behavioral health | Clinicians, groups, BH | Online “request to join” form · roster adds → `MichiganMarket@humana.com` / `MIBHMedicaid@humana.com` |
| ❌ Pharmacy / dental / vision / hearing | Not DDI’s wedge | Separate specialty networks |

**Aug 1 override:** Abby Davidson (Humana Contracting IN & MI) invited DDI into **Quickbase** — that is the **primary** path now. DAAA remains a **backup / LTSS-specific** route if Abby’s team says HCBS must go through DAAA.

---

## Run order (do in this sequence)

### Step 1 — Quickbase packet (Abby invite) — DO THIS NOW

Portal: https://humana-6853.quickbase.com/nav/app/buwr742wd  
See **ACTIVE PATH** checklist above. No contract progress until uploads are done.

### Step 2 — CAQH in parallel

Record: `CREDENTIALING/CAQH_PROVIDER_PORTAL.md`

1. [ ] Register at https://proview.caqh.org/pr — CAQH ID **16876320**
2. [ ] Complete profile (NPI 1538939111, CHAMPS 6309049, address **48084**, licenses/docs)
3. [ ] **Authorize Humana** (and other MI MHPs) to pull the profile
4. [ ] Attest + upload supporting docs
5. [ ] Flip `company_info.py` → `CAQH_STATUS = "ATTESTED"` + update this file

**Support:** 888-599-1771

### Step 3 — If Abby / Humana redirects to LTSS-only

1. [ ] Send DAAA kickoff → `contractmgt@daaa1a.org`  
   Draft: `CREDENTIALING/SEND_HUMANA_DAAA_LTSS_EMAIL.md`
2. [ ] Or `LTSSContracting@humana.com` for counties outside Wayne/Macomb
3. [ ] Log in `OUTBOUND_EMAIL_LOG.md`

### Step 4 — Portal access (after contracting path opens)

Humana commonly routes claims/self-service via **Availity Essentials** (DDI already approved — Customer ID **3878016**). Confirm Humana payer tools appear after network approval.  
Record: `CREDENTIALING/AVAILITY_PORTAL.md`

### Step 5 — Same-day companion (scheduled Aug 1 block)

Priority Health **prism** password still open (link expires ~**Aug 7, 2026**):  
`CREDENTIALING/PRIORITY_HEALTH_PRISM_PORTAL.md` · username `info@deedavis.biz.prism`

---

## Do NOT do

- ❌ Email SafeRide first and call that “Humana credentialing” (that’s the medical trip broker lane)
- ❌ Use physical-health join form for atypical NEMT / LTSS TPA
- ❌ Claim SWFT or unverified past performance
- ❌ Name fulfillment partners (Uber, Roadie, etc.) in Humana/DAAA emails
- ❌ Treat CAQH or DAAA email as a signed contract

---

## Contacts (from Humana join-our-network page)

| Role | Contact |
|---|---|
| LTSS / HCBS — Region 10 & 12 (Wayne/Macomb) | `contractmgt@daaa1a.org` (DAAA) |
| LTSS / HCBS — other MI counties | `LTSSContracting@humana.com` |
| Physical health roster adds | `MichiganMarket@humana.com` |
| Behavioral health roster adds | `MIBHMedicaid@humana.com` |
| Medical transportation network | SafeRide Health (broker) |
| Credentialing hotline (dental note on page) | 800-233-1468 |

**Prior Humana MI outreach (relationship, not enrollment):** Eric Doeh `edoeh@humana.com` · Nancy Centeno `ncenteno1@humana.com` — check `OUTBOUND_EMAIL_LOG.md` before re-sending intro emails. **LTSS enrollment goes to DAAA / LTSS Contracting, not those inboxes.**

---

## Status log

| Date | Event |
|---|---|
| Jul 2026 | Marked “credentialing in progress” in `COMPANY_INFO_MASTER.md` (relationship status) |
| Jul 27, 2026 | CAQH invite received — ID 16876320 |
| Aug 1, 2026 | Playbook created; started Quickbase Add Provider Request (taxonomies 347E / 251B); market warning appeared |
| Aug 1, 2026 | **Abby Davidson** (Supervisor IN & MI, Contracting) emailed invite to Quickbase download/upload path — primary path switched to Abby portal |
| Aug 1, 2026 | Quickbase Taxonomy Warning blocked submit (MI market not available online for provider type). **Reply SENT to Abby** ~6:12 PM ET — logged `OUTBOUND_EMAIL_LOG.md`. Status: awaiting her routing. |

---

## Related files

- `CREDENTIALING/CAQH_PROVIDER_PORTAL.md`
- `CREDENTIALING/AVAILITY_PORTAL.md`
- `CREDENTIALING/PRIORITY_HEALTH_PRISM_PORTAL.md`
- `COMPANY_INFO_MASTER.md` → MCO CREDENTIALING STATUS
- `PENDING_ACTIONS.md` → Priority + Humana enrollment block
- Molina parallel (what “done” looks like): `BIDS:RESOURCES/MOLINA HIDE SNP LTSS NETWORK/`
