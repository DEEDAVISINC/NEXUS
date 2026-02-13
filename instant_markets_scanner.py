#!/usr/bin/env python3
"""
NEXUS — InstantMarkets Opportunity Scanner
Scans ALL categories DDI bids on across ALL states.
Uses Playwright (already installed) to handle JavaScript rendering.

Categories scanned:
  - Janitorial Services / Cleaning Supplies
  - Landscape / Snow Removal  
  - Wholesale / Retail / Electronics (reseller)
  - Manufacturer / Machinery / Tools (industrial supply)
  - Fabricated Metal / Sheet Metal / Structural Steel
  - Plumber / Electrician / Carpenter / Painter (trades)
  - Furniture / Furnishings
  - Uniforms / Dry Cleaning / Laundry
  - Healthcare / Medical
  - Transportation / Warehouse / Truck
  - Chemicals / Salt / Additives
  - Building / Construction / Demolition

Run: python3 instant_markets_scanner.py
"""

import json
import os
import re
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

# DDI capability categories on InstantMarkets
CATEGORIES = [
    {"name": "Janitorial Services", "url_key": "Janitorial_Services"},
    {"name": "Cleaning Supplies", "url_key": "Cleaning_Supplies"},
    {"name": "Landscape", "url_key": "Landscape"},
    {"name": "Snow Removal", "url_key": "Snow_Removal"},
    {"name": "Wholesale / Retail", "url_key": "Wholesale"},
    {"name": "Healthcare / Medical", "url_key": "Medical"},
    {"name": "Manufacturer / Machinery", "url_key": "Machinery"},
    {"name": "Tools", "url_key": "Tools"},
    {"name": "Fabricated Metal", "url_key": "Fabricated_Metal"},
    {"name": "Chemicals / Salt", "url_key": "Chemicals"},
    {"name": "Furniture / Furnishings", "url_key": "Furniture"},
    {"name": "Uniforms / Dry Cleaning", "url_key": "Uniforms"},
    {"name": "Transportation / Warehouse", "url_key": "Transportation"},
    {"name": "Building / Construction", "url_key": "Construction"},
    {"name": "Plumber / Electrician / Trades", "url_key": "Plumber"},
    {"name": "Gasoline / Fuel", "url_key": "Fuel"},
]

BASE_URL = "https://www.instantmarkets.com/q/{key}?ot=Bid%20Notification,Pre-Bid%20Notification&os=Active"

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "instantmarkets_opportunities.json")
REPORT_FILE = os.path.join(OUTPUT_DIR, "INSTANTMARKETS_REPORT.md")


def parse_date(date_str):
    """Try to parse a date string into a datetime object."""
    if not date_str:
        return None
    date_str = date_str.strip()
    formats = [
        "%b %d, %Y", "%B %d, %Y", "%m/%d/%Y", "%m-%d-%Y",
        "%Y-%m-%d", "%d %b %Y", "%d %B %Y",
        "%b %d %Y", "%B %d %Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def scrape_category(page, category):
    """Scrape a single category page and return bid listings."""
    url = BASE_URL.format(key=category["url_key"])
    print(f"  Scanning: {category['name']}...")

    try:
        page.goto(url, timeout=30000, wait_until="networkidle")
        page.wait_for_timeout(3000)  # extra wait for dynamic content
    except Exception as e:
        print(f"    ⚠ Page load failed: {e}")
        return []

    # Scroll to load all results
    for _ in range(5):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1500)

    # Extract bid data from the page
    bids = []
    try:
        # InstantMarkets renders bid cards — try multiple selector strategies
        # Strategy 1: Look for links that contain /view/ (individual bid pages)
        bid_links = page.query_selector_all("a[href*='/view/']")
        
        if bid_links:
            seen_titles = set()
            for link in bid_links:
                try:
                    title = link.inner_text().strip()
                    href = link.get_attribute("href") or ""
                    
                    # Skip navigation / non-bid links
                    if not title or len(title) < 5 or title in seen_titles:
                        continue
                    if any(skip in title.lower() for skip in [
                        "login", "register", "subscribe", "home", "search",
                        "next", "previous", "page", "show more", "loading"
                    ]):
                        continue
                    
                    seen_titles.add(title)
                    
                    # Try to get parent card for additional info
                    parent = link.evaluate_handle("el => el.closest('div[class]') || el.parentElement")
                    parent_text = ""
                    if parent:
                        try:
                            parent_text = parent.inner_text()
                        except:
                            pass

                    # Extract due date from parent text
                    due_date = ""
                    date_patterns = [
                        r'Due[:\s]+(\w+\s+\d{1,2},?\s+\d{4})',
                        r'Closing[:\s]+(\w+\s+\d{1,2},?\s+\d{4})',
                        r'Deadline[:\s]+(\w+\s+\d{1,2},?\s+\d{4})',
                        r'(\d{1,2}/\d{1,2}/\d{4})',
                        r'(\w{3}\s+\d{1,2},\s+\d{4})',
                    ]
                    for pat in date_patterns:
                        m = re.search(pat, parent_text, re.IGNORECASE)
                        if m:
                            due_date = m.group(1)
                            break

                    # Extract location
                    location = ""
                    loc_patterns = [
                        r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s*[A-Z]{2})',
                        r'([A-Z]{2}\s*\d{5})',
                    ]
                    for pat in loc_patterns:
                        m = re.search(pat, parent_text)
                        if m:
                            location = m.group(1)
                            break

                    # Extract agency/org
                    agency = ""
                    lines = [l.strip() for l in parent_text.split('\n') if l.strip()]
                    for line in lines:
                        if line != title and len(line) > 5 and len(line) < 120:
                            if not any(skip in line.lower() for skip in [
                                "due", "closing", "deadline", "active", "bid notification",
                                "pre-bid", "open", "view"
                            ]):
                                agency = line
                                break

                    bid = {
                        "title": title[:200],
                        "agency": agency[:200] if agency else "",
                        "location": location,
                        "due_date": due_date,
                        "url": f"https://www.instantmarkets.com{href}" if href.startswith("/") else href,
                        "category": category["name"],
                    }
                    bids.append(bid)
                except Exception:
                    continue

        # Strategy 2: If no links found, extract all visible text blocks
        if not bids:
            body_text = page.inner_text("body")
            lines = [l.strip() for l in body_text.split('\n') if l.strip()]
            
            # Filter out noise
            meaningful = [l for l in lines if len(l) > 10 and not any(
                skip in l.lower() for skip in [
                    "loading", "login", "register", "subscribe", "cookie",
                    "instantmarkets", "search", "home", "menu"
                ]
            )]
            
            if meaningful:
                bids.append({
                    "title": f"[RAW DATA - {category['name']}]",
                    "raw_lines": meaningful[:50],
                    "category": category["name"],
                    "note": "Could not parse structured data. Review raw lines."
                })

    except Exception as e:
        print(f"    ⚠ Parse error: {e}")

    print(f"    Found {len(bids)} opportunities")
    return bids


def generate_report(all_bids, scan_time):
    """Generate a markdown report of all opportunities."""
    now = datetime.now()
    
    # Sort bids: those with due dates first (soonest first), then undated
    dated = []
    undated = []
    for b in all_bids:
        if "raw_lines" in b:
            continue  # skip raw data entries for the report
        d = parse_date(b.get("due_date", ""))
        if d and d >= now:
            dated.append((d, b))
        else:
            undated.append(b)
    
    dated.sort(key=lambda x: x[0])

    lines = [
        f"# INSTANTMARKETS OPPORTUNITY SCAN",
        f"**Scanned:** {scan_time}",
        f"**Total Opportunities Found:** {len(all_bids)}",
        f"**Categories Scanned:** {len(CATEGORIES)}",
        "",
        "---",
        "",
    ]

    # URGENT — due within 7 days
    urgent = [(d, b) for d, b in dated if d <= now + timedelta(days=7)]
    if urgent:
        lines.append("## 🔴 URGENT — Due Within 7 Days\n")
        for d, b in urgent:
            lines.append(f"### {b['title']}")
            lines.append(f"- **Due:** {b['due_date']}")
            if b.get("agency"): lines.append(f"- **Agency:** {b['agency']}")
            if b.get("location"): lines.append(f"- **Location:** {b['location']}")
            lines.append(f"- **Category:** {b['category']}")
            if b.get("url"): lines.append(f"- **Link:** {b['url']}")
            lines.append("")

    # UPCOMING — due within 30 days
    upcoming = [(d, b) for d, b in dated if now + timedelta(days=7) < d <= now + timedelta(days=30)]
    if upcoming:
        lines.append("## 🟡 UPCOMING — Due Within 30 Days\n")
        for d, b in upcoming:
            lines.append(f"### {b['title']}")
            lines.append(f"- **Due:** {b['due_date']}")
            if b.get("agency"): lines.append(f"- **Agency:** {b['agency']}")
            if b.get("location"): lines.append(f"- **Location:** {b['location']}")
            lines.append(f"- **Category:** {b['category']}")
            if b.get("url"): lines.append(f"- **Link:** {b['url']}")
            lines.append("")

    # ALL OTHERS
    later = [(d, b) for d, b in dated if d > now + timedelta(days=30)]
    if later or undated:
        lines.append("## 🟢 LATER / NO DATE\n")
        for d, b in later:
            lines.append(f"- **{b['title']}** | Due: {b['due_date']} | {b['category']}")
        for b in undated:
            lines.append(f"- **{b['title']}** | {b.get('agency', '')} | {b['category']}")
        lines.append("")

    # BY CATEGORY SUMMARY
    lines.append("---")
    lines.append("## Summary by Category\n")
    cat_counts = {}
    for b in all_bids:
        cat = b.get("category", "Unknown")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- **{cat}:** {count} opportunities")

    lines.append("")
    lines.append("---")
    lines.append(f"*Nexus InstantMarkets Scanner — {scan_time}*")

    return "\n".join(lines)


def main():
    scan_time = datetime.now().strftime("%B %d, %Y %I:%M %p")
    print(f"\n{'='*60}")
    print(f"  NEXUS — InstantMarkets Opportunity Scanner")
    print(f"  {scan_time}")
    print(f"  Scanning {len(CATEGORIES)} categories...")
    print(f"{'='*60}\n")

    all_bids = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
        )
        page = context.new_page()

        for cat in CATEGORIES:
            try:
                bids = scrape_category(page, cat)
                all_bids.extend(bids)
            except Exception as e:
                print(f"  ⚠ Failed on {cat['name']}: {e}")
                continue

        browser.close()

    # Save raw JSON
    output = {
        "scan_time": scan_time,
        "categories_scanned": len(CATEGORIES),
        "total_opportunities": len(all_bids),
        "opportunities": all_bids,
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nRaw data saved: {OUTPUT_FILE}")

    # Generate markdown report
    report = generate_report(all_bids, scan_time)
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    print(f"Report saved: {REPORT_FILE}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"  SCAN COMPLETE")
    print(f"  {len(all_bids)} opportunities found across {len(CATEGORIES)} categories")
    print(f"{'='*60}\n")

    # Print first 20 as preview
    preview = [b for b in all_bids if "raw_lines" not in b][:20]
    for i, b in enumerate(preview, 1):
        print(f"  {i}. {b['title']}")
        if b.get("due_date"):
            print(f"     Due: {b['due_date']}")
        if b.get("category"):
            print(f"     Category: {b['category']}")
        print()

    if len(all_bids) > 20:
        print(f"  ... and {len(all_bids) - 20} more. See {REPORT_FILE} for full list.")


if __name__ == "__main__":
    main()
