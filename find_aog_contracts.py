#!/usr/bin/env python3
"""CLI wrapper — runs the same scan as NEXUS scheduler (mine_aog_sam)."""

import argparse
import json
import sys

from mine_aog_sam import run_aog_sam_scan


def main() -> None:
    p = argparse.ArgumentParser(description="AOG SAM scan (same as automated NEXUS mining)")
    p.add_argument("--days", type=int, default=90)
    p.add_argument("--json", action="store_true", help="Print full JSON to stdout")
    args = p.parse_args()

    r = run_aog_sam_scan(days_back=args.days)
    if args.json:
        print(json.dumps(r, indent=2))
        sys.exit(0 if r.get("ok") or r.get("skipped") else 1)

    if r.get("skipped"):
        print("AOG scan skipped (SAM key not available in this process).", file=sys.stderr)
        sys.exit(1)

    print(f"Posted {r.get('posted_from')} – {r.get('posted_to')} | {r.get('count')} notices\n")
    for o in r.get("opportunities") or []:
        print(f"{o.get('lane'):<16} {o.get('postedDate'):<12} {o.get('solicitationNumber','')[:22]:<22} {o.get('title','')[:100]}")
        print(f"                 {o.get('url')}")
    print(f"\nCache: aog_sam_cache.json")


if __name__ == "__main__":
    main()
