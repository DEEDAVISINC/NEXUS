"""
NEXUS Bid Folder Scanner
Reads BIDS:RESOURCES/ folder structure to detect real bid status.
No mock data. No hardcoded lists. Reads the actual filesystem.

Detects:
- Submitted bids (from confirmation files)
- Active bids (folders with recent activity)
- Stale bids (no activity near deadline)
- Bid values (from confirmation/strategy files)
- Last activity timestamps
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


# Base path for bid folders
BIDS_ROOT = os.path.join(os.path.dirname(__file__), "BIDS:RESOURCES")

# Patterns that indicate a bid was submitted
SUBMISSION_PATTERNS = [
    "SUBMISSION_CONFIRMATION",
    "SUBMITTED_CONFIRMATION",
    "BID_SUBMITTED",
    "SUBMISSION_COMPLETE",
    "SUCCESSFULLY_SUBMITTED",
    "NEXUS_INTEGRATION_COMPLETE",
]

# Patterns that indicate a bid is ready to submit
READY_PATTERNS = [
    "BID_SUBMISSION_READY",
    "READY_TO_SUBMIT",
    "FINAL_BID_READY",
    "BIDNET_ENTRY_COPYABLE",
]

# Patterns that indicate supplier quotes exist
QUOTE_PATTERNS = [
    "QUOTE_REQUEST",
    "QUOTE_TRACKING",
    "GRAINGER_QUOTE",
    "SUPPLIER_QUOTE",
    "PRICING_WORKSHEET",
    "BID_CALCULATION",
]

# Patterns that indicate strategy/analysis exists
STRATEGY_PATTERNS = [
    "STRATEGY",
    "BID_GUIDE",
    "ACTION_PLAN",
    "ANALYSIS",
    "QUICK_START",
    "WORKFLOW_STATUS",  # Created when opportunity is reviewed
]

# Folders to skip (not actual bids)
SKIP_FOLDERS = {
    "COMPANY FORMS",
    "REFERENCE GUIDES",
    "RCOC MASTER FILES",
    "MISCELLANEOUS",
    "PERSONAL LEGAL",
    ".DS_Store",
}


def scan_all_bids() -> Dict:
    """
    Scan BIDS:RESOURCES/ and return real bid data.
    Returns dict with submitted, active, needs_review, and stale bids.
    """
    if not os.path.exists(BIDS_ROOT):
        return {"error": f"BIDS:RESOURCES folder not found at {BIDS_ROOT}"}

    bids = []
    now = datetime.now()

    for entry in os.scandir(BIDS_ROOT):
        if not entry.is_dir():
            continue
        if entry.name in SKIP_FOLDERS or entry.name.startswith("."):
            continue

        bid = scan_single_bid(entry.path, entry.name, now)
        if bid:
            bids.append(bid)

    # Sort and categorize
    submitted = [b for b in bids if b["status"] == "submitted"]
    active = [b for b in bids if b["status"] == "active"]
    needs_review = [b for b in bids if b["status"] == "needs_review"]
    stale = [b for b in bids if b["status"] == "stale"]

    # Sort submitted by value descending
    submitted.sort(key=lambda b: b["value"], reverse=True)
    # Sort active by deadline ascending (most urgent first)
    active.sort(key=lambda b: b.get("deadline_date") or "9999-99-99")

    total_submitted_value = sum(b["value"] for b in submitted)
    total_active_value = sum(b["value"] for b in active)

    return {
        "success": True,
        "scanned_at": now.isoformat(),
        "summary": {
            "total_folders": len(bids),
            "submitted_count": len(submitted),
            "active_count": len(active),
            "needs_review_count": len(needs_review),
            "stale_count": len(stale),
            "submitted_value": total_submitted_value,
            "active_value": total_active_value,
        },
        "submitted": submitted,
        "active": active,
        "needs_review": needs_review,
        "stale": stale,
    }


def scan_single_bid(folder_path: str, folder_name: str, now: datetime) -> Optional[Dict]:
    """Scan a single bid folder and determine its status."""
    files = []
    latest_modified = None
    has_submission = False
    has_ready = False
    has_quotes = False
    has_strategy = False
    submission_details = {}
    estimated_value = 0

    try:
        for item in os.scandir(folder_path):
            if item.name.startswith("."):
                continue

            stat = item.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            files.append({
                "name": item.name,
                "modified": mod_time,
                "size": stat.st_size,
                "is_dir": item.is_dir(),
            })

            if latest_modified is None or mod_time > latest_modified:
                latest_modified = mod_time

            name_upper = item.name.upper()

            # Check for submission confirmation
            if any(p in name_upper for p in SUBMISSION_PATTERNS):
                has_submission = True
                # Try to extract details from the file
                if item.name.endswith(".md") or item.name.endswith(".txt"):
                    details = extract_submission_details(item.path)
                    if details:
                        submission_details = details

            # Check for ready-to-submit
            if any(p in name_upper for p in READY_PATTERNS):
                has_ready = True

            # Check for quotes
            if any(p in name_upper for p in QUOTE_PATTERNS):
                has_quotes = True

            # Check for strategy
            if any(p in name_upper for p in STRATEGY_PATTERNS):
                has_strategy = True

            # Recurse one level into subdirectories
            if item.is_dir():
                for subitem in os.scandir(item.path):
                    if subitem.name.startswith("."):
                        continue
                    sub_stat = subitem.stat()
                    sub_mod = datetime.fromtimestamp(sub_stat.st_mtime)
                    files.append({
                        "name": f"{item.name}/{subitem.name}",
                        "modified": sub_mod,
                        "size": sub_stat.st_size,
                        "is_dir": subitem.is_dir(),
                    })
                    if sub_mod > latest_modified:
                        latest_modified = sub_mod

                    sub_upper = subitem.name.upper()
                    if any(p in sub_upper for p in SUBMISSION_PATTERNS):
                        has_submission = True
                        if subitem.name.endswith(".md") or subitem.name.endswith(".txt"):
                            details = extract_submission_details(subitem.path)
                            if details:
                                submission_details = details

    except PermissionError:
        return None

    if not files:
        return None

    # Determine value
    estimated_value = submission_details.get("value", 0)
    if not estimated_value:
        # Try to find value from strategy files
        estimated_value = extract_value_from_files(folder_path)

    # Calculate days since last activity
    days_since_activity = (now - latest_modified).days if latest_modified else 999

    # Determine status
    if has_submission:
        status = "submitted"
    elif days_since_activity > 14:
        status = "stale"
    elif has_ready:
        status = "active"  # ready to submit
    elif has_quotes or has_strategy:
        status = "active"  # work in progress
    elif len(files) <= 3 and not has_strategy:
        status = "needs_review"  # new, minimal work done
    else:
        status = "active"

    return {
        "id": folder_name.replace(" ", "_").upper(),
        "name": folder_name,
        "folder_path": folder_path,
        "status": status,
        "value": estimated_value,
        "file_count": len(files),
        "last_activity": latest_modified.isoformat() if latest_modified else None,
        "last_activity_relative": format_relative_time(latest_modified, now) if latest_modified else "Unknown",
        "days_since_activity": days_since_activity,
        "has_submission": has_submission,
        "has_ready": has_ready,
        "has_quotes": has_quotes,
        "has_strategy": has_strategy,
        "submission_details": submission_details if submission_details else None,
        "deadline_date": submission_details.get("deadline"),
        "confirmation_number": submission_details.get("confirmation"),
    }


def extract_submission_details(filepath: str) -> Dict:
    """Extract bid amount, confirmation number, and date from a submission file."""
    details = {}
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(10000)  # Read first 10KB to catch values deeper in file

        # Extract bid amount — handles markdown bold like **$80,436.52**
        amount_patterns = [
            r"(?:Total Bid|Bid Amount|Your Bid)[:\s]*\*{0,2}\$?([\d,]+\.?\d*)",
            r"\*\*Total Bid Amount[:\s]*\*\*\s*\*{0,2}\$?([\d,]+\.?\d*)",
            r"\*\*Bid Amount[:\s]*\*\*\s*\*{0,2}\$?([\d,]+\.?\d*)",
            r"\*\*TOTAL[:\s]*\*\*\s*\*{0,2}\$?([\d,]+\.?\d*)",
            r"TOTAL BID[:\s]*\*{0,2}\$?([\d,]+\.?\d*)",
            r"Total Bid Amount[:\s]*\*{0,2}\$?([\d,]+\.?\d*)",
            r"Contract Value.*?[\$]([\d,]+\.?\d*)",
            r"Total Revenue.*?[\$]([\d,]+\.?\d*)",
            r"Estimated Value.*?[\$]([\d,]+\.?\d*)",
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(",", "")
                try:
                    val = float(value_str)
                    # Check for K/M suffix after the number
                    after = content[match.end():match.end()+5].strip().upper()
                    if after.startswith("K"):
                        val *= 1000
                    elif after.startswith("M"):
                        val *= 1000000
                    details["value"] = val
                except ValueError:
                    pass
                break

        # Extract confirmation number — handles **0000378881** format
        conf_patterns = [
            r"[Cc]onfirmation[:\s#]*\*{0,2}(\d{7,})\*{0,2}",
            r"[Cc]onfirmation [Nn]umber[:\s]*\*{0,2}(\d{7,})\*{0,2}",
            r"Confirmation.*?(\d{10})",
        ]
        for pattern in conf_patterns:
            match = re.search(pattern, content)
            if match:
                details["confirmation"] = match.group(1)
                break

        # Extract submission date
        date_patterns = [
            r"[Ss]ubmitted?[:\s]*(?:\*\*)?(\w+ \d{1,2},? \d{4})",
            r"[Ss]ubmission [Dd]ate[:\s]*(?:\*\*)?(\w+ \d{1,2},? \d{4})",
        ]
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                details["submitted_date"] = match.group(1)
                break

        # Extract deadline
        deadline_patterns = [
            r"[Dd]ue[:\s]*(?:\*\*)?(\w+ \d{1,2},? \d{4})",
            r"[Dd]eadline[:\s]*(?:\*\*)?(\w+ \d{1,2},? \d{4})",
            r"[Cc]losing [Dd]ate[:\s]*(?:\*\*)?(\w+ \d{1,2},? \d{4})",
        ]
        for pattern in deadline_patterns:
            match = re.search(pattern, content)
            if match:
                details["deadline"] = match.group(1)
                break

        # Extract profit
        profit_patterns = [
            r"[Pp]rofit[:\s]*\$?([\d,]+\.?\d*)",
            r"[Ee]stimated [Pp]rofit[:\s]*\*?\*?\$?([\d,]+\.?\d*)",
        ]
        for pattern in profit_patterns:
            match = re.search(pattern, content)
            if match:
                profit_str = match.group(1).replace(",", "")
                try:
                    details["profit"] = float(profit_str)
                except ValueError:
                    pass
                break

    except Exception:
        pass

    return details


def extract_value_from_files(folder_path: str) -> float:
    """Try to find estimated value from strategy/analysis files in a folder."""
    for item in os.scandir(folder_path):
        if item.name.startswith(".") or not (item.name.endswith(".md") or item.name.endswith(".txt")):
            continue
        name_upper = item.name.upper()
        if any(p in name_upper for p in ["STRATEGY", "ANALYSIS", "BID_GUIDE", "CALCULATION", "PRICING"]):
            try:
                with open(item.path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(3000)
                # Look for value mentions
                patterns = [
                    r"(?:Value|Estimated Value|Contract Value|Total)[:\s]*\$?([\d,]+(?:\.?\d*))[Kk]?",
                    r"\$([\d,]+(?:\.?\d*))\s*(?:total|value|contract)",
                ]
                for pattern in patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        val = match.group(1).replace(",", "")
                        try:
                            v = float(val)
                            if v > 100:  # skip percentages
                                return v
                        except ValueError:
                            pass
            except Exception:
                pass
    return 0


def format_relative_time(dt: datetime, now: datetime) -> str:
    """Format a datetime as relative time string."""
    delta = now - dt
    if delta.days == 0:
        hours = delta.seconds // 3600
        if hours == 0:
            return "Just now"
        return f"{hours}h ago"
    elif delta.days == 1:
        return "Yesterday"
    elif delta.days < 7:
        return f"{delta.days}d ago"
    elif delta.days < 30:
        weeks = delta.days // 7
        return f"{weeks}w ago"
    else:
        return dt.strftime("%b %d")


def get_dashboard_data() -> Dict:
    """
    Get formatted dashboard data for the frontend BidsDashboard component.
    This replaces the hardcoded mock data.
    """
    scan = scan_all_bids()
    if "error" in scan:
        return scan

    # Format for BidsDashboard frontend
    focus_bid = None
    urgent_bids = []
    this_week_bids = []
    completed_bids = []

    now = datetime.now()

    # Submitted bids -> completed
    for bid in scan["submitted"]:
        completed_bids.append({
            "name": bid["name"],
            "value": bid["value"],
            "deadline": bid.get("deadline_date") or "",
            "daysLeft": 0,
            "status": "completed",
            "activity": {
                "fileCount": bid["file_count"],
                "lastEdited": bid["last_activity_relative"],
            },
            "hasQuotes": bid["has_quotes"],
            "hasSubmission": True,
            "confirmation": bid.get("confirmation_number"),
        })

    # Active bids -> urgent or this_week based on days since activity
    active_sorted = sorted(scan["active"], key=lambda b: b.get("days_since_activity", 999))
    for i, bid in enumerate(active_sorted):
        entry = {
            "name": bid["name"],
            "value": bid["value"],
            "deadline": bid.get("deadline_date") or "",
            "daysLeft": 0,  # Will be calculated if deadline exists
            "status": "active" if bid["days_since_activity"] <= 7 else "monitoring",
            "activity": {
                "fileCount": bid["file_count"],
                "lastEdited": bid["last_activity_relative"],
            },
            "hasQuotes": bid["has_quotes"],
            "hasSubmission": False,
        }

        if i == 0 and bid["days_since_activity"] <= 3:
            focus_bid = entry
            focus_bid["status"] = "urgent"
        elif bid["days_since_activity"] <= 3:
            entry["status"] = "urgent"
            urgent_bids.append(entry)
        else:
            this_week_bids.append(entry)

    return {
        "focusBid": focus_bid,
        "urgentBids": urgent_bids,
        "thisWeekBids": this_week_bids,
        "completedBids": completed_bids,
        "totalValue": scan["summary"]["active_value"],
        "completedValue": scan["summary"]["submitted_value"],
        "autoRemovedCount": scan["summary"]["stale_count"],
    }


if __name__ == "__main__":
    """Run standalone to test the scanner."""
    import json
    result = scan_all_bids()
    print(json.dumps(result, indent=2, default=str))
    print(f"\n--- SUMMARY ---")
    print(f"Submitted: {result['summary']['submitted_count']} (${result['summary']['submitted_value']:,.0f})")
    print(f"Active: {result['summary']['active_count']} (${result['summary']['active_value']:,.0f})")
    print(f"Needs Review: {result['summary']['needs_review_count']}")
    print(f"Stale: {result['summary']['stale_count']}")
