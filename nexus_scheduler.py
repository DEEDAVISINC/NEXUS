#!/usr/bin/env python3
"""
NEXUS Automation Scheduler
Runs automated tasks on schedule — no manual intervention needed.

Tasks:
1. Email monitoring — checks inbox for new solicitations (every 30 min)
2. Federal forecasts mining — pulls SAM.gov opportunities (every 6 hours)
3. Folder scan — updates workflow queues from BIDS:RESOURCES/ (every 15 min)
4. Stale bid detection — flags bids with no activity near deadline (hourly)

Usage:
  python3 nexus_scheduler.py            # Run all tasks once
  python3 nexus_scheduler.py --loop     # Run continuously on schedule
  python3 nexus_scheduler.py --email    # Run email check only
  python3 nexus_scheduler.py --mine     # Run federal mining only
  python3 nexus_scheduler.py --portals  # Run vendor portal mining only
  python3 nexus_scheduler.py --scan     # Run folder scan only

For cron (recommended):
  # Every 30 minutes — email + folder scan
  */30 * * * * cd /Users/deedavis/NEXUS\\ BACKEND && python3 nexus_scheduler.py --email --scan >> logs/scheduler.log 2>&1

  # Every 6 hours — federal forecasts mining
  0 */6 * * * cd /Users/deedavis/NEXUS\\ BACKEND && python3 nexus_scheduler.py --mine >> logs/scheduler.log 2>&1
"""

import os
import sys
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Set up logging
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "scheduler.log")),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("nexus_scheduler")


def run_email_monitor():
    """Check inbox for new solicitation emails and create Airtable records."""
    log.info("--- EMAIL MONITOR ---")
    try:
        from nexus_email_automation import main as email_main
        email_main()
        log.info("Email monitor completed successfully")
        return True
    except Exception as e:
        log.error(f"Email monitor failed: {e}")
        return False


def run_federal_mining():
    """
    Mine SAM.gov and federal forecast sources for opportunities.
    FILTERS: EDWOSB, WOSB, Small Business ONLY.
    Excludes SDVOSB, VOSB, HUBZone, 8(a) — we don't qualify.
    """
    log.info("--- FEDERAL FORECASTS MINING ---")
    log.info("Filtering for: EDWOSB, WOSB, Small Business")
    log.info("Excluding: SDVOSB, VOSB, HUBZone, 8(a)")

    try:
        from mine_real_federal_forecasts import RealFederalForecastsMiner
        miner = RealFederalForecastsMiner()

        # Mine SAM.gov pre-solicitations (already filtered for EDWOSB+WOSB)
        log.info("Mining SAM.gov pre-solicitations (EDWOSB/WOSB filtered)...")
        sam_results = miner.mine_sam_presolicitations()
        log.info(f"SAM.gov pre-solic: found {len(sam_results)} EDWOSB/WOSB opportunities")

        # Mine SAM.gov forecasts (already filtered for EDWOSB+WOSB)
        log.info("Mining SAM.gov forecasted opportunities (EDWOSB/WOSB filtered)...")
        try:
            sam_forecasts = miner.mine_sam_forecasts()
            log.info(f"SAM.gov forecasts: found {len(sam_forecasts)} EDWOSB/WOSB forecasts")
        except Exception as e:
            log.warning(f"SAM.gov forecasts skipped: {e}")

        # Also run the main SAM API search with proper filters
        log.info("Running SAM.gov API search (EDWOSB/WOSB/SB filtered)...")
        try:
            from nexus_backend import handle_sam_api_search
            sam_api_result = handle_sam_api_search()
            imported = sam_api_result.get('imported', 0)
            log.info(f"SAM.gov API: imported {imported} eligible opportunities")
        except Exception as e:
            log.warning(f"SAM.gov API search skipped: {e}")

        # Mine DHS forecasts
        log.info("Mining DHS APFS forecasts...")
        try:
            dhs_results = miner.mine_dhs_apfs()
            log.info(f"DHS APFS: found {len(dhs_results)} forecasts")
        except Exception as e:
            log.warning(f"DHS APFS mining skipped: {e}")

        # Run the dedicated EDWOSB/WOSB-only miner (built specifically for Dee Davis Inc)
        log.info("Running dedicated EDWOSB/WOSB-only miner...")
        try:
            from auto_mine_edwosb_wosb_only import EDWOSBWOSBMiner
            edwosb_miner = EDWOSBWOSBMiner()
            edwosb_result = edwosb_miner.mine_edwosb_wosb_opportunities(days_back=14)
            new_opps = edwosb_result.get('new_opportunities_added', 0)
            log.info(f"EDWOSB/WOSB miner: added {new_opps} new eligible opportunities")
        except Exception as e:
            log.warning(f"EDWOSB/WOSB miner skipped: {e}")

        log.info("Federal mining completed successfully")
        return True
    except Exception as e:
        log.error(f"Federal mining failed: {e}")
        return False


def run_folder_scan():
    """Scan BIDS:RESOURCES/ and update workflow status."""
    log.info("--- FOLDER SCAN ---")
    try:
        from bid_folder_scanner import scan_all_bids
        result = scan_all_bids()

        if "error" in result:
            log.error(f"Folder scan error: {result['error']}")
            return False

        summary = result["summary"]
        log.info(
            f"Scan complete: {summary['submitted_count']} submitted "
            f"(${summary['submitted_value']:,.0f}), "
            f"{summary['active_count']} active, "
            f"{summary['needs_review_count']} needs review, "
            f"{summary['stale_count']} stale"
        )

        # Save scan results for quick API access
        cache_path = os.path.join(os.path.dirname(__file__), "scan_cache.json")
        with open(cache_path, "w") as f:
            json.dump(result, f, default=str)
        log.info(f"Scan cache saved to {cache_path}")

        # Log stale bids as warnings
        for bid in result.get("stale", []):
            log.warning(
                f"STALE BID: {bid['name']} — "
                f"no activity in {bid['days_since_activity']}d"
            )

        return True
    except Exception as e:
        log.error(f"Folder scan failed: {e}")
        return False


def run_stale_detection():
    """Detect bids that need attention based on activity and deadlines."""
    log.info("--- STALE BID DETECTION ---")
    try:
        from bid_folder_scanner import scan_all_bids
        result = scan_all_bids()

        if "error" in result:
            return False

        alerts = []
        now = datetime.now()

        for bid in result.get("active", []):
            # Flag bids with no activity in 7+ days
            if bid["days_since_activity"] >= 7:
                alerts.append({
                    "type": "stale",
                    "bid": bid["name"],
                    "days_inactive": bid["days_since_activity"],
                    "message": f"{bid['name']} has had no activity in {bid['days_since_activity']} days",
                })

        for bid in result.get("needs_review", []):
            # Flag unreviewed bids with minimal files
            if bid["file_count"] <= 3:
                alerts.append({
                    "type": "unreviewed",
                    "bid": bid["name"],
                    "file_count": bid["file_count"],
                    "message": f"{bid['name']} needs review — only {bid['file_count']} files",
                })

        if alerts:
            log.warning(f"Found {len(alerts)} bids needing attention:")
            for alert in alerts:
                log.warning(f"  [{alert['type'].upper()}] {alert['message']}")
        else:
            log.info("All bids look active and healthy")

        # Save alerts for dashboard
        alerts_path = os.path.join(os.path.dirname(__file__), "bid_alerts.json")
        with open(alerts_path, "w") as f:
            json.dump({"alerts": alerts, "checked_at": now.isoformat()}, f, default=str)

        return True
    except Exception as e:
        log.error(f"Stale detection failed: {e}")
        return False


def run_forecast_mining():
    """
    Mine agency forecast pages for UPCOMING opportunities.
    Scrapes 6 agency forecast sites + SAM.gov pre-solicitations.
    AI scores each forecast for fit with Dee Davis Inc.
    """
    log.info("--- AGENCY FORECAST MINING ---")
    log.info("Sources: NASA, GSA, DHS, USAID, Commerce, Treasury + SAM.gov")
    try:
        from federal_forecasts_system import FederalForecastsMiner
        miner = FederalForecastsMiner()
        result = miner.mine_all_forecasts()

        log.info(
            f"Forecast mining complete: {result.get('total_mined', 0)} forecasts found, "
            f"{result.get('stored', 0)} new stored, "
            f"{result.get('high_fit_matches', 0)} high-fit matches"
        )
        return True
    except Exception as e:
        log.error(f"Forecast mining failed: {e}")
        return False


def run_portal_mining():
    """
    Mine ALL vendor portals for new opportunities.
    Scrapes portal websites and uses AI to extract opportunities.
    """
    log.info("--- VENDOR PORTAL MINING ---")
    try:
        from nexus_backend import GPSSOpportunityMiningAgent
        agent = GPSSOpportunityMiningAgent()
        result = agent.auto_mine_all_portals()

        if result.get('success'):
            log.info(
                f"Portal mining complete: {result['portals_checked']} portals checked, "
                f"{result['total_opportunities_found']} opportunities found"
            )
            if result.get('errors'):
                for err in result['errors'][:5]:
                    log.warning(f"  Mining error: {err}")
        else:
            log.error(f"Portal mining failed: {result.get('error')}")
            return False

        return True
    except Exception as e:
        log.error(f"Portal mining failed: {e}")
        return False


def run_quote_followups():
    """
    Check for outstanding quote requests and send follow-ups.
    Day 3: Flag for follow-up
    Day 5: Auto-send reminder email
    Day 7: Urgent flag + call script generated
    """
    log.info("--- QUOTE FOLLOW-UP CHECK ---")
    try:
        from supplier_quote_workflow import check_and_send_followups
        result = check_and_send_followups()

        checked = result.get('checked', 0)
        sent = result.get('sent', 0)
        log.info(f"Quote follow-ups: {checked} checked, {sent} reminders sent")
        return True
    except Exception as e:
        log.error(f"Quote follow-up check failed: {e}")
        return False


def run_all():
    """Run all scheduled tasks."""
    log.info("=" * 60)
    log.info("NEXUS SCHEDULER — Running all tasks")
    log.info("=" * 60)

    results = {}
    results["folder_scan"] = run_folder_scan()
    results["stale_detection"] = run_stale_detection()
    results["email_monitor"] = run_email_monitor()
    results["portal_mining"] = run_portal_mining()
    results["forecast_mining"] = run_forecast_mining()
    results["quote_followups"] = run_quote_followups()

    log.info("=" * 60)
    log.info("SCHEDULER COMPLETE")
    for task, success in results.items():
        status = "OK" if success else "FAILED"
        log.info(f"  {task}: {status}")
    log.info("=" * 60)

    return results


def run_loop():
    """Run continuously on schedule."""
    log.info("NEXUS SCHEDULER — Starting continuous loop")
    log.info("  Email check: every 30 minutes")
    log.info("  Folder scan: every 15 minutes")
    log.info("  Federal mining (SAM.gov): every 6 hours")
    log.info("  Portal mining: every 4 hours")
    log.info("  Agency forecasts (NASA/GSA/DHS/USAID/Commerce/Treasury): daily")
    log.info("  Quote follow-ups: every 4 hours")
    log.info("  Press Ctrl+C to stop")

    last_email = datetime.min
    last_scan = datetime.min
    last_mine = datetime.min
    last_portal = datetime.min
    last_forecast = datetime.min
    last_followup = datetime.min

    EMAIL_INTERVAL = timedelta(minutes=30)
    SCAN_INTERVAL = timedelta(minutes=15)
    MINE_INTERVAL = timedelta(hours=6)
    PORTAL_INTERVAL = timedelta(hours=4)
    FORECAST_INTERVAL = timedelta(hours=24)  # Daily — forecasts don't change fast
    FOLLOWUP_INTERVAL = timedelta(hours=4)   # Check for outstanding quotes

    while True:
        now = datetime.now()

        if now - last_scan >= SCAN_INTERVAL:
            run_folder_scan()
            run_stale_detection()
            last_scan = now

        if now - last_email >= EMAIL_INTERVAL:
            run_email_monitor()
            last_email = now

        if now - last_mine >= MINE_INTERVAL:
            run_federal_mining()
            last_mine = now

        if now - last_portal >= PORTAL_INTERVAL:
            run_portal_mining()
            last_portal = now

        if now - last_forecast >= FORECAST_INTERVAL:
            run_forecast_mining()
            last_forecast = now

        if now - last_followup >= FOLLOWUP_INTERVAL:
            run_quote_followups()
            last_followup = now

        # Sleep 60 seconds between checks
        time.sleep(60)


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--loop" in args:
        try:
            run_loop()
        except KeyboardInterrupt:
            log.info("Scheduler stopped by user")
    elif "--email" in args:
        run_email_monitor()
    elif "--mine" in args:
        run_federal_mining()
    elif "--portals" in args:
        run_portal_mining()
    elif "--forecasts" in args:
        run_forecast_mining()
    elif "--followups" in args:
        run_quote_followups()
    elif "--scan" in args:
        run_folder_scan()
        run_stale_detection()
    elif not args:
        run_all()
    else:
        print(__doc__)
