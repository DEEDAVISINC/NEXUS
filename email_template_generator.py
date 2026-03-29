"""
Email Template Generator — DDCSS
Mirrors capability_statement_generator pattern: HTML on disk, {{PLACEHOLDER}} replacement,
company credentials from company_info.py.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from company_info import (
    ADDRESS_FULL,
    CAGE_CODE,
    CERT_LINE,
    CHAMPS_PROVIDER_ID,
    COMPANY_NAME,
    DUNS,
    EIN,
    EMAIL,
    MC_NUMBER,
    NPI,
    OWNER_FULL_NAME,
    OWNER_NAME,
    OWNER_TITLE,
    PHONE_PRIMARY,
    SAM_STATUS,
    SIGNATURE_BLOCK,
    UEI,
    US_DOT,
    WEBSITE,
)

_TEMPLATE_ROOT = Path(__file__).parent / "email_templates" / "categories"

# category_key -> folder name under categories/
CATEGORY_DIRS: Dict[str, str] = {
    "mco_hide_snp": "mco_hide_snp",
}

# variant_key -> filename
VARIANT_FILES: Dict[str, str] = {
    "cold_outreach": "cold_outreach.html",
    "warm_follow_up": "warm_follow_up.html",
    "inbound_response": "inbound_response.html",
}

SUBJECT_BY_CATEGORY_VARIANT: Dict[str, Dict[str, str]] = {
    "mco_hide_snp": {
        "cold_outreach": "EDWOSB — MI Health Link / HIDE SNP — Dee Davis Inc.",
        "warm_follow_up": "Following up — HIDE SNP network — Dee Davis Inc.",
        "inbound_response": "RE: HIDE SNP / MI Health Link — Dee Davis Inc.",
    },
}

AVAILABLE_EMAIL_CATEGORIES: List[Dict[str, Any]] = [
    {
        "key": "mco_hide_snp",
        "label": "MCO — MI Health Link / HIDE SNP",
        "variants": [
            {"key": "cold_outreach", "label": "Cold Outreach"},
            {"key": "warm_follow_up", "label": "Warm Follow Up"},
            {"key": "inbound_response", "label": "Inbound Response"},
        ],
    },
]


def _signature_block_html() -> str:
    """Signature with HTML line breaks for email body."""
    return SIGNATURE_BLOCK.replace("\n", "<br/>")


def _default_replacements() -> Dict[str, str]:
    return {
        "{{COMPANY_NAME}}": COMPANY_NAME,
        "{{OWNER_NAME}}": OWNER_NAME,
        "{{OWNER_FULL_NAME}}": OWNER_FULL_NAME,
        "{{OWNER_TITLE}}": OWNER_TITLE,
        "{{NPI}}": NPI,
        "{{CHAMPS_PROVIDER_ID}}": CHAMPS_PROVIDER_ID,
        "{{ADDRESS_FULL}}": ADDRESS_FULL,
        "{{PHONE_PRIMARY}}": PHONE_PRIMARY,
        "{{EMAIL}}": EMAIL,
        "{{WEBSITE}}": WEBSITE,
        "{{CAGE_CODE}}": CAGE_CODE,
        "{{UEI}}": UEI,
        "{{DUNS}}": DUNS,
        "{{EIN}}": EIN,
        "{{MC_NUMBER}}": MC_NUMBER,
        "{{US_DOT}}": US_DOT,
        "{{SAM_STATUS}}": SAM_STATUS,
        "{{CERT_LINE}}": CERT_LINE,
        "{{SIGNATURE_BLOCK}}": _signature_block_html(),
    }


def _validate_category_variant(category: str, variant: str) -> Optional[str]:
    if category not in CATEGORY_DIRS:
        return f"Unknown category: {category}. Available: {list(CATEGORY_DIRS.keys())}"
    if variant not in VARIANT_FILES:
        return f"Unknown variant: {variant}. Available: {list(VARIANT_FILES.keys())}"
    return None


def _template_path(category: str) -> Path:
    sub = CATEGORY_DIRS[category]
    return _TEMPLATE_ROOT / sub


def generate_email_template(
    category: str,
    variant: str,
    recipient_first_name: str = "there",
    plan_display_name: str = "your MI Health Link plan",
    custom_paragraph: str = "",
    extra_replacements: Optional[Dict[str, str]] = None,
    output_path: Optional[str] = None,
) -> str:
    """
    Load HTML template and apply {{PLACEHOLDER}} replacements.
    Returns final HTML string.
    """
    err = _validate_category_variant(category, variant)
    if err:
        raise ValueError(err)

    fname = VARIANT_FILES[variant]
    path = _template_path(category) / fname
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")

    html = path.read_text(encoding="utf-8")
    replacements = _default_replacements()
    replacements["{{RECIPIENT_FIRST_NAME}}"] = recipient_first_name.strip() or "there"
    replacements["{{PLAN_DISPLAY_NAME}}"] = plan_display_name.strip() or "your MI Health Link plan"
    _cp = (custom_paragraph or "").strip()
    if _cp and not _cp.lstrip().startswith("<"):
        _cp = f"<p>{_cp}</p>"
    replacements["{{CUSTOM_PARAGRAPH}}"] = _cp
    if extra_replacements:
        for k, v in extra_replacements.items():
            key = k.strip()
            if not (key.startswith("{{") and key.endswith("}}")):
                key = "{{" + key.strip("{}") + "}}"
            replacements[key] = str(v)

    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    # Remove any unreplaced {{TOKENS}} for safety (optional: leave for debugging)
    # html = re.sub(r"\{\{[A-Z0-9_]+\}\}", "", html)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")

    return html


def handle_generate_email_template(
    category: str = "mco_hide_snp",
    variant: str = "cold_outreach",
    recipient_first_name: Optional[str] = None,
    plan_display_name: Optional[str] = None,
    custom_paragraph: Optional[str] = None,
    extra_replacements: Optional[Dict[str, str]] = None,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    API-style handler: returns dict with success, html, subject, paths.
    Matches pattern used by capability statement / document flows.
    """
    try:
        cat = (category or "mco_hide_snp").strip()
        var = (variant or "cold_outreach").strip()
        err = _validate_category_variant(cat, var)
        if err:
            return {"success": False, "error": err}

        html = generate_email_template(
            category=cat,
            variant=var,
            recipient_first_name=recipient_first_name or "there",
            plan_display_name=plan_display_name or "your MI Health Link plan",
            custom_paragraph=custom_paragraph or "",
            extra_replacements=extra_replacements,
        )

        subject = SUBJECT_BY_CATEGORY_VARIANT.get(cat, {}).get(var, f"Dee Davis Inc. — {cat} / {var}")

        html_file = None
        if output_dir:
            safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", f"{cat}_{var}")[:80]
            html_file = str(Path(output_dir) / f"email_{safe}.html")
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            Path(html_file).write_text(html, encoding="utf-8")

        return {
            "success": True,
            "category": cat,
            "variant": var,
            "subject": subject,
            "html": html,
            "html_file": html_file,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
