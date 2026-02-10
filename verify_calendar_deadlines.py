#!/usr/bin/env python3
"""
CRITICAL DEADLINE VERIFICATION SCRIPT

Purpose: Cross-check calendar entries against verified source deadlines
Author: NEXUS System
Created: February 5, 2026

Usage:
    python3 verify_calendar_deadlines.py

This script prevents missed deadlines by:
1. Reading verified deadlines from CRITICAL_DEADLINE_VERIFICATION_FEB_2026.md
2. Checking all calendar .ics files for matching entries
3. Verifying DATE and TIME match exactly
4. Alerting if any mismatches found
"""

import os
import re
from datetime import datetime
from pathlib import Path

# Verified deadlines (SOURCE OF TRUTH)
VERIFIED_DEADLINES = {
    "RCOC 7732": {
        "name": "Disposable Paper Products",
        "deadline": datetime(2026, 2, 10, 14, 30),  # 2:30 PM EST
        "value": "$81,478",
        "status": "Ready to submit"
    },
    "RCOC 7842": {
        "name": "Safety Supplies",
        "deadline": datetime(2026, 2, 17, 14, 30),  # 2:30 PM EST
        "value": "$31,558",
        "status": "Ready to submit"
    },
    "RCOC 7814": {
        "name": "Pickup Trucks",
        "deadline": datetime(2026, 2, 17, 14, 30),  # 2:30 PM EST
        "value": "$640K-$800K",
        "status": "Awaiting dealer quotes"
    },
    "RCOC 7790": {
        "name": "Prefabricated Traffic Signs",
        "deadline": datetime(2026, 2, 17, 14, 30),  # 2:30 PM EST
        "value": "$30K-$50K",
        "status": "Awaiting supplier quotes"
    },
}

# Missed deadlines (for logging)
MISSED_DEADLINES = {
    "RCOC 7803": {
        "name": "Hammers, Tape, Levels",
        "deadline": datetime(2026, 2, 5, 10, 0),  # 10:00 AM EST
        "calendar_showed": datetime(2026, 2, 6, 10, 0),  # WRONG!
        "value": "$2,641",
        "status": "MISSED - Calendar showed wrong date"
    }
}


def parse_ics_datetime(dtstart_line):
    """
    Parse DTSTART from .ics file
    Format: DTSTART:20260210T143000 (Feb 10, 2026 @ 2:30 PM = 14:30)
    """
    match = re.search(r'DTSTART:(\d{8})T(\d{6})', dtstart_line)
    if match:
        date_part = match.group(1)  # 20260210
        time_part = match.group(2)  # 143000
        
        year = int(date_part[0:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        hour = int(time_part[0:2])
        minute = int(time_part[2:4])
        
        return datetime(year, month, day, hour, minute)
    return None


def check_calendar_file(filepath, bid_id, expected_deadline):
    """
    Read a calendar file and check if deadline matches expected
    """
    with open(filepath, 'r') as f:
        content = f.read()
        
    # Find DTSTART line
    for line in content.split('\n'):
        if line.startswith('DTSTART:'):
            calendar_deadline = parse_ics_datetime(line)
            if calendar_deadline:
                if calendar_deadline == expected_deadline:
                    return "✅ CORRECT", calendar_deadline
                else:
                    return "❌ WRONG", calendar_deadline
            break
    
    return "⚠️ NOT FOUND", None


def main():
    print("=" * 70)
    print("🚨 CRITICAL DEADLINE VERIFICATION")
    print("=" * 70)
    print()
    
    calendars_dir = Path("/Users/deedavis/NEXUS BACKEND/calendars")
    
    errors_found = []
    correct_count = 0
    
    # Check each verified deadline
    for bid_id, info in VERIFIED_DEADLINES.items():
        print(f"\n📋 {bid_id}: {info['name']}")
        print(f"   Expected: {info['deadline'].strftime('%A, %B %d, %Y @ %I:%M %p')} EST")
        print(f"   Value: {info['value']}")
        
        # Find all calendar files for this bid
        bid_number = bid_id.split()[1]  # Extract "7732" from "RCOC 7732"
        pattern = f"*{bid_number.lower()}*.ics"
        
        calendar_files = list(calendars_dir.glob(pattern))
        
        if not calendar_files:
            print(f"   ⚠️  WARNING: No calendar file found!")
            errors_found.append(f"{bid_id}: No calendar file")
            continue
        
        print(f"   Found {len(calendar_files)} calendar file(s)")
        
        for cal_file in calendar_files:
            status, actual_deadline = check_calendar_file(cal_file, bid_id, info['deadline'])
            
            if status == "✅ CORRECT":
                print(f"   ✅ {cal_file.name}: CORRECT")
                correct_count += 1
            elif status == "❌ WRONG":
                print(f"   ❌ {cal_file.name}: WRONG!")
                print(f"      Calendar shows: {actual_deadline.strftime('%A, %B %d, %Y @ %I:%M %p')}")
                print(f"      Should be:      {info['deadline'].strftime('%A, %B %d, %Y @ %I:%M %p')}")
                errors_found.append(f"{bid_id} ({cal_file.name}): Wrong date/time")
            else:
                print(f"   ⚠️  {cal_file.name}: Could not parse DTSTART")
                errors_found.append(f"{bid_id} ({cal_file.name}): Parse error")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    
    if errors_found:
        print(f"\n❌ ERRORS FOUND: {len(errors_found)}")
        for error in errors_found:
            print(f"   • {error}")
        print(f"\n⚠️  ACTION REQUIRED: Fix calendar entries immediately!")
        print(f"   See: CRITICAL_DEADLINE_VERIFICATION_FEB_2026.md")
    else:
        print(f"\n✅ All calendar entries verified correct!")
    
    print(f"\n✅ Correct entries: {correct_count}")
    print(f"❌ Errors found: {len(errors_found)}")
    
    # Show missed deadlines log
    if MISSED_DEADLINES:
        print("\n" + "=" * 70)
        print("❌ PREVIOUSLY MISSED DEADLINES (DO NOT FORGET)")
        print("=" * 70)
        for bid_id, info in MISSED_DEADLINES.items():
            print(f"\n   {bid_id}: {info['name']}")
            print(f"   • Actual deadline: {info['deadline'].strftime('%A, %B %d, %Y @ %I:%M %p')}")
            print(f"   • Calendar showed: {info['calendar_showed'].strftime('%A, %B %d, %Y @ %I:%M %p')}")
            print(f"   • Value lost: {info['value']}")
            print(f"   • Status: {info['status']}")
    
    print("\n" + "=" * 70)
    print("✅ Verification complete")
    print("=" * 70)
    print()
    
    return len(errors_found)


if __name__ == "__main__":
    error_count = main()
    exit(error_count)  # Exit with error count (0 = success)
