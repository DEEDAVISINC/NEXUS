#!/usr/bin/env python3
"""
NEXUS AUTONOMOUS ENGINE — "AI THAT WORKS WHILE YOU SLEEP"
============================================================
The self-learning autonomous layer that wraps nexus_scheduler tasks
with intelligence, feedback loops, and adaptive behavior.

WHAT IT DOES:
  1. SCANS    — Mines opportunities across all portals on schedule
  2. SCORES   — AI-evaluates every discovery against DDI's evolving profile
  3. PACKAGES — Auto-generates cap statements + buyer emails for hot matches
  4. MONITORS — Watches deadlines, compliance, contract health, follow-ups
  5. LEARNS   — Every cycle feeds outcomes back into the learning engine
  6. ADAPTS   — Adjusts scan frequency, scoring weights, and priorities based on what works
  7. BRIEFS   — Generates a daily morning brief with everything Dee needs to know

SELF-LEARNING LOOP:
  Cycle runs → Actions taken → Outcomes tracked → Patterns analyzed →
  Weights adjusted → Next cycle is smarter → Repeat forever

API CONTROL:
  POST /autonomous/start     — Start the engine
  POST /autonomous/stop      — Stop the engine
  GET  /autonomous/status    — Current state, last run, next run, learning stats
  GET  /autonomous/brief     — Latest morning brief
  GET  /autonomous/history   — Action history with learning annotations
  PUT  /autonomous/config    — Update intervals, thresholds, preferences
"""

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "autonomous.log")),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("nexus_autonomous")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(BASE_DIR, "autonomous_state.json")
BRIEF_PATH = os.path.join(BASE_DIR, "morning_brief.json")
CONFIG_PATH = os.path.join(BASE_DIR, "autonomous_config.json")

# ─── DEFAULT CONFIGURATION ───────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "enabled": False,
    "intervals": {
        "opportunity_scan": 240,      # minutes — scan portals for new opps
        "ai_scoring": 120,            # minutes — score unscored opportunities
        "auto_package": 60,           # minutes — generate packages for hot matches
        "deadline_watch": 60,         # minutes — check all active bid deadlines
        "supplier_followup": 240,     # minutes — check for unanswered RFQs
        "compass_monitor": 360,       # minutes — check contract health + deliverables
        "prism_compliance": 720,      # minutes — check agent certs + insurance
        "folder_scan": 15,            # minutes — scan BIDS:RESOURCES status
        "learning_cycle": 360,        # minutes — full learning analysis + weight adjustment
        "morning_brief": 1440,        # minutes — daily morning brief (24h)
    },
    "thresholds": {
        "auto_package_score": 75,     # minimum AI score to auto-generate package
        "bid_now_score": 85,          # score threshold for "BID NOW" alert
        "deadline_yellow_hours": 72,  # hours before deadline = yellow alert
        "deadline_red_hours": 24,     # hours before deadline = red alert
        "supplier_followup_days": 3,  # days before first supplier follow-up
        "coi_expiry_warn_days": 30,   # days before COI expiry = warning
    },
    "preferences": {
        "auto_email_alerts": True,    # send email for BID NOW opportunities
        "auto_generate_packages": True,  # auto-create cap statement + email
        "morning_brief_time": "06:00",   # when to generate morning brief
        "priority_naics": [],         # NAICS codes to prioritize (learned over time)
        "priority_agencies": [],      # agencies to prioritize (learned over time)
        "depriority_sources": [],     # sources that yield low results (learned)
    },
}


class NexusAutonomous:
    """The self-learning autonomous engine for NEXUS."""

    def __init__(self):
        self.config = self._load_config()
        self.state = self._load_state()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    # ─── STATE MANAGEMENT ────────────────────────────────────────────────────

    def _load_config(self) -> Dict:
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH) as f:
                    saved = json.load(f)
                merged = {**DEFAULT_CONFIG}
                for k, v in saved.items():
                    if isinstance(v, dict) and k in merged and isinstance(merged[k], dict):
                        merged[k] = {**merged[k], **v}
                    else:
                        merged[k] = v
                return merged
            except Exception:
                pass
        return dict(DEFAULT_CONFIG)

    def _save_config(self):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.config, f, indent=2, default=str)

    def _load_state(self) -> Dict:
        if os.path.exists(STATE_PATH):
            try:
                with open(STATE_PATH) as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "last_runs": {},
            "cycle_count": 0,
            "total_opportunities_found": 0,
            "total_packages_generated": 0,
            "total_alerts_sent": 0,
            "total_followups_queued": 0,
            "learning_adjustments": 0,
            "started_at": None,
            "action_log": [],
        }

    def _save_state(self):
        with open(STATE_PATH, 'w') as f:
            json.dump(self.state, f, indent=2, default=str)

    def _log_action(self, task: str, result: Dict):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "success": result.get("success", False),
            "summary": result.get("summary", ""),
            "items_processed": result.get("items_processed", 0),
            "learning_logged": result.get("learning_logged", False),
        }
        self.state["action_log"].append(entry)
        # Keep last 500 actions
        if len(self.state["action_log"]) > 500:
            self.state["action_log"] = self.state["action_log"][-500:]

    # ─── LEARNING INTEGRATION ────────────────────────────────────────────────

    def _get_learning_engine(self):
        try:
            from nexus_learning_engine import NexusLearningEngine
            return NexusLearningEngine()
        except Exception as e:
            log.warning(f"Learning engine unavailable: {e}")
            return None

    def _get_advisor(self):
        try:
            from nexus_advisor import advise
            return advise
        except Exception as e:
            log.warning(f"Advisor unavailable: {e}")
            return None

    def _learn(self, domain: str, entity_id: str, action: str, metadata: Dict = None) -> bool:
        engine = self._get_learning_engine()
        if engine:
            try:
                engine.log(domain, entity_id, action, metadata or {})
                return True
            except Exception as e:
                log.warning(f"Learning log failed: {e}")
        return False

    # ─── AUTONOMOUS TASKS ────────────────────────────────────────────────────

    def task_opportunity_scan(self) -> Dict:
        """Scan all portals for new opportunities, feed results into learning engine."""
        log.info("AUTONOMOUS: Opportunity scan starting...")
        result = {"success": False, "items_processed": 0, "summary": "", "learning_logged": False}

        try:
            from nexus_scheduler import (
                run_federal_mining,
                run_portal_mining,
                run_state_local_mining,
                run_public_portal_scan,
            )

            fed_ok = run_federal_mining()
            portal_ok = run_portal_mining()
            local_ok = run_state_local_mining()
            public_ok = run_public_portal_scan()

            tasks_ok = sum([fed_ok, portal_ok, local_ok, public_ok])
            result["success"] = tasks_ok > 0
            result["summary"] = f"{tasks_ok}/4 scan sources completed"

            # Learn which sources are producing results
            engine = self._get_learning_engine()
            if engine:
                for source, ok in [("federal", fed_ok), ("portals", portal_ok),
                                   ("state_local", local_ok), ("public", public_ok)]:
                    action = "discovered" if ok else "expired"
                    engine.log("opportunities", f"scan_{source}_{datetime.now().strftime('%Y%m%d')}",
                               action, {"source": source, "scan_success": ok})
                result["learning_logged"] = True

            # Count new opportunities from scan cache
            try:
                cache_path = os.path.join(BASE_DIR, "scan_cache.json")
                if os.path.exists(cache_path):
                    with open(cache_path) as f:
                        cache = json.load(f)
                    total = cache.get("summary", {}).get("total_count", 0)
                    result["items_processed"] = total
                    self.state["total_opportunities_found"] += total
            except Exception:
                pass

        except Exception as e:
            log.error(f"Opportunity scan failed: {e}")
            result["summary"] = str(e)

        return result

    def task_ai_scoring(self) -> Dict:
        """Score unscored opportunities and learn from scoring patterns."""
        log.info("AUTONOMOUS: AI scoring starting...")
        result = {"success": False, "items_processed": 0, "summary": "", "learning_logged": False}

        try:
            from nexus_scheduler import run_ai_scoring_and_alerts
            ok = run_ai_scoring_and_alerts()
            result["success"] = ok
            result["summary"] = "AI scoring completed" if ok else "AI scoring failed"

            # Learn from scoring distribution
            engine = self._get_learning_engine()
            if engine:
                engine.log("opportunities", f"scoring_cycle_{datetime.now().strftime('%Y%m%d_%H')}",
                           "scored", {"cycle": "autonomous", "success": ok})
                result["learning_logged"] = True

        except Exception as e:
            log.error(f"AI scoring failed: {e}")
            result["summary"] = str(e)

        return result

    def task_auto_package(self) -> Dict:
        """Auto-generate cap statement + buyer email for high-scoring presolicitations."""
        log.info("AUTONOMOUS: Auto-package generation starting...")
        result = {"success": False, "items_processed": 0, "summary": "", "learning_logged": False}

        try:
            from nexus_backend import AirtableClient
            airtable = AirtableClient()
            threshold = self.config["thresholds"]["auto_package_score"]

            # Find high-scoring opportunities without packages
            try:
                opps = airtable.get_all_records('GPSS OPPORTUNITIES')
            except Exception:
                opps = []

            packages_generated = 0
            for opp in opps:
                fields = opp.get('fields', {})
                score = fields.get('AI Score', 0) or fields.get('Score', 0) or 0
                status = fields.get('Status', '')
                has_package = fields.get('Package Generated', False)

                if score >= threshold and not has_package and status in (
                    'New - API', 'New - Presolicitation/Sources Sought',
                    'BID NOW', 'WORTH A LOOK', 'New'
                ):
                    pkg = self._generate_package(opp)
                    if pkg.get("success"):
                        packages_generated += 1
                        # Mark as packaged in Airtable
                        try:
                            airtable.update_record('GPSS OPPORTUNITIES', opp['id'], {
                                'Package Generated': True,
                                'Package Date': datetime.now().isoformat(),
                            })
                        except Exception:
                            pass

            result["success"] = True
            result["items_processed"] = packages_generated
            result["summary"] = f"{packages_generated} packages auto-generated (threshold: {threshold})"
            self.state["total_packages_generated"] += packages_generated

            # Learn from package generation
            if packages_generated > 0:
                self._learn("outreach", f"auto_pkg_{datetime.now().strftime('%Y%m%d')}",
                            "email_drafted", {"count": packages_generated, "autonomous": True})
                result["learning_logged"] = True

        except Exception as e:
            log.error(f"Auto-package failed: {e}")
            result["summary"] = str(e)

        return result

    def _generate_package(self, opportunity: Dict) -> Dict:
        """Generate a cap statement + buyer email for a single opportunity."""
        fields = opportunity.get('fields', {})
        agency = fields.get('Agency Name', '') or fields.get('Agency', '')
        title = fields.get('Title', '')
        sol_number = fields.get('RFP Number', '') or fields.get('Solicitation Number', '')
        naics = fields.get('NAICS', '')
        co_name = fields.get('CO Name', '')
        co_email = fields.get('CO Email', '')
        set_aside = fields.get('Set-Aside Type', '')

        if not agency or not title:
            return {"success": False, "reason": "Missing agency or title"}

        # Create bid folder
        safe_name = f"{agency} {title}"[:40].strip().upper().replace("/", "-")
        bid_folder = os.path.join(BASE_DIR, "BIDS:RESOURCES", safe_name)
        send_to_buyer = os.path.join(bid_folder, "SEND_TO_BUYER")

        try:
            os.makedirs(send_to_buyer, exist_ok=True)
            os.makedirs(os.path.join(bid_folder, "SEND_TO_SUPPLIER"), exist_ok=True)
            os.makedirs(os.path.join(bid_folder, "SEND_TO_SUBCONTRACTOR"), exist_ok=True)
        except Exception as e:
            return {"success": False, "reason": str(e)}

        # Generate buyer email
        email_content = self._build_buyer_email(agency, title, sol_number, naics, co_name, set_aside)
        email_path = os.path.join(send_to_buyer, "SEND_TO_BUYER_EMAIL_READY.md")
        try:
            with open(email_path, 'w') as f:
                f.write(email_content)
        except Exception as e:
            return {"success": False, "reason": str(e)}

        # Generate workflow checklist
        checklist = self._build_workflow_checklist(agency, title, sol_number, co_name, co_email)
        try:
            with open(os.path.join(bid_folder, "WORKFLOW_CHECKLIST.md"), 'w') as f:
                f.write(checklist)
        except Exception:
            pass

        log.info(f"AUTO-PACKAGE: {safe_name} — email + folder ready in SEND_TO_BUYER")

        # Teach about auto-packaging
        advise = self._get_advisor()
        if advise:
            try:
                advise('gpss', 'opportunity_discovered', {
                    'agency': agency, 'set_aside': set_aside, 'naics': naics,
                })
            except Exception:
                pass

        return {"success": True, "folder": bid_folder}

    def _build_buyer_email(self, agency: str, title: str, sol_number: str,
                           naics: str, co_name: str, set_aside: str) -> str:
        greeting = f"Hi {co_name.split()[0]}," if co_name else "Hi,"
        sol_ref = f" ({sol_number})" if sol_number else ""
        set_aside_line = f"\n\nAs a certified EDWOSB, we are well-positioned to support this {set_aside} requirement." if set_aside else ""

        return f"""## PROPOSALBIO FRAMEWORK

| Biohack | Application in This Email |
|---|---|
| #1 Mirror Neuron | Federal/formal tone matched to agency culture |
| #2 Cognitive Ease | Short sentences, clear structure |
| #4 Reciprocity | Smart questions showing research |
| #5 Yes Stacking | Capabilities mirror scope |
| #6 Familiarity | Agency language mirrored |
| #7 Name Recognition | {agency} referenced 3+ times |

**BUYER LANGUAGE SOURCE:** SAM.gov listing{sol_ref}

---

**TO:** {co_name or '[CO Name]'}
**SUBJECT:** EDWOSB Interest — {title}{sol_ref}

---

{greeting}

I'm reaching out regarding {agency}'s {title}{sol_ref}. Dee Davis Inc. is a certified Economically Disadvantaged Woman-Owned Small Business (EDWOSB) based in Troy, Michigan, and we are very interested in supporting {agency} on this requirement.{set_aside_line}

**Our relevant capabilities include:**
- Full-service delivery aligned with {title} scope
- EDWOSB/WOSB/MBE/SBE certified — maximizing socioeconomic value for {agency}
- Proven track record managing government contracts with quality and compliance focus
- Michigan-based operations with nationwide service capability

I've attached our capability statement for your review. A few questions as we prepare:

1. Is there an anticipated timeline for the full solicitation release?
2. Will there be a pre-bid conference or site visit?
3. Can Dee Davis Inc. be added to the interested vendors list?

We would welcome the opportunity to serve {agency} and are ready to demonstrate our full technical capability.

Looking forward to hearing from you!

Best regards,
Dee Davis
President & CEO
Dee Davis Inc.
755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084
(248) 376-4550 | info@deedavis.biz
EDWOSB | WOSB | WBENC | MBE | SBE | E-Verify
"""

    def _build_workflow_checklist(self, agency: str, title: str, sol_number: str,
                                  co_name: str, co_email: str) -> str:
        return f"""# WORKFLOW CHECKLIST — {agency} {title}

**Solicitation:** {sol_number or 'TBD'}
**CO:** {co_name or 'TBD'} | {co_email or 'TBD'}
**Auto-Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')} by NEXUS Autonomous Engine

---

## STEP 1: REVIEW NOTICE
- [ ] Read solicitation / presolicitation notice
- [ ] Identify NAICS, set-aside type, evaluation criteria
- [ ] Note deadlines

## STEP 2: GO / NO-GO DECISION
- [ ] AI Score reviewed
- [ ] EDWOSB advantage assessed
- [ ] Decision: PURSUE / SKIP

## STEP 3: SEND BUYER EMAIL + CAP STATEMENT
- [ ] Review auto-generated email in SEND_TO_BUYER/
- [ ] Generate tailored capability statement
- [ ] Send to {co_name or 'CO'} at {co_email or '[email]'}

## STEP 4: MONITOR FOR FULL RFP
- [ ] Set SAM.gov alert for {sol_number or 'this solicitation'}
- [ ] Check weekly for updates

## STEP 5: IDENTIFY SUPPLIERS / SUBS (when RFP drops)
- [ ] Research suppliers for required products/services
- [ ] Identify subcontractors if service contract

## STEP 6: CREATE SUPPLIER RFQ
- [ ] Generate DDI-numbered RFQ (no buyer info)
- [ ] Place in SEND_TO_SUPPLIER/

## STEP 7: COLLECT QUOTES & PRICE
- [ ] Track supplier responses
- [ ] Calculate markup and bid price

## STEP 8: PREPARE BID SUBMISSION
- [ ] Build proposal / quote response
- [ ] Place in SEND_TO_BUYER/

## STEP 9: REVIEW & SUBMIT
- [ ] Final review by Dee
- [ ] Submit before deadline

## STEP 10: TRACK OUTCOME
- [ ] Log win/loss in GPSS
- [ ] If won → COMPASS auto-creates contract
- [ ] Debrief with Advisor
"""

    def task_deadline_watch(self) -> Dict:
        """Monitor all active bid deadlines and flag approaching ones."""
        log.info("AUTONOMOUS: Deadline watch starting...")
        result = {"success": False, "items_processed": 0, "summary": "", "learning_logged": False}

        try:
            from nexus_backend import AirtableClient
            airtable = AirtableClient()
            yellow_hours = self.config["thresholds"]["deadline_yellow_hours"]
            red_hours = self.config["thresholds"]["deadline_red_hours"]
            now = datetime.now()
            alerts = []

            try:
                opps = airtable.get_all_records('GPSS OPPORTUNITIES')
            except Exception:
                opps = []

            for opp in opps:
                fields = opp.get('fields', {})
                status = fields.get('Status', '')
                if status in ('Won', 'Lost', 'Expired', 'Cancelled', 'Skipped'):
                    continue

                deadline_str = fields.get('Deadline', '') or fields.get('Due Date', '') or fields.get('Response Date', '')
                if not deadline_str:
                    continue

                try:
                    deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00').replace('+00:00', ''))
                except Exception:
                    try:
                        from dateutil.parser import parse
                        deadline = parse(deadline_str)
                    except Exception:
                        continue

                hours_left = (deadline - now).total_seconds() / 3600
                # Do NOT keep EXPIRED rows in deadline_alerts.json — they balloon
                # into tens of thousands and spam the dashboard with dead bids.
                # Learning for missed deadlines still runs via a short grace window below.
                if hours_left < 0:
                    # Only learn if missed within last 14 days (avoid re-logging ancient Airtable junk)
                    if hours_left >= -(14 * 24):
                        self._learn(
                            "bids",
                            opp["id"],
                            "expired",
                            {
                                "agency": fields.get("Agency Name", ""),
                                "missed_by": abs(hours_left),
                            },
                        )
                    continue
                elif hours_left <= red_hours:
                    alert_level = "RED"
                elif hours_left <= yellow_hours:
                    alert_level = "YELLOW"
                else:
                    continue

                alerts.append({
                    "opportunity_id": opp['id'],
                    "title": fields.get('Title', 'Unknown') or fields.get('Name', 'Unknown'),
                    "agency": fields.get('Agency Name', ''),
                    "deadline": deadline_str,
                    "hours_left": round(hours_left, 1),
                    "alert_level": alert_level,
                })

            result["success"] = True
            result["items_processed"] = len(alerts)

            red_count = len([a for a in alerts if a["alert_level"] == "RED"])
            yellow_count = len([a for a in alerts if a["alert_level"] == "YELLOW"])
            expired_count = 0
            result["summary"] = f"{red_count} RED, {yellow_count} YELLOW (expired omitted from alert feed)"

            # Save alerts for dashboard — live deadlines only
            alerts_path = os.path.join(BASE_DIR, "deadline_alerts.json")
            with open(alerts_path, 'w') as f:
                json.dump({"alerts": alerts, "checked_at": now.isoformat()}, f, default=str)

            result["learning_logged"] = True

        except Exception as e:
            log.error(f"Deadline watch failed: {e}")
            result["summary"] = str(e)

        return result

    def task_supplier_followup(self) -> Dict:
        """Check for unanswered supplier RFQs and queue follow-ups."""
        log.info("AUTONOMOUS: Supplier follow-up check starting...")
        result = {"success": False, "items_processed": 0, "summary": "", "learning_logged": False}

        try:
            from nexus_scheduler import run_quote_followups
            ok = run_quote_followups()
            result["success"] = ok
            result["summary"] = "Supplier follow-ups checked" if ok else "Follow-up check failed"

            if ok:
                self._learn("suppliers", f"followup_cycle_{datetime.now().strftime('%Y%m%d')}",
                            "rfq_sent", {"type": "followup_check", "autonomous": True})
                result["learning_logged"] = True

        except Exception as e:
            log.error(f"Supplier follow-up failed: {e}")
            result["summary"] = str(e)

        return result

    def task_compass_monitor(self) -> Dict:
        """Check contract health, deliverable due dates, COI expirations."""
        log.info("AUTONOMOUS: COMPASS contract monitoring starting...")
        result = {"success": False, "items_processed": 0, "summary": "", "learning_logged": False}

        try:
            from nexus_backend import AirtableClient
            airtable = AirtableClient()
            now = datetime.now()
            warnings = []

            # Check COMPASS contracts
            try:
                contracts = airtable.get_all_records('COMPASS Contracts')
            except Exception:
                contracts = []

            for contract in contracts:
                fields = contract.get('fields', {})
                if fields.get('Status') != 'Active':
                    continue

                end_date_str = fields.get('End Date', '')
                if end_date_str:
                    try:
                        end_date = datetime.fromisoformat(end_date_str)
                        days_left = (end_date - now).days
                        if days_left <= 30:
                            warnings.append({
                                "type": "contract_expiring",
                                "contract": fields.get('Title', ''),
                                "days_left": days_left,
                            })
                    except Exception:
                        pass

            # Check deliverables
            try:
                deliverables = airtable.get_all_records('COMPASS Deliverables')
            except Exception:
                deliverables = []

            overdue = 0
            for deliv in deliverables:
                fields = deliv.get('fields', {})
                if fields.get('Status') in ('Completed', 'Accepted'):
                    continue
                due_str = fields.get('Due Date', '')
                if due_str:
                    try:
                        due = datetime.fromisoformat(due_str)
                        if due < now:
                            overdue += 1
                            warnings.append({
                                "type": "deliverable_overdue",
                                "deliverable": fields.get('Title', ''),
                                "days_overdue": (now - due).days,
                            })
                    except Exception:
                        pass

            result["success"] = True
            result["items_processed"] = len(contracts) + len(deliverables)
            result["summary"] = f"{len(contracts)} contracts monitored, {overdue} overdue deliverables, {len(warnings)} warnings"

            # Save warnings
            warnings_path = os.path.join(BASE_DIR, "compass_warnings.json")
            with open(warnings_path, 'w') as f:
                json.dump({"warnings": warnings, "checked_at": now.isoformat()}, f, default=str)

            if warnings:
                self._learn("intelligence", f"compass_monitor_{now.strftime('%Y%m%d')}",
                            "reviewed", {"warnings": len(warnings), "overdue": overdue})
                result["learning_logged"] = True

        except Exception as e:
            log.error(f"COMPASS monitor failed: {e}")
            result["summary"] = str(e)

        return result

    def task_prism_compliance(self) -> Dict:
        """Check field agent compliance — certs, insurance, background checks."""
        log.info("AUTONOMOUS: PRISM compliance check starting...")
        result = {"success": False, "items_processed": 0, "summary": "", "learning_logged": False}

        try:
            from nexus_backend import AirtableClient
            airtable = AirtableClient()
            now = datetime.now()
            warn_days = self.config["thresholds"]["coi_expiry_warn_days"]
            flags = []

            try:
                agents = airtable.get_all_records('PRISM AGENTS')
            except Exception:
                agents = []

            for agent in agents:
                fields = agent.get('fields', {})
                if fields.get('Status') != 'Active':
                    continue

                # Check cert expiry
                cert_expiry = fields.get('Certification Expiry', '') or fields.get('Cert Expiry', '')
                if cert_expiry:
                    try:
                        expiry = datetime.fromisoformat(cert_expiry)
                        days_left = (expiry - now).days
                        if days_left <= warn_days:
                            flags.append({
                                "type": "cert_expiring",
                                "agent": fields.get('Name', ''),
                                "days_left": days_left,
                            })
                    except Exception:
                        pass

                # Check insurance
                ins_expiry = fields.get('Insurance Expiry', '') or fields.get('COI Expiry', '')
                if ins_expiry:
                    try:
                        expiry = datetime.fromisoformat(ins_expiry)
                        days_left = (expiry - now).days
                        if days_left <= warn_days:
                            flags.append({
                                "type": "insurance_expiring",
                                "agent": fields.get('Name', ''),
                                "days_left": days_left,
                            })
                    except Exception:
                        pass

            result["success"] = True
            result["items_processed"] = len(agents)
            result["summary"] = f"{len(agents)} agents checked, {len(flags)} compliance flags"

            flags_path = os.path.join(BASE_DIR, "prism_compliance_flags.json")
            with open(flags_path, 'w') as f:
                json.dump({"flags": flags, "checked_at": now.isoformat()}, f, default=str)

            if flags:
                for flag in flags:
                    self._learn("subcontractors", f"agent_{flag['agent']}", "performing_poorly",
                                {"issue": flag["type"], "days_left": flag["days_left"]})
                result["learning_logged"] = True

        except Exception as e:
            log.error(f"PRISM compliance check failed: {e}")
            result["summary"] = str(e)

        return result

    def task_folder_scan(self) -> Dict:
        """Scan BIDS:RESOURCES and update workflow status."""
        log.info("AUTONOMOUS: Folder scan starting...")
        result = {"success": False, "items_processed": 0, "summary": "", "learning_logged": False}

        try:
            from nexus_scheduler import run_folder_scan, run_stale_detection
            scan_ok = run_folder_scan()
            stale_ok = run_stale_detection()
            result["success"] = scan_ok
            result["summary"] = "Folder scan + stale detection completed"
        except Exception as e:
            log.error(f"Folder scan failed: {e}")
            result["summary"] = str(e)

        return result

    def task_learning_cycle(self) -> Dict:
        """Run the full learning engine analysis and weight adjustment."""
        log.info("AUTONOMOUS: Learning cycle starting...")
        result = {"success": False, "items_processed": 0, "summary": "", "learning_logged": True}

        try:
            engine = self._get_learning_engine()
            if not engine:
                result["summary"] = "Learning engine unavailable"
                return result

            analysis = engine.analyze(use_ai=False)
            domains_analyzed = len(analysis.get("domains", {}))

            # Extract weight adjustments
            adjustments = 0
            insights = []
            for domain, data in analysis.get("domains", {}).items():
                adj = data.get("weight_adjustments", {})
                if adj:
                    adjustments += len(adj)
                ins = data.get("insights", [])
                insights.extend(ins[:3])

            # Update priority lists based on learning
            self._update_priorities_from_learning(engine)

            result["success"] = True
            result["items_processed"] = domains_analyzed
            result["summary"] = f"{domains_analyzed} domains analyzed, {adjustments} weight adjustments, {len(insights)} insights"
            self.state["learning_adjustments"] += adjustments

        except Exception as e:
            log.error(f"Learning cycle failed: {e}")
            result["summary"] = str(e)

        return result

    def _update_priorities_from_learning(self, engine):
        """Use learning data to update priority NAICS codes, agencies, and sources."""
        try:
            insights = engine.get_insights("opportunities", limit=20)
            # Extract patterns from won opportunities
            won_events = [i for i in insights if i.get("action") in ("won", "pursued")]
            naics_counts = {}
            agency_counts = {}
            for event in won_events:
                meta = event.get("metadata", {})
                naics = meta.get("naics", "")
                agency = meta.get("agency", "")
                if naics:
                    naics_counts[naics] = naics_counts.get(naics, 0) + 1
                if agency:
                    agency_counts[agency] = agency_counts.get(agency, 0) + 1

            if naics_counts:
                top_naics = sorted(naics_counts, key=naics_counts.get, reverse=True)[:10]
                self.config["preferences"]["priority_naics"] = top_naics

            if agency_counts:
                top_agencies = sorted(agency_counts, key=agency_counts.get, reverse=True)[:10]
                self.config["preferences"]["priority_agencies"] = top_agencies

            self._save_config()
        except Exception as e:
            log.warning(f"Priority update failed: {e}")

    def task_morning_brief(self) -> Dict:
        """Generate the daily morning brief — everything Dee needs in one view."""
        log.info("AUTONOMOUS: Morning brief generation starting...")
        result = {"success": False, "items_processed": 0, "summary": "", "learning_logged": False}

        try:
            brief = {
                "generated_at": datetime.now().isoformat(),
                "greeting": f"Good morning, Dee. Here's your NEXUS brief for {datetime.now().strftime('%A, %B %d')}.",
                "sections": {},
            }

            # 1. New Opportunities Overnight
            try:
                from nexus_backend import AirtableClient
                airtable = AirtableClient()
                opps = airtable.get_all_records('GPSS OPPORTUNITIES')
                yesterday = datetime.now() - timedelta(hours=24)
                new_opps = []
                for opp in opps:
                    created = opp.get('fields', {}).get('Created Date', '') or opp.get('createdTime', '')
                    if created:
                        try:
                            ct = datetime.fromisoformat(created.replace('Z', ''))
                            if ct >= yesterday:
                                new_opps.append({
                                    "title": opp['fields'].get('Title', ''),
                                    "agency": opp['fields'].get('Agency Name', ''),
                                    "score": opp['fields'].get('AI Score', 0) or opp['fields'].get('Score', 0) or 0,
                                    "set_aside": opp['fields'].get('Set-Aside Type', ''),
                                })
                        except Exception:
                            pass

                bid_now = [o for o in new_opps if o["score"] >= 85]
                worth_look = [o for o in new_opps if 60 <= o["score"] < 85]

                brief["sections"]["opportunities"] = {
                    "title": "New Opportunities (Last 24h)",
                    "total_new": len(new_opps),
                    "bid_now": bid_now,
                    "worth_a_look": worth_look,
                    "message": f"{len(bid_now)} BID NOW, {len(worth_look)} worth a look out of {len(new_opps)} new."
                }
            except Exception as e:
                brief["sections"]["opportunities"] = {"error": str(e)}

            # 2. Deadline Alerts
            try:
                alerts_path = os.path.join(BASE_DIR, "deadline_alerts.json")
                if os.path.exists(alerts_path):
                    with open(alerts_path) as f:
                        deadline_data = json.load(f)
                    brief["sections"]["deadlines"] = {
                        "title": "Upcoming Deadlines",
                        "alerts": deadline_data.get("alerts", []),
                        "message": f"{len(deadline_data.get('alerts', []))} deadlines need attention."
                    }
            except Exception:
                pass

            # 3. Packages Ready to Send
            try:
                bids_dir = os.path.join(BASE_DIR, "BIDS:RESOURCES")
                packages_ready = 0
                ready_list = []
                if os.path.isdir(bids_dir):
                    for folder in os.listdir(bids_dir):
                        send_to_buyer = os.path.join(bids_dir, folder, "SEND_TO_BUYER")
                        if os.path.isdir(send_to_buyer):
                            email_file = os.path.join(send_to_buyer, "SEND_TO_BUYER_EMAIL_READY.md")
                            if os.path.exists(email_file):
                                stat = os.stat(email_file)
                                modified = datetime.fromtimestamp(stat.st_mtime)
                                if modified >= yesterday:
                                    packages_ready += 1
                                    ready_list.append(folder)

                brief["sections"]["packages"] = {
                    "title": "Packages Ready to Send",
                    "count": packages_ready,
                    "folders": ready_list[:10],
                    "message": f"{packages_ready} buyer packages generated overnight, ready for your review."
                }
            except Exception:
                pass

            # 4. Supplier Follow-ups Needed
            try:
                brief["sections"]["followups"] = {
                    "title": "Supplier Follow-ups",
                    "message": "Check SEND_TO_SUPPLIER folders for outstanding quotes."
                }
            except Exception:
                pass

            # 5. COMPASS Contract Health
            try:
                warnings_path = os.path.join(BASE_DIR, "compass_warnings.json")
                if os.path.exists(warnings_path):
                    with open(warnings_path) as f:
                        compass_data = json.load(f)
                    brief["sections"]["contracts"] = {
                        "title": "Contract Health",
                        "warnings": compass_data.get("warnings", []),
                        "message": f"{len(compass_data.get('warnings', []))} items need attention."
                    }
            except Exception:
                pass

            # 6. Learning Insights
            try:
                engine = self._get_learning_engine()
                if engine:
                    insights = engine.get_insights(limit=5)
                    brief["sections"]["learning"] = {
                        "title": "What NEXUS Learned",
                        "insights": [{"domain": i.get("domain", ""), "action": i.get("action", ""),
                                      "metadata": i.get("metadata", {})} for i in insights[:5]],
                        "message": "Latest patterns from your bid activity."
                    }

                    status = engine.get_status()
                    brief["sections"]["growth"] = {
                        "title": "Growth Metrics",
                        "total_events": status.get("total_events", 0),
                        "domains_active": status.get("domains_tracked", 0),
                        "message": f"NEXUS has logged {status.get('total_events', 0)} learning events across {status.get('domains_tracked', 0)} domains."
                    }
            except Exception:
                pass

            # 7. Autonomous Engine Stats
            brief["sections"]["autonomous"] = {
                "title": "Autonomous Engine Stats",
                "cycles_run": self.state.get("cycle_count", 0),
                "opportunities_found": self.state.get("total_opportunities_found", 0),
                "packages_generated": self.state.get("total_packages_generated", 0),
                "learning_adjustments": self.state.get("learning_adjustments", 0),
                "message": "NEXUS worked while you slept."
            }

            # Save brief
            with open(BRIEF_PATH, 'w') as f:
                json.dump(brief, f, indent=2, default=str)

            result["success"] = True
            result["items_processed"] = len(brief["sections"])
            result["summary"] = f"Morning brief generated with {len(brief['sections'])} sections"

        except Exception as e:
            log.error(f"Morning brief failed: {e}")
            result["summary"] = str(e)

        return result

    # ─── MAIN LOOP ───────────────────────────────────────────────────────────

    def _should_run(self, task_name: str) -> bool:
        interval_minutes = self.config["intervals"].get(task_name, 60)
        last_run_str = self.state["last_runs"].get(task_name)
        if not last_run_str:
            return True
        try:
            last_run = datetime.fromisoformat(last_run_str)
            return (datetime.now() - last_run) >= timedelta(minutes=interval_minutes)
        except Exception:
            return True

    def _run_task(self, task_name: str, task_fn):
        if not self._should_run(task_name):
            return
        log.info(f"─── Running: {task_name} ───")
        try:
            result = task_fn()
            self._log_action(task_name, result)
            self.state["last_runs"][task_name] = datetime.now().isoformat()
            self._save_state()

            status = "OK" if result.get("success") else "FAILED"
            learned = " [LEARNED]" if result.get("learning_logged") else ""
            log.info(f"  {task_name}: {status} — {result.get('summary', '')}{learned}")
        except Exception as e:
            log.error(f"  {task_name}: EXCEPTION — {e}")
            self._log_action(task_name, {"success": False, "summary": str(e)})

    def run_cycle(self):
        """Run one full autonomous cycle."""
        self.state["cycle_count"] = self.state.get("cycle_count", 0) + 1
        cycle = self.state["cycle_count"]
        log.info(f"{'='*60}")
        log.info(f"NEXUS AUTONOMOUS — Cycle #{cycle}")
        log.info(f"{'='*60}")

        tasks = [
            ("folder_scan", self.task_folder_scan),
            ("opportunity_scan", self.task_opportunity_scan),
            ("ai_scoring", self.task_ai_scoring),
            ("auto_package", self.task_auto_package),
            ("deadline_watch", self.task_deadline_watch),
            ("supplier_followup", self.task_supplier_followup),
            ("compass_monitor", self.task_compass_monitor),
            ("prism_compliance", self.task_prism_compliance),
            ("learning_cycle", self.task_learning_cycle),
            ("morning_brief", self.task_morning_brief),
        ]

        for task_name, task_fn in tasks:
            if self._stop_event.is_set():
                log.info("Stop requested — breaking cycle")
                break
            self._run_task(task_name, task_fn)

        self._save_state()
        log.info(f"Cycle #{cycle} complete")
        log.info(f"{'='*60}")

    def start(self):
        """Start the autonomous engine in a background thread."""
        if self._running:
            return {"status": "already_running"}

        self.config["enabled"] = True
        self._save_config()
        self._stop_event.clear()
        self._running = True
        self.state["started_at"] = datetime.now().isoformat()
        self._save_state()

        def loop():
            log.info("NEXUS AUTONOMOUS ENGINE — STARTED")
            log.info(f"Intervals: {json.dumps(self.config['intervals'], indent=2)}")
            while not self._stop_event.is_set():
                try:
                    self.run_cycle()
                except Exception as e:
                    log.error(f"Cycle error: {e}")
                # Sleep 60 seconds between cycle checks
                self._stop_event.wait(60)
            self._running = False
            log.info("NEXUS AUTONOMOUS ENGINE — STOPPED")

        self._thread = threading.Thread(target=loop, daemon=True, name="nexus-autonomous")
        self._thread.start()
        return {"status": "started", "started_at": self.state["started_at"]}

    def stop(self):
        """Stop the autonomous engine."""
        if not self._running:
            return {"status": "not_running"}
        self._stop_event.set()
        self.config["enabled"] = False
        self._save_config()
        return {"status": "stopping"}

    def get_status(self) -> Dict:
        """Get current engine status."""
        now = datetime.now()
        next_runs = {}
        for task_name, interval in self.config["intervals"].items():
            last_str = self.state["last_runs"].get(task_name)
            if last_str:
                try:
                    last = datetime.fromisoformat(last_str)
                    next_time = last + timedelta(minutes=interval)
                    minutes_until = max(0, (next_time - now).total_seconds() / 60)
                    next_runs[task_name] = {
                        "last_run": last_str,
                        "next_run": next_time.isoformat(),
                        "minutes_until": round(minutes_until),
                        "interval_minutes": interval,
                    }
                except Exception:
                    next_runs[task_name] = {"last_run": "never", "interval_minutes": interval}
            else:
                next_runs[task_name] = {"last_run": "never", "interval_minutes": interval}

        return {
            "running": self._running,
            "enabled": self.config.get("enabled", False),
            "started_at": self.state.get("started_at"),
            "cycle_count": self.state.get("cycle_count", 0),
            "stats": {
                "opportunities_found": self.state.get("total_opportunities_found", 0),
                "packages_generated": self.state.get("total_packages_generated", 0),
                "alerts_sent": self.state.get("total_alerts_sent", 0),
                "learning_adjustments": self.state.get("learning_adjustments", 0),
            },
            "tasks": next_runs,
            "recent_actions": self.state.get("action_log", [])[-10:],
        }

    def get_brief(self) -> Dict:
        """Get the latest morning brief."""
        if os.path.exists(BRIEF_PATH):
            try:
                with open(BRIEF_PATH) as f:
                    return json.load(f)
            except Exception:
                pass
        return {"generated_at": None, "greeting": "No brief generated yet.", "sections": {}}

    def update_config(self, updates: Dict) -> Dict:
        """Update autonomous engine configuration."""
        for key, value in updates.items():
            if key in self.config:
                if isinstance(value, dict) and isinstance(self.config[key], dict):
                    self.config[key].update(value)
                else:
                    self.config[key] = value
        self._save_config()
        return self.config


# ─── SINGLETON ───────────────────────────────────────────────────────────────

_engine: Optional[NexusAutonomous] = None

def get_engine() -> NexusAutonomous:
    global _engine
    if _engine is None:
        _engine = NexusAutonomous()
    return _engine


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    engine = get_engine()

    if "--start" in sys.argv:
        print("Starting NEXUS Autonomous Engine...")
        engine.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            engine.stop()
            print("\nStopped.")
    elif "--cycle" in sys.argv:
        print("Running single autonomous cycle...")
        engine.run_cycle()
    elif "--brief" in sys.argv:
        print("Generating morning brief...")
        result = engine.task_morning_brief()
        print(json.dumps(engine.get_brief(), indent=2))
    elif "--status" in sys.argv:
        print(json.dumps(engine.get_status(), indent=2))
    else:
        print(__doc__)
        print("\nUsage:")
        print("  python3 nexus_autonomous.py --start    # Start autonomous engine")
        print("  python3 nexus_autonomous.py --cycle    # Run one cycle")
        print("  python3 nexus_autonomous.py --brief    # Generate morning brief")
        print("  python3 nexus_autonomous.py --status   # Show engine status")
