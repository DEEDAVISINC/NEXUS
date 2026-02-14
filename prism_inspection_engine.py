#!/usr/bin/env python3
"""
PRISM DOCUMENT INSPECTION ENGINE
=================================
"See every detail. Miss nothing."

Built from real-world QC knowledge:
- Premium Closing Solutions CommonErrorsForm (21-page reference)
- 49 CFR Part 40 — DOT Drug Testing (Fatal Flaws, Correctable Flaws, CCF 5-Copy System)
- AABB 15th Edition — DNA Relationship Testing Standards
- DDC / Validity Genetics — DNA Collection Provider Guidelines
- FBI CJIS Division — Fingerprint Quality & Livescan Rejection Standards
- Hague Apostille Convention 1961 — Apostille Authentication QC
- USCIS Form I-9 / E-Verify — Employment Eligibility Verification
- FCRA / EEOC — Background Check Compliance & Adverse Action
- CLSI H21-A5 — Phlebotomy Specimen Collection & Handling Standards
- Notary Permit Runner (NPR) — 62-page permit running business guide
- The 7 Fundamentals (never change)
- Client-specific rules per order
- Adaptive learning (Phase 2)

Service Types Covered:
  notary         — 31 rules (PCS CommonErrors, 49 state laws)
  drug_test      — 25 rules (49 CFR Part 40, SAMHSA, FMCSA Clearinghouse, CCF 5-copy system)
  dna            — 15 rules (AABB, DDC, Forensic Biology)
  fingerprint    — 14 rules (FBI CJIS, Biometric Training)
  apostille      — 12 rules (Hague Convention, Secretary of State requirements)
  i9_everify     — 11 rules (USCIS M-274 Handbook, E-Verify guidelines)
  background_chk — 10 rules (FCRA, EEOC Green Factors, BackgroundChecks.com)
  phlebotomy     — 12 rules (CLSI H21-A5, specimen rejection data, chain of custody)
  permit_runner  — 14 rules (NPR Guide, building dept procedures, contractor authorization)

This is the competitive moat. Nobody else has it.
Snapdocs doesn't. ZigSig doesn't. SigningOrder doesn't.
"""

import json
import os
from datetime import datetime
from flask import Blueprint, request, jsonify

prism_inspection = Blueprint('prism_inspection', __name__)


# ═══════════════════════════════════════════════════════════════════
# THE 7 FUNDAMENTALS — These NEVER change
# ═══════════════════════════════════════════════════════════════════
# A missing signature is a missing signature. Has been for decades.
# Will be for decades. No regulatory update changes these.

FUNDAMENTALS = [
    {
        'id': 'F1',
        'check': 'Is every required SIGNATURE present?',
        'severity': 'CRITICAL',
        'description': 'All signature lines must be signed by the correct signer. Signers cannot sign for each other.',
    },
    {
        'id': 'F2',
        'check': 'Is every required INITIAL present?',
        'severity': 'CRITICAL',
        'description': 'All initial lines must be initialed. Each statement with an initial line must be individually initialed.',
    },
    {
        'id': 'F3',
        'check': 'Is every required DATE filled in?',
        'severity': 'CRITICAL',
        'description': 'All dates must be written by the signer themselves. Signers cannot date for each other. Agent cannot date for signer.',
    },
    {
        'id': 'F4',
        'check': 'Is the NOTARY SEAL/STAMP present where required?',
        'severity': 'CRITICAL',
        'description': 'Every notarized page must have the notary seal/stamp clearly visible and legible.',
    },
    {
        'id': 'F5',
        'check': 'Are ALL required PAGES/FORMS included?',
        'severity': 'CRITICAL',
        'description': 'Expected page count must match. No pages removed, reordered, or missing from the package.',
    },
    {
        'id': 'F6',
        'check': 'Is the ID COPY included?',
        'severity': 'CRITICAL',
        'description': 'Signer ID copies must be uploaded to system or printed and included in return package.',
    },
    {
        'id': 'F7',
        'check': 'Are there MARKINGS where there should NOT be?',
        'severity': 'WARNING',
        'description': 'No check marks, X markings, highlighters, or signatures obscuring boxes/verbiage (especially 4506-C).',
    },
]


# ═══════════════════════════════════════════════════════════════════
# KNOWN ERROR RULES — Built from Premium Closing Solutions + industry
# ═══════════════════════════════════════════════════════════════════
# Every rule is a known, repeatable, preventable mistake.
# Each maps back to one of the 7 Fundamentals.

KNOWN_ERROR_RULES = [
    # ── 1. Termite/Wood Destroying Insect Reports ──
    {
        'id': 'PCS-001',
        'category': 'Termite Report',
        'fundamental': 'F1',
        'check': 'Termite/wood destroying insect report signed by borrower',
        'description': 'Signature lines may be small, hard to find, or have an X placed where the borrower previously signed. Borrower must still sign — on any signature line, or on the bottom of the page.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors #1',
    },
    # ── 2. IDs and Patriot Act Forms ──
    {
        'id': 'PCS-002',
        'category': 'Patriot Act / ID',
        'fundamental': 'F6',
        'check': 'ID copies provided for all signers',
        'description': 'Notary is REQUIRED to provide ID copies for the signers. These can be uploaded to the system or printed and added to the return package.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors #2',
    },
    {
        'id': 'PCS-003',
        'category': 'Patriot Act / ID',
        'fundamental': 'F2',
        'check': 'Patriot Act form ID fields completed correctly',
        'description': 'ID numbers, issue dates, and expiration dates must be written correctly. Some forms require 2 forms of ID — check what the form says.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors #2',
    },
    {
        'id': 'PCS-004',
        'category': 'Patriot Act / ID',
        'fundamental': 'F2',
        'check': 'Expired IDs NOT used for Patriot Act forms',
        'description': 'Lenders will NO LONGER accept expired ID copies for Patriot Act forms, even if the state allows recently expired IDs for notarization.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors #2',
    },
    {
        'id': 'PCS-005',
        'category': 'Patriot Act / ID',
        'fundamental': 'F1',
        'check': 'Notary title written next to name on Patriot Act',
        'description': 'Notary must input "Notary Public" after their printed name on Patriot Act forms.',
        'severity': 'WARNING',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors #2',
    },
    # ── 3. VA Form 1820 ──
    {
        'id': 'PCS-006',
        'category': 'VA Forms',
        'fundamental': 'F2',
        'check': 'VA 1820 demographic info or initials provided',
        'description': 'Anyone who signs must either provide demographic info or initial indicating they do not wish to provide it. All 3 pages must be completed.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'loan_types': ['VA'],
        'source': 'PCS CommonErrors #3',
    },
    {
        'id': 'PCS-007',
        'category': 'VA Forms',
        'fundamental': 'F1',
        'check': 'VA 1820 Page 3 — spouse signature present',
        'description': 'Page 3 requires signature of veteran AND spouse. Spouse must still sign and provide demographic info even though they are not the veteran.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'loan_types': ['VA'],
        'source': 'PCS CommonErrors #3',
    },
    # ── 4. Verification of VA Benefits ──
    {
        'id': 'PCS-008',
        'category': 'VA Forms',
        'fundamental': 'F2',
        'check': 'VA Benefits — Section 7 & 8 answered, Section 9 signed, Section 10 dated',
        'description': 'Sections 7 & 8 MUST be answered by borrowers. Section 9 must be signed. Section 10 must be dated.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'loan_types': ['VA'],
        'source': 'PCS CommonErrors #4',
    },
    # ── 5. Right to Cancel ──
    {
        'id': 'PCS-009',
        'category': 'Right to Cancel',
        'fundamental': 'F1',
        'check': 'Right to Cancel — borrower signed CORRECT line',
        'description': 'TWO lines exist: one to acknowledge the right to cancel, one to actually cancel. If borrower signs the "I wish to cancel" line, loan must reclose. Fee will be removed. If error occurs, have a new blank copy signed.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors #5',
    },
    # ── 6. Acknowledgement of Continued Employment ──
    {
        'id': 'PCS-010',
        'category': 'Continued Employment',
        'fundamental': 'F2',
        'check': 'Each statement initialed by borrower(s)',
        'description': 'Each statement has an initial line that must be initialed by the borrower(s). Every statement individually.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors #6',
    },
    # ── 7. HUD Addendum ──
    {
        'id': 'PCS-011',
        'category': 'HUD Addendum',
        'fundamental': 'F1',
        'check': 'HUD Addendum Page 1 signatures present',
        'description': 'Signatures required on page 1 of the HUD Addendum to Uniform Residential Loan Application.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors #7',
    },
    # ── 8. FACTS Sheet ──
    {
        'id': 'PCS-012',
        'category': 'FACTS Sheet',
        'fundamental': 'F1',
        'check': 'FACTS sheet signed and dated',
        'description': 'Increasing number of packages returned with signature and date missed on the FACTS sheet.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors #8',
    },
    # ── 9. Loan Application (1003/1009) ──
    {
        'id': 'PCS-013',
        'category': 'Loan Application',
        'fundamental': 'F2',
        'check': '1003 — Primary borrower initialed page 1, co-borrower initialed page 8',
        'description': 'When there are two borrowers: primary initials on page 1, co-borrower initials on page 8 of the 1003. Small line for joint credit.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors #9',
    },
    {
        'id': 'PCS-014',
        'category': 'Loan Application',
        'fundamental': 'F1',
        'check': '1009 (Reverse) — Top line(s) on Page 1 signed',
        'description': 'Even if only one signer, they must sign the top line(s) on Page 1. Lender requirement even though the form says "only if applying for joint credit."',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors #9',
    },
    # ── 10. Printing/Font Errors ──
    {
        'id': 'PCS-015',
        'category': 'Print Quality',
        'fundamental': 'F7',
        'check': 'No font substitution errors in printed documents',
        'description': 'Font discrepancies between PDF and printer can replace characters with symbols (e.g., "N" replaced by symbol on NOTE). Agent must review printed docs before leaving. Contact title company immediately if found.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors #10',
    },
    {
        'id': 'PCS-016',
        'category': 'Print Quality',
        'fundamental': 'F7',
        'check': 'Print not too light',
        'description': 'Fees removed for packages printed too light for lender to use. Agent must verify print quality before leaving.',
        'severity': 'WARNING',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors #10',
    },
    {
        'id': 'PCS-017',
        'category': 'Print Quality',
        'fundamental': 'F5',
        'check': 'Documents printed single-sided',
        'description': 'Documents must be printed single-sided. Fee removed for double-sided printing.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS Reference Sheet',
    },
    {
        'id': 'PCS-018',
        'category': 'Print Quality',
        'fundamental': 'F5',
        'check': 'Legal-sized documents printed on legal paper',
        'description': 'Legal-sized forms (8.5x14) must be on legal paper. Lender will not accept legal documents printed to letter size.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS Reference Sheet',
    },
    # ── 11. 4506-C ──
    {
        'id': 'PCS-019',
        'category': '4506-C',
        'fundamental': 'F7',
        'check': '4506-C — No markings in signatory box',
        'description': 'No check marks, X markings, highlighters in the signatory box. Signature must not obscure any other boxes or verbiage.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors #11',
    },
    # ── General Signing Rules ──
    {
        'id': 'PCS-020',
        'category': 'Signing Rules',
        'fundamental': 'F3',
        'check': 'Each signer signed and dated individually',
        'description': 'All signers must sign and date each document individually. Documents CANNOT be dated by the other signer(s) or the signing agent. Return trip required if anyone signs/dates on behalf of another.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS CommonErrors Intro',
    },
    {
        'id': 'PCS-021',
        'category': 'Signing Rules',
        'fundamental': 'F1',
        'check': 'Borrower signature matches pre-printed name',
        'description': 'Signature must match the name pre-printed on the signature line unless title company instructs otherwise.',
        'severity': 'WARNING',
        'service_types': ['notary'],
        'source': 'PCS Reference Sheet',
    },
    {
        'id': 'PCS-022',
        'category': 'Signing Rules',
        'fundamental': 'F3',
        'check': 'Note — NOT dated by agent (borrower only)',
        'description': 'Do Not date the Note. Borrower signature only.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'source': 'PCS Reference Sheet',
    },
    {
        'id': 'PCS-023',
        'category': 'Package Completeness',
        'fundamental': 'F5',
        'check': 'Two copies printed — one signed, one for borrower',
        'description': 'Must print 2 copies. One package signed and shipped back, second left with borrower. This is a requirement.',
        'severity': 'WARNING',
        'service_types': ['notary'],
        'source': 'PCS Reference Sheet',
    },
    {
        'id': 'PCS-024',
        'category': 'Package Completeness',
        'fundamental': 'F5',
        'check': 'All duplicate documents signed at the table',
        'description': 'Some lenders require duplicates of tax forms/mortgage/right to cancel forms to be signed at closing.',
        'severity': 'WARNING',
        'service_types': ['notary'],
        'source': 'PCS Reference Sheet',
    },
    {
        'id': 'PCS-025',
        'category': 'Package Completeness',
        'fundamental': 'F5',
        'check': 'Documents returned in original print order',
        'description': 'Do not remove or reorder pages prior to shipping.',
        'severity': 'WARNING',
        'service_types': ['notary'],
        'source': 'PCS Reference Sheet',
    },
    # ── Witness Rules (State-Specific) ──
    {
        'id': 'PCS-026',
        'category': 'Witness Requirements',
        'fundamental': 'F1',
        'check': 'Witness signatures present (if property in witness state)',
        'description': 'CT: 2 witnesses (1 may be notary). FL: 2 witnesses (1 may be notary, deed of conveyance only). GA: 1 witness (cannot be notary). LA: 2 witnesses (neither can be notary). SC: 2 witnesses (1 may be notary).',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'states': ['CT', 'FL', 'GA', 'LA', 'SC'],
        'source': 'PCS Reference Sheet',
    },
    # ── Shipping Rules ──
    {
        'id': 'PCS-027',
        'category': 'Shipping',
        'fundamental': 'F5',
        'check': 'FedEx label covered in clear tape',
        'description': 'Completely cover FedEx label in clear wrap/tape. Delays if FedEx cannot scan/read the label.',
        'severity': 'WARNING',
        'service_types': ['notary'],
        'source': 'PCS Reference Sheet',
    },
    {
        'id': 'PCS-028',
        'category': 'Shipping',
        'fundamental': 'F5',
        'check': 'Package securely closed',
        'description': 'Package must be securely closed. Packages received open or partially open is a security issue with sensitive borrower information.',
        'severity': 'WARNING',
        'service_types': ['notary'],
        'source': 'PCS Reference Sheet',
    },
    {
        'id': 'PCS-029',
        'category': 'Shipping',
        'fundamental': 'F5',
        'check': 'Shipped via FedEx Ship Center or drop box (NOT CVS/Walgreens)',
        'description': 'CVS/Walgreens FedEx locations can take up to 4 days for pickup. Must use FedEx Ship Center or FedEx drop box.',
        'severity': 'WARNING',
        'service_types': ['notary'],
        'source': 'PCS Reference Sheet',
    },
    {
        'id': 'PCS-030',
        'category': 'Shipping',
        'fundamental': 'F5',
        'check': 'Shipped same day or next available pickup',
        'description': 'Ship for next available UPS/FedEx pickup. Delays because agents do not drop right after closing cannot happen.',
        'severity': 'WARNING',
        'service_types': ['notary'],
        'source': 'PCS Reference Sheet',
    },
    # ── State-Specific Rules ──
    {
        'id': 'PCS-031',
        'category': 'State-Specific',
        'fundamental': 'F5',
        'check': 'Indiana Property Tax Benefit form on Gold/Yellow paper',
        'description': 'Indiana files ONLY — form MUST be printed on Gold/Yellow paper. Return trip required if not printed correctly.',
        'severity': 'CRITICAL',
        'service_types': ['notary'],
        'states': ['IN'],
        'source': 'PCS Reference Sheet',
    },
    # ═══════════════════════════════════════════════════════════════
    # DRUG TESTING (DOT / Non-DOT) — 49 CFR Part 40
    # Source: ODAPC, SAMHSA MRO Guidance Manual, 49 CFR §40.83
    # ═══════════════════════════════════════════════════════════════

    # ── FATAL FLAWS (§40.83) — Always cause rejection, cannot be fixed ──
    {
        'id': 'DOT-001',
        'category': 'CCF Fatal Flaw',
        'fundamental': 'F5',
        'check': 'CCF present with specimen',
        'description': 'No CCF submitted with specimen = automatic rejection. The CCF IS the chain of custody. Without it, the specimen has no legal standing.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR §40.83(a)(1)',
    },
    {
        'id': 'DOT-002',
        'category': 'CCF Fatal Flaw',
        'fundamental': 'F5',
        'check': 'Specimen submitted with the CCF',
        'description': 'CCF exists but no specimen = rejection. A form without a specimen is paperwork for nothing.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR §40.83(a)(2)',
    },
    {
        'id': 'DOT-003',
        'category': 'CCF Fatal Flaw',
        'fundamental': 'F1',
        'check': 'Collector printed name AND signature present on CCF',
        'description': 'No printed collector name and no collector signature = fatal flaw. Must have BOTH. This identifies who collected the specimen.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR §40.83(a)(3)',
    },
    {
        'id': 'DOT-004',
        'category': 'CCF Fatal Flaw',
        'fundamental': 'F5',
        'check': 'One CCF used per collection (not two collections on one form)',
        'description': 'Two separate collections using one CCF = fatal flaw. Each collection must have its own form.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR §40.83(a)(4)',
    },
    {
        'id': 'DOT-005',
        'category': 'CCF Fatal Flaw',
        'fundamental': 'F4',
        'check': 'Specimen ID numbers on bottle and CCF match',
        'description': 'Specimen ID on the bottle must match the ID on the CCF. Mismatch = fatal flaw. This is the core of chain of custody.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR §40.83(a)(5)',
    },
    {
        'id': 'DOT-006',
        'category': 'CCF Fatal Flaw',
        'fundamental': 'F4',
        'check': 'Specimen bottle seal intact (not broken or tampered)',
        'description': 'Broken or tampered specimen bottle seal = fatal flaw. If split specimen can be redesignated, that is the only exception.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR §40.83(a)(6)',
    },
    {
        'id': 'DOT-007',
        'category': 'CCF Fatal Flaw',
        'fundamental': 'F5',
        'check': 'Sufficient specimen volume in primary bottle',
        'description': 'Insufficient specimen in primary bottle for analysis = fatal flaw (unless specimens can be redesignated).',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR §40.83(a)(7)',
    },
    {
        'id': 'DOT-008',
        'category': 'CCF Fatal Flaw',
        'fundamental': 'F5',
        'check': 'Oral fluid: collection device NOT expired',
        'description': 'For oral fluid collection, using an expired device = fatal flaw. Expiration date must be entered in Step 4 of CCF.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR §40.83(a)(8-9)',
    },

    # ── CORRECTABLE FLAWS (§40.205) — Lab tries to fix within 5 days ──
    {
        'id': 'DOT-009',
        'category': 'CCF Correctable Flaw',
        'fundamental': 'F1',
        'check': 'Collector signature present on certification statement',
        'description': 'Missing collector signature on certification = correctable flaw. Lab retains specimen 5 business days and attempts correction. If not corrected, test is rejected.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR §40.83(b), §40.205(b)(1)',
    },
    {
        'id': 'DOT-010',
        'category': 'CCF Correctable Flaw',
        'fundamental': 'F2',
        'check': 'Temperature checked and recorded (or remarks explain why not)',
        'description': 'Specimen temperature must be recorded on CCF within 4 minutes of collection. If not checked, remarks must explain. Lab attempts correction for 5 business days.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR §40.83(b), §40.208',
    },
    {
        'id': 'DOT-011',
        'category': 'CCF Correctable Flaw',
        'fundamental': 'F5',
        'check': 'Correct CCF form used (current federal version)',
        'description': 'Must use the current Federal CCF. Revised form (as of Aug 30, 2021) includes CDL State and Number field required for FMCSA Clearinghouse reporting.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR §40.40(a), FMCSA Clearinghouse',
    },

    # ── CCF Step-by-Step Completion ──
    {
        'id': 'DOT-012',
        'category': 'CCF Completion',
        'fundamental': 'F1',
        'check': 'CCF Step 1 — Donor signed and dated',
        'description': 'Donor must sign and date Step 1 of the CCF. This is the donor\'s certification that they provided the specimen.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR Part 40 Subpart C',
    },
    {
        'id': 'DOT-013',
        'category': 'CCF Completion',
        'fundamental': 'F2',
        'check': 'CCF Step 2 — Collector completed ALL fields (site, date, time, temp, collection type)',
        'description': 'Step 2 must include: collector name, date, time, collection site address, specimen temperature, observed/not observed, reason for test, and collector signature.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR Part 40 Subpart D',
    },
    {
        'id': 'DOT-014',
        'category': 'CCF Completion',
        'fundamental': 'F2',
        'check': 'CDL State and Number filled in (if applicable)',
        'description': 'Required for FMCSA-regulated drivers. Must be filled in on the revised Federal CCF for Clearinghouse reporting.',
        'severity': 'WARNING',
        'service_types': ['drug_test'],
        'source': 'FMCSA Clearinghouse',
    },

    # ── Specimen Handling ──
    {
        'id': 'DOT-015',
        'category': 'Specimen Handling',
        'fundamental': 'F4',
        'check': 'Specimen seal applied with donor initials and date',
        'description': 'Tamper-evident seal must be applied to the specimen bottle. Donor must initial and date the seal. This proves the specimen hasn\'t been opened since collection.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR Part 40 Subpart D',
    },
    {
        'id': 'DOT-016',
        'category': 'Specimen Handling',
        'fundamental': 'F7',
        'check': 'No corrections or cross-outs on CCF without proper initials and date',
        'description': 'Any corrections on the CCF must be initialed and dated by the person making the correction. Unmarked cross-outs raise chain of custody concerns.',
        'severity': 'WARNING',
        'service_types': ['drug_test'],
        'source': '49 CFR §40.205',
    },
    {
        'id': 'DOT-017',
        'category': 'Specimen Handling',
        'fundamental': 'F5',
        'check': 'Split specimen collected (if required by test type)',
        'description': 'DOT tests require split specimen collection. Primary and split bottles must both be sealed and accounted for.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': '49 CFR Part 40 Subpart D',
    },

    # ── CCF 5-Copy Distribution ──
    {
        'id': 'DOT-018',
        'category': 'CCF Distribution',
        'fundamental': 'F5',
        'check': 'All 5 CCF copies accounted for (Lab, MRO, Collector, Employer, Donor)',
        'description': 'Federal CCF has 5 copies: Copy 1 (Lab), Copy 2 (MRO), Copy 3 (Collector), Copy 4 (Employer/DER), Copy 5 (Donor). All must be distributed correctly.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': 'Federal CCF Instructions, DrugFreeBiz.com',
    },
    {
        'id': 'DOT-019',
        'category': 'CCF Distribution',
        'fundamental': 'F5',
        'check': 'Donor received Copy 5 of CCF',
        'description': 'Donor must receive their copy (Copy 5) of the CCF after collection. Failure to provide donor copy = procedural violation.',
        'severity': 'WARNING',
        'service_types': ['drug_test'],
        'source': 'Federal CCF Instructions',
    },
    {
        'id': 'DOT-020',
        'category': 'CCF Distribution',
        'fundamental': 'F6',
        'check': 'Donor government-issued photo ID verified before collection',
        'description': 'Collector must confirm donor identity with government-issued photo ID before specimen collection begins. This is the first step in the chain of custody.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': 'New Era Drug Testing, 49 CFR Part 40',
    },

    # ── Collection Environment ──
    {
        'id': 'DOT-021',
        'category': 'Collection Environment',
        'fundamental': 'F7',
        'check': 'Specimen kept in collector\'s view during entire process',
        'description': 'The specimen must remain in the collector\'s view during the entire collection process. Losing sight of the specimen breaks chain of custody.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': 'New Era Drug Testing, 49 CFR Part 40',
    },
    {
        'id': 'DOT-022',
        'category': 'Collection Environment',
        'fundamental': 'F4',
        'check': 'Specimen sealed immediately in donor\'s presence',
        'description': 'Collection container must be sealed in the presence of the donor immediately after collection. Sealing after donor leaves = chain of custody break.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': 'New Era Drug Testing, 49 CFR Part 40',
    },
    {
        'id': 'DOT-023',
        'category': 'Collection Environment',
        'fundamental': 'F5',
        'check': 'Only ONE collection performed at a time',
        'description': 'Collector may only perform one collection at a time. Processing multiple donors simultaneously creates mix-up risk.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': 'New Era Drug Testing',
    },
    {
        'id': 'DOT-024',
        'category': 'Collection Environment',
        'fundamental': 'F7',
        'check': 'Collection area secured (water sources restricted, soap removed, bluing agent in toilet)',
        'description': 'Collection site must remove soap/cleaning agents, restrict water sources, and use bluing agent in toilet bowl to prevent specimen adulteration.',
        'severity': 'WARNING',
        'service_types': ['drug_test'],
        'source': 'New Era Drug Testing, 49 CFR Part 40',
    },

    # ── Non-DOT Form Usage ──
    {
        'id': 'DOT-025',
        'category': 'CCF Form Compliance',
        'fundamental': 'F5',
        'check': 'DOT form NOT used for non-DOT test (and vice versa)',
        'description': 'A federal CCF cannot be used for a non-DOT test, and a non-DOT form cannot be used for a DOT test. Using the wrong form type is a correctable flaw but triggers MRO investigation.',
        'severity': 'CRITICAL',
        'service_types': ['drug_test'],
        'source': 'DrugFreeBiz.com, 49 CFR Part 40',
    },

    # ═══════════════════════════════════════════════════════════════
    # DNA COLLECTION — AABB Standards for Relationship Testing
    # Source: AABB 15th Edition, DDC Collection Provider Guidelines,
    #         Validity Genetics Legal Collection Procedures
    # ═══════════════════════════════════════════════════════════════

    # ── Chain of Custody ──
    {
        'id': 'DNA-001',
        'category': 'DNA Chain of Custody',
        'fundamental': 'F1',
        'check': 'All participants signed and dated the consent/chain of custody form',
        'description': 'Every test participant must sign and date the Client ID and Consent Form. The sample collector must also sign. Failure to complete documentation invalidates the test.',
        'severity': 'CRITICAL',
        'service_types': ['dna'],
        'source': 'AABB Standards, Validity Genetics',
    },
    {
        'id': 'DNA-002',
        'category': 'DNA Chain of Custody',
        'fundamental': 'F1',
        'check': 'Sample collector signed all documentation',
        'description': 'The SAMPLE COLLECTOR (not the participant) must complete and sign all collection documentation. An unsigned form by the collector invalidates the entire test.',
        'severity': 'CRITICAL',
        'service_types': ['dna'],
        'source': 'Validity Genetics Legal Collection',
    },
    {
        'id': 'DNA-003',
        'category': 'DNA Chain of Custody',
        'fundamental': 'F5',
        'check': 'Collection materials were NOT in participant possession before/after collection',
        'description': 'Collection materials cannot be in the possession of test participants before or after collection. This is a chain of custody requirement for court admissibility.',
        'severity': 'CRITICAL',
        'service_types': ['dna'],
        'source': 'Validity Genetics Legal Collection',
    },
    {
        'id': 'DNA-004',
        'category': 'DNA Chain of Custody',
        'fundamental': 'F5',
        'check': 'Samples and paperwork remained in collector\'s secure possession until shipped',
        'description': 'From collection to shipment, samples and documentation must stay in the collector\'s secure possession. Any break in custody = not court-admissible.',
        'severity': 'CRITICAL',
        'service_types': ['dna'],
        'source': 'Validity Genetics Legal Collection',
    },

    # ── Identification ──
    {
        'id': 'DNA-005',
        'category': 'DNA Identification',
        'fundamental': 'F6',
        'check': 'Government-issued photo ID verified for ALL participants',
        'description': 'All test participants must present government-issued photo ID (original or legible photocopy). Required for legal/court-admissible DNA tests.',
        'severity': 'CRITICAL',
        'service_types': ['dna'],
        'source': 'AABB Standards, Validity Genetics',
    },
    {
        'id': 'DNA-006',
        'category': 'DNA Identification',
        'fundamental': 'F6',
        'check': 'Photograph taken of each participant with identification sheet',
        'description': 'A photograph suitable for positive identification must be taken of each participant along with their identification sheet.',
        'severity': 'CRITICAL',
        'service_types': ['dna'],
        'source': 'AABB Standards, DDC Guidelines',
    },

    # ── Sample Collection ──
    {
        'id': 'DNA-007',
        'category': 'DNA Sample Handling',
        'fundamental': 'F4',
        'check': 'Buccal swabs placed in labeled PAPER envelopes (not plastic)',
        'description': 'Swabs must go into labeled paper envelopes, NOT back into plastic wrappers. Plastic creates moisture that encourages mold and destroys DNA samples.',
        'severity': 'CRITICAL',
        'service_types': ['dna'],
        'source': 'DDC Collection Provider Guidelines',
    },
    {
        'id': 'DNA-008',
        'category': 'DNA Sample Handling',
        'fundamental': 'F7',
        'check': 'Envelopes labeled one at a time DURING collection (not pre-labeled)',
        'description': 'Labels must be applied one at a time during collection to prevent sample switching. Pre-labeling envelopes = risk of cross-contamination.',
        'severity': 'CRITICAL',
        'service_types': ['dna'],
        'source': 'DDC Collection Provider Guidelines',
    },
    {
        'id': 'DNA-009',
        'category': 'DNA Sample Handling',
        'fundamental': 'F7',
        'check': 'Collector wore gloves and changed between participants',
        'description': 'Gloves must be worn and changed between each participant. Touching face, phone, or exposed skin with gloved hands can transfer collector\'s DNA to samples.',
        'severity': 'CRITICAL',
        'service_types': ['dna'],
        'source': 'Forensic Biology Standards',
    },
    {
        'id': 'DNA-010',
        'category': 'DNA Sample Handling',
        'fundamental': 'F4',
        'check': 'Tamper-evident seal applied to specimen packaging',
        'description': 'Specimen must be sealed with tamper-evident seal after collection. Seal integrity is required for court admissibility.',
        'severity': 'CRITICAL',
        'service_types': ['dna'],
        'source': 'AABB Standards',
    },
    {
        'id': 'DNA-011',
        'category': 'DNA Sample Handling',
        'fundamental': 'F7',
        'check': 'Collector did NOT talk over biological evidence / wore face mask',
        'description': 'Talking over samples can deposit collector\'s DNA. Face mask should be worn during collection. This is a contamination prevention requirement.',
        'severity': 'WARNING',
        'service_types': ['dna'],
        'source': 'Forensic Biology Standards',
    },
    {
        'id': 'DNA-012',
        'category': 'DNA Sample Handling',
        'fundamental': 'F5',
        'check': 'Samples air-dried before packaging',
        'description': 'Buccal swabs must be air-dried briefly before packaging to prevent moisture damage. Wet swabs in sealed packaging = mold = destroyed DNA.',
        'severity': 'WARNING',
        'service_types': ['dna'],
        'source': 'DDC Collection Provider Guidelines',
    },

    # ── Collector Requirements ──
    {
        'id': 'DNA-013',
        'category': 'DNA Collector Requirements',
        'fundamental': 'F1',
        'check': 'Collector is unrelated to participants with no interest in outcome',
        'description': 'The sample collector must be an unrelated third party with no interest in the test outcome. Family members or interested parties cannot collect.',
        'severity': 'CRITICAL',
        'service_types': ['dna'],
        'source': 'Validity Genetics Legal Collection',
    },
    {
        'id': 'DNA-014',
        'category': 'DNA Collector Requirements',
        'fundamental': 'F1',
        'check': 'Collector observed the ENTIRE collection process',
        'description': 'The collector must be present and observe the entire collection process for every participant. Unobserved collection = not court-admissible.',
        'severity': 'CRITICAL',
        'service_types': ['dna'],
        'source': 'Validity Genetics Legal Collection',
    },

    # ── Shipping ──
    {
        'id': 'DNA-015',
        'category': 'DNA Shipping',
        'fundamental': 'F5',
        'check': 'Shipped via trackable/traceable service',
        'description': 'Samples must be mailed using a trackable or traceable shipping service. Standard mail without tracking breaks chain of custody.',
        'severity': 'CRITICAL',
        'service_types': ['dna'],
        'source': 'Validity Genetics Legal Collection',
    },

    # ═══════════════════════════════════════════════════════════════
    # FINGERPRINTING — FBI CJIS Standards, Livescan Requirements
    # Source: FBI Biometric Training, FBI CJIS Division,
    #         San Diego County Reject Notice Guidelines
    # ═══════════════════════════════════════════════════════════════

    # ── Top 8 FBI Rejection Reasons ──
    {
        'id': 'FP-001',
        'category': 'Fingerprint Quality',
        'fundamental': 'F5',
        'check': 'All 10 fingerprints captured (or missing fingers properly notated)',
        'description': 'All 10 fingerprints must be captured. Missing fingers must be notated: "UP" (unable to print) or "XX" (amputated). Fingers missing without notation = rejection.',
        'severity': 'CRITICAL',
        'service_types': ['fingerprint'],
        'source': 'FBI CJIS Division — Reject Reason #6, #7, #8',
    },
    {
        'id': 'FP-002',
        'category': 'Fingerprint Quality',
        'fundamental': 'F7',
        'check': 'No low-quality / illegible fingerprint images',
        'description': 'Prints must show clear ridge detail. Low quality images are the #1 reason for FBI rejection. Must be rolled nail-to-nail, fingertip to below first joint.',
        'severity': 'CRITICAL',
        'service_types': ['fingerprint'],
        'source': 'FBI CJIS Division — Reject Reason #1',
    },
    {
        'id': 'FP-003',
        'category': 'Fingerprint Quality',
        'fundamental': 'F7',
        'check': 'No duplicated finger images',
        'description': 'Same finger printed in two different boxes = rejection. Each block must contain a unique finger. #2 FBI rejection reason.',
        'severity': 'CRITICAL',
        'service_types': ['fingerprint'],
        'source': 'FBI CJIS Division — Reject Reason #2',
    },
    {
        'id': 'FP-004',
        'category': 'Fingerprint Quality',
        'fundamental': 'F7',
        'check': 'No smudges or shadowing around fingerprint images',
        'description': 'Smudges and shadowing make prints unreadable. Clean scanner surface between each use. #3 FBI rejection reason.',
        'severity': 'CRITICAL',
        'service_types': ['fingerprint'],
        'source': 'FBI CJIS Division — Reject Reason #3',
    },
    {
        'id': 'FP-005',
        'category': 'Fingerprint Quality',
        'fundamental': 'F7',
        'check': 'Only ONE fingerprint image per block (no multiple images)',
        'description': 'Each block on the card must contain only one fingerprint. Multiple images per block = rejection.',
        'severity': 'CRITICAL',
        'service_types': ['fingerprint'],
        'source': 'FBI CJIS Division — Reject Reason #4',
    },
    {
        'id': 'FP-006',
        'category': 'Fingerprint Quality',
        'fundamental': 'F5',
        'check': 'Correct hand printed in correct position (not same hand twice)',
        'description': 'Right hand in right hand blocks, left hand in left hand blocks. Same hand printed twice = rejection.',
        'severity': 'CRITICAL',
        'service_types': ['fingerprint'],
        'source': 'FBI CJIS Division — Reject Reason #5',
    },
    {
        'id': 'FP-007',
        'category': 'Fingerprint Quality',
        'fundamental': 'F5',
        'check': 'Fingers printed in correct boxes (not in adjacent/wrong blocks)',
        'description': 'Each finger must be in its designated box. No fingerprint images intruding into adjacent blocks. Fingers in wrong boxes = rejection.',
        'severity': 'CRITICAL',
        'service_types': ['fingerprint'],
        'source': 'FBI CJIS Division — Reject Reason #7',
    },

    # ── Card/Form Completion ──
    {
        'id': 'FP-008',
        'category': 'Fingerprint Card',
        'fundamental': 'F1',
        'check': 'Subject signed the fingerprint card',
        'description': 'Subject must sign the fingerprint card in the designated signature block.',
        'severity': 'CRITICAL',
        'service_types': ['fingerprint'],
        'source': 'FBI CJIS Standards',
    },
    {
        'id': 'FP-009',
        'category': 'Fingerprint Card',
        'fundamental': 'F2',
        'check': 'Subject demographic information complete (name, DOB, SSN, address)',
        'description': 'All demographic fields must be completed. Missing information delays processing and may cause rejection.',
        'severity': 'CRITICAL',
        'service_types': ['fingerprint'],
        'source': 'FBI CJIS Standards',
    },
    {
        'id': 'FP-010',
        'category': 'Fingerprint Card',
        'fundamental': 'F2',
        'check': 'ORI (Originating Agency Identifier) number present',
        'description': 'The ORI must be included on the fingerprint card. Without it, the FBI cannot route results to the requesting agency.',
        'severity': 'CRITICAL',
        'service_types': ['fingerprint'],
        'source': 'FBI CJIS Standards',
    },

    # ── Equipment & Process ──
    {
        'id': 'FP-011',
        'category': 'Fingerprint Process',
        'fundamental': 'F7',
        'check': 'Scanner surface cleaned between subjects',
        'description': 'Livescan platen must be cleaned between each subject to prevent residual prints. Dust and residue cause smudging.',
        'severity': 'WARNING',
        'service_types': ['fingerprint'],
        'source': 'FBI Biometric Training',
    },
    {
        'id': 'FP-012',
        'category': 'Fingerprint Process',
        'fundamental': 'F7',
        'check': 'Proper ink coverage (not too light or too dark)',
        'description': 'For ink-and-roll: proper ink coverage is essential. Too light = no ridge detail. Too dark = smudged/filled ridges. Either = rejection.',
        'severity': 'WARNING',
        'service_types': ['fingerprint'],
        'source': 'FBI Biometric Training',
    },
    {
        'id': 'FP-013',
        'category': 'Fingerprint Process',
        'fundamental': 'F5',
        'check': 'Both rolled AND plain impressions captured',
        'description': 'Both rolled (individual) and plain (slap) impressions are typically required. Plains verify the rolled prints are in the correct sequence.',
        'severity': 'CRITICAL',
        'service_types': ['fingerprint'],
        'source': 'FBI CJIS Standards',
    },
    {
        'id': 'FP-014',
        'category': 'Fingerprint Process',
        'fundamental': 'F6',
        'check': 'Subject photo ID verified and documented',
        'description': 'Government-issued photo ID must be verified before fingerprinting. Document the ID type and number.',
        'severity': 'CRITICAL',
        'service_types': ['fingerprint'],
        'source': 'FBI CJIS Standards',
    },

    # ═══════════════════════════════════════════════════════════════
    # APOSTILLE — Hague Convention of 5 October 1961
    # Source: Hague Conference on Private International Law,
    #         Secretary of State requirements, ApostillesUSA.us,
    #         Colorado SOS Reject Reasons, US Dept of State
    # ═══════════════════════════════════════════════════════════════

    # ── Document Preparation ──
    {
        'id': 'APO-001',
        'category': 'Apostille Document Prep',
        'fundamental': 'F1',
        'check': 'Document is properly notarized (if required)',
        'description': 'Documents requiring notarization (affidavits, powers of attorney, diplomas) must have notary signature, seal, expiration date, and correct acknowledgment wording BEFORE apostille is requested. Missing notarization = rejection.',
        'severity': 'CRITICAL',
        'service_types': ['apostille'],
        'source': 'ApostillesUSA — Top 5 Rejection Reasons',
    },
    {
        'id': 'APO-002',
        'category': 'Apostille Document Prep',
        'fundamental': 'F5',
        'check': 'Original document or certified copy submitted (NOT photocopy)',
        'description': 'Plain photocopies of vital records or diplomas CANNOT be apostilled. Must submit the original document, a certified copy from the record custodian, or a properly notarized "certified true copy."',
        'severity': 'CRITICAL',
        'service_types': ['apostille'],
        'source': 'ApostillesUSA — Top 5 Rejection Reasons',
    },
    {
        'id': 'APO-003',
        'category': 'Apostille Document Prep',
        'fundamental': 'F7',
        'check': 'No blank spaces on document',
        'description': 'Documents with blank spaces cannot be notarized or apostilled. All fields must be filled in or marked N/A before submission.',
        'severity': 'CRITICAL',
        'service_types': ['apostille'],
        'source': 'Colorado SOS Reject Reasons',
    },

    # ── Jurisdiction ──
    {
        'id': 'APO-004',
        'category': 'Apostille Jurisdiction',
        'fundamental': 'F5',
        'check': 'Submitted to the CORRECT Secretary of State (same state as issuance/notarization)',
        'description': 'Apostille must be issued by the Secretary of State in the SAME STATE where the document was originally issued or notarized. A California birth certificate cannot be apostilled by Texas.',
        'severity': 'CRITICAL',
        'service_types': ['apostille'],
        'source': 'ApostillesUSA — Top 5 Rejection Reasons',
    },
    {
        'id': 'APO-005',
        'category': 'Apostille Jurisdiction',
        'fundamental': 'F5',
        'check': 'Federal documents sent to US Dept of State (NOT state office)',
        'description': 'Federal documents (FBI background checks, USDA documents, patents) must be apostilled by the U.S. Department of State in Washington, D.C. — NOT state Secretary of State offices.',
        'severity': 'CRITICAL',
        'service_types': ['apostille'],
        'source': 'ApostillesUSA — Top 5 Rejection Reasons',
    },
    {
        'id': 'APO-006',
        'category': 'Apostille Jurisdiction',
        'fundamental': 'F5',
        'check': 'Destination country is party to the Hague Apostille Convention',
        'description': 'Apostilles only work between countries that are both party to the Hague Convention. If destination country is NOT a member, full embassy legalization is required instead.',
        'severity': 'CRITICAL',
        'service_types': ['apostille'],
        'source': 'Hague Conference — ABCs of Apostilles',
    },

    # ── Notary Compliance ──
    {
        'id': 'APO-007',
        'category': 'Apostille Notary Requirements',
        'fundamental': 'F4',
        'check': 'Notary commission NOT expired at time of notarization',
        'description': 'If the notary\'s commission was expired at the time they notarized the document, the apostille will be rejected. Check notary expiration date against the notarization date.',
        'severity': 'CRITICAL',
        'service_types': ['apostille'],
        'source': 'ApostillesUSA — Rejection Reasons',
    },
    {
        'id': 'APO-008',
        'category': 'Apostille Notary Requirements',
        'fundamental': 'F4',
        'check': 'Notary seal/stamp is clear and legible',
        'description': 'The notary seal must be fully legible. Smudged, partial, or illegible seals will cause the Secretary of State to reject the apostille request.',
        'severity': 'CRITICAL',
        'service_types': ['apostille'],
        'source': 'Colorado SOS Reject Reasons',
    },
    {
        'id': 'APO-009',
        'category': 'Apostille Notary Requirements',
        'fundamental': 'F5',
        'check': 'Notary did not exceed their authority',
        'description': 'Notaries cannot provide legal conclusions (e.g., drafting power of attorney language when not licensed to practice law). Documents where notary exceeded authority = rejected.',
        'severity': 'CRITICAL',
        'service_types': ['apostille'],
        'source': 'Colorado SOS Reject Reasons',
    },

    # ── Apostille Certificate ──
    {
        'id': 'APO-010',
        'category': 'Apostille Certificate',
        'fundamental': 'F5',
        'check': 'Apostille certificate has all 10 required informational items',
        'description': 'Apostille must include: country, signer name, capacity, seal/stamp info, location, date, issuing authority, certificate number, seal, and signature. Per Hague Convention Model Certificate.',
        'severity': 'CRITICAL',
        'service_types': ['apostille'],
        'source': 'Hague Convention — Model Apostille Certificate',
    },
    {
        'id': 'APO-011',
        'category': 'Apostille Certificate',
        'fundamental': 'F5',
        'check': 'Apostille is NOT detached from the underlying document',
        'description': 'An Apostille must never be detached from its public document, whether placed directly on it or on an allonge (attached page). Detached apostille = invalid.',
        'severity': 'CRITICAL',
        'service_types': ['apostille'],
        'source': 'Hague Conference — ABCs of Apostilles',
    },
    {
        'id': 'APO-012',
        'category': 'Apostille Certificate',
        'fundamental': 'F3',
        'check': 'Document recency meets destination country requirements',
        'description': 'Some foreign governments require documents to be recent (e.g., background checks within 6 months, medical certs within 3 months). Check destination country recency requirements.',
        'severity': 'WARNING',
        'service_types': ['apostille'],
        'source': 'ApostillesUSA — Expired Documents',
    },

    # ═══════════════════════════════════════════════════════════════
    # I-9 / E-VERIFY — Employment Eligibility Verification
    # Source: USCIS Handbook for Employers (M-274),
    #         E-Verify Self-Assessment Guide, 8 USC §1324a
    # ═══════════════════════════════════════════════════════════════

    # ── Section 1 (Employee) ──
    {
        'id': 'I9-001',
        'category': 'I-9 Section 1 (Employee)',
        'fundamental': 'F1',
        'check': 'Section 1 signed and dated by employee',
        'description': 'Employee must sign and date Section 1 of Form I-9. Unsigned Section 1 = the form is incomplete and the verification is invalid.',
        'severity': 'CRITICAL',
        'service_types': ['i9_everify'],
        'source': 'USCIS M-274 Handbook §9.0',
    },
    {
        'id': 'I9-002',
        'category': 'I-9 Section 1 (Employee)',
        'fundamental': 'F2',
        'check': 'All Section 1 fields completed (name, DOB, address, SSN, citizenship status)',
        'description': 'Section 1 must be fully completed — no blank fields. Citizenship or immigration status must be checked. SSN is required for E-Verify users.',
        'severity': 'CRITICAL',
        'service_types': ['i9_everify'],
        'source': 'USCIS M-274 Handbook §9.0',
    },
    {
        'id': 'I9-003',
        'category': 'I-9 Section 1 (Employee)',
        'fundamental': 'F3',
        'check': 'Section 1 completed no later than first day of employment',
        'description': 'Employee must complete Section 1 no later than their first day of employment. Section 1 completed after the start date = violation.',
        'severity': 'CRITICAL',
        'service_types': ['i9_everify'],
        'source': 'USCIS M-274 Handbook',
    },

    # ── Section 2 (Employer/Agent) ──
    {
        'id': 'I9-004',
        'category': 'I-9 Section 2 (Employer/Agent)',
        'fundamental': 'F1',
        'check': 'Section 2 signed and dated by employer or authorized representative',
        'description': 'Employer or authorized representative must sign and date Section 2. This certifies that documents were physically examined.',
        'severity': 'CRITICAL',
        'service_types': ['i9_everify'],
        'source': 'USCIS M-274 Handbook §9.0',
    },
    {
        'id': 'I9-005',
        'category': 'I-9 Section 2 (Employer/Agent)',
        'fundamental': 'F2',
        'check': 'Document title, issuing authority, number, and expiration entered for all List A, B, or C docs',
        'description': 'All identification document details must be entered: document title, issuing authority, document number, and expiration date. Missing any field = incomplete form.',
        'severity': 'CRITICAL',
        'service_types': ['i9_everify'],
        'source': 'USCIS M-274 Handbook §9.0',
    },
    {
        'id': 'I9-006',
        'category': 'I-9 Section 2 (Employer/Agent)',
        'fundamental': 'F3',
        'check': 'Section 2 completed within 3 business days of employee start date',
        'description': 'Employer must complete Section 2 within 3 business days of the employee\'s first day of employment. Late completion = violation. For E-Verify, case must also be created within 3 days of Section 2.',
        'severity': 'CRITICAL',
        'service_types': ['i9_everify'],
        'source': 'USCIS M-274 Handbook, E-Verify §3.1',
    },
    {
        'id': 'I9-007',
        'category': 'I-9 Section 2 (Employer/Agent)',
        'fundamental': 'F6',
        'check': 'Documents physically examined in person (not photocopied or faxed)',
        'description': 'The employer or authorized representative must physically examine the original documents in the employee\'s presence. Reviewing photocopies or faxed docs does NOT satisfy the requirement.',
        'severity': 'CRITICAL',
        'service_types': ['i9_everify'],
        'source': 'USCIS M-274 Handbook',
    },

    # ── Document Acceptance ──
    {
        'id': 'I9-008',
        'category': 'I-9 Document Rules',
        'fundamental': 'F5',
        'check': 'Correct document combination used (List A alone, OR List B + List C)',
        'description': 'Employee must present either one List A document (identity + work auth) OR one List B (identity) AND one List C (work auth). Cannot mix and match outside these combos.',
        'severity': 'CRITICAL',
        'service_types': ['i9_everify'],
        'source': 'USCIS M-274 Handbook',
    },
    {
        'id': 'I9-009',
        'category': 'I-9 Document Rules',
        'fundamental': 'F5',
        'check': 'Documents appear reasonably genuine and relate to the person presenting them',
        'description': 'Employer must accept documents that reasonably appear to be genuine. However, employer cannot specify which documents to present (that is document abuse / discrimination).',
        'severity': 'CRITICAL',
        'service_types': ['i9_everify'],
        'source': 'DOJ Civil Rights Division, 8 USC §1324b',
    },

    # ── Corrections ──
    {
        'id': 'I9-010',
        'category': 'I-9 Corrections',
        'fundamental': 'F7',
        'check': 'Corrections initialed and dated (no white-out or erasure)',
        'description': 'Errors must be corrected by drawing a line through incorrect info, entering correct info, and initialing/dating the correction. White-out, correction fluid, or erasures are NOT allowed — increases liability under federal immigration law.',
        'severity': 'CRITICAL',
        'service_types': ['i9_everify'],
        'source': 'USCIS M-274 Handbook §9.0',
    },
    {
        'id': 'I9-011',
        'category': 'I-9 Corrections',
        'fundamental': 'F7',
        'check': 'Section 1 corrections made ONLY by employee or preparer (not employer)',
        'description': 'Only the employee, preparer, or translator can correct Section 1. The employer cannot make corrections to Section 1 — that is a violation.',
        'severity': 'CRITICAL',
        'service_types': ['i9_everify'],
        'source': 'USCIS M-274 Handbook §9.0',
    },

    # ═══════════════════════════════════════════════════════════════
    # BACKGROUND CHECKS — FCRA Compliance & Adverse Action
    # Source: Fair Credit Reporting Act (15 USC §1681),
    #         EEOC Enforcement Guidance, BackgroundChecks.com,
    #         Checkr Adverse Action Report
    # ═══════════════════════════════════════════════════════════════

    # ── Consent & Disclosure ──
    {
        'id': 'BGC-001',
        'category': 'Background Check Consent',
        'fundamental': 'F1',
        'check': 'Written consent/authorization obtained from subject BEFORE running report',
        'description': 'FCRA requires written authorization from the subject before ordering a background check. No consent = illegal report. $825M+ in FCRA settlements over 5 years proves this matters.',
        'severity': 'CRITICAL',
        'service_types': ['background_chk'],
        'source': 'FCRA 15 USC §1681b(b)(2)',
    },
    {
        'id': 'BGC-002',
        'category': 'Background Check Consent',
        'fundamental': 'F5',
        'check': 'Disclosure provided as STANDALONE document (not buried in application)',
        'description': 'The FCRA disclosure must be a clear, standalone document — not combined with the employment application or other paperwork. Bundled disclosures = FCRA violation.',
        'severity': 'CRITICAL',
        'service_types': ['background_chk'],
        'source': 'FCRA §1681b(b)(2), Checkr Report',
    },
    {
        'id': 'BGC-003',
        'category': 'Background Check Consent',
        'fundamental': 'F1',
        'check': 'Subject signed and dated the consent form',
        'description': 'Subject must physically or electronically sign the consent/authorization. Unsigned consent forms = no valid authorization = report cannot be used.',
        'severity': 'CRITICAL',
        'service_types': ['background_chk'],
        'source': 'FCRA §1681b(b)(2)',
    },

    # ── Adverse Action Process ──
    {
        'id': 'BGC-004',
        'category': 'Adverse Action Compliance',
        'fundamental': 'F5',
        'check': 'Pre-Adverse Action Notice sent BEFORE final decision (with report copy + FCRA rights summary)',
        'description': '70% of organizations fail this step. Before taking adverse action, employer MUST send: (1) copy of the background report, (2) A Summary of Your Rights Under the FCRA. Then WAIT at least 5 business days.',
        'severity': 'CRITICAL',
        'service_types': ['background_chk'],
        'source': 'FCRA §1681b(b)(3), Checkr Adverse Action Report',
    },
    {
        'id': 'BGC-005',
        'category': 'Adverse Action Compliance',
        'fundamental': 'F5',
        'check': 'Minimum 5 business day waiting period observed between pre-adverse and final notice',
        'description': 'After sending pre-adverse notice, employer must wait at least 5 business days before making final adverse decision. Rushing this timeline = FCRA violation.',
        'severity': 'CRITICAL',
        'service_types': ['background_chk'],
        'source': 'FCRA §1681b(b)(3)',
    },
    {
        'id': 'BGC-006',
        'category': 'Adverse Action Compliance',
        'fundamental': 'F5',
        'check': 'Final Adverse Action Notice issued with CRA contact info and FCRA rights',
        'description': 'If adverse action is taken, final notice must include: CRA name/address/phone, statement that CRA did not make the decision, and subject\'s right to dispute.',
        'severity': 'CRITICAL',
        'service_types': ['background_chk'],
        'source': 'FCRA §1681m(a)',
    },

    # ── Report Accuracy ──
    {
        'id': 'BGC-007',
        'category': 'Report Accuracy',
        'fundamental': 'F7',
        'check': 'No duplicative, expunged, sealed, or legally restricted records reported',
        'description': 'CRA must have procedures preventing reporting of duplicate records, expunged convictions, sealed records, or legally restricted information. Reporting these = FCRA §607(b) violation.',
        'severity': 'CRITICAL',
        'service_types': ['background_chk'],
        'source': 'CFPB Final Rule, FCRA §607(b)',
    },
    {
        'id': 'BGC-008',
        'category': 'Report Accuracy',
        'fundamental': 'F5',
        'check': 'EEOC individualized assessment performed for criminal records (nature, time, job relevance)',
        'description': 'When criminal records are found, employer must apply EEOC Green Factors: (1) Nature/gravity of offense, (2) Time elapsed since conviction, (3) Nature of the job. Blanket rejection policies = discrimination risk.',
        'severity': 'WARNING',
        'service_types': ['background_chk'],
        'source': 'EEOC Enforcement Guidance on Criminal Records',
    },

    # ── State/Local Compliance ──
    {
        'id': 'BGC-009',
        'category': 'Ban-the-Box / Local Laws',
        'fundamental': 'F5',
        'check': 'State/local ban-the-box and fair chance hiring laws followed',
        'description': 'Many states and cities (CA, NJ, MA, NY, WA, NYC, SF, LA) have additional disclosure requirements, timing restrictions on when background checks can be run, or ban-the-box rules. Check jurisdiction.',
        'severity': 'WARNING',
        'service_types': ['background_chk'],
        'source': 'State/Local Fair Chance Laws',
    },
    {
        'id': 'BGC-010',
        'category': 'Ban-the-Box / Local Laws',
        'fundamental': 'F6',
        'check': 'Subject identity verified (SSN, DOB, name match report)',
        'description': 'Background report must match the actual subject. Verify SSN, DOB, and name match the person being screened. Wrong-person reports = FCRA liability and potential lawsuit.',
        'severity': 'CRITICAL',
        'service_types': ['background_chk'],
        'source': 'FCRA §607(b), BackgroundChecks.com',
    },

    # ═══════════════════════════════════════════════════════════════
    # PHLEBOTOMY — Specimen Collection & Handling
    # Source: CLSI H21-A5, Clinical Chemistry Lab Rejection Data,
    #         ExamOne/Quest Collection Standards, WHO Venipuncture
    # ═══════════════════════════════════════════════════════════════

    # ── Patient Identification ──
    {
        'id': 'PHL-001',
        'category': 'Patient Identification',
        'fundamental': 'F6',
        'check': 'Two patient identifiers verified (full name AND date of birth)',
        'description': 'Must verify patient identity using at least TWO identifiers (full name + DOB). Do not rely on visual recognition alone. Wrong-patient specimen = critical safety event.',
        'severity': 'CRITICAL',
        'service_types': ['phlebotomy'],
        'source': 'CLSI H21-A5, WHO Venipuncture Guidelines',
    },
    {
        'id': 'PHL-002',
        'category': 'Patient Identification',
        'fundamental': 'F6',
        'check': 'Government-issued photo ID examined for mobile/insurance draws',
        'description': 'For mobile phlebotomy, insurance exams, and legal collections, government-issued photo ID must be verified and documented.',
        'severity': 'CRITICAL',
        'service_types': ['phlebotomy'],
        'source': 'ExamOne Collection Standards',
    },

    # ── Specimen Labeling ──
    {
        'id': 'PHL-003',
        'category': 'Specimen Labeling',
        'fundamental': 'F2',
        'check': 'Specimen tubes labeled IMMEDIATELY after collection (at bedside/collection point)',
        'description': 'Tubes must be labeled immediately at the point of collection — NOT after leaving the patient. Labeling errors account for ~15% of all specimen rejections. Delayed labeling = specimen mix-up risk.',
        'severity': 'CRITICAL',
        'service_types': ['phlebotomy'],
        'source': 'CLSI H21-A5, Rejection Data (~14.7%)',
    },
    {
        'id': 'PHL-004',
        'category': 'Specimen Labeling',
        'fundamental': 'F2',
        'check': 'Label includes: patient name, DOB, date/time of collection, collector initials',
        'description': 'Every tube must be labeled with patient full name, date of birth, date and time of collection, and collector\'s initials. Missing any field = lab may reject.',
        'severity': 'CRITICAL',
        'service_types': ['phlebotomy'],
        'source': 'CLSI H21-A5',
    },

    # ── Collection Technique ──
    {
        'id': 'PHL-005',
        'category': 'Collection Technique',
        'fundamental': 'F7',
        'check': 'Alcohol at puncture site allowed to DRY completely before collection',
        'description': 'Alcohol must dry completely before venipuncture. Wet alcohol contaminates the specimen and causes hemolysis. Contamination = #1 specimen rejection reason (~35% of rejections).',
        'severity': 'CRITICAL',
        'service_types': ['phlebotomy'],
        'source': 'CLSI H21-A5, Rejection Data (35.1%)',
    },
    {
        'id': 'PHL-006',
        'category': 'Collection Technique',
        'fundamental': 'F5',
        'check': 'Correct tube type/color used for ordered test (order of draw followed)',
        'description': 'Wrong tube type = specimen rejected (~15% of rejections). Follow standard order of draw (blood culture → light blue → red/gold → green → lavender → gray) to prevent additive cross-contamination.',
        'severity': 'CRITICAL',
        'service_types': ['phlebotomy'],
        'source': 'CLSI H21-A5, Rejection Data (15.2%)',
    },
    {
        'id': 'PHL-007',
        'category': 'Collection Technique',
        'fundamental': 'F5',
        'check': 'Sufficient specimen volume collected (tubes filled to minimum line)',
        'description': 'Quantity Not Sufficient (QNS) causes ~15% of rejections. Tubes must be filled to the minimum fill line. Underfilled tubes with additives have wrong blood-to-additive ratio = inaccurate results.',
        'severity': 'CRITICAL',
        'service_types': ['phlebotomy'],
        'source': 'CLSI H21-A5, Rejection Data (15.1%)',
    },
    {
        'id': 'PHL-008',
        'category': 'Collection Technique',
        'fundamental': 'F7',
        'check': 'Tubes with additives gently inverted (mixed) immediately after collection',
        'description': 'Tubes with additives must be gently inverted 5-10 times immediately after draw. Failure to mix = clotted specimens (~9% of rejections). Do NOT shake — shaking causes hemolysis.',
        'severity': 'CRITICAL',
        'service_types': ['phlebotomy'],
        'source': 'CLSI H21-A5, Rejection Data (9.3%)',
    },

    # ── Chain of Custody (Insurance/Legal Draws) ──
    {
        'id': 'PHL-009',
        'category': 'Phlebotomy Chain of Custody',
        'fundamental': 'F1',
        'check': 'Chain of custody form signed by patient and collector',
        'description': 'For insurance exams, legal collections, or forensic draws, chain of custody form must be signed by both the patient and the phlebotomist. Unsigned = no legal standing.',
        'severity': 'CRITICAL',
        'service_types': ['phlebotomy'],
        'source': 'ExamOne Collection Standards',
    },
    {
        'id': 'PHL-010',
        'category': 'Phlebotomy Chain of Custody',
        'fundamental': 'F4',
        'check': 'Specimens sealed with tamper-evident seal in patient\'s presence',
        'description': 'For chain of custody collections, specimens must be sealed with tamper-evident closure while the patient is still present. Patient should witness the sealing.',
        'severity': 'CRITICAL',
        'service_types': ['phlebotomy'],
        'source': 'CLSI H21-A5, ExamOne Standards',
    },

    # ── Transport & Handling ──
    {
        'id': 'PHL-011',
        'category': 'Specimen Transport',
        'fundamental': 'F5',
        'check': 'Specimens transported at correct temperature (not exposed to extreme heat/cold)',
        'description': 'Most specimens require transport at room temperature or refrigerated. Extreme heat or cold destroys specimen integrity. Use insulated transport containers for mobile collections.',
        'severity': 'CRITICAL',
        'service_types': ['phlebotomy'],
        'source': 'CLSI H21-A5',
    },
    {
        'id': 'PHL-012',
        'category': 'Specimen Transport',
        'fundamental': 'F7',
        'check': 'Collection complications documented (difficult stick, hematoma, patient reaction)',
        'description': 'Any complications during collection must be documented: difficult venipuncture, hematoma formation, patient adverse reactions, or deviations from standard procedure.',
        'severity': 'WARNING',
        'service_types': ['phlebotomy'],
        'source': 'CLSI H21-A5, Clinical Standards',
    },

    # ═══════════════════════════════════════════════════════════════
    # PERMIT RUNNING — Building & Construction Permit Services
    # Source: Notary Permit Runner (NPR) Guide (62-page reference),
    #         Building & Zoning Department procedures,
    #         Contractor authorization requirements
    # ═══════════════════════════════════════════════════════════════

    # ── Application Completeness ──
    {
        'id': 'NPR-001',
        'category': 'Permit Application',
        'fundamental': 'F2',
        'check': 'Application filled out COMPLETELY — no blank fields (use N/A where not applicable)',
        'description': 'Permit clerks will not accept incomplete applications. Every field must be filled in or marked N/A. "Application must be filled out completely or it will not be accepted. If section is not applicable, enter N/A in space." — NPR Guide pg 58',
        'severity': 'CRITICAL',
        'service_types': ['permit_runner'],
        'source': 'NPR Guide pg 58, Building Dept Procedures',
    },
    {
        'id': 'NPR-002',
        'category': 'Permit Application',
        'fundamental': 'F2',
        'check': 'Property information complete (lot, block, subdivision, folio #, job address)',
        'description': 'Legal description of property must be included: lot, block, subdivision, and folio number. This info comes from County Records Division, tax records, or property survey. Missing = rejection.',
        'severity': 'CRITICAL',
        'service_types': ['permit_runner'],
        'source': 'NPR Guide pg 56-57',
    },
    {
        'id': 'NPR-003',
        'category': 'Permit Application',
        'fundamental': 'F2',
        'check': 'Contractor information matches qualifying license exactly',
        'description': 'Contractor name on application must match their qualifying license exactly. Also requires mailing address, phone, fax, and email. Mismatch = application rejected.',
        'severity': 'CRITICAL',
        'service_types': ['permit_runner'],
        'source': 'NPR Guide pg 56',
    },
    {
        'id': 'NPR-004',
        'category': 'Permit Application',
        'fundamental': 'F2',
        'check': 'Description of work and scope clearly stated',
        'description': '"A brief description of work must accompany ALL permit applications." Vague or missing scope = permit clerk sends you back.',
        'severity': 'CRITICAL',
        'service_types': ['permit_runner'],
        'source': 'NPR Guide pg 61',
    },
    {
        'id': 'NPR-005',
        'category': 'Permit Application',
        'fundamental': 'F5',
        'check': 'Correct permit type for the work being performed',
        'description': 'Must submit the right application for the work (electrical, plumbing, mechanical, roofing, building, etc.). Wrong permit type = wasted trip.',
        'severity': 'CRITICAL',
        'service_types': ['permit_runner'],
        'source': 'NPR Guide pg 7-8',
    },

    # ── Authorization & Signatures ──
    {
        'id': 'NPR-006',
        'category': 'Permit Authorization',
        'fundamental': 'F1',
        'check': 'Notarized letter of authorization from contractor on file or attached',
        'description': 'Most permit offices require a notarized letter of authorization allowing the NPR to pull permits on the contractor\'s behalf. Some counties keep these on file; others need it each time. No authorization = cannot pull.',
        'severity': 'CRITICAL',
        'service_types': ['permit_runner'],
        'source': 'NPR Guide pg 11-12',
    },
    {
        'id': 'NPR-007',
        'category': 'Permit Authorization',
        'fundamental': 'F1',
        'check': 'Owner signature present where required',
        'description': '"Owner\'s signature required. Application will not be accepted without this signature." When owner is not the contractor, separate owner authorization is needed.',
        'severity': 'CRITICAL',
        'service_types': ['permit_runner'],
        'source': 'NPR Guide pg 61-62',
    },
    {
        'id': 'NPR-008',
        'category': 'Permit Authorization',
        'fundamental': 'F4',
        'check': 'Forms requiring notarization are properly notarized BEFORE submission',
        'description': 'Many permit forms MUST be notarized before submission: building permit applications, homeowner affidavits, notice of commencement, roofing applications, disclosure statements, and more. Un-notarized = rejected.',
        'severity': 'CRITICAL',
        'service_types': ['permit_runner'],
        'source': 'NPR Guide pg 53-54',
    },

    # ── Jurisdiction & Routing ──
    {
        'id': 'NPR-009',
        'category': 'Permit Jurisdiction',
        'fundamental': 'F5',
        'check': 'Application submitted to the CORRECT permit office / jurisdiction',
        'description': 'Each county, city, and municipality has its own permit office. Submitting to the wrong jurisdiction = wasted trip. Verify which office has jurisdiction over the job site address.',
        'severity': 'CRITICAL',
        'service_types': ['permit_runner'],
        'source': 'NPR Guide pg 13-14',
    },
    {
        'id': 'NPR-010',
        'category': 'Permit Jurisdiction',
        'fundamental': 'F5',
        'check': 'Zoning approval obtained (if required before building permit)',
        'description': 'Some permits require zoning approval before the building permit can be issued. Check if zoning clearance is needed for the project type and location.',
        'severity': 'CRITICAL',
        'service_types': ['permit_runner'],
        'source': 'NPR Guide pg 19-20, 61',
    },

    # ── Plans & Supporting Documents ──
    {
        'id': 'NPR-011',
        'category': 'Permit Plans & Documents',
        'fundamental': 'F5',
        'check': 'Engineered stamped plans included (for plan-review permits)',
        'description': 'Home improvement, new construction, roofing, concrete, garages, pool permits ALL require engineered stamped plans. These go through plan review (can take a month+). No plans = cannot submit.',
        'severity': 'CRITICAL',
        'service_types': ['permit_runner'],
        'source': 'NPR Guide pg 11-12',
    },
    {
        'id': 'NPR-012',
        'category': 'Permit Plans & Documents',
        'fundamental': 'F5',
        'check': 'Correct payment amount for permit fees (verified before trip)',
        'description': 'Verify the exact permit fee amount with the permit office before making the trip. Wrong amount = cannot pull the permit. "Always be certain that the amount of money you are collecting for the permits is the correct amount."',
        'severity': 'CRITICAL',
        'service_types': ['permit_runner'],
        'source': 'NPR Guide pg 33-34',
    },

    # ── Trade-Specific Checks ──
    {
        'id': 'NPR-013',
        'category': 'Permit Trade-Specific',
        'fundamental': 'F2',
        'check': 'Electrical permit: building permit number included if part of larger project',
        'description': 'If the electrical work is part of a larger project with an existing building permit, that building permit number MUST be entered on the electrical application. Missing = rejection.',
        'severity': 'CRITICAL',
        'service_types': ['permit_runner'],
        'source': 'NPR Guide pg 58-59',
    },
    {
        'id': 'NPR-014',
        'category': 'Permit Trade-Specific',
        'fundamental': 'F2',
        'check': 'Flood zone information included (where required)',
        'description': 'Some jurisdictions require flood zone information on the permit application. Available at Building Division front desk or county flood maps. Ask if not sure.',
        'severity': 'WARNING',
        'service_types': ['permit_runner'],
        'source': 'NPR Guide pg 59',
    },
]


# ═══════════════════════════════════════════════════════════════════
# INSPECTION ENGINE — Run rules against an order
# ═══════════════════════════════════════════════════════════════════

def run_inspection(order_data: dict) -> dict:
    """
    Run the inspection engine against an order's scanback.

    order_data should include:
    - order_id: str
    - service_type: str (notary, drug_test, dna, fingerprint, apostille, i9_everify, background_chk, phlebotomy, permit_runner)
    - page_count_expected: int
    - page_count_actual: int
    - state: str (2-letter state code)
    - loan_type: str (optional — VA, FHA, Conventional)
    - client_rules: list of str (custom client rules)
    - checklist_responses: list of {rule_id: str, passed: bool, notes: str}

    Returns inspection result.
    """
    service_type = order_data.get('service_type', 'notary')
    state = order_data.get('state', '').upper()
    loan_type = order_data.get('loan_type', '').upper()
    page_expected = order_data.get('page_count_expected', 0)
    page_actual = order_data.get('page_count_actual', 0)
    checklist = {r['rule_id']: r for r in order_data.get('checklist_responses', [])}

    errors = []
    warnings = []
    passed = []

    # 1. Page count check (always)
    if page_expected > 0 and page_actual > 0:
        if page_actual < page_expected:
            errors.append({
                'rule_id': 'F5',
                'category': 'Page Count',
                'severity': 'CRITICAL',
                'description': f'Page count mismatch: expected {page_expected}, received {page_actual}. {page_expected - page_actual} page(s) missing.',
            })
        elif page_actual > page_expected:
            warnings.append({
                'rule_id': 'F5',
                'category': 'Page Count',
                'severity': 'INFO',
                'description': f'Extra pages: expected {page_expected}, received {page_actual}. Verify no duplicate pages.',
            })

    # 2. Run applicable known error rules
    applicable_rules = []
    for rule in KNOWN_ERROR_RULES:
        # Filter by service type
        if service_type not in rule.get('service_types', [service_type]):
            continue
        # Filter by state (only if rule is state-specific)
        if 'states' in rule and state not in rule['states']:
            continue
        # Filter by loan type (only if rule is loan-type-specific)
        if 'loan_types' in rule and loan_type not in rule.get('loan_types', []):
            continue
        applicable_rules.append(rule)

    for rule in applicable_rules:
        response = checklist.get(rule['id'])
        if response:
            if not response.get('passed', True):
                entry = {
                    'rule_id': rule['id'],
                    'category': rule['category'],
                    'severity': rule['severity'],
                    'description': rule['description'],
                    'check': rule['check'],
                    'notes': response.get('notes', ''),
                }
                if rule['severity'] == 'CRITICAL':
                    errors.append(entry)
                else:
                    warnings.append(entry)
            else:
                passed.append({'rule_id': rule['id'], 'check': rule['check']})
        # If no response for this rule, it hasn't been checked yet

    # 3. Run the 7 Fundamentals
    for fund in FUNDAMENTALS:
        response = checklist.get(fund['id'])
        if response and not response.get('passed', True):
            entry = {
                'rule_id': fund['id'],
                'category': 'Fundamental',
                'severity': fund['severity'],
                'description': fund['description'],
                'check': fund['check'],
                'notes': response.get('notes', ''),
            }
            if fund['severity'] == 'CRITICAL':
                errors.append(entry)
            else:
                warnings.append(entry)

    # Determine result
    if len(errors) > 0:
        result = 'HOLD'
        status = 'Correction Requested'
        message = f'HOLD — {len(errors)} critical error(s) found. Correct before shipping.'
    elif len(warnings) > 0:
        result = 'REVIEW'
        status = 'Under Review'
        message = f'REVIEW — {len(warnings)} warning(s). Human verification recommended.'
    else:
        result = 'CLEAN'
        status = 'Verified'
        message = 'CLEAN — All checks passed. Ready to ship.'

    return {
        'order_id': order_data.get('order_id', ''),
        'result': result,
        'status': status,
        'message': message,
        'critical_errors': errors,
        'warnings': warnings,
        'passed': passed,
        'rules_checked': len(applicable_rules) + len(FUNDAMENTALS),
        'page_check': {
            'expected': page_expected,
            'actual': page_actual,
            'match': page_expected == page_actual,
        },
        'timestamp': datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@prism_inspection.route('/prism/inspection/run', methods=['POST'])
def api_run_inspection():
    """Run the inspection engine against an order."""
    data = request.json or {}
    if not data.get('order_id'):
        return jsonify({'error': 'order_id required'}), 400

    result = run_inspection(data)

    # Save inspection report
    reports_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'inspection_reports')
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, f"{data['order_id']}_inspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_path, 'w') as f:
        json.dump(result, f, indent=2)

    return jsonify(result)


@prism_inspection.route('/prism/inspection/rules', methods=['GET'])
def api_get_rules():
    """Get all inspection rules, optionally filtered by service type."""
    service_type = request.args.get('service_type', '')
    state = request.args.get('state', '').upper()

    rules = KNOWN_ERROR_RULES
    if service_type:
        rules = [r for r in rules if service_type in r.get('service_types', [])]
    if state:
        rules = [r for r in rules if 'states' not in r or state in r['states']]

    return jsonify({
        'fundamentals': FUNDAMENTALS,
        'rules': rules,
        'total': len(rules),
        'categories': sorted(set(r['category'] for r in rules)),
    })


@prism_inspection.route('/prism/inspection/checklist/<service_type>', methods=['GET'])
def api_get_checklist(service_type):
    """
    Get the inspection checklist for a specific service type.
    This is what the QC reviewer sees when inspecting a scanback.
    """
    state = request.args.get('state', '').upper()
    loan_type = request.args.get('loan_type', '').upper()

    # Start with fundamentals
    checklist = []
    for f in FUNDAMENTALS:
        checklist.append({
            'id': f['id'],
            'check': f['check'],
            'severity': f['severity'],
            'category': 'Fundamental',
            'required': True,
        })

    # Add applicable rules
    for rule in KNOWN_ERROR_RULES:
        if service_type not in rule.get('service_types', []):
            continue
        if 'states' in rule and state and state not in rule['states']:
            continue
        if 'loan_types' in rule and loan_type and loan_type not in rule.get('loan_types', []):
            continue

        checklist.append({
            'id': rule['id'],
            'check': rule['check'],
            'severity': rule['severity'],
            'category': rule['category'],
            'description': rule.get('description', ''),
            'required': rule['severity'] == 'CRITICAL',
        })

    # Group by category
    categories = {}
    for item in checklist:
        cat = item['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    return jsonify({
        'service_type': service_type,
        'state': state,
        'loan_type': loan_type,
        'checklist': checklist,
        'total_checks': len(checklist),
        'categories': categories,
    })