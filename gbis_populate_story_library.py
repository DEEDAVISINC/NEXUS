#!/usr/bin/env python3
"""
Populate GRANT STORY LIBRARY from Grant Application Package
============================================================
Reads 01_GRANT_MASTER_PROFILE.md and creates/updates Airtable records
in GRANT STORY LIBRARY for AI application generation.

Run: python3 gbis_populate_story_library.py
"""

import os
import re
from pathlib import Path

try:
    from nexus_backend import AirtableClient
except ImportError:
    raise ImportError("Run from NEXUS BACKEND root directory.")

PACKAGE_ROOT = Path(__file__).resolve().parent / "GRANT_APPLICATION_PACKAGE"
MASTER_PROFILE = PACKAGE_ROOT / "01_GRANT_MASTER_PROFILE.md"

# Module definitions: (Module Name, section pattern or content key, optional tags)
STORY_MODULES = [
    ("Business Basics", "SECTION 1", ["company", "basics", "contact"]),
    ("Certifications & Divisions", "SECTION 2", ["certifications", "divisions"]),
    ("Owner Bio — Short", "SECTION 3", ["owner", "bio", "short"]),
    ("Owner Bio — Full", "SECTION 4", ["owner", "bio", "full"]),
    ("Business Narrative", "SECTION 5", ["narrative", "company"]),
    ("Mission Statement", "SECTION 6", ["mission", "vision"]),
    ("Community Impact", "SECTION 7", ["community", "impact"]),
    ("Use of Funds ($5K)", "SECTION 8", ["use-of-funds", "5k"]),
    ("Use of Funds ($10K)", "SECTION 8", ["use-of-funds", "10k"]),
    ("Use of Funds ($25K)", "SECTION 8", ["use-of-funds", "25k"]),
    ("Use of Funds ($50K)", "SECTION 8", ["use-of-funds", "50k"]),
    ("Use of Funds ($100K)", "SECTION 8", ["use-of-funds", "100k"]),
    ("Financial Need", "SECTION 9", ["financial", "need"]),
    ("Business Plan Summary", "SECTION 10", ["business-plan", "strategy"]),
    ("Social Proof", "SECTION 11", ["social-proof", "credibility"]),
    ("FAQ Answers", "SECTION 12", ["faq", "answers"]),
]


def extract_section(content: str, section_ref: str) -> str:
    """Extract markdown content for a section. Handles SECTION N and Use of Funds variants."""
    # Match ## SECTION N: Title
    if section_ref == "SECTION 8":
        # Use of Funds — extract all amount variants into separate modules via caller
        start = content.find("## SECTION 8: USE OF FUNDS TEMPLATES")
        if start == -1:
            return ""
        end = content.find("## SECTION 9:")
        if end == -1:
            end = len(content)
        block = content[start:end]
        return block

    pattern = rf"## {re.escape(section_ref)}[^\n]*\n(.*?)(?=\n## SECTION|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else ""


def extract_use_of_funds_block(full_section: str, amount: str) -> str:
    """Extract a specific Use of Funds amount block (e.g. 5,000, 10,000)."""
    # Match ### If awarded $X,XXX: then capture blockquote content
    escaped = re.escape(amount)
    pattern = rf"### If awarded \${escaped}:\s*\n(> .*?)(?=\n### If awarded|\n## |\Z)"
    match = re.search(pattern, full_section, re.DOTALL)
    if match:
        return match.group(1).strip().replace("> ", "").replace("\n> ", " ")
    return ""


def build_modules_from_profile() -> list[dict]:
    """Parse 01_GRANT_MASTER_PROFILE.md and build module records."""
    if not MASTER_PROFILE.exists():
        print(f"❌ Master profile not found: {MASTER_PROFILE}")
        return []

    content = MASTER_PROFILE.read_text(encoding="utf-8")
    modules = []

    use_of_funds_full = extract_section(content, "SECTION 8")

    for mod_name, section_ref, tags in STORY_MODULES:
        if "Use of Funds" in mod_name and section_ref == "SECTION 8":
            amount = mod_name.replace("Use of Funds (", "").replace(")", "")
            if amount == "$5K":
                amount_num = "5,000"
            elif amount == "$10K":
                amount_num = "10,000"
            elif amount == "$25K":
                amount_num = "25,000"
            elif amount == "$50K":
                amount_num = "50,000"
            elif amount == "$100K":
                amount_num = "100,000"
            else:
                amount_num = "5,000"
            text = extract_use_of_funds_block(use_of_funds_full, amount_num)
        else:
            text = extract_section(content, section_ref)

        if not text or len(text) < 20:
            continue

        modules.append({
            "Module Name": mod_name,
            "Content": text,
            "Status": "Active",
            "Module Type": "Grant Application",
            "Key Themes": tags,
        })

    return modules


def main():
    import sys
    dry_run = "--dry-run" in sys.argv
    print("📚 GBIS Story Library — Populate from Grant Application Package\n")
    print(f"Source: {MASTER_PROFILE}")

    modules = build_modules_from_profile()
    if not modules:
        print("No modules extracted. Check 01_GRANT_MASTER_PROFILE.md structure.")
        return

    print(f"Extracted {len(modules)} modules\n")
    if dry_run:
        for m in modules:
            print(f"  • {m['Module Name']} ({len(m['Content'])} chars)")
        print("\n(Dry run — no Airtable changes. Remove --dry-run to sync.)")
        return

    try:
        airtable = AirtableClient()
        # Airtable table: GRANT STORY LIBRARY (all caps)
        table_name = "GRANT STORY LIBRARY"
        try:
            existing = airtable.get_all_records(table_name)
        except Exception as e:
            raise RuntimeError(
                f"Could not access GRANT STORY LIBRARY: {e}. "
                "Verify Airtable base and token permissions."
            )
        by_name = {r["fields"].get("Module Name", ""): r for r in existing}

        created = 0
        updated = 0

        for mod in modules:
            name = mod["Module Name"]
            fields = {
                "Module Name": name,
                "Content": mod["Content"],
                "Status": "Active",
                "Module Type": mod.get("Module Type", "Grant Application"),
                "Key Themes": mod.get("Key Themes", []),
            }
            if "Word Count" in mod:
                fields["Word Count"] = mod["Word Count"]

            if name in by_name:
                rec = by_name[name]
                airtable.update_record(table_name, rec["id"], fields)
                updated += 1
                print(f"  ✓ Updated: {name}")
            else:
                airtable.create_record(table_name, fields)
                created += 1
                print(f"  + Created: {name}")

        print(f"\n✅ Done. Created: {created} | Updated: {updated}")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
