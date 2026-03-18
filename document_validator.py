"""
Document Validator — Automated Enforcement Engine

Scans any generated document (HTML, Markdown, or plain text) and returns
PASS/FAIL results for every critical business rule. Run this BEFORE presenting
any document to Dee.

Usage:
    from document_validator import validate_document

    results = validate_document(
        content=html_string,
        doc_type="buyer_email",          # or "cap_statement", "supplier_rfq", "sub_outreach", "quote_response"
        known_buyer_names=["USACE"],     # for supplier/sub docs — names that must NOT appear
        solicitation_numbers=["W912..."],
    )

    if not results["all_passed"]:
        # FIX the failures before presenting to Dee
        for failure in results["failures"]:
            print(failure)
"""

import re
from typing import Dict, List, Optional

from company_info import (
    PHONE_PRIMARY,
    PHONE_ALT,
    EMAIL,
    ADDRESS_ZIP,
    CAGE_CODE,
    UEI,
    COMPANY_NAME,
    BANNED_PHONES,
    BANNED_ZIPS,
    BANNED_EMAILS,
    BANNED_EINS,
    BANNED_WEBSITES,
    WEBSITE,
    OWNER_NAME,
    EIN,
)


# ─────────────────────────────────────────────────────────────────────────────
# KNOWN BUYER / AGENCY NAMES — suppliers and subs must NEVER see these
# ─────────────────────────────────────────────────────────────────────────────
KNOWN_AGENCY_NAMES = [
    "Canton Township",
    "City of Detroit",
    "Oakland County",
    "Wayne County",
    "Macomb County",
    "Genesee County",
    "RCOC",
    "Road Commission for Oakland County",
    "Rock Island",
    "CPS Energy",
    "Sterling Heights",
    "Madison Heights",
    "Livonia",
    "Warren",
    "Troy",
    "USACE",
    "US Army Corps",
    "Army Corps of Engineers",
    "DECA",
    "DeCA",
    "Fort Bragg",
    "Fort Riley",
    "Travis AFB",
    "State Department",
    "Department of State",
    "Palatka",
    "MICC",
    "DLA",
    "Defense Logistics Agency",
    "VA ",
    "Department of Veterans Affairs",
    "NIH",
    "National Institutes of Health",
]

KNOWN_PROCUREMENT_OFFICERS = [
    "Brad Thompson",
    "Jennifer Coleman",
    "Monique Euter",
    "Eileen Meyer",
    "Valerie Gregorio",
    "Lauren Elkins",
]


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATOR CHECKS
# ─────────────────────────────────────────────────────────────────────────────

def _check_company_info(content: str) -> List[Dict]:
    """Verify correct company info and flag banned values."""
    issues = []

    for banned in BANNED_PHONES:
        if banned in content:
            issues.append({
                "rule": "COMPANY_INFO",
                "severity": "CRITICAL",
                "message": f"WRONG PHONE NUMBER found: '{banned}' — must be {PHONE_PRIMARY}",
                "fix": f"Replace '{banned}' with '{PHONE_PRIMARY}'",
            })

    for banned in BANNED_ZIPS:
        if re.search(rf"\b{re.escape(banned)}\b", content):
            issues.append({
                "rule": "COMPANY_INFO",
                "severity": "CRITICAL",
                "message": f"WRONG ZIP CODE found: '{banned}' — must be {ADDRESS_ZIP}",
                "fix": f"Replace '{banned}' with '{ADDRESS_ZIP}'",
            })

    for banned in BANNED_EMAILS:
        if banned.lower() in content.lower():
            issues.append({
                "rule": "COMPANY_INFO",
                "severity": "CRITICAL",
                "message": f"WRONG EMAIL found: '{banned}' — must be {EMAIL}",
                "fix": f"Replace '{banned}' with '{EMAIL}'",
            })

    for banned in BANNED_EINS:
        if banned in content:
            issues.append({
                "rule": "COMPANY_INFO",
                "severity": "CRITICAL",
                "message": f"WRONG EIN found: '{banned}' — must be {EIN}",
                "fix": f"Replace '{banned}' with '{EIN}'",
            })

    for banned in BANNED_WEBSITES:
        if banned.lower() in content.lower():
            issues.append({
                "rule": "COMPANY_INFO",
                "severity": "CRITICAL",
                "message": f"WRONG WEBSITE found: '{banned}' — must be {WEBSITE}",
                "fix": f"Replace '{banned}' with '{WEBSITE}'",
            })

    return issues


def _check_required_info_present(content: str, doc_type: str) -> List[Dict]:
    """Verify required company identifiers are present in buyer-facing docs."""
    issues = []
    if doc_type not in ("buyer_email", "cap_statement", "quote_response"):
        return issues

    checks = {
        "CAGE Code (8UMX3)": CAGE_CODE,
        "UEI (HJB4KNYJVGZ1)": UEI,
    }
    if doc_type in ("cap_statement", "quote_response"):
        checks["Phone number"] = PHONE_PRIMARY
        checks["Email address"] = EMAIL

    for label, value in checks.items():
        if value not in content:
            issues.append({
                "rule": "REQUIRED_INFO",
                "severity": "HIGH",
                "message": f"Missing {label} in {doc_type}",
                "fix": f"Add '{value}' to the document",
            })

    return issues


def _check_edwosb_mention(content: str, doc_type: str) -> List[Dict]:
    """Buyer-facing docs must mention EDWOSB."""
    issues = []
    if doc_type not in ("buyer_email", "cap_statement", "quote_response"):
        return issues

    if not re.search(r"EDWOSB", content, re.IGNORECASE):
        issues.append({
            "rule": "EDWOSB_MENTION",
            "severity": "HIGH",
            "message": "EDWOSB certification not mentioned in buyer-facing document",
            "fix": "Add EDWOSB reference — this is DDI's competitive weapon",
        })
    return issues


def _check_buyer_protection(
    content: str,
    doc_type: str,
    known_buyer_names: Optional[List[str]] = None,
    solicitation_numbers: Optional[List[str]] = None,
    procurement_officers: Optional[List[str]] = None,
) -> List[Dict]:
    """Supplier and sub docs must NEVER contain buyer identifiers."""
    issues = []
    if doc_type not in ("supplier_rfq", "sub_outreach"):
        return issues

    all_names = list(KNOWN_AGENCY_NAMES)
    if known_buyer_names:
        all_names.extend(known_buyer_names)

    for name in all_names:
        pattern = re.escape(name.strip())
        if re.search(pattern, content, re.IGNORECASE):
            issues.append({
                "rule": "BUYER_PROTECTION",
                "severity": "CRITICAL",
                "message": f"BUYER NAME LEAKED: '{name}' found in {doc_type}",
                "fix": f"Remove '{name}' — replace with generic term like 'municipal client' or 'government client'",
            })

    all_officers = list(KNOWN_PROCUREMENT_OFFICERS)
    if procurement_officers:
        all_officers.extend(procurement_officers)

    for name in all_officers:
        if name.lower() in content.lower():
            issues.append({
                "rule": "BUYER_PROTECTION",
                "severity": "CRITICAL",
                "message": f"PROCUREMENT OFFICER NAME LEAKED: '{name}' found in {doc_type}",
                "fix": f"Remove '{name}' immediately",
            })

    if solicitation_numbers:
        for sol_num in solicitation_numbers:
            if sol_num in content:
                issues.append({
                    "rule": "BUYER_PROTECTION",
                    "severity": "CRITICAL",
                    "message": f"SOLICITATION NUMBER LEAKED: '{sol_num}' found in {doc_type}",
                    "fix": f"Remove '{sol_num}' — use DDI-YYYY-### format instead",
                })

    gov_terms = [
        r"\bsolicitation\s+#",
        r"\bRFP\s+#?\d",
        r"\bRFQ\s+#?\d",
        r"\bITB\s+#?\d",
        r"\bRFB\s+#?\d",
    ]
    for pattern in gov_terms:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append({
                "rule": "BUYER_PROTECTION",
                "severity": "HIGH",
                "message": f"Government solicitation reference pattern found in supplier doc: {pattern}",
                "fix": "Remove all government solicitation references from supplier-facing documents",
            })

    return issues


def _check_supplier_rfq_format(content: str, doc_type: str) -> List[Dict]:
    """Supplier RFQs must use DDI-YYYY-### numbering."""
    issues = []
    if doc_type != "supplier_rfq":
        return issues

    if not re.search(r"DDI-\d{4}-\d{3}", content):
        issues.append({
            "rule": "RFQ_FORMAT",
            "severity": "HIGH",
            "message": "Supplier RFQ missing DDI-YYYY-### number",
            "fix": "Add DDI sequential number (e.g., DDI-2026-001)",
        })

    return issues


def _check_proposalbio_table(content: str, doc_type: str) -> List[Dict]:
    """Buyer emails must include the ProposalBio framework table."""
    issues = []
    if doc_type != "buyer_email":
        return issues

    if not re.search(r"PROPOSALBIO\s+FRAMEWORK", content, re.IGNORECASE):
        issues.append({
            "rule": "PROPOSALBIO_TABLE",
            "severity": "HIGH",
            "message": "Missing ProposalBio framework table in buyer email",
            "fix": "Add the ProposalBio biohack application table at the top of the email file",
        })

    return issues


def _check_cap_statement_sections(content: str, doc_type: str) -> List[Dict]:
    """Cap statements must have all required sections."""
    issues = []
    if doc_type != "cap_statement":
        return issues

    required_patterns = [
        ("EDWOSB advantage box", r"EDWOSB", "Add EDWOSB certification section"),
        ("Core competencies", r"(?:CORE\s+COMPETENC|competenc)", "Add core competencies grid"),
        ("Contact info", PHONE_PRIMARY, f"Add contact info with {PHONE_PRIMARY}"),
    ]

    for label, pattern, fix in required_patterns:
        if not re.search(pattern, content, re.IGNORECASE):
            issues.append({
                "rule": "CAP_STATEMENT_SECTIONS",
                "severity": "HIGH",
                "message": f"Missing required cap statement section: {label}",
                "fix": fix,
            })

    if "<img" in content.lower() and "base64" not in content:
        issues.append({
            "rule": "CAP_STATEMENT_SECTIONS",
            "severity": "MEDIUM",
            "message": "Cap statement has <img> tags without base64 logo — logo may not render",
            "fix": "Embed logo as base64 data URI",
        })

    return issues


def _check_signature_block(content: str, doc_type: str) -> List[Dict]:
    """Buyer emails must have the full signature block."""
    issues = []
    if doc_type != "buyer_email":
        return issues

    if OWNER_NAME not in content:
        issues.append({
            "rule": "SIGNATURE_BLOCK",
            "severity": "MEDIUM",
            "message": "Missing 'Dee Davis' in signature block",
            "fix": "Add full signature block with name, title, company, address, phone, email, certs",
        })

    if PHONE_PRIMARY not in content:
        issues.append({
            "rule": "SIGNATURE_BLOCK",
            "severity": "HIGH",
            "message": f"Missing phone number ({PHONE_PRIMARY}) in email",
            "fix": f"Add {PHONE_PRIMARY} to the signature block",
        })

    return issues


def _check_diversity_section(content: str, doc_type: str) -> List[Dict]:
    """Quote responses and cap statements should have diversity info."""
    issues = []
    if doc_type not in ("quote_response",):
        return issues

    if not re.search(r"DIVERSITY\s+ADVANTAGE", content, re.IGNORECASE):
        issues.append({
            "rule": "DIVERSITY_SCAN",
            "severity": "MEDIUM",
            "message": "Missing DIVERSITY ADVANTAGE section in quote response",
            "fix": "Add diversity advantage section per diversity-inclusion-scanning rule",
        })

    return issues


# ─────────────────────────────────────────────────────────────────────────────
# MAIN VALIDATOR
# ─────────────────────────────────────────────────────────────────────────────

def validate_document(
    content: str,
    doc_type: str,
    known_buyer_names: Optional[List[str]] = None,
    solicitation_numbers: Optional[List[str]] = None,
    procurement_officers: Optional[List[str]] = None,
) -> Dict:
    """
    Validate a document against all critical business rules.

    Args:
        content: The full text/HTML of the document
        doc_type: One of: buyer_email, cap_statement, supplier_rfq,
                  sub_outreach, quote_response
        known_buyer_names: Agency/client names that must NOT appear in
                          supplier/sub docs
        solicitation_numbers: Sol numbers that must NOT appear in
                             supplier/sub docs
        procurement_officers: CO names that must NOT appear in supplier/sub docs

    Returns:
        Dict with:
            all_passed: bool
            total_checks: int
            failures: list of dicts with rule, severity, message, fix
            warnings: list of dicts (severity=MEDIUM)
            critical_failures: list of dicts (severity=CRITICAL)
            summary: str (human-readable)
    """
    valid_types = ("buyer_email", "cap_statement", "supplier_rfq",
                   "sub_outreach", "quote_response")
    if doc_type not in valid_types:
        return {
            "all_passed": False,
            "error": f"Invalid doc_type '{doc_type}'. Must be one of: {valid_types}",
        }

    all_issues: List[Dict] = []

    all_issues.extend(_check_company_info(content))
    all_issues.extend(_check_required_info_present(content, doc_type))
    all_issues.extend(_check_edwosb_mention(content, doc_type))
    all_issues.extend(
        _check_buyer_protection(
            content, doc_type, known_buyer_names,
            solicitation_numbers, procurement_officers,
        )
    )
    all_issues.extend(_check_supplier_rfq_format(content, doc_type))
    all_issues.extend(_check_proposalbio_table(content, doc_type))
    all_issues.extend(_check_cap_statement_sections(content, doc_type))
    all_issues.extend(_check_signature_block(content, doc_type))
    all_issues.extend(_check_diversity_section(content, doc_type))

    critical = [i for i in all_issues if i["severity"] == "CRITICAL"]
    high = [i for i in all_issues if i["severity"] == "HIGH"]
    medium = [i for i in all_issues if i["severity"] == "MEDIUM"]

    all_passed = len(critical) == 0 and len(high) == 0

    if all_passed and not medium:
        summary = f"PASSED — {doc_type} cleared all validation checks."
    elif all_passed and medium:
        summary = f"PASSED WITH WARNINGS — {len(medium)} non-blocking issue(s). Review recommended."
    else:
        summary = (
            f"FAILED — {len(critical)} critical, {len(high)} high severity issue(s). "
            f"Fix ALL critical and high issues before presenting to Dee."
        )

    return {
        "all_passed": all_passed,
        "total_issues": len(all_issues),
        "critical_failures": critical,
        "high_failures": high,
        "warnings": medium,
        "failures": critical + high,
        "all_issues": all_issues,
        "summary": summary,
        "doc_type": doc_type,
    }


def validate_file(
    filepath: str,
    doc_type: str,
    **kwargs,
) -> Dict:
    """Convenience: read a file and validate its contents."""
    with open(filepath, "r", errors="ignore") as f:
        content = f.read()
    return validate_document(content, doc_type, **kwargs)


def print_validation_report(results: Dict) -> str:
    """Format validation results as a readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"  DOCUMENT VALIDATION REPORT — {results.get('doc_type', 'unknown')}")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  Result: {'PASS' if results['all_passed'] else 'FAIL'}")
    lines.append(f"  Issues: {results['total_issues']}")
    lines.append("")

    if results.get("critical_failures"):
        lines.append("  CRITICAL FAILURES (must fix):")
        for issue in results["critical_failures"]:
            lines.append(f"    [{issue['rule']}] {issue['message']}")
            lines.append(f"      Fix: {issue['fix']}")
        lines.append("")

    if results.get("high_failures"):
        lines.append("  HIGH SEVERITY (must fix):")
        for issue in results["high_failures"]:
            lines.append(f"    [{issue['rule']}] {issue['message']}")
            lines.append(f"      Fix: {issue['fix']}")
        lines.append("")

    if results.get("warnings"):
        lines.append("  WARNINGS (review recommended):")
        for issue in results["warnings"]:
            lines.append(f"    [{issue['rule']}] {issue['message']}")
            lines.append(f"      Fix: {issue['fix']}")
        lines.append("")

    lines.append(f"  {results['summary']}")
    lines.append("=" * 60)

    report = "\n".join(lines)
    print(report)
    return report


# ─────────────────────────────────────────────────────────────────────────────
# CLI — run from terminal: python document_validator.py <file> <doc_type>
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python document_validator.py <filepath> <doc_type>")
        print("  doc_type: buyer_email | cap_statement | supplier_rfq | sub_outreach | quote_response")
        sys.exit(1)

    filepath = sys.argv[1]
    doc_type = sys.argv[2]
    buyer_names = sys.argv[3].split(",") if len(sys.argv) > 3 else None

    results = validate_file(filepath, doc_type, known_buyer_names=buyer_names)
    print_validation_report(results)
    sys.exit(0 if results["all_passed"] else 1)
