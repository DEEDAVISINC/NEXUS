#!/usr/bin/env python3
"""
Log an outbound email to NEXUS master tracking files.

Run when Dee confirms a send (or NEXUS logs after "sent" in chat):

  python3 log_outbound_email.py \\
    --to stephanie.logan@medicaid.alabama.gov \\
    --contact "Stephanie Logan" \\
    --org "Alabama Medicaid" \\
    --subject "NEMT TPA Program Administration" \\
    --date "2026-05-11 19:53" \\
    --category mco \\
    --source "CLIENT OUTREACH/ALABAMA MCO NEMT HAVEN/ALABAMA_HOT_REPLY_EMAILS_MAY11.md"

Updates:
  - OUTBOUND_EMAIL_LOG.md (master — search before ANY new email)
  - CLIENT OUTREACH/EMAIL_SENT_REGISTRY.md (dedupe index)
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MASTER_LOG = ROOT / "OUTBOUND_EMAIL_LOG.md"
REGISTRY = ROOT / "CLIENT OUTREACH" / "EMAIL_SENT_REGISTRY.md"


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _already_logged(email: str) -> bool:
    if not REGISTRY.exists():
        return False
    return _normalize_email(email) in REGISTRY.read_text(encoding="utf-8").lower()


def _ensure_master_log() -> None:
    if MASTER_LOG.exists():
        return
    MASTER_LOG.write_text(
        """# Outbound Email Log — Every Email Dee Sends

**Single source of truth.** Search this file before drafting or recommending ANY outbound email.

**Rule:** The moment Dee confirms a send → run `log_outbound_email.py` or NEXUS logs the row in chat → **before anything else.**

---

""",
        encoding="utf-8",
    )


def _parse_date(date_str: str) -> datetime:
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%m/%d/%Y %H:%M", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {date_str!r}")


def append_master_log(
    *,
    sent_at: datetime,
    to_email: str,
    contact: str,
    org: str,
    subject: str,
    category: str,
    source: str,
    notes: str,
) -> None:
    _ensure_master_log()
    text = MASTER_LOG.read_text(encoding="utf-8")
    header = f"## {sent_at.strftime('%Y-%m-%d')}"
    row = (
        f"| {sent_at.strftime('%H:%M ET')} | {to_email} | {contact} | {org} | "
        f"{subject} | {category} | {source or '—'} | {notes or 'SENT'} |"
    )

    if header not in text:
        block = f"\n{header}\n\n| Time | To | Contact | Organization | Subject | Category | Source file | Status |\n|------|-----|---------|--------------|---------|----------|-------------|--------|\n{row}\n"
        text = text.rstrip() + "\n" + block
    else:
        # Insert row after table header under this date
        pattern = re.compile(
            re.escape(header) + r"\n\n\| Time \|.*?\n\|------\|.*?\n",
            re.DOTALL,
        )
        match = pattern.search(text)
        if match:
            insert_at = match.end()
            text = text[:insert_at] + row + "\n" + text[insert_at:]
        else:
            text = text.rstrip() + f"\n{row}\n"

    MASTER_LOG.write_text(text, encoding="utf-8")


def append_registry(
    *,
    sent_at: datetime,
    to_email: str,
    contact: str,
    org: str,
    subject: str,
    source: str,
    notes: str,
) -> None:
    if not REGISTRY.exists():
        return
    if _already_logged(to_email):
        return
    text = REGISTRY.read_text(encoding="utf-8")
    marker = "## Confirmed sends (do not cold re-pitch)"
    row = (
        f"| {sent_at.strftime('%Y-%m-%d %H:%M ET')} | {to_email} | {contact} / {org} | "
        f"{subject} | {notes or 'SENT'} | {source or 'log_outbound_email.py'} |"
    )
    if marker in text:
        text = text.replace(
            marker,
            marker + "\n" + row,
            1,
        )
        REGISTRY.write_text(text, encoding="utf-8")


def mark_source_sent(source: Path, to_email: str, sent_at: datetime) -> bool:
    """Mark ⬜ → ✅ in source file checklist if email appears in that file."""
    if not source.is_file():
        return False
    content = source.read_text(encoding="utf-8")
    if to_email.lower() not in content.lower():
        return False
    stamp = f"✅ **{sent_at.strftime('%Y-%m-%d %H:%M ET')}**"
    new_content, n = re.subn(r"\|\s*⬜\s*\|", f"| {stamp} |", content, count=1)
    if n:
        source.write_text(new_content, encoding="utf-8")
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Log outbound email to NEXUS master files")
    parser.add_argument("--to", required=True, help="Recipient email")
    parser.add_argument("--contact", default="—", help="Contact name")
    parser.add_argument("--org", default="—", help="Organization")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d %H:%M"),
        help="Send datetime (YYYY-MM-DD HH:MM)",
    )
    parser.add_argument(
        "--category",
        default="other",
        choices=["co", "mco", "buyer", "supplier", "sub", "partner", "grant", "other"],
    )
    parser.add_argument("--source", default="", help="Source draft file path")
    parser.add_argument("--notes", default="SENT", help="Status notes")
    args = parser.parse_args()

    sent_at = _parse_date(args.date)
    to_email = args.to.strip()
    source_path = (ROOT / args.source).resolve() if args.source else None

    if _already_logged(to_email):
        print(f"⚠️  Already in registry: {to_email} — skipping duplicate registry row")
    else:
        append_registry(
            sent_at=sent_at,
            to_email=to_email,
            contact=args.contact,
            org=args.org,
            subject=args.subject,
            source=args.source,
            notes=args.notes,
        )
        print(f"✓ Registry updated: {to_email}")

    append_master_log(
        sent_at=sent_at,
        to_email=to_email,
        contact=args.contact,
        org=args.org,
        subject=args.subject,
        category=args.category,
        source=args.source,
        notes=args.notes,
    )
    print(f"✓ Master log updated: OUTBOUND_EMAIL_LOG.md")

    if source_path:
        if mark_source_sent(source_path, to_email, sent_at):
            print(f"✓ Source checklist marked sent: {args.source}")
        else:
            print(f"— Source file not updated (no ⬜ row or email not in file): {args.source}")


if __name__ == "__main__":
    main()
