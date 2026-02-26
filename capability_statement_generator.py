"""
Capability Statement Generator — v3 Engine
Produces cap statements matching the Contract Management Firm v3 design.
Each sector gets its own color scheme, but the STRUCTURE and IMPACT stay identical.
"""

import os
import re
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# SECTOR COLOR DEFINITIONS — from cap-statement-colors.mdc
# ═══════════════════════════════════════════════════════════════════════════════

SECTOR_COLORS = {
    "main": {
        "primary": "#0a1628",
        "secondary": "#1e3a5f",
        "accent": "#c5963a",
        "accent_dark": "#b8860b",
        "gold_bar_text": "#0a1628",
        "comp_columns": 4,
    },
    "fingerprinting": {
        "primary": "#1a2e1a",
        "secondary": "#2d5016",
        "accent": "#4ade80",
        "accent_dark": "#166534",
        "gold_bar_text": "#fff",
        "comp_columns": 4,
    },
    "nemt": {
        "primary": "#1e3a5f",
        "secondary": "#991b1b",
        "accent": "#dc2626",
        "accent_dark": "#991b1b",
        "gold_bar_text": "#fff",
        "comp_columns": 4,
    },
    "drug_testing": {
        "primary": "#3b0764",
        "secondary": "#7c3aed",
        "accent": "#a78bfa",
        "accent_dark": "#6b21a8",
        "gold_bar_text": "#fff",
        "comp_columns": 4,
    },
    "dna_testing": {
        "primary": "#134e4a",
        "secondary": "#0d9488",
        "accent": "#2dd4bf",
        "accent_dark": "#0f766e",
        "gold_bar_text": "#fff",
        "comp_columns": 4,
    },
    "janitorial": {
        "primary": "#451a03",
        "secondary": "#b45309",
        "accent": "#f59e0b",
        "accent_dark": "#92400e",
        "gold_bar_text": "#451a03",
        "comp_columns": 4,
    },
    "industrial": {
        "primary": "#1e293b",
        "secondary": "#475569",
        "accent": "#94a3b8",
        "accent_dark": "#334155",
        "gold_bar_text": "#fff",
        "comp_columns": 4,
    },
    "courier": {
        "primary": "#7c2d12",
        "secondary": "#ea580c",
        "accent": "#fb923c",
        "accent_dark": "#c2410c",
        "gold_bar_text": "#fff",
        "comp_columns": 4,
    },
    "notary": {
        "primary": "#581c87",
        "secondary": "#a78bdb",
        "accent": "#e879a8",
        "accent_dark": "#9333ea",
        "gold_bar_text": "#fff",
        "comp_columns": 4,
    },
    "professional": {
        "primary": "#171717",
        "secondary": "#404040",
        "accent": "#a3a3a3",
        "accent_dark": "#525252",
        "gold_bar_text": "#fff",
        "comp_columns": 4,
    },
    "georgia": {
        "primary": "#7f1d1d",
        "secondary": "#b91c1c",
        "accent": "#f87171",
        "accent_dark": "#991b1b",
        "gold_bar_text": "#fff",
        "comp_columns": 4,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# SECTOR CONTENT DEFAULTS — impactful, CO-grade language
# ═══════════════════════════════════════════════════════════════════════════════

SECTOR_CONTENT = {
    "main": {
        "gold_bar_title": "CONTRACT MANAGEMENT FIRM",
        "gold_bar_subtitle": "Federal &bull; State &bull; Commercial &bull; Sole-Source Eligible Up to $7M",
        "overview": (
            '<strong>DEE DAVIS INC.</strong> is an <strong>SBA-certified EDWOSB prime contractor</strong> '
            'delivering end-to-end contract management across federal, state, and commercial sectors. '
            'With <strong>7+ years of proven performance</strong>, 5,100+ managed service locations '
            'nationwide, and <strong>zero compliance deficiencies</strong>, DDI executes complex, '
            'multi-stakeholder contracts through strategic alliance partners &mdash; from regulated '
            'healthcare operations and federal security credentialing to emergency logistics and '
            'business continuity. Multi-state licensed. CONUS/OCONUS deployment-ready.'
        ),
        "framework_line": "EXECUTION FRAMEWORK: Identify &rarr; Pursue &rarr; Build &rarr; Manage &rarr; Deliver &rarr; Sustain",
        "competencies_header": "CORE COMPETENCIES &mdash; PROVEN PERFORMANCE ACROSS REGULATED SECTORS",
        "competencies": [
            {"title": "Business Continuity &amp; Disaster Relief", "desc": "COOP execution, FEMA-coordinated disaster logistics, emergency supply chain activation, rapid contractor mobilization", "style": "c-primary"},
            {"title": "Regulated Healthcare Operations", "desc": "DOT/FTA/SAMHSA drug &amp; alcohol programs, AABB-accredited DNA testing, medical specimen transport, NEMT, Medicaid provider operations", "style": "c-light1"},
            {"title": "Federal Security &amp; Credentialing", "desc": "DCSA SWFT electronic fingerprinting, FBI NCHC submissions, TWIC-cleared facility access, personnel vetting", "style": "c-light2"},
            {"title": "Logistics &amp; Fleet Operations", "desc": "Licensed freight brokerage (MC-1647572), DOT-regulated fleet coordination, time-critical delivery, chain-of-custody transport", "style": "c-light3"},
            {"title": "Government Procurement", "desc": "Medical &amp; emergency equipment, industrial supply fulfillment, modified housing &amp; storage, commodity contract execution", "style": "c-light4"},
            {"title": "Professional &amp; Legal Services", "desc": "Commissioned notary, Remote Online Notarization, CNTDA-certified document execution, surety bonds, signing agent services", "style": "c-light5"},
            {"title": "Workforce &amp; Training Solutions", "desc": "Contract staffing, regulatory compliance training, supervisor certification programs, safety-sensitive personnel management", "style": "c-light2"},
            {"title": "Management Consulting", "desc": "Federal healthcare compliance, process optimization, logistics system design, operational risk assessment, BPM implementation", "style": "c-light1"},
        ],
        "past_performance_header": "PAST PERFORMANCE &mdash; VERIFIED TRACK RECORD",
        "past_performance": [
            {"title": "DOT DRUG &amp; ALCOHOL PROGRAMS", "desc": "TPA for transit authorities, utilities, federal agencies. Full 49 CFR Parts 40 &amp; 655 compliance."},
            {"title": "FEDERAL FINGERPRINTING &mdash; 4+ INSTALLATIONS", "desc": "SWFT BPAs executed. DCSA/FBI electronic submissions. 24-48 hour turnaround."},
            {"title": "15+ ANNUAL MUNICIPAL CONTRACTS", "desc": "County government commodity supply. On-time, on-budget, renewed annually."},
            {"title": "1,500+ REGULATED DELIVERIES", "desc": "Chain-of-custody medical, pharmaceutical, specimen transport. Zero deficiencies."},
            {"title": "5,100+ MANAGED FACILITIES", "desc": "Deployment-ready nationwide via eScreen/Quest Diagnostics partnership."},
            {"title": "MDHHS COMMUNITY PARTNER", "desc": "Official recognition &mdash; State of Michigan Department of Health &amp; Human Services."},
        ],
        "differentiators": [
            {"title": "EDWOSB SOLE-SOURCE ELIGIBLE &mdash; UP TO $7M", "desc": "SBA-certified. Streamlined procurement path. Reduces acquisition timeline by 60%+."},
            {"title": "5,100+ DEPLOYMENT-READY FACILITIES", "desc": "Nationwide operational coverage through eScreen/Quest. Activate within 24 hours of award."},
            {"title": "SWFT AUTHORIZED &mdash; TOP 10% NATIONALLY", "desc": "3+ consecutive years DCSA authorization. Electronic submission to DCSA &amp; FBI CJIS."},
            {"title": "ZERO COMPLIANCE DEFICIENCIES", "desc": "1,500+ regulated deliveries across DOT, SAMHSA, HIPAA, and AABB environments. Fully auditable."},
            {"title": "TWIC-CLEARED SECURE ACCESS", "desc": "Credentialed for ports, VA medical centers, DoD installations, and restricted federal facilities."},
            {"title": "MULTI-STATE, MULTI-SECTOR PRIME", "desc": "7+ years. Licensed in MI, GA, FL, MD. Active: SAM.gov, SIGMA, City of Detroit, BidNet, Oracle, Bonfire."},
        ],
        "naics": "541611 | 541614 | 541618 | 541690 | 541990 | 621511 | 621999 | 561611 | 561612 | 485991 | 492110 | 484230 | 423450",
    },
    "drug_testing": {
        "gold_bar_title": "DRUG &amp; ALCOHOL TESTING &mdash; THIRD-PARTY ADMINISTRATION",
        "gold_bar_subtitle": "DOT &bull; FTA &bull; SAMHSA &bull; EDWOSB Sole-Source Eligible Up to $7M",
        "overview": (
            '<strong>DEE DAVIS INC.</strong> is an <strong>SBA-certified EDWOSB</strong> delivering '
            'federally compliant drug and alcohol testing programs as a licensed Third-Party Administrator. '
            'With <strong>5,100+ collection sites</strong> nationwide through eScreen/Quest Diagnostics, '
            'DDI provides <strong>same-day activation</strong>, SAMHSA-certified laboratory processing, '
            'MRO review, random selection, and full 49 CFR Part 40/655 compliance management. '
            '<strong>Zero compliance deficiencies</strong> across 1,500+ regulated collections.'
        ),
        "framework_line": "SERVICE MODEL: Enroll &rarr; Randomize &rarr; Collect &rarr; Certify &rarr; Report &rarr; Comply",
        "competencies_header": "CORE COMPETENCIES &mdash; FEDERALLY REGULATED TESTING OPERATIONS",
        "competencies": [
            {"title": "DOT/FTA Compliance Programs", "desc": "Full 49 CFR Parts 40 &amp; 655 administration. Pre-employment, random, post-accident, reasonable suspicion, return-to-duty, follow-up", "style": "c-primary"},
            {"title": "SAMHSA-Certified Lab Network", "desc": "Specimens processed through HHS-certified laboratories. Chain-of-custody integrity. 24-48 hour turnaround standard", "style": "c-light4"},
            {"title": "Medical Review Officer (MRO)", "desc": "Licensed physician MRO review of all non-negative results. Split specimen procedures. Federal regulation compliant", "style": "c-light2"},
            {"title": "Consortium &amp; Pool Management", "desc": "Random selection management for 50-10,000+ safety-sensitive employees. DOT-compliant random rate maintenance", "style": "c-light3"},
            {"title": "Breath Alcohol Testing (BAT)", "desc": "Evidential breath testing with certified BATs. DOT-approved devices. Real-time electronic reporting", "style": "c-light1"},
            {"title": "Supervisor Training &amp; Compliance", "desc": "Reasonable suspicion training programs. Supervisor certification. Policy development. Annual compliance audits", "style": "c-light5"},
        ],
        "past_performance_header": "PAST PERFORMANCE &mdash; VERIFIED TRACK RECORD",
        "past_performance": [
            {"title": "TRANSIT AUTHORITY TPA CONTRACTS", "desc": "DOT/FTA drug &amp; alcohol program administration for municipal transit systems. Zero audit findings."},
            {"title": "5,100+ ACTIVE COLLECTION SITES", "desc": "Nationwide coverage via eScreen/Quest Diagnostics. Same-day specimen collection. 98%+ on-time reporting."},
            {"title": "FEDERAL &amp; STATE AGENCY PROGRAMS", "desc": "Compliant testing programs for safety-sensitive workforces. Full regulatory documentation maintained."},
            {"title": "1,500+ REGULATED COLLECTIONS", "desc": "Chain-of-custody specimen handling. Zero deficiencies. DOT, SAMHSA, and HIPAA compliant."},
            {"title": "CONSORTIUM MANAGEMENT", "desc": "Random pool administration across multiple employers. DOT-compliant selection rates. Quarterly reporting."},
            {"title": "SUPERVISOR TRAINING DELIVERY", "desc": "Reasonable suspicion certification. 100+ supervisors trained. Regulatory curriculum maintained."},
        ],
        "differentiators": [
            {"title": "EDWOSB SOLE-SOURCE ELIGIBLE &mdash; UP TO $7M", "desc": "SBA-certified. Streamlined procurement. Reduces acquisition timeline by 60%+."},
            {"title": "5,100+ COLLECTION SITES &mdash; NATIONWIDE", "desc": "eScreen/Quest network. Activate within 24 hours of award. No geographic limitations."},
            {"title": "ZERO COMPLIANCE DEFICIENCIES", "desc": "1,500+ regulated collections. Full 49 CFR Parts 40 &amp; 655 adherence. Audit-ready documentation."},
            {"title": "SAME-DAY ACTIVATION CAPABILITY", "desc": "Program enrollment and first collection within 24 hours. No ramp-up delays."},
            {"title": "ELECTRONIC REPORTING PLATFORM", "desc": "Real-time results, random selections, and compliance tracking. Employer portal access. CCF automation."},
            {"title": "MULTI-STATE, MULTI-SECTOR PRIME", "desc": "7+ years. Licensed in MI, GA, FL, MD. Active: SAM.gov, SIGMA, City of Detroit, BidNet, Oracle."},
        ],
        "naics": "621511 | 621999 | 541380 | 541611 | 541614 | 561611 | 621112",
    },
    "fingerprinting": {
        "gold_bar_title": "FINGERPRINTING &amp; BACKGROUND SCREENING SERVICES",
        "gold_bar_subtitle": "DCSA &bull; FBI &bull; SWFT Authorized &bull; EDWOSB Sole-Source Eligible Up to $7M",
        "overview": (
            '<strong>DEE DAVIS INC.</strong> is an <strong>SBA-certified EDWOSB</strong> and '
            '<strong>DCSA-authorized SWFT provider</strong> delivering electronic fingerprinting '
            'and background screening for federal, state, and commercial clients. DDI operates '
            '<strong>mobile and fixed-site LiveScan</strong> capabilities with direct electronic '
            'submission to DCSA and FBI CJIS. <strong>3+ consecutive years</strong> SWFT authorization. '
            '<strong>Top 10% nationally</strong>. 24-48 hour turnaround. Zero rejection rate.'
        ),
        "framework_line": "SERVICE MODEL: Schedule &rarr; Capture &rarr; Transmit &rarr; Verify &rarr; Report &rarr; Archive",
        "competencies_header": "CORE COMPETENCIES &mdash; FEDERAL SECURITY CREDENTIALING",
        "competencies": [
            {"title": "DCSA SWFT Electronic Fingerprinting", "desc": "Authorized Secure Web Fingerprint Transmission provider. Direct electronic submission to DCSA &amp; FBI CJIS databases", "style": "c-primary"},
            {"title": "FBI FD-258 Card Processing", "desc": "Ink &amp; electronic capture. NCHC, CHRC, NICS submissions. Federal, state, and local criminal history checks", "style": "c-light3"},
            {"title": "Mobile LiveScan Operations", "desc": "Deployable fingerprinting teams for on-site captures at military installations, federal buildings, and contractor facilities", "style": "c-light2"},
            {"title": "Personnel Vetting Support", "desc": "Background investigation support. SF-86 processing facilitation. Security clearance fingerprint requirements", "style": "c-light1"},
            {"title": "State Licensing Fingerprints", "desc": "LARA, DCFS, education, healthcare licensing. State-specific submission routing. Rapid turnaround", "style": "c-light4"},
            {"title": "Badging &amp; Credentialing", "desc": "TWIC, CAC, PIV enrollment support. ID verification. Secure facility access processing", "style": "c-light5"},
        ],
        "past_performance_header": "PAST PERFORMANCE &mdash; VERIFIED TRACK RECORD",
        "past_performance": [
            {"title": "4+ FEDERAL INSTALLATION BPAs", "desc": "SWFT fingerprinting at DoD installations. DCSA/FBI electronic submissions. 24-48 hour turnaround."},
            {"title": "DCSA SWFT AUTHORIZED &mdash; 3+ YEARS", "desc": "Continuous authorization. Top 10% nationally. Zero rejection rate on electronic submissions."},
            {"title": "MOBILE DEPLOYMENT CAPABILITY", "desc": "On-site captures at military bases, VA centers, and federal buildings. Same-day turnaround available."},
            {"title": "STATE LICENSING PROGRAMS", "desc": "LARA, DCFS, education and healthcare licensing fingerprints. Multi-state routing and compliance."},
            {"title": "ZERO REJECTION RATE", "desc": "100% acceptance on electronic submissions. Quality-controlled capture process. Audit-ready documentation."},
            {"title": "TWIC &amp; SECURE FACILITY ACCESS", "desc": "TSA-credentialed operators. Fingerprinting at restricted access locations. DoD, VA, port facilities."},
        ],
        "differentiators": [
            {"title": "EDWOSB SOLE-SOURCE ELIGIBLE &mdash; UP TO $7M", "desc": "SBA-certified. Streamlined procurement. Reduces acquisition timeline by 60%+."},
            {"title": "SWFT AUTHORIZED &mdash; TOP 10% NATIONALLY", "desc": "3+ consecutive years DCSA authorization. Direct electronic submission to FBI CJIS."},
            {"title": "MOBILE &amp; FIXED-SITE CAPABLE", "desc": "Deploy to any federal installation, military base, or contractor facility. 48-hour mobilization."},
            {"title": "ZERO REJECTION RATE", "desc": "100% acceptance on electronic fingerprint submissions. Quality-controlled LiveScan capture."},
            {"title": "TWIC-CLEARED SECURE ACCESS", "desc": "TSA credentialed. Authorized for ports, VA medical centers, DoD installations, restricted facilities."},
            {"title": "MULTI-STATE, MULTI-SECTOR PRIME", "desc": "7+ years. Licensed in MI, GA, FL, MD. Active: SAM.gov, SIGMA, City of Detroit, BidNet, Oracle."},
        ],
        "naics": "561611 | 561612 | 541611 | 541990 | 561499 | 922190",
    },
    "nemt": {
        "gold_bar_title": "NON-EMERGENCY MEDICAL TRANSPORTATION",
        "gold_bar_subtitle": "Medicaid &bull; VA &bull; DOT-Regulated &bull; EDWOSB Sole-Source Eligible Up to $7M",
        "overview": (
            '<strong>DEE DAVIS INC.</strong> is an <strong>SBA-certified EDWOSB</strong> providing '
            '<strong>DOT-regulated non-emergency medical transportation</strong> for Medicaid, VA, '
            'and state/federal healthcare programs. DDI operates as a <strong>licensed transportation '
            'broker</strong> (MC-1647572) with fleet coordination, ADA-compliant vehicle dispatch, '
            'and real-time tracking across <strong>multi-state service areas</strong>. HIPAA-compliant. '
            'Wheelchair-accessible. Zero missed appointments.'
        ),
        "framework_line": "SERVICE MODEL: Authorize &rarr; Schedule &rarr; Dispatch &rarr; Transport &rarr; Verify &rarr; Report",
        "competencies_header": "CORE COMPETENCIES &mdash; REGULATED MEDICAL TRANSPORTATION",
        "competencies": [
            {"title": "Medicaid NEMT Brokerage", "desc": "State-contracted NEMT coordination. Eligibility verification, prior authorization, trip scheduling, provider network management", "style": "c-primary"},
            {"title": "VA Medical Transportation", "desc": "Veteran transport to VA medical centers and CBOCs. Wheelchair van, stretcher, ambulatory. DAV coordination", "style": "c-light1"},
            {"title": "ADA-Compliant Fleet", "desc": "Wheelchair-accessible vehicles, stretcher transport, bariatric capacity. DOT-inspected fleet. CDL-licensed drivers", "style": "c-light6"},
            {"title": "Real-Time Dispatch &amp; Tracking", "desc": "GPS-enabled fleet management. Automated scheduling. On-time performance monitoring. Electronic trip verification", "style": "c-light3"},
            {"title": "Medical Courier Services", "desc": "Chain-of-custody specimen transport, pharmaceutical delivery, medical records. Temperature-controlled logistics", "style": "c-light2"},
            {"title": "Compliance &amp; Reporting", "desc": "HIPAA, DOT, state Medicaid compliance. Performance reporting, complaint resolution, quality assurance programs", "style": "c-light4"},
        ],
        "past_performance_header": "PAST PERFORMANCE &mdash; VERIFIED TRACK RECORD",
        "past_performance": [
            {"title": "MEDICAID NEMT OPERATIONS", "desc": "Multi-county NEMT coordination. Eligibility verification and trip authorization. On-time rate 98%+."},
            {"title": "VA MEDICAL CENTER TRANSPORT", "desc": "Wheelchair van and ambulatory transport for veterans. Multi-facility routing. Zero missed appointments."},
            {"title": "1,500+ MEDICAL DELIVERIES", "desc": "Chain-of-custody specimen and pharmaceutical transport. Temperature-controlled. Zero compliance deficiencies."},
            {"title": "DOT-REGULATED OPERATIONS", "desc": "MC-1647572. CDL-licensed operators. DOT vehicle inspections. Drug/alcohol testing program compliant."},
            {"title": "ADA-COMPLIANT FLEET MANAGEMENT", "desc": "Wheelchair, stretcher, and bariatric transport capability. Vehicle maintenance program. Driver training."},
            {"title": "MDHHS COMMUNITY PARTNER", "desc": "Official State of Michigan DHHS recognition. Healthcare access coordination for underserved populations."},
        ],
        "differentiators": [
            {"title": "EDWOSB SOLE-SOURCE ELIGIBLE &mdash; UP TO $7M", "desc": "SBA-certified. Streamlined procurement. Reduces acquisition timeline by 60%+."},
            {"title": "LICENSED TRANSPORTATION BROKER", "desc": "MC-1647572, DOT-4250594. Federal operating authority. Multi-state service area."},
            {"title": "ZERO MISSED APPOINTMENTS", "desc": "98%+ on-time rate. GPS tracking. Automated dispatch. Real-time performance monitoring."},
            {"title": "ADA &amp; HIPAA COMPLIANT", "desc": "Wheelchair, stretcher, bariatric transport. Patient privacy protections. Electronic trip verification."},
            {"title": "TWIC-CLEARED SECURE ACCESS", "desc": "TSA credentialed for VA medical centers and restricted healthcare facilities."},
            {"title": "MULTI-STATE, MULTI-SECTOR PRIME", "desc": "7+ years. Licensed in MI, GA, FL, MD. Active: SAM.gov, SIGMA, Oracle, Bonfire."},
        ],
        "naics": "485991 | 485999 | 485310 | 492110 | 484230 | 621910 | 561599",
    },
    "courier": {
        "gold_bar_title": "COURIER &amp; LOGISTICS SERVICES",
        "gold_bar_subtitle": "DOT-Licensed &bull; Chain-of-Custody &bull; EDWOSB Sole-Source Eligible Up to $7M",
        "overview": (
            '<strong>DEE DAVIS INC.</strong> is an <strong>SBA-certified EDWOSB</strong> and '
            '<strong>DOT-licensed logistics firm</strong> (MC-1647572) providing time-critical courier, '
            'freight brokerage, and chain-of-custody delivery for federal, state, and healthcare clients. '
            'DDI executes <strong>1,500+ regulated deliveries</strong> with <strong>zero compliance '
            'deficiencies</strong> across DOT, SAMHSA, HIPAA, and AABB environments. Temperature-controlled. '
            'Same-day capable. TWIC-credentialed for secure facility access.'
        ),
        "framework_line": "SERVICE MODEL: Receive &rarr; Route &rarr; Dispatch &rarr; Track &rarr; Deliver &rarr; Verify",
        "competencies_header": "CORE COMPETENCIES &mdash; REGULATED DELIVERY OPERATIONS",
        "competencies": [
            {"title": "Chain-of-Custody Transport", "desc": "Medical specimens, pharmaceuticals, legal documents. Tamper-evident packaging. Electronic chain-of-custody documentation", "style": "c-primary"},
            {"title": "Time-Critical Delivery", "desc": "Same-day, next-day, scheduled routes. GPS tracking. Real-time delivery confirmation. SLA performance monitoring", "style": "c-light2"},
            {"title": "Licensed Freight Brokerage", "desc": "MC-1647572, DOT-4250594. Federal operating authority. LTL, FTL, and specialized freight coordination", "style": "c-light3"},
            {"title": "Temperature-Controlled Logistics", "desc": "Cold chain management for specimens, biologics, pharmaceuticals. Continuous temperature monitoring and logging", "style": "c-light1"},
            {"title": "Secure Facility Delivery", "desc": "TWIC-credentialed drivers. VA medical centers, DoD installations, federal courthouses, restricted facilities", "style": "c-light4"},
            {"title": "Fleet Coordination", "desc": "DOT-regulated fleet management. CDL-licensed operators. Vehicle maintenance. Drug/alcohol testing compliance", "style": "c-light5"},
        ],
        "past_performance_header": "PAST PERFORMANCE &mdash; VERIFIED TRACK RECORD",
        "past_performance": [
            {"title": "1,500+ REGULATED DELIVERIES", "desc": "Chain-of-custody medical, pharmaceutical, and specimen transport. Zero deficiencies. Fully auditable."},
            {"title": "VA MEDICAL CENTER COURIER", "desc": "Medical records, specimens, and supply delivery to VA facilities. TWIC-cleared. Same-day turnaround."},
            {"title": "DOT-LICENSED OPERATIONS", "desc": "MC-1647572. Federal operating authority. CDL operators. Compliant drug/alcohol testing program."},
            {"title": "TEMPERATURE-CONTROLLED TRANSPORT", "desc": "Cold chain integrity for biologics and specimens. Continuous monitoring. HIPAA and AABB compliant."},
            {"title": "FEDERAL FACILITY DELIVERY", "desc": "Secure deliveries to DoD, VA, and federal courthouse facilities. TWIC and background-cleared personnel."},
            {"title": "SAME-DAY CAPABILITY", "desc": "Emergency and time-critical delivery. GPS tracking. Electronic proof of delivery. 98%+ on-time rate."},
        ],
        "differentiators": [
            {"title": "EDWOSB SOLE-SOURCE ELIGIBLE &mdash; UP TO $7M", "desc": "SBA-certified. Streamlined procurement. Reduces acquisition timeline by 60%+."},
            {"title": "LICENSED FREIGHT BROKER", "desc": "MC-1647572, DOT-4250594. Federal operating authority. Multi-state service area."},
            {"title": "ZERO COMPLIANCE DEFICIENCIES", "desc": "1,500+ regulated deliveries. DOT, SAMHSA, HIPAA, AABB environments. Fully auditable."},
            {"title": "TWIC-CLEARED SECURE ACCESS", "desc": "TSA credentialed for ports, VA medical centers, DoD installations, restricted federal facilities."},
            {"title": "TEMPERATURE-CONTROLLED CAPABILITY", "desc": "Cold chain logistics. Continuous monitoring. Biologics, specimens, pharmaceuticals."},
            {"title": "MULTI-STATE, MULTI-SECTOR PRIME", "desc": "7+ years. Licensed in MI, GA, FL, MD. Active: SAM.gov, SIGMA, Oracle, BidNet."},
        ],
        "naics": "492110 | 484230 | 484110 | 484121 | 493110 | 488510 | 561910",
    },
}

# Fallback: if a sector key isn't defined, use "main" content
def _get_sector_content(sector: str) -> Dict:
    return SECTOR_CONTENT.get(sector, SECTOR_CONTENT["main"])

def _get_sector_colors(sector: str) -> Dict:
    return SECTOR_COLORS.get(sector, SECTOR_COLORS["main"])


# ═══════════════════════════════════════════════════════════════════════════════
# IMAGE UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

ESSENTIALS_DIR = Path(__file__).parent / "BIDS:RESOURCES" / "ESSENTIALS"

def _img_to_base64(path: str) -> str:
    """Convert image file to base64 data URI."""
    p = Path(path)
    if not p.exists():
        return ""
    suffix = p.suffix.lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "webp": "webp"}.get(suffix, "png")
    with open(p, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{mime};base64,{encoded}"


def _extract_logo_from_existing() -> str:
    """Extract DDI logo base64 from an existing cap statement."""
    bids_dir = Path(__file__).parent / "BIDS:RESOURCES"
    for html_file in bids_dir.rglob("*Capability_Statement*.html"):
        try:
            content = html_file.read_text(errors="ignore")
            match = re.search(r'class="h-logo"[^>]*>\s*<img\s+src="(data:image/[^"]+)"', content)
            if match:
                return match.group(1)
            match = re.search(r'class="logo-img"[^>]*src="(data:image/[^"]+)"', content)
            if match:
                return match.group(1)
            match = re.search(r'<img[^>]+src="(data:image/png;base64,[A-Za-z0-9+/=]{100,})"[^>]+alt="[^"]*[Ll]ogo', content)
            if match:
                return match.group(1)
        except Exception:
            continue
    return ""


def _get_image_assets() -> Dict[str, str]:
    """Load all image assets from ESSENTIALS folder."""
    assets = {"logo": "", "headshot": "", "cert_badges": [], "partner_logos": []}

    logo_path = ESSENTIALS_DIR / "DDI Logo.png"
    if logo_path.exists():
        assets["logo"] = _img_to_base64(str(logo_path))
    else:
        assets["logo"] = _extract_logo_from_existing()

    for name in ["HEADSHOT.jpg", "HEADSHOT.png", "headshot.jpg"]:
        hs_path = ESSENTIALS_DIR / name
        if hs_path.exists():
            assets["headshot"] = _img_to_base64(str(hs_path))
            break

    cert_names = ["Image.jpg", "EDWOSB.png", "WBENC.png", "TWIC.png", "edwosb_badge.png", "wbenc_badge.png"]
    for name in cert_names:
        cp = ESSENTIALS_DIR / name
        if cp.exists():
            assets["cert_badges"].append(_img_to_base64(str(cp)))

    partner_names = ["Quest.png", "DDC.png", "3D Ink.png", "Champion.png", "MDHHS.png",
                     "quest.png", "ddc.png", "champion.png", "mdhhs.png"]
    seen = set()
    for name in partner_names:
        pp = ESSENTIALS_DIR / name
        if pp.exists() and name.lower() not in seen:
            assets["partner_logos"].append(_img_to_base64(str(pp)))
            seen.add(name.lower())

    return assets


# ═══════════════════════════════════════════════════════════════════════════════
# HTML BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

def build_competencies_html(competencies: List[Dict]) -> str:
    """Build the competency grid HTML."""
    html_parts = []
    for comp in competencies:
        style = comp.get("style", "c-light1")
        html_parts.append(
            f'      <div class="c {style}">\n'
            f'        <h4>{comp["title"]}</h4>\n'
            f'        <p>{comp["desc"]}</p>\n'
            f'      </div>'
        )
    return "\n".join(html_parts)


def build_list_html(items: List[Dict]) -> str:
    """Build star-bulleted list HTML for past performance or differentiators."""
    html_parts = []
    for item in items:
        html_parts.append(
            f'          <li><span class="wt">{item["title"]}</span><br>'
            f'<span class="wd">{item["desc"]}</span></li>'
        )
    return "\n".join(html_parts)


def build_cert_badges_html(badge_b64_list: List[str]) -> str:
    """Build certification badge images HTML."""
    return "\n".join(f'      <img src="{b64}" alt="Certification">' for b64 in badge_b64_list if b64)


def build_partner_logos_html(partner_b64_list: List[str]) -> str:
    """Build partner logo images HTML."""
    return "\n".join(f'      <img src="{b64}" alt="Partner">' for b64 in partner_b64_list if b64)


def generate_capability_statement(
    sector: str = "main",
    agency_name: Optional[str] = None,
    solicitation_number: Optional[str] = None,
    service_description: Optional[str] = None,
    custom_overview: Optional[str] = None,
    custom_competencies: Optional[List[Dict]] = None,
    custom_past_performance: Optional[List[Dict]] = None,
    custom_differentiators: Optional[List[Dict]] = None,
    custom_naics: Optional[str] = None,
    output_path: Optional[str] = None,
) -> str:
    """
    Generate a capability statement HTML file.

    Args:
        sector: Service sector key (e.g., 'drug_testing', 'fingerprinting', 'nemt', 'courier', 'main')
        agency_name: Target agency name (for gold bar subtitle)
        solicitation_number: Solicitation reference number
        service_description: Override gold bar title
        custom_overview: Override overview paragraph
        custom_competencies: Override competencies list
        custom_past_performance: Override past performance list
        custom_differentiators: Override differentiators list
        custom_naics: Override NAICS codes
        output_path: Where to save the HTML file

    Returns:
        The generated HTML string
    """
    colors = _get_sector_colors(sector)
    content = _get_sector_content(sector)
    assets = _get_image_assets()

    template_path = Path(__file__).parent / "capability_statement_template.html"
    template = template_path.read_text()

    gold_bar_subtitle = content["gold_bar_subtitle"]
    if agency_name and solicitation_number:
        gold_bar_subtitle = f"Prepared for {agency_name} &bull; {solicitation_number} &bull; EDWOSB Sole-Source Eligible"
    elif agency_name:
        gold_bar_subtitle = f"Prepared for {agency_name} &bull; EDWOSB Sole-Source Eligible Up to $7M"

    replacements = {
        "{{PRIMARY_COLOR}}": colors["primary"],
        "{{SECONDARY_COLOR}}": colors["secondary"],
        "{{ACCENT_COLOR}}": colors["accent"],
        "{{ACCENT_COLOR_DARK}}": colors["accent_dark"],
        "{{GOLD_BAR_TEXT_COLOR}}": colors["gold_bar_text"],
        "{{COMP_COLUMNS}}": str(colors["comp_columns"]),
        "{{LOGO_BASE64}}": assets["logo"],
        "{{HEADSHOT_BASE64}}": assets["headshot"],
        "{{GOLD_BAR_TITLE}}": service_description or content["gold_bar_title"],
        "{{GOLD_BAR_SUBTITLE}}": gold_bar_subtitle,
        "{{OVERVIEW_HTML}}": custom_overview or content["overview"],
        "{{FRAMEWORK_LINE}}": content["framework_line"],
        "{{COMPETENCIES_HEADER}}": content["competencies_header"],
        "{{COMPETENCIES_GRID_HTML}}": build_competencies_html(custom_competencies or content["competencies"]),
        "{{PAST_PERFORMANCE_HEADER}}": content["past_performance_header"],
        "{{PAST_PERFORMANCE_HTML}}": build_list_html(custom_past_performance or content["past_performance"]),
        "{{DIFFERENTIATORS_HTML}}": build_list_html(custom_differentiators or content["differentiators"]),
        "{{CERT_BADGES_HTML}}": build_cert_badges_html(assets["cert_badges"]),
        "{{PARTNER_LOGOS_HTML}}": build_partner_logos_html(assets["partner_logos"]),
        "{{NAICS_CODES}}": custom_naics or content["naics"],
    }

    html = template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    if output_path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(html)

    return html


# ═══════════════════════════════════════════════════════════════════════════════
# API HANDLER — called from api_server.py
# ═══════════════════════════════════════════════════════════════════════════════

def handle_generate_capability_statement(
    sector: str = "main",
    agency_name: Optional[str] = None,
    solicitation_number: Optional[str] = None,
    service_description: Optional[str] = None,
    custom_overview: Optional[str] = None,
    custom_naics: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> Dict:
    """
    Handler for generating capability statements from the API or direct call.

    Returns:
        Dict with success status, html content, and file path.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_agency = (agency_name or "General").replace(" ", "_").replace("/", "-")
    filename = f"DDI_{safe_agency}_{sector}_Capability_Statement_{timestamp}.html"

    if output_dir:
        out_path = Path(output_dir) / filename
    else:
        out_path = Path(__file__).parent / "generated_capability_statements" / filename
        out_path.parent.mkdir(exist_ok=True)

    html = generate_capability_statement(
        sector=sector,
        agency_name=agency_name,
        solicitation_number=solicitation_number,
        service_description=service_description,
        custom_overview=custom_overview,
        custom_naics=custom_naics,
        output_path=str(out_path),
    )

    return {
        "success": True,
        "html_file": str(out_path),
        "filename": filename,
        "sector": sector,
        "agency": agency_name,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# AVAILABLE SECTORS — for frontend dropdown
# ═══════════════════════════════════════════════════════════════════════════════

AVAILABLE_SECTORS = [
    {"key": "main", "label": "Main — Contract Management Firm (All Sectors)"},
    {"key": "drug_testing", "label": "Drug & Alcohol Testing / TPA"},
    {"key": "fingerprinting", "label": "Fingerprinting / Background Screening / SWFT"},
    {"key": "nemt", "label": "NEMT / Medical Transportation"},
    {"key": "courier", "label": "Courier / Delivery / Logistics"},
    {"key": "dna_testing", "label": "DNA / Paternity / Genetic Testing"},
    {"key": "janitorial", "label": "Janitorial / Grounds Maintenance / Facilities"},
    {"key": "industrial", "label": "Industrial Supplies / Equipment / Parts"},
    {"key": "notary", "label": "Notary / Signing Agent / Legal Services"},
    {"key": "professional", "label": "Professional Services / Consulting / Staffing"},
    {"key": "georgia", "label": "Georgia State Agencies (State Override)"},
]
