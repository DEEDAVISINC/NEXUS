#!/usr/bin/env python3
"""
NEXUS Automation Scheduler
Runs automated tasks on schedule — no manual intervention needed.

RADAR — Revenue Acquisition Discovery And Reconnaissance
  The --radar flag runs the FULL DDI opportunity mining sweep:
    Government (SAM.gov EDWOSB/WOSB/SB) + Healthcare/MCO + Sources Sought +
    AOG/Freight + Federal Forecasts + Public Portals + State/Local + AI Scoring.
  This is DDI's unified mining system. One command, every channel.

GBIS grant mining audit (built vs scheduled):
- POST /gbis/mine-all → run_gbis_mine_all_pipeline() — SCHEDULED daily 7:00 AM ET (full pipeline).
- Sub-APIs (POST /gbis/mine-source, research-lane seeds, mine-federal) are subsets of
  community_miner.run_full_pipeline(); no separate schedule needed.
- POST /gbis/mine-small-grants/seed* → covered by mine-all (seed_all_sources).
- Weekly free-only seed removed from loop; use run_gbis_small_grants_seed() manually if needed.

GPSS forecasting: run_forecast_mining() calls FederalForecastsMiner.mine_all_forecasts() — same
orchestrator as POST /gpss/forecasting/mine (handle_mine_federal_forecasts). Tier-specific
API routes (mine-edwosb, mine-renewals) are subsets of that default tier list.

Tasks:
1. Email monitoring — checks inbox for new solicitations (every 30 min)
2. Federal forecasts mining — pulls SAM.gov opportunities (every 6 hours); includes **AOG / 488190** scan → `aog_sam_cache.json`
3. Folder scan — updates workflow queues from BIDS:RESOURCES/ (every 15 min)
4. Stale bid detection — flags bids with no activity near deadline (hourly)
5. Healthcare/MCO scan — state Medicaid + hospital + MCO portals (every 6 hours)

Usage:
  python3 nexus_scheduler.py            # Run all tasks once
  python3 nexus_scheduler.py --loop     # Run continuously on schedule
  python3 nexus_scheduler.py --radar    # Run FULL RADAR sweep (all mining channels)
  python3 nexus_scheduler.py --email    # Run email check only
  python3 nexus_scheduler.py --mine     # Run federal mining only
  python3 nexus_scheduler.py --portals  # Run vendor portal mining only
  python3 nexus_scheduler.py --public   # Run public portal scan (nationwide, all tiers)
  python3 nexus_scheduler.py --public-tier1  # Run public portal scan (tier 1 only: SAM, BidNet, MITN, TX)
  python3 nexus_scheduler.py --healthcare    # Healthcare & MCO scanner (State Medicaid, hospitals, MCO portals)
  python3 nexus_scheduler.py --scan     # Run folder scan only
  python3 nexus_scheduler.py --gbis     # Run GBIS mine-all (full grant pipeline, same as POST /gbis/mine-all)
  python3 nexus_scheduler.py --primes   # Run prime contractor mining (find subs-needed primes)
  python3 nexus_scheduler.py --vertex   # Run all VERTEX daily financial jobs (6 AM suite)
  python3 nexus_scheduler.py --vertex-collect  # Run AR collection sweep + TODAY_AGENDA update
  python3 nexus_scheduler.py --vertex-advisor  # Run AI financial advisor + briefing update
  python3 nexus_scheduler.py --jeta-market     # JETA: sync IATA jet fuel $/bbl → Airtable JETA_MarketData
  python3 nexus_scheduler.py --aog           # AOG / 488190 SAM scan only → aog_sam_cache.json (also runs inside --mine)
  python3 nexus_scheduler.py --compile-radar # Rebuild RADAR_RESULTS.md from caches (no full sweep)
  python3 nexus_scheduler.py --digital-nav   # Digital navigation SAM scan → digital_nav_sam_cache.json
  python3 nexus_scheduler.py --sync-cos                    # Harvest SAM.gov COs → GPSS CONTACTS (manual only; not in --mine)
  python3 nexus_scheduler.py --sync-cos --limit-naics 5    # Quick targeted sweep (top 5 NAICS, low bandwidth)
  python3 nexus_scheduler.py --sync-cos --days 7           # Custom look-back window

For cron (optional — launchd --loop is primary on this Mac):
  # RADAR full sweep — daily at 6:30 AM ET (also wired in run_loop with catch-up windows)
  30 6 * * * cd /Users/deedavis/NEXUS\\ BACKEND && python3 nexus_scheduler.py --radar >> logs/radar.log 2>&1

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

        # AOG / NAICS 488190 — Freight 1st Direct lane (SAM keyword + NAICS scan → aog_sam_cache.json)
        log.info("Running AOG / 488190 SAM scan (mine_aog_sam)...")
        try:
            from mine_aog_sam import run_aog_sam_scan

            aog_result = run_aog_sam_scan(days_back=90)
            if aog_result.get("skipped"):
                log.info("AOG SAM scan skipped: %s", aog_result.get("reason", "unknown"))
            else:
                log.info(
                    "AOG SAM scan: %s notices (%s AOG_COURIER, %s TRIAGE_488190) → aog_sam_cache.json",
                    aog_result.get("count", 0),
                    aog_result.get("aog_courier_count", 0),
                    aog_result.get("triage_488190_count", 0),
                )
        except Exception as e:
            log.warning(f"AOG SAM scan failed: {e}")

        # Digital navigation / benefits enrollment — NAICS 624190 lane → digital_nav_sam_cache.json
        log.info("Running digital navigation SAM scan (mine_digital_navigation_sam)...")
        try:
            from mine_digital_navigation_sam import run_digital_nav_scan

            nav_result = run_digital_nav_scan(days_back=90)
            if nav_result.get("skipped"):
                log.info("Digital nav SAM scan skipped: %s", nav_result.get("reason", "unknown"))
            else:
                log.info(
                    "Digital nav SAM scan: %s notices → digital_nav_sam_cache.json",
                    nav_result.get("count", 0),
                )
        except Exception as e:
            log.warning(f"Digital nav SAM scan failed: {e}")

        # NOTE: SAM.gov CO contact sync (sam_co_contact_sync) is intentionally
        # NOT called from --mine. It's bandwidth-heavy (sweeps ~50 NAICS codes
        # against api.sam.gov). Run it explicitly when desired:
        #   python3 nexus_scheduler.py --sync-cos --limit-naics 5

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
    """Detect bids that need attention based on activity and deadlines.
    Uses a persistent cache to avoid re-alerting on the same stale bids."""
    log.info("--- STALE BID DETECTION ---")
    try:
        from bid_folder_scanner import scan_all_bids
        result = scan_all_bids()

        if "error" in result:
            return False

        # Load previously-flagged stale bids to avoid repeat alerts
        stale_cache_path = os.path.join(os.path.dirname(__file__), "stale_alert_cache.json")
        try:
            with open(stale_cache_path, 'r') as f:
                stale_cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            stale_cache = {}

        # Prune cache entries older than 30 days
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        stale_cache = {k: v for k, v in stale_cache.items() if v.get('first_flagged', '') > cutoff}

        alerts = []
        new_alerts = []
        now = datetime.now()

        for bid in result.get("active", []):
            if bid["days_since_activity"] >= 7:
                alert = {
                    "type": "stale",
                    "bid": bid["name"],
                    "days_inactive": bid["days_since_activity"],
                    "message": f"{bid['name']} has had no activity in {bid['days_since_activity']} days",
                }
                alerts.append(alert)
                if bid["name"] not in stale_cache:
                    new_alerts.append(alert)
                    stale_cache[bid["name"]] = {
                        "first_flagged": now.isoformat(),
                        "days_inactive": bid["days_since_activity"],
                    }

        for bid in result.get("needs_review", []):
            if bid["file_count"] <= 3:
                alert = {
                    "type": "unreviewed",
                    "bid": bid["name"],
                    "file_count": bid["file_count"],
                    "message": f"{bid['name']} needs review — only {bid['file_count']} files",
                }
                alerts.append(alert)
                key = f"review_{bid['name']}"
                if key not in stale_cache:
                    new_alerts.append(alert)
                    stale_cache[key] = {
                        "first_flagged": now.isoformat(),
                        "file_count": bid["file_count"],
                    }

        if new_alerts:
            log.warning(f"Found {len(new_alerts)} NEW bids needing attention (skipped {len(alerts) - len(new_alerts)} already-flagged):")
            for alert in new_alerts:
                log.warning(f"  [{alert['type'].upper()}] {alert['message']}")
        else:
            log.info(f"No new stale bids ({len(alerts)} total stale, all previously flagged)")

        # Save stale cache
        with open(stale_cache_path, 'w') as f:
            json.dump(stale_cache, f, indent=2)

        # Save alerts for dashboard (all alerts, not just new)
        alerts_path = os.path.join(os.path.dirname(__file__), "bid_alerts.json")
        with open(alerts_path, "w") as f:
            json.dump({
                "alerts": alerts,
                "new_alerts": len(new_alerts),
                "checked_at": now.isoformat(),
            }, f, default=str)

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


def run_ai_scoring_and_alerts():
    """
    AI OPPORTUNITY SCORER + EMAIL ALERTS
    1. Pull all "New - API" and "New - Presolicitation/Sources Sought" opps from Airtable
    2. Score each against Dee Davis Inc. profile using AI
    3. Tag with BID NOW / WORTH A LOOK / SKIP
    4. Email Dee immediately for BID NOW opportunities
    5. Update Airtable status with score and recommendation
    """
    log.info("--- AI OPPORTUNITY SCORING & ALERTS ---")
    try:
        from nexus_opportunity_intelligence import OpportunityIntelligenceEngine
        engine = OpportunityIntelligenceEngine()
        result = engine.score_and_alert()
        
        bid_now = result.get('bid_now', 0)
        worth_look = result.get('worth_a_look', 0)
        skipped = result.get('skip', 0)
        emails_sent = result.get('emails_sent', 0)
        
        log.info(f"Scored {bid_now + worth_look + skipped} opportunities:")
        log.info(f"  🔴 BID NOW: {bid_now}")
        log.info(f"  🟡 WORTH A LOOK: {worth_look}")
        log.info(f"  ⚪ SKIP: {skipped}")
        if emails_sent > 0:
            log.info(f"  📧 Alert emails sent: {emails_sent}")
        
        return True
    except Exception as e:
        log.error(f"AI scoring/alerts failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_state_local_mining():
    """Mine Michigan state/local portals — MITN, Detroit, Oakland County."""
    log.info("--- STATE & LOCAL MINING ---")
    try:
        from nexus_opportunity_intelligence import MichiganLocalMiner
        miner = MichiganLocalMiner()
        result = miner.mine_all()
        
        log.info(f"State/local mining: {result.get('total_found', 0)} found, {result.get('imported', 0)} imported")
        return True
    except Exception as e:
        log.error(f"State/local mining failed: {e}")
        return False


def run_gbis_small_grants_seed():
    """
    Legacy: seed only free small-business sources (subset of mine-all).
    Prefer run_gbis_mine_all_pipeline() for autonomous discovery.
    """
    log.info("--- GBIS SMALL GRANTS SEED (free-only) ---")
    try:
        from gbis_small_grants_miner import GBISSmallGrantsMiner
        miner = GBISSmallGrantsMiner()
        miner.seed_free_sources_only()
        log.info("GBIS small grants seed (free sources) completed")
        return True
    except Exception as e:
        log.error(f"GBIS small grants seed failed: {e}")
        return False


def run_gbis_mine_all_pipeline():
    """
    Full GBIS autonomous grant discovery — mirrors POST /gbis/mine-all (api_server.gbis_mine_all):
      - GBISCommunityHealthMiner.run_full_pipeline() (Michigan foundations + CWC expansion + veteran seeds + Grants.gov)
      - GBISSmallGrantsMiner.seed_all_sources() (all small-business grant rows; skips duplicates)
    Safe to run daily; does not replace GPSS/federal miners.
    """
    log.info("--- GBIS MINE-ALL (full pipeline) ---")
    try:
        from gbis_community_health_miner import GBISCommunityHealthMiner
        from gbis_small_grants_miner import GBISSmallGrantsMiner

        community_miner = GBISCommunityHealthMiner()
        small_miner = GBISSmallGrantsMiner()

        community_result = community_miner.run_full_pipeline()
        small_result = small_miner.seed_all_sources()

        mich = community_result["michigan_foundations"]
        cwc = community_result.get("cwc_expansion", {"imported": 0, "skipped": 0})
        vets = community_result["veteran_sources"]
        fed = community_result["grants_gov"]
        sm = small_result

        total_new = mich["imported"] + cwc["imported"] + vets["imported"] + fed["imported"] + sm["imported"]
        log.info(
            f"GBIS mine-all complete: {total_new} new rows "
            f"(foundations +{mich['imported']}, cwc_expansion +{cwc['imported']}, "
            f"veteran +{vets['imported']}, grants.gov +{fed['imported']}, small business +{sm['imported']})"
        )
        return True
    except Exception as e:
        log.error(f"GBIS mine-all failed: {e}")
        import traceback

        traceback.print_exc()
        return False


GBIS_DAILY_RUN_STATE = os.path.join(LOG_DIR, "gbis_last_daily_run.json")
RADAR_DAILY_RUN_STATE = os.path.join(LOG_DIR, "radar_last_daily_run.json")
RADAR_LOG_FILE = os.path.join(LOG_DIR, "radar.log")


def _radar_now_et():
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo("America/Detroit"))
    except Exception:
        return datetime.now()


def _radar_completed_today_et() -> bool:
    today = _radar_now_et().strftime("%Y-%m-%d")
    try:
        if os.path.exists(RADAR_DAILY_RUN_STATE):
            with open(RADAR_DAILY_RUN_STATE, "r") as f:
                data = json.load(f)
            if data.get("date") == today and data.get("compile_ok"):
                return True
    except Exception:
        pass
    return False


def _should_trigger_radar_daily_et():
    """
    Run full RADAR once per calendar day (America/Detroit).
    Primary: 6:30–6:44 AM. Catch-up if Mac was asleep: 7:00–7:14, 12:00–12:14, 6:00–6:14 PM.
    """
    if _radar_completed_today_et():
        return False
    now = _radar_now_et()
    windows = (
        (6, 30, 45),
        (7, 0, 15),
        (12, 0, 15),
        (18, 0, 15),
    )
    for hour, minute_start, minute_end in windows:
        if now.hour == hour and minute_start <= now.minute < minute_end:
            return True
    return False


def _mark_radar_daily_run_et(*, compile_ok: bool = True):
    now = _radar_now_et()
    try:
        with open(RADAR_DAILY_RUN_STATE, "w") as f:
            json.dump(
                {
                    "date": now.strftime("%Y-%m-%d"),
                    "iso": now.isoformat(),
                    "compile_ok": compile_ok,
                },
                f,
                indent=2,
            )
    except Exception as e:
        log.warning(f"Could not write RADAR daily run state: {e}")


def run_radar_daily_scheduled():
    """Full RADAR sweep + compile; append to logs/radar.log."""
    log.info("--- RADAR DAILY (scheduled) ---")
    try:
        with open(RADAR_LOG_FILE, "a", encoding="utf-8") as rf:
            rf.write(f"\n{'=' * 60}\nRADAR daily start {datetime.now().isoformat()}\n")
    except Exception:
        pass
    results = run_radar()
    compile_ok = bool(results.get("compile_radar"))
    try:
        with open(RADAR_LOG_FILE, "a", encoding="utf-8") as rf:
            rf.write(
                f"RADAR daily end {datetime.now().isoformat()} "
                f"compile_ok={compile_ok} results={results}\n"
            )
    except Exception:
        pass
    return compile_ok


def _should_run_gbis_daily_7am_et():
    """Once per calendar day, only in the 7:00–7:14 AM America/Detroit window."""
    try:
        from zoneinfo import ZoneInfo

        now = datetime.now(ZoneInfo("America/Detroit"))
    except Exception:
        now = datetime.now()
    if now.hour != 7 or now.minute >= 15:
        return False
    today = now.strftime("%Y-%m-%d")
    try:
        if os.path.exists(GBIS_DAILY_RUN_STATE):
            with open(GBIS_DAILY_RUN_STATE, "r") as f:
                data = json.load(f)
            if data.get("date") == today:
                return False
    except Exception:
        pass
    return True


def _mark_gbis_daily_run_et():
    try:
        from zoneinfo import ZoneInfo

        now = datetime.now(ZoneInfo("America/Detroit"))
    except Exception:
        now = datetime.now()
    try:
        with open(GBIS_DAILY_RUN_STATE, "w") as f:
            json.dump({"date": now.strftime("%Y-%m-%d"), "iso": now.isoformat()}, f, indent=2)
    except Exception as e:
        log.warning(f"Could not write GBIS daily run state: {e}")


def run_prime_contractor_mining():
    """
    Mine USASpending.gov for prime contractors with $10M+ federal contracts
    who are LEGALLY REQUIRED to meet diversity subcontracting goals.
    These primes NEED EDWOSB/WOSB subs like DDI.
    """
    log.info("--- PRIME CONTRACTOR MINING (SUB OPPORTUNITIES) ---")
    log.info("Finding primes with $10M+ contracts who need EDWOSB subs...")
    try:
        from nexus_backend import handle_ddcss_mine_prime_contractors
        results = handle_ddcss_mine_prime_contractors(
            min_contract_value=10000000,
            limit=50
        )

        if results.get('success'):
            log.info(
                f"Prime mining complete: {results.get('total_found', 0)} primes analyzed, "
                f"{results.get('prospects_created', 0)} new prospects created, "
                f"{results.get('duplicates_skipped', 0)} duplicates skipped"
            )
        else:
            log.error(f"Prime mining failed: {results.get('error', 'Unknown')}")
            return False

        return True
    except Exception as e:
        log.error(f"Prime contractor mining failed: {e}")
        return False


def run_public_portal_scan(tier1_only=False):
    """
    Scan ALL public procurement portals nationwide for DDI opportunities.
    No login required — scrapes publicly accessible solicitation pages.
    Sources: SAM.gov, BidNet Direct, MITN, Texas ESBD, Virginia, SC, IN, LA, CT
    """
    log.info("--- PUBLIC PORTAL SCANNER (NATIONWIDE) ---")
    log.info(f"Mode: {'Tier 1 Only' if tier1_only else 'Full Scan (All Public Portals)'}")
    try:
        from public_portal_scanner import run_scan
        result = run_scan(tier1_only=tier1_only)
        
        total = result.get('total_found', 0)
        log.info(f"Public portal scan complete: {total} DDI-relevant opportunities found")
        log.info(f"Report saved to DAILY_OPPORTUNITIES_REPORT.md")
        return True
    except Exception as e:
        log.error(f"Public portal scan failed: {e}")
        return False


def run_healthcare_mco_scan(tier1_only=False):
    """
    Scan Healthcare & MCO portals for NEMT, transportation, courier opportunities.
    Sources: State Medicaid portals, Hospital RFP sites, MCO vendor portals (manual checklist).
    THIS IS THE COMMERCIAL/ENTERPRISE HEALTHCARE SEARCH.
    """
    log.info("--- HEALTHCARE & MCO SCANNER ---")
    log.info(f"Mode: {'Tier 1 (State Medicaid) Only' if tier1_only else 'Full Scan'}")
    try:
        from healthcare_mco_scanner import run_scan
        result = run_scan(tier1_only=tier1_only)
        
        total = result.get('total_found', 0)
        log.info(f"Healthcare scan complete: {total} opportunities found")
        log.info(f"Report saved to HEALTHCARE_OPPORTUNITIES_REPORT.md")
        log.info(f"MCO checklist saved to MCO_PORTAL_DAILY_CHECKLIST.md")
        return True
    except Exception as e:
        log.error(f"Healthcare/MCO scan failed: {e}")
        return False


def run_jeta_market_price_sync():
    """
    JETA — weekly IATA Jet Fuel Price Monitor sync.
    Calls GET /api/jeta/market/price?refresh=1 (stores USD/bbl in Airtable JETA_MarketData).
    """
    log.info("--- JETA IATA MARKET PRICE SYNC ---")
    try:
        import requests

        base_url = os.environ.get("NEXUS_API_URL", "http://127.0.0.1:5000")
        url = f"{base_url.rstrip('/')}/api/jeta/market/price"
        resp = requests.get(url, params={"refresh": "1"}, timeout=120)
        data = resp.json()
        if resp.status_code >= 400 or not data.get("success"):
            log.error("JETA market price sync failed: %s %s", resp.status_code, data.get("error"))
            return False
        latest = data.get("latest") or {}
        log.info(
            "JETA market price: $%s/bbl (%s) synced=%s",
            latest.get("pricePerBarrel"),
            latest.get("priceDate"),
            data.get("synced"),
        )
        return True
    except Exception as e:
        log.error("JETA market price sync failed: %s", e)
        return False


# ============================================================================
# VERTEX FINANCIAL JOBS (Phases 10, 11, 12, 13)
# ============================================================================

def run_vertex_recurring_invoices():
    """Phase 3: Generate all recurring invoices that are due today."""
    log.info("--- VERTEX RECURRING INVOICES ---")
    try:
        import requests
        base_url = os.environ.get("NEXUS_API_URL", "http://localhost:5000")
        resp = requests.post(f"{base_url}/vertex/invoices/recurring/run-all", timeout=60)
        result = resp.json()
        generated = result.get("generated", 0)
        errors    = result.get("errors", 0)
        log.info(f"Recurring invoices: {generated} generated, {errors} errors")
        return errors == 0
    except Exception as e:
        log.error(f"Recurring invoice run failed: {e}")
        return False


def run_vertex_collection_sweep():
    """
    Phase 11: Auto-Collection Engine.
    Query all overdue invoices, generate tiered reminders, write to TODAY_AGENDA.md.
    60+ days escalations flagged for Dee to call directly.
    """
    log.info("--- VERTEX COLLECTION SWEEP ---")
    try:
        from nexus_backend import AirtableClient
        from api_server import VI
        at    = AirtableClient()
        today = datetime.now().date()

        ps_field = VI["payment_status"]
        formula  = f"OR({{{ps_field}}}='Unpaid',{{{ps_field}}}='Partial',{{{ps_field}}}='Overdue')"
        invoices = at.search_records("VERTEX INVOICES", formula)

        actions_due = []
        escalations = []

        for inv in invoices:
            f       = inv.get("fields", {})
            due_str = f.get(VI["due_date"], "")
            if not due_str:
                continue
            try:
                due  = datetime.fromisoformat(due_str[:10]).date()
                days = (today - due).days
            except Exception:
                days = 0

            if days < 1:
                continue

            amount  = f.get(VI["total_amount"], 0) or 0
            client  = f.get(VI["client_name"], "")
            inv_num = f.get(VI["invoice_number"], inv["id"])

            if days >= 60:
                escalations.append({
                    "invoice_number": inv_num,
                    "client_name":    client,
                    "amount":         amount,
                    "days_overdue":   days,
                })
            elif days >= 15:
                actions_due.append({
                    "invoice_number": inv_num,
                    "client_name":    client,
                    "amount":         amount,
                    "days_overdue":   days,
                    "action":         "second_reminder" if days >= 30 else "first_reminder",
                })

            # Advance follow-up date
            try:
                next_fu = (today + timedelta(days=7)).isoformat()
                at.update_record("VERTEX INVOICES", inv["id"], {
                    VI.get("follow_up_date", "FOLLOW-UP DATE"): next_fu
                })
            except Exception:
                pass

        # Write collection actions to TODAY_AGENDA.md
        agenda_path = os.path.join(os.path.dirname(__file__), "TODAY_AGENDA.md")
        try:
            existing = open(agenda_path, "r", encoding="utf-8").read() if os.path.exists(agenda_path) else ""
            marker   = "## COLLECTION ACTIONS DUE"
            if marker in existing:
                existing = existing[:existing.index(marker)].rstrip()

            section = f"\n\n---\n## COLLECTION ACTIONS DUE — {today.isoformat()}\n\n"
            if escalations:
                section += "### 🚨 ESCALATIONS — CALL DIRECTLY (60+ days overdue)\n\n"
                for item in escalations:
                    section += (
                        f"- **CALL {item['client_name']}** — Invoice {item['invoice_number']} "
                        f"${item['amount']:,.2f} ({item['days_overdue']} days overdue)\n"
                    )
                section += "\n"
            if actions_due:
                section += "### 📧 SEND REMINDERS\n\n"
                for item in actions_due:
                    section += (
                        f"- Email {item['client_name']} — Invoice {item['invoice_number']} "
                        f"${item['amount']:,.2f} ({item['days_overdue']} days overdue) "
                        f"[{item['action'].replace('_', ' ').title()}]\n"
                    )
                section += "\n"
            if not escalations and not actions_due:
                section += "_No collection actions due today. AR is current._\n"

            with open(agenda_path, "w", encoding="utf-8") as fh:
                fh.write(existing + section)
        except Exception as e:
            log.warning(f"Could not update TODAY_AGENDA.md collection section: {e}")

        log.info(f"Collection sweep: {len(actions_due)} reminders, {len(escalations)} escalations")
        return True
    except Exception as e:
        log.error(f"Collection sweep failed: {e}")
        return False


def run_vertex_ai_advisor():
    """Phase 10: Run AI Financial Advisor — cash analysis, alerts, briefing update."""
    log.info("--- VERTEX AI FINANCIAL ADVISOR ---")
    try:
        from vertex_ai_advisor import run_vertex_ai_advisor as _run
        result = _run()
        cash   = result.get("cash_position", {})
        alerts = result.get("high_alerts_count", 0)
        log.info(
            f"AI Advisor: net cash ${cash.get('net_cash', 0):,.2f} | "
            f"AR ${cash.get('total_ar', 0):,.2f} | "
            f"AP ${cash.get('total_ap', 0):,.2f} | "
            f"{alerts} high alerts"
        )
        return True
    except Exception as e:
        log.error(f"AI Advisor failed: {e}")
        return False


def run_vertex_bank_reconciliation():
    """Phase 12: Run AI bank reconciliation on any unmatched transactions."""
    log.info("--- VERTEX BANK RECONCILIATION ---")
    try:
        import requests
        base_url = os.environ.get("NEXUS_API_URL", "http://localhost:5000")
        resp     = requests.post(f"{base_url}/vertex/bank/reconcile", timeout=120)
        result   = resp.json()
        matched  = result.get("matched", 0)
        unmatched = result.get("unmatched", 0)
        log.info(f"Bank reconciliation: {matched} matched, {unmatched} unmatched")
        return True
    except Exception as e:
        log.error(f"Bank reconciliation failed: {e}")
        return False


VERTEX_DAILY_RUN_STATE = os.path.join(LOG_DIR, "vertex_daily_run.json")


def _should_run_vertex_daily_6am_et():
    """Once per calendar day, only in the 6:00–6:14 AM America/Detroit window."""
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("America/Detroit"))
    except Exception:
        now = datetime.now()
    if now.hour != 6 or now.minute >= 15:
        return False
    today = now.strftime("%Y-%m-%d")
    try:
        if os.path.exists(VERTEX_DAILY_RUN_STATE):
            with open(VERTEX_DAILY_RUN_STATE, "r") as f:
                data = json.load(f)
            if data.get("date") == today:
                return False
    except Exception:
        pass
    return True


def _mark_vertex_daily_run_et():
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("America/Detroit"))
    except Exception:
        now = datetime.now()
    try:
        with open(VERTEX_DAILY_RUN_STATE, "w") as f:
            json.dump({"date": now.strftime("%Y-%m-%d"), "iso": now.isoformat()}, f, indent=2)
    except Exception as e:
        log.warning(f"Could not write VERTEX daily run state: {e}")


def run_vertex_daily_jobs():
    """
    Run all VERTEX daily financial jobs (6 AM ET):
      1. Recurring invoice generation
      2. Collection sweep + agenda update
      3. AI Financial Advisor + briefing update
      4. Bank reconciliation
    """
    log.info("=== VERTEX DAILY FINANCIAL JOBS (6 AM) ===")
    results = {}
    results["recurring_invoices"]    = run_vertex_recurring_invoices()
    results["collection_sweep"]      = run_vertex_collection_sweep()
    results["ai_advisor"]            = run_vertex_ai_advisor()
    results["bank_reconciliation"]   = run_vertex_bank_reconciliation()
    log.info(f"=== VERTEX DAILY JOBS COMPLETE: {results} ===")
    return all(results.values())


# ============================================================================
# END VERTEX FINANCIAL JOBS
# ============================================================================


def run_radar():
    """
    RADAR — Revenue Acquisition Discovery And Reconnaissance.
    Full DDI opportunity mining sweep across ALL channels:
      1. Federal SAM.gov (EDWOSB/WOSB/SB set-asides + AOG/freight)
      2. Healthcare & MCO (State Medicaid, hospitals, MCO portals)
      3. Federal forecasts (agency procurement pipelines)
      4. State & local (Michigan portals)
      5. Public portal scan (nationwide)
      6. AI scoring & email alerts (score all new opps, email BID NOW)

    Run with:  python3 nexus_scheduler.py --radar
    """
    log.info("=" * 60)
    log.info("RADAR — Revenue Acquisition Discovery And Reconnaissance")
    log.info("Full opportunity sweep: Government + Healthcare + Commercial")
    log.info("=" * 60)

    results = {}

    # Channel 1: Federal SAM.gov (EDWOSB/WOSB/SB + AOG/freight)
    log.info("[RADAR 1/6] Federal SAM.gov mining...")
    results["federal_mining"] = run_federal_mining()

    # Channel 2: Healthcare & MCO (commercial/enterprise)
    log.info("[RADAR 2/6] Healthcare & MCO scanner...")
    results["healthcare_mco"] = run_healthcare_mco_scan()

    # Channel 3: Federal forecasts
    log.info("[RADAR 3/6] Federal forecasts...")
    results["forecast_mining"] = run_forecast_mining()

    # Channel 4: State & local (Michigan)
    log.info("[RADAR 4/6] State & local mining...")
    results["state_local"] = run_state_local_mining()

    # Channel 5: Public portals (nationwide)
    log.info("[RADAR 5/6] Public portal scan...")
    results["public_portals"] = run_public_portal_scan()

    # Channel 6: AI scoring + email alerts (process everything found above)
    log.info("[RADAR 6/6] AI scoring & alerts...")
    results["ai_scoring"] = run_ai_scoring_and_alerts()

    log.info("[RADAR COMPILE] Writing RADAR_RESULTS.md...")
    try:
        from compile_radar_results import compile_radar

        out = compile_radar()
        log.info("RADAR results compiled → %s", out.name)
        results["compile_radar"] = True
    except Exception as e:
        log.warning("RADAR compile failed: %s", e)
        results["compile_radar"] = False

    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)

    log.info("=" * 60)
    log.info(f"RADAR SWEEP COMPLETE — {passed} passed, {failed} failed")
    for task, success in results.items():
        status = "OK" if success else "FAILED"
        log.info(f"  {task}: {status}")
    log.info("=" * 60)

    return results


def run_all():
    """Run all scheduled tasks."""
    log.info("=" * 60)
    log.info("NEXUS SCHEDULER — Running all tasks")
    log.info("=" * 60)

    results = {}
    results["folder_scan"] = run_folder_scan()
    results["stale_detection"] = run_stale_detection()
    results["email_monitor"] = run_email_monitor()
    results["federal_mining"] = run_federal_mining()
    results["portal_mining"] = run_portal_mining()
    results["forecast_mining"] = run_forecast_mining()
    results["state_local_mining"] = run_state_local_mining()
    results["public_portal_scan"] = run_public_portal_scan()
    results["healthcare_mco_scan"] = run_healthcare_mco_scan()
    results["gbis_mine_all"] = run_gbis_mine_all_pipeline()
    results["prime_contractor_mining"] = run_prime_contractor_mining()
    results["ai_scoring_alerts"] = run_ai_scoring_and_alerts()
    results["quote_followups"] = run_quote_followups()
    # VERTEX financial jobs (run on-demand or via daily 6AM trigger in loop)
    results["vertex_collection_sweep"] = run_vertex_collection_sweep()
    results["vertex_ai_advisor"]       = run_vertex_ai_advisor()

    log.info("=" * 60)
    log.info("SCHEDULER COMPLETE")
    for task, success in results.items():
        status = "OK" if success else "FAILED"
        log.info(f"  {task}: {status}")
    log.info("=" * 60)

    return results


def run_loop():
    """Run continuously on schedule."""
    log.info("=" * 60)
    log.info("NEXUS SCHEDULER — Starting continuous loop")
    log.info("=" * 60)
    log.info("  Email check:          every 30 minutes")
    log.info("  Folder scan:          every 15 minutes")
    log.info("  Federal mining:       every 4 hours")
    log.info("  Portal mining:        every 4 hours")
    log.info("  Healthcare/MCO:       every 6 hours (RADAR)")
    log.info("  State/local mining:   every 6 hours")
    log.info("  Agency forecasts:     daily")
    log.info("  AI scoring + alerts:  every 2 hours")
    log.info("  Quote follow-ups:     every 4 hours")
    log.info("  RADAR full sweep:     daily 6:30 AM ET (+ 7 AM / noon / 6 PM catch-up) → RADAR_RESULTS.md")
    log.info("  GBIS mine-all:        daily 7:00 AM ET (full grant pipeline)")
    log.info("  Prime contractor mining: weekly")
    log.info("  JETA IATA market price: weekly (jet fuel $/bbl → JETA_MarketData)")
    log.info("  VERTEX financial jobs: daily 6:00 AM ET (recurring invoices, collection, AI advisor, reconciliation)")
    log.info("  Press Ctrl+C to stop")
    log.info("=" * 60)

    last_email = datetime.min
    last_scan = datetime.min
    last_mine = datetime.min
    last_portal = datetime.min
    last_forecast = datetime.min
    last_followup = datetime.min
    last_ai_score = datetime.min
    last_state_local = datetime.min
    last_digest = datetime.min
    last_public_scan = datetime.min
    last_prime_mining = datetime.min
    last_jeta_market = datetime.min
    last_healthcare = datetime.min

    EMAIL_INTERVAL = timedelta(minutes=30)
    SCAN_INTERVAL = timedelta(minutes=15)
    MINE_INTERVAL = timedelta(hours=4)       # Federal mining every 4h (was 6h)
    PORTAL_INTERVAL = timedelta(hours=4)
    STATE_LOCAL_INTERVAL = timedelta(hours=6) # Michigan portals every 6h
    HEALTHCARE_INTERVAL = timedelta(hours=6)  # Healthcare/MCO scan every 6h (RADAR)
    FORECAST_INTERVAL = timedelta(hours=24)   # Daily — forecasts don't change fast
    FOLLOWUP_INTERVAL = timedelta(hours=4)    # Check for outstanding quotes
    AI_SCORE_INTERVAL = timedelta(hours=2)    # Score new opps every 2h
    DIGEST_INTERVAL = timedelta(hours=24)     # Daily digest email
    PUBLIC_SCAN_INTERVAL = timedelta(hours=6)  # Public portal scan every 6h
    PRIME_MINING_INTERVAL = timedelta(days=7)   # Weekly — find primes needing EDWOSB subs
    JETA_MARKET_INTERVAL = timedelta(days=7)    # Weekly — IATA jet fuel $/bbl

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

        if now - last_state_local >= STATE_LOCAL_INTERVAL:
            run_state_local_mining()
            last_state_local = now

        if now - last_forecast >= FORECAST_INTERVAL:
            run_forecast_mining()
            last_forecast = now

        if now - last_ai_score >= AI_SCORE_INTERVAL:
            run_ai_scoring_and_alerts()
            last_ai_score = now

        if now - last_followup >= FOLLOWUP_INTERVAL:
            run_quote_followups()
            last_followup = now

        if now - last_public_scan >= PUBLIC_SCAN_INTERVAL:
            run_public_portal_scan()
            last_public_scan = now

        # RADAR: Healthcare & MCO scanner (State Medicaid, hospitals, MCO portals)
        if now - last_healthcare >= HEALTHCARE_INTERVAL:
            run_healthcare_mco_scan()
            last_healthcare = now

        # RADAR — full sweep + RADAR_RESULTS.md (6:30 AM primary; catch-up if Mac was asleep)
        if _should_trigger_radar_daily_et():
            if run_radar_daily_scheduled():
                _mark_radar_daily_run_et(compile_ok=True)
            else:
                log.warning("RADAR daily run finished without compile — will retry next catch-up window")

        # GBIS autonomous grant discovery — daily 7:00 AM America/Detroit (same as POST /gbis/mine-all)
        if _should_run_gbis_daily_7am_et():
            if run_gbis_mine_all_pipeline():
                _mark_gbis_daily_run_et()

        # VERTEX daily financial jobs — 6:00 AM America/Detroit
        if _should_run_vertex_daily_6am_et():
            if run_vertex_daily_jobs():
                _mark_vertex_daily_run_et()

        # Prime contractor mining — weekly (find primes needing EDWOSB subs)
        if now - last_prime_mining >= PRIME_MINING_INTERVAL:
            run_prime_contractor_mining()
            last_prime_mining = now

        # JETA — IATA jet fuel price weekly sync (requires api_server reachable at NEXUS_API_URL)
        if now - last_jeta_market >= JETA_MARKET_INTERVAL:
            run_jeta_market_price_sync()
            last_jeta_market = now

        # Daily digest at 7 AM
        if now - last_digest >= DIGEST_INTERVAL:
            try:
                from nexus_opportunity_intelligence import send_daily_digest
                send_daily_digest()
            except Exception as e:
                log.error(f"Daily digest failed: {e}")
            last_digest = now

        # Sleep 60 seconds between checks
        time.sleep(60)


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--loop" in args:
        try:
            run_loop()
        except KeyboardInterrupt:
            log.info("Scheduler stopped by user")
    elif "--radar" in args:
        run_radar()
    elif "--email" in args:
        run_email_monitor()
    elif "--mine" in args:
        run_federal_mining()
    elif "--aog" in args:
        from mine_aog_sam import run_aog_sam_scan

        run_aog_sam_scan(days_back=90)
    elif "--compile-radar" in args:
        from compile_radar_results import compile_radar

        path = compile_radar()
        print(f"Compiled {path}")
    elif "--digital-nav" in args:
        from mine_digital_navigation_sam import run_digital_nav_scan

        run_digital_nav_scan(days_back=90)
    elif "--sync-cos" in args:
        from sam_co_contact_sync import sync_co_contacts_from_sam

        # Optional: --limit-naics N (caps the sweep to the first N NAICS codes)
        limit_naics = None
        if "--limit-naics" in args:
            try:
                limit_naics = int(args[args.index("--limit-naics") + 1])
            except (ValueError, IndexError):
                log.warning("--limit-naics requires an integer; ignoring")

        # Optional: --days N (default 14)
        days_back = 14
        if "--days" in args:
            try:
                days_back = int(args[args.index("--days") + 1])
            except (ValueError, IndexError):
                log.warning("--days requires an integer; using default 14")

        result = sync_co_contacts_from_sam(days_back=days_back, limit_naics=limit_naics)
        log.info(
            "CO sync: %s opps, %s POCs, %s created, %s updated, %s skipped",
            result.get("opps_seen", 0),
            result.get("pocs_extracted", 0),
            result.get("created", 0),
            result.get("updated", 0),
            result.get("skipped", 0),
        )
    elif "--portals" in args:
        run_portal_mining()
    elif "--forecasts" in args:
        run_forecast_mining()
    elif "--followups" in args:
        run_quote_followups()
    elif "--score" in args:
        run_ai_scoring_and_alerts()
    elif "--local" in args:
        run_state_local_mining()
    elif "--public" in args:
        run_public_portal_scan()
    elif "--public-tier1" in args:
        run_public_portal_scan(tier1_only=True)
    elif "--healthcare" in args:
        run_healthcare_mco_scan()
    elif "--scan" in args:
        run_folder_scan()
        run_stale_detection()
    elif "--gbis" in args:
        run_gbis_mine_all_pipeline()
    elif "--primes" in args:
        run_prime_contractor_mining()
    elif "--vertex" in args:
        run_vertex_daily_jobs()
    elif "--vertex-collect" in args:
        run_vertex_collection_sweep()
    elif "--vertex-advisor" in args:
        run_vertex_ai_advisor()
    elif "--jeta-market" in args:
        run_jeta_market_price_sync()
    elif not args:
        run_all()
    else:
        print(__doc__)
