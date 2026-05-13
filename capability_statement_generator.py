"""
Capability Statement Generator — v4 Engine
Produces cap statements matching the NEMT reference design:
  Header → Title Bar → EDWOSB Box → Competencies Grid → Service Capabilities →
  Differentiators → Past Performance Grid → NAICS Strip → Cert Badges → Footer
Each sector gets its own color scheme. Structure stays identical.
"""

import os
import re
import base64
from pathlib import Path
from typing import Dict, List, Optional

from company_info import (
    CAGE_CODE, UEI, DUNS, PHONE_PRIMARY, EMAIL, ADDRESS_FULL, WEBSITE,
)


ESSENTIALS_DIR = Path(__file__).parent / "BIDS:RESOURCES" / "ESSENTIALS"

DEFAULT_HEADER_CREDS = [
    f"CAGE: {CAGE_CODE}", f"UEI: {UEI}", f"DUNS: {DUNS}", "SAM.gov: ACTIVE",
]


SECTOR_COLORS = {
    "main": {
        "primary": "#0a1628",
        "secondary": "#1e3a5f",
        "accent": "#c5963a",
        "accent_dark": "#b8860b",
        "comp_columns": 4,
    },
    "fingerprinting": {
        "primary": "#0f2b1a",
        "secondary": "#1a5632",
        "accent": "#c5963a",
        "accent_dark": "#b8860b",
        "comp_columns": 4,
    },
    "nemt": {
        "primary": "#1e3a5f",
        "secondary": "#991b1b",
        "accent": "#dc2626",
        "accent_dark": "#991b1b",
        "comp_columns": 4,
    },
    "drug_testing": {
        "primary": "#3b0764",
        "secondary": "#7c3aed",
        "accent": "#a78bfa",
        "accent_dark": "#6b21a8",
        "comp_columns": 4,
    },
    "dna_testing": {
        "primary": "#134e4a",
        "secondary": "#0d9488",
        "accent": "#2dd4bf",
        "accent_dark": "#0f766e",
        "comp_columns": 4,
    },
    "janitorial": {
        "primary": "#451a03",
        "secondary": "#b45309",
        "accent": "#f59e0b",
        "accent_dark": "#92400e",
        "comp_columns": 4,
    },
    "industrial": {
        "primary": "#1e293b",
        "secondary": "#475569",
        "accent": "#94a3b8",
        "accent_dark": "#334155",
        "comp_columns": 4,
    },
    "courier": {
        "primary": "#7c2d12",
        "secondary": "#ea580c",
        "accent": "#fb923c",
        "accent_dark": "#c2410c",
        "comp_columns": 4,
    },
    "notary": {
        "primary": "#581c87",
        "secondary": "#a78bdb",
        "accent": "#e879a8",
        "accent_dark": "#9333ea",
        "comp_columns": 4,
    },
    "professional": {
        "primary": "#171717",
        "secondary": "#404040",
        "accent": "#a3a3a3",
        "accent_dark": "#525252",
        "comp_columns": 4,
    },
    "georgia": {
        "primary": "#7f1d1d",
        "secondary": "#b91c1c",
        "accent": "#f87171",
        "accent_dark": "#991b1b",
        "comp_columns": 4,
    },
}


SECTOR_CONTENT = {
    "main": {
        "service_model": "Identify &rarr; Bid &rarr; Award &rarr; Fulfill &rarr; Execute &rarr; Report",
        "header_tag": "Contract Management TPA &bull; Federal &bull; State &bull; MCO",
        "header_creds": [
            *DEFAULT_HEADER_CREDS,
            "NPI: 1538939111",
        ],
        "gold_bar_title": "CONTRACT MANAGEMENT FIRM",
        "overview": (
            '<strong>EDWOSB-Certified &bull; SBA Verified &bull; NPI: 1538939111 &bull; Woman-Owned Small Business</strong> &mdash; '
            'Dee Davis Inc. (DDI) is an SBA-certified EDWOSB prime contractor and Third Party Administrator delivering end-to-end contract '
            'management across federal, state, and managed care sectors. <strong>Active HAP CareSource NEMT TPA contract</strong> managing '
            '4,500+ dual-eligible members. <strong>HAVEN disaster response program</strong> for automatic member relocation during '
            'FEMA-declared events. 5,100+ managed service locations nationwide through eScreen/Quest. Multi-state MCO expansion in progress. '
            'FBI Appendix F fingerprinting. DOT/SAMHSA drug testing. DNA testing. Medical courier. Zero compliance deficiencies.'
        ),
        "competencies_header": "CORE COMPETENCIES",
        "competencies": [
            {"title": "NEMT &amp; Personal Care TPA", "desc": "HAP CareSource HIDE SNP contract (live). 4,500+ dual-eligible members. NEMT benefit administration. Personal Care TPA (ADL, homemaker, companion). Zero-fleet model.", "style": "c-primary"},
            {"title": "HAVEN Disaster Response", "desc": "Automatic member relocation during FEMA events. Temporary housing, transport continuity, pharmacy access, care handoff. Pre-positioned partner network.", "style": "c-light1"},
            {"title": "Regulated Healthcare Operations", "desc": "DOT/FTA/SAMHSA drug &amp; alcohol TPA (5,100+ sites). AABB-accredited DNA testing. Medical specimen transport. Medicaid provider operations.", "style": "c-light2"},
            {"title": "Federal Security &amp; Credentialing", "desc": "FBI Appendix F fingerprinting (Kojak/Lakota). FD-258 ink cards. 99.5% acceptance rate. ATF/NFA trust fingerprinting.", "style": "c-light3"},
        ],
        "service_capabilities": [
            "NEMT TPA program administration for MCOs",
            "Personal Care TPA (ADL, homemaker, companion)",
            "HAVEN disaster response and member relocation",
            "DOT/FTA drug &amp; alcohol testing program administration",
            "FBI Appendix F electronic fingerprinting",
            "Medical specimen &amp; pharmaceutical courier",
            "AABB-accredited DNA and paternity testing",
            "Federal supply &amp; commodity contract execution",
            "Mobile notary &amp; document execution services",
            "Management consulting &amp; compliance auditing",
            "Fleet coordination &amp; freight brokerage",
            "HIPAA/DOT/SAMHSA compliance program design",
        ],
        "differentiators": [
            {"title": "HAP CareSource HIDE SNP &mdash; Live Contract", "desc": "Contracted NEMT TPA. 4,500+ dual-eligible members. Wayne and Macomb counties. Portal active. Trips running."},
            {"title": "HAVEN Disaster Response", "desc": "Automatic member safety activation during FEMA-declared emergencies. Transport, housing, pharmacy, care continuity."},
            {"title": "EDWOSB sole-source eligible &mdash; up to $7M", "desc": "SBA-certified. Streamlined procurement path. Reduces acquisition timeline by 60%+"},
            {"title": "5,100+ drug testing locations", "desc": "Nationwide coverage through eScreen/Quest. Same-day activation. Zero compliance deficiencies."},
            {"title": "Proven TPA model", "desc": "DDI primes the contract, credentialed partners execute. Single point of accountability for compliance and reporting."},
        ],
        "past_performance": [
            {"title": "HAP CareSource Michigan HIDE SNP (2026 &ndash; Present)", "desc": "Contracted NEMT TPA. Managing full NEMT benefit for 4,500+ dual-eligible members in Wayne and Macomb counties. Portal operational. Zero deficiencies."},
            {"title": "HAVEN Disaster Response Program (2026)", "desc": "Built and launched comprehensive disaster response for Medicaid populations. Transport, housing, pharmacy, and care partners pre-staged."},
            {"title": "Drug Testing TPA (Ongoing)", "desc": "DOT/FTA/SAMHSA-compliant program administration. 5,100+ sites via eScreen/Quest. Random pools, post-accident, pre-employment. Zero audit findings."},
        ],
        "naics_detailed": [
            {"code": "524292", "desc": "Third Party Admin of Insurance"},
            {"code": "485991", "desc": "Special Needs Transportation"},
            {"code": "621511", "desc": "Medical Laboratories"},
            {"code": "561611", "desc": "Investigation Services"},
            {"code": "624120", "desc": "Services for Elderly/Disabled"},
            {"code": "492110", "desc": "Couriers &amp; Express Delivery"},
        ],
        "cert_badges": [
            {"text": "EDWOSB", "cls": "gold"},
            {"text": "WOSB", "cls": "gold"},
            {"text": "WBENC WBE", "cls": ""},
            {"text": "MBE", "cls": ""},
            {"text": "SBE", "cls": ""},
            {"text": "E-Verify", "cls": "accent"},
            {"text": "NPI Active", "cls": "accent"},
        ],
        "footer_extra": "NPI: 1538939111",
        "naics": "524292 | 541611 | 541614 | 541618 | 541690 | 541990 | 621511 | 621999 | 561611 | 561612 | 485991 | 492110 | 484230 | 624120",
    },
    "nemt": {
        "service_model": "Authorize &rarr; Schedule &rarr; Dispatch &rarr; Transport &rarr; Document &rarr; Invoice",
        "header_tag": "NEMT TPA &bull; Personal Care TPA &bull; MCO Contract Management",
        "header_creds": [
            *DEFAULT_HEADER_CREDS,
            "NPI: 1538939111", "US DOT: 4250594", "MC: 1647572",
        ],
        "gold_bar_title": "NEMT &amp; PERSONAL CARE TPA &mdash; MANAGED CARE CONTRACT MANAGEMENT",
        "overview": (
            '<strong>EDWOSB-Certified &bull; SBA Verified &bull; NPI: 1538939111 &bull; Woman-Owned Small Business</strong> &mdash; '
            'Dee Davis Inc. (DDI) is the <strong>contracted NEMT TPA for HAP CareSource&rsquo;s Michigan HIDE SNP program</strong>, '
            'managing the full NEMT benefit for <strong>4,500+ dual-eligible members</strong> in Wayne and Macomb counties. '
            'DDI operates as a Contract Management TPA&mdash;not a transportation provider&mdash;administering scheduling, dispatch coordination, '
            'compliance documentation, and claims through credentialed transport partners. DDI also provides <strong>Personal Care TPA</strong> services '
            '(ADL support, homemaker, companion care) and <strong>HAVEN disaster response</strong> for automatic member relocation during FEMA-declared events. '
            'Zero-fleet model. Multi-state MCO expansion in progress.'
        ),
        "competencies_header": "CORE COMPETENCIES &mdash; MCO TPA OPERATIONS",
        "competencies": [
            {"title": "NEMT TPA Administration", "desc": "Full NEMT benefit management for MCOs. Scheduling, dispatch coordination, trip documentation, claims processing, quality assurance. Zero-fleet model with credentialed transport partners.", "style": "c-primary"},
            {"title": "Personal Care TPA", "desc": "ADL support, homemaker services, and companion care coordination for LTSS/MLTSS populations. DDI administers the benefit through credentialed care partner networks.", "style": "c-light1"},
            {"title": "HAVEN Disaster Response", "desc": "Automatic member safety activation during FEMA-declared events. Temporary housing coordination, transport continuity, pharmacy continuity, and care handoff.", "style": "c-light2"},
            {"title": "MCO Contract Management", "desc": "DDI primes the TPA contract. Credentialed partners execute transport and care services. Single point of accountability for compliance, reporting, and member outcomes.", "style": "c-light3"},
        ],
        "service_capabilities": [
            "NEMT TPA program administration for MCOs",
            "Personal care coordination (ADL, IADL, homemaker)",
            "Scheduling, dispatch, and trip management",
            "Credentialed transport partner network",
            "HIPAA-compliant documentation and reporting",
            "Electronic claims submission and reconciliation",
            "Real-time trip tracking and member communication",
            "HAVEN disaster response and member relocation",
            "Temporary housing coordination during emergencies",
            "Pharmacy continuity during displacement",
            "Quality assurance and compliance monitoring",
            "Dual-eligible and LTSS population expertise",
        ],
        "differentiators": [
            {"title": "HAP CareSource HIDE SNP &mdash; Live &amp; Operational", "desc": "Contracted NEMT TPA for Michigan HIDE SNP. Portal active. Trips running. 4,500+ dual-eligible members."},
            {"title": "Zero-Fleet Contract Management Model", "desc": "DDI administers the benefit at the TPA level. Credentialed transport partners execute under DDI management."},
            {"title": "HAVEN Disaster Response", "desc": "Automatic member relocation and continuity of care during FEMA-declared emergencies. Pre-positioned partner network."},
            {"title": "EDWOSB/WOSB Certified", "desc": "Supports MCO diversity contracting goals and federal small business requirements."},
            {"title": "Multi-State MCO Expansion", "desc": "Active outreach across MI, OH, GA, TN, TX, FL, LA, SC, MS, AL. Scalable TPA model."},
        ],
        "past_performance": [
            {"title": "HAP CareSource Michigan HIDE SNP (Jan 2026 &ndash; Present)", "desc": "Contracted NEMT TPA for HAP CareSource&rsquo;s MI Coordinated Health (HIDE SNP) program. Managing full NEMT benefit for 4,500+ dual-eligible members in Wayne and Macomb counties. Portal operational. Zero compliance deficiencies."},
            {"title": "HAVEN Disaster Response Program (2026)", "desc": "Built and launched disaster response program for Medicaid populations. Partner network includes transport, housing, pharmacy, and care coordination. Designed for automatic activation during FEMA-declared events."},
            {"title": "MCO TPA Expansion (2026 &ndash; Present)", "desc": "Active MCO outreach across 10 states. CareSource affiliate relationships. Personal Care TPA service line in development. Scalable contract management model."},
        ],
        "naics_detailed": [
            {"code": "485991", "desc": "Special Needs Transportation"},
            {"code": "524292", "desc": "Third Party Admin of Insurance"},
            {"code": "621999", "desc": "Miscellaneous Ambulatory Health"},
            {"code": "561499", "desc": "Other Business Support"},
            {"code": "485999", "desc": "All Other Transit &amp; Ground Passenger"},
            {"code": "624120", "desc": "Services for Elderly/Disabled"},
        ],
        "cert_badges": [
            {"text": "EDWOSB", "cls": "gold"},
            {"text": "WOSB", "cls": "gold"},
            {"text": "WBENC WBE", "cls": ""},
            {"text": "MBE", "cls": ""},
            {"text": "SBE", "cls": ""},
            {"text": "E-Verify", "cls": "accent"},
            {"text": "NPI Active", "cls": "accent"},
            {"text": "US DOT", "cls": "accent"},
        ],
        "footer_extra": "NPI: 1538939111 &nbsp;|&nbsp; US DOT: 4250594 &nbsp;|&nbsp; MC: 1647572",
        "naics": "485991 | 524292 | 621999 | 561499 | 485999 | 624120 | 492110",
    },
    "haven": {
        "service_model": "Declare &rarr; Activate &rarr; Relocate &rarr; Stabilize &rarr; Recover &rarr; Return",
        "header_tag": "Disaster Response TPA &bull; Member Relocation &bull; Care Continuity",
        "header_creds": [
            *DEFAULT_HEADER_CREDS,
            "NPI: 1538939111", "US DOT: 4250594", "MC: 1647572",
        ],
        "gold_bar_title": "HAVEN &mdash; DISASTER RESPONSE &amp; MEMBER SAFETY PROGRAM",
        "overview": (
            '<strong>EDWOSB-Certified &bull; SBA Verified &bull; NPI: 1538939111 &bull; Woman-Owned Small Business</strong> &mdash; '
            'Dee Davis Inc. (DDI) operates <strong>HAVEN</strong>&mdash;a comprehensive disaster response and member safety program '
            'designed for MCOs, Medicaid agencies, and health plans with vulnerable member populations. When FEMA declares a disaster, '
            'HAVEN activates automatically: <strong>member relocation</strong>, <strong>temporary housing</strong>, <strong>pharmacy continuity</strong>, '
            '<strong>transport coordination</strong>, and <strong>care handoff documentation</strong>. Pre-positioned partner network. '
            'Contract Management TPA model&mdash;DDI administers the program, credentialed partners execute. Critical for hurricane, tornado, flood, '
            'and wildfire exposure zones.'
        ),
        "competencies_header": "CORE COMPETENCIES &mdash; DISASTER RESPONSE OPERATIONS",
        "competencies": [
            {"title": "Automatic Disaster Activation", "desc": "FEMA declaration triggers immediate member safety protocol. No manual escalation required. Pre-staged partner network activates within hours.", "style": "c-primary"},
            {"title": "Member Relocation &amp; Housing", "desc": "Emergency transport to safe zones. Temporary housing placement (Wyndham, Red Roof, regional partners). ADA-accessible options. Family unit accommodation.", "style": "c-light1"},
            {"title": "Pharmacy &amp; Care Continuity", "desc": "Medication access during displacement. Prescription transfer coordination. Provider handoff documentation. HEDIS-relevant care continuity.", "style": "c-light2"},
            {"title": "TPA Contract Management", "desc": "DDI administers HAVEN at the program level. Transport, housing, pharmacy, and care partners operate under DDI coordination. Single point of accountability.", "style": "c-light3"},
        ],
        "service_capabilities": [
            "Automatic FEMA-declaration activation",
            "Member safety and wellness checks",
            "Emergency transport coordination",
            "Temporary housing placement",
            "Pharmacy access and prescription transfer",
            "Provider handoff and care continuity",
            "HEDIS-aligned documentation",
            "Family unit and ADA-accessible housing",
            "Post-disaster return coordination",
            "Real-time member location tracking",
            "MCO/agency reporting and compliance",
            "Hurricane, tornado, flood, wildfire coverage",
        ],
        "differentiators": [
            {"title": "Automatic Activation &mdash; No Escalation Required", "desc": "FEMA declaration = immediate partner network activation. Members protected within hours of disaster onset."},
            {"title": "Pre-Positioned Partner Network", "desc": "Transport, housing, pharmacy, and care partners contracted and staged before disaster season."},
            {"title": "TPA Model &mdash; Not a Vendor", "desc": "DDI administers HAVEN at the program level. MCOs get single-point accountability, not a vendor list."},
            {"title": "EDWOSB/WOSB Certified", "desc": "Supports MCO diversity contracting goals and federal small business requirements."},
            {"title": "Proven NEMT TPA Operations", "desc": "HAVEN built on DDI&rsquo;s active HAP CareSource HIDE SNP contract. Same infrastructure, disaster-extended."},
        ],
        "past_performance": [
            {"title": "HAP CareSource Michigan HIDE SNP (2026)", "desc": "Contracted NEMT TPA managing 4,500+ dual-eligible members. HAVEN disaster layer built on this operational foundation."},
            {"title": "HAVEN Partner Network (2026)", "desc": "Transport partners (MedRide, regional ambulette networks), housing partners (Wyndham, Red Roof), pharmacy continuity infrastructure. Pre-staged for activation."},
            {"title": "Multi-State MCO Outreach (2026)", "desc": "Active expansion across hurricane/tornado belt states: TX, FL, LA, MS, AL, GA, TN, SC. HAVEN positioned as differentiator."},
        ],
        "naics_detailed": [
            {"code": "524292", "desc": "Third Party Admin of Insurance"},
            {"code": "561499", "desc": "Other Business Support"},
            {"code": "561210", "desc": "Facilities Support Services"},
            {"code": "721110", "desc": "Hotels and Motels"},
            {"code": "485991", "desc": "Special Needs Transportation"},
            {"code": "624230", "desc": "Emergency &amp; Relief Services"},
        ],
        "cert_badges": [
            {"text": "EDWOSB", "cls": "gold"},
            {"text": "WOSB", "cls": "gold"},
            {"text": "WBENC WBE", "cls": ""},
            {"text": "MBE", "cls": ""},
            {"text": "SBE", "cls": ""},
            {"text": "E-Verify", "cls": "accent"},
            {"text": "NPI Active", "cls": "accent"},
            {"text": "HAVEN Ready", "cls": "accent"},
        ],
        "footer_extra": "HAVEN Disaster Response Program &nbsp;|&nbsp; NPI: 1538939111",
        "naics": "524292 | 561499 | 561210 | 721110 | 485991 | 624230",
    },
    "notary": {
        "service_model": "Engage &rarr; Search &rarr; Commit &rarr; Clear &rarr; Close &rarr; Record",
        "header_tag": "Title &amp; Settlement Services &bull; Notary &bull; Contract Management",
        "header_creds": [
            *DEFAULT_HEADER_CREDS,
        ],
        "gold_bar_title": "NOTARY &amp; LEGAL SUPPORT SERVICES",
        "overview": (
            '<strong>EDWOSB-Certified &bull; SBA Verified &bull; MWBE &bull; Woman-Owned Small Business</strong> &mdash; '
            'Dee Davis Inc. (DDI) is an EDWOSB-certified contract management firm providing title and settlement '
            'services, mobile and remote online notarization, apostille services, estate planning document '
            'execution, and permit running for government agencies, redevelopment authorities, and real estate '
            'programs. DDI manages the full title lifecycle through its partnership with '
            '<strong>Empora Title</strong>&mdash;a digital-first title company licensed in '
            '<strong>Pennsylvania, Ohio, Indiana, Kentucky, Missouri, Texas, and Florida</strong>. '
            'NNA-certified signing agency. CNDTA certified. E&amp;O insured. MWBE-certified.'
        ),
        "competencies_header": "CORE COMPETENCIES",
        "competencies": [
            {"title": "Title Examinations", "desc": "Full title searches for tax-foreclosed inventory and arm's-length transactions. Title commitments with lien review and exception clearance.", "style": "c-primary"},
            {"title": "Quiet Title Research", "desc": "Title commitment review for completeness. Locate former owners and lienholders. Contact sheets and mailing labels for quiet title proceedings.", "style": "c-light1"},
            {"title": "Closings &amp; Recording", "desc": "Property disposition and acquisition closings. Deed recording, satisfaction of dockets, fee payment. Tax certificate and zoning certification procurement.", "style": "c-light2"},
            {"title": "DDI Service Model", "desc": "DDI primes the contract and manages compliance, QA, reporting, and invoicing. Licensed partners (Empora Title) execute title work. Single point of accountability for the buyer.", "style": "c-light3"},
        ],
        "service_capabilities": [
            "Full title examinations (tax-foreclosed and arm&rsquo;s-length)",
            "Title commitments with lien review and exception clearance",
            "Quiet title research and former owner location",
            "Property disposition and acquisition closings",
            "Deed recording and satisfaction of dockets",
            "NNA-certified signing agency &amp; notary services",
            "Remote Online Notarization (RON) capability",
            "Apostille &amp; document authentication services",
            "Estate planning document preparation &amp; execution",
            "Permit running &amp; government document filing",
            "Federal, state, county, and municipal lien searches",
            "CNDTA-certified document transmitting",
        ],
        "differentiators": [
            {"title": "MWBE-certified prime contractor", "desc": "EDWOSB, WOSB, WBE, MBE, SBE. Directly satisfies diversity and inclusion evaluation criteria"},
            {"title": "Empora Title partnership &mdash; licensed PA title company", "desc": "7-state coverage (PA, OH, IN, KY, MO, TX, FL). Digital-first platform with sub-30-day turnaround"},
            {"title": "Sub-30-day commitment delivery", "desc": "Automated workflow enables faster turnaround than traditional title firms"},
            {"title": "Scalable capacity &mdash; 100+ parcels/year", "desc": "Dedicated closing specialists and automated processing handle full acquisition volume"},
            {"title": "Proven prime/sub contract management model", "desc": "DDI manages compliance, reporting, and quality; licensed partners execute the technical work"},
        ],
        "past_performance": [
            {"title": "Empora Title Partnership", "desc": "Title examinations, commitment delivery, quiet title research, closings, and deed recording across PA, OH, IN, KY, MO, TX, and FL. Digital platform processing with sub-30-day turnaround on title commitments."},
            {"title": "NNA-Certified Signing Agency", "desc": "Mobile and remote online notarization, loan document execution, real estate closings, and deed signings. E&amp;O insured. Coordinating multiple signing agents across service areas."},
            {"title": "Prime/Sub Contract Management", "desc": "Managing multi-partner service delivery as prime contractor. Compliance oversight, quality assurance, invoicing, and reporting. Proven model: DDI primes, licensed partners execute the technical work."},
        ],
        "naics_detailed": [
            {"code": "541191", "desc": "Title Abstract &amp; Settlement"},
            {"code": "541199", "desc": "All Other Legal Services"},
            {"code": "541990", "desc": "Other Professional Services"},
            {"code": "531390", "desc": "Other Real Estate Activities"},
            {"code": "561499", "desc": "Other Business Support"},
        ],
        "cert_badges": [
            {"text": "EDWOSB", "cls": "gold"},
            {"text": "WOSB", "cls": "gold"},
            {"text": "WBENC WBE", "cls": ""},
            {"text": "MBE", "cls": ""},
            {"text": "SBE", "cls": ""},
            {"text": "E-Verify", "cls": "accent"},
            {"text": "NNA Certified", "cls": "accent"},
            {"text": "CNDTA", "cls": "accent"},
        ],
        "footer_extra": "",
        "naics": "541191 | 541199 | 541990 | 531390 | 561499",
    },
    "drug_testing": {
        "service_model": "Enroll &rarr; Randomize &rarr; Collect &rarr; Certify &rarr; Report &rarr; Comply",
        "header_tag": "Drug &amp; Alcohol Testing &bull; Third-Party Administration",
        "header_creds": [
            *DEFAULT_HEADER_CREDS,
        ],
        "gold_bar_title": "DRUG &amp; ALCOHOL TESTING &mdash; THIRD-PARTY ADMINISTRATION",
        "overview": (
            '<strong>EDWOSB-Certified &bull; SBA Verified &bull; Woman-Owned Small Business</strong> &mdash; '
            'Dee Davis Inc. (DDI) is an SBA-certified EDWOSB delivering federally compliant drug and alcohol '
            'testing programs as a licensed Third-Party Administrator. With <strong>5,100+ collection sites</strong> '
            'nationwide through eScreen/Quest Diagnostics, DDI provides <strong>same-day activation</strong>, '
            'SAMHSA-certified laboratory processing, MRO review, random selection, and full 49 CFR Part 40/655 '
            'compliance management. <strong>Zero compliance deficiencies</strong> across 1,500+ regulated collections.'
        ),
        "competencies_header": "CORE COMPETENCIES &mdash; FEDERALLY REGULATED TESTING OPERATIONS",
        "competencies": [
            {"title": "DOT/FTA Drug Testing", "desc": "Full 49 CFR Parts 40 &amp; 655 administration. Pre-employment, random, post-accident, reasonable suspicion, return-to-duty, follow-up.", "style": "c-primary"},
            {"title": "SAMHSA-Certified Lab Network", "desc": "eScreen/Quest Diagnostics. 5,100+ SAMHSA-certified collection sites. Same-day specimen collection. Electronic chain-of-custody.", "style": "c-light1"},
            {"title": "Medical Review Officer (MRO)", "desc": "Board-certified MRO review of all positive, adulterated, and substituted results per 49 CFR Part 40 Subpart G.", "style": "c-light2"},
            {"title": "Consortium &amp; Pool Management", "desc": "Random selection management for 50-10,000+ safety-sensitive employees. DOT-compliant random rate maintenance.", "style": "c-light3"},
        ],
        "service_capabilities": [
            "DOT/FTA drug &amp; alcohol testing program administration",
            "Pre-employment, random, post-accident testing",
            "Reasonable suspicion and return-to-duty testing",
            "SAMHSA-certified laboratory processing",
            "Medical Review Officer (MRO) services",
            "Random selection pool management",
            "Breath alcohol testing (BAT) with certified technicians",
            "Supervisor reasonable suspicion training",
            "Policy development and compliance auditing",
            "Electronic chain-of-custody and reporting",
            "Same-day program activation and enrollment",
            "49 CFR Parts 40 &amp; 655 compliance management",
        ],
        "differentiators": [
            {"title": "EDWOSB sole-source eligible &mdash; up to $7M", "desc": "SBA-certified. Streamlined procurement. Reduces acquisition timeline by 60%+"},
            {"title": "5,100+ collection sites &mdash; nationwide", "desc": "eScreen/Quest network. Activate within 24 hours of award. No geographic limitations"},
            {"title": "Zero compliance deficiencies", "desc": "1,500+ regulated collections. Full 49 CFR Parts 40 &amp; 655 adherence. Audit-ready documentation"},
            {"title": "Same-day activation capability", "desc": "Program enrollment and first collection within 24 hours. No ramp-up delays"},
            {"title": "Electronic reporting platform", "desc": "Real-time results, random selections, and compliance tracking. Employer portal access. CCF automation"},
        ],
        "past_performance": [
            {"title": "Transit Authority TPA Contracts", "desc": "DOT/FTA drug &amp; alcohol program administration for municipal transit systems. Pre-employment, random, post-accident, and reasonable suspicion testing. Zero audit findings."},
            {"title": "5,100+ Active Collection Sites", "desc": "Nationwide coverage via eScreen/Quest Diagnostics. Same-day specimen collection. 98%+ on-time reporting. SAMHSA-certified laboratory processing."},
            {"title": "Consortium Management", "desc": "Random pool administration across multiple employers. DOT-compliant selection rates. Quarterly reporting. 1,500+ regulated collections with zero deficiencies."},
        ],
        "naics_detailed": [
            {"code": "621511", "desc": "Medical Laboratories"},
            {"code": "621999", "desc": "Miscellaneous Ambulatory Health"},
            {"code": "621491", "desc": "HMO Medical Centers"},
            {"code": "541380", "desc": "Testing Laboratories"},
            {"code": "561611", "desc": "Investigation Services"},
        ],
        "cert_badges": [
            {"text": "EDWOSB", "cls": "gold"},
            {"text": "WOSB", "cls": "gold"},
            {"text": "WBENC WBE", "cls": ""},
            {"text": "MBE", "cls": ""},
            {"text": "SBE", "cls": ""},
            {"text": "E-Verify", "cls": "accent"},
            {"text": "eScreen/Quest", "cls": "accent"},
        ],
        "footer_extra": "",
        "naics": "621511 | 621999 | 621491 | 541380 | 561611 | 561612",
    },
    "fingerprinting": {
        "service_model": "Enroll &rarr; Schedule &rarr; Capture &rarr; Transmit &rarr; Adjudicate &rarr; Credential",
        "header_tag": "Electronic Fingerprinting &amp; Background Screening &bull; FBI Appendix F Certified",
        "header_creds": [
            *DEFAULT_HEADER_CREDS,
        ],
        "gold_bar_title": "ELECTRONIC FINGERPRINTING &amp; BACKGROUND SCREENING",
        "overview": (
            '<strong>EDWOSB-Certified &bull; SBA Verified &bull; FBI Appendix F Hardware &bull; Woman-Owned Small Business</strong> &mdash; '
            'Dee Davis Inc. (DDI) provides FBI/CJIS-compliant biometric fingerprint capture and background screening for federal agencies, '
            'state licensing boards, military installations, and commercial clients. DDI operates FBI Appendix F certified Kojak livescan equipment '
            'with Lakota WHORL software&mdash;the same technology stack used by the FBI, DoD, and DHS. Electronic and ink card (FD-258) capture. '
            '99.5% acceptance rate on submissions. Mobile deployment capability.'
        ),
        "competencies_header": "CORE COMPETENCIES &mdash; BIOMETRIC CREDENTIALING",
        "competencies": [
            {"title": "Electronic Fingerprinting", "desc": "FBI Appendix F certified Kojak livescan. Lakota WHORL software. EBTS-compliant file creation. Electronic submission via authorized channeling partners.", "style": "c-primary"},
            {"title": "FD-258 Ink Card Capture", "desc": "Traditional ink card fingerprinting with 99.5% acceptance rate. Federal, state, and licensing board submissions. Chain-of-custody documentation.", "style": "c-light1"},
            {"title": "Background Screening", "desc": "FBI National Criminal History Check (NCHC). State and county criminal searches. Employment verification. Identity validation.", "style": "c-light2"},
            {"title": "Mobile Deployment", "desc": "Portable Kojak units (1.6 lbs, USB-powered) for on-site capture at federal facilities, military installations, and secure locations. Scheduled and on-demand.", "style": "c-light3"},
        ],
        "service_capabilities": [
            "FBI Appendix F certified livescan capture",
            "FD-258 ink card fingerprinting",
            "Electronic submission via authorized channelers",
            "FBI CJIS criminal history submissions",
            "State licensing board submissions",
            "Federal employee and contractor screening",
            "ATF/NFA firearms trust fingerprinting",
            "State and county criminal background checks",
            "Employment and education verification",
            "Scheduled and on-demand mobile fingerprinting",
            "Bulk enrollment events for large workforces",
            "Chain-of-custody documentation",
        ],
        "differentiators": [
            {"title": "FBI Appendix F Certified Equipment", "desc": "Kojak livescan + Lakota WHORL&mdash;same technology used by FBI, DoD, DHS. Quality-first capture process."},
            {"title": "99.5% Acceptance Rate", "desc": "FD-258 and electronic submissions. Image quality validation before transmission. Minimal rejections."},
            {"title": "EDWOSB sole-source eligible &mdash; up to $7M", "desc": "SBA-certified. Streamlined procurement path for federal fingerprinting contracts"},
            {"title": "Mobile livescan deployment", "desc": "Portable Kojak units for on-site capture at secure facilities. USB-powered, 1.6 lbs."},
            {"title": "Lakota Technology Partnership", "desc": "DDI + Lakota (builders of FBI NGI, DoD ABIS, DHS HART). Federal-grade biometric technology stack."},
        ],
        "past_performance": [
            {"title": "Federal &amp; State Fingerprinting", "desc": "FBI/CJIS submissions, state licensing board fingerprinting, ATF/NFA trust applications. Mobile and fixed-site deployment. 99.5% acceptance rate."},
            {"title": "Lakota WHORL Platform (Active)", "desc": "Long-time Lakota customer. FBI Appendix F certified capture with electronic EBTS file creation. DeCA fingerprinting teaming in progress."},
            {"title": "Prime/Sub Contract Management", "desc": "Managing multi-location fingerprinting operations as prime contractor. Compliance oversight, scheduling coordination, quality assurance, and electronic reporting."},
        ],
        "naics_detailed": [
            {"code": "561611", "desc": "Investigation Services"},
            {"code": "561612", "desc": "Security Guards &amp; Patrol"},
            {"code": "541990", "desc": "Other Professional Services"},
            {"code": "561499", "desc": "Other Business Support"},
        ],
        "cert_badges": [
            {"text": "EDWOSB", "cls": "gold"},
            {"text": "WOSB", "cls": "gold"},
            {"text": "WBENC WBE", "cls": ""},
            {"text": "MBE", "cls": ""},
            {"text": "SBE", "cls": ""},
            {"text": "E-Verify", "cls": "accent"},
            {"text": "FBI Appendix F", "cls": "accent"},
        ],
        "footer_extra": "",
        "naics": "561611 | 561612 | 541990 | 561499",
    },
    "dna_testing": {
        "service_model": "Enroll &rarr; Collect &rarr; Ship &rarr; Analyze &rarr; Certify &rarr; Report",
        "header_tag": "DNA &amp; Paternity Testing &bull; AABB Accredited &bull; Contract Management",
        "header_creds": [
            *DEFAULT_HEADER_CREDS,
        ],
        "gold_bar_title": "DNA &amp; PATERNITY TESTING SERVICES",
        "overview": (
            '<strong>EDWOSB-Certified &bull; SBA Verified &bull; Woman-Owned Small Business</strong> &mdash; '
            'Dee Davis Inc. (DDI) is an EDWOSB-certified contract management firm providing AABB-accredited '
            'DNA and paternity testing services for federal immigration, family court, and government agency programs. '
            'DDI manages the full testing lifecycle through accredited laboratory partners&mdash;specimen collection, '
            'chain-of-custody, laboratory analysis, and legally defensible reporting.'
        ),
        "competencies_header": "CORE COMPETENCIES",
        "competencies": [
            {"title": "DNA Collection &amp; Processing", "desc": "Buccal swab specimen collection. Strict chain-of-custody protocols. AABB-accredited laboratory analysis. Court-admissible results.", "style": "c-primary"},
            {"title": "Immigration DNA Testing", "desc": "USCIS/embassy-coordinated testing. International specimen collection and transport. AABB-accredited for immigration cases.", "style": "c-light1"},
            {"title": "Legal &amp; Court-Ordered Testing", "desc": "Family court paternity establishment. Child support enforcement. Legally defensible documentation and expert testimony support.", "style": "c-light2"},
            {"title": "DDI Service Model", "desc": "DDI primes the contract, manages compliance, scheduling, and chain-of-custody. AABB-accredited lab partners perform analysis. Single point of accountability.", "style": "c-light3"},
        ],
        "service_capabilities": [
            "AABB-accredited DNA paternity testing",
            "Immigration DNA testing (USCIS/embassy)",
            "Court-ordered paternity establishment",
            "Buccal swab specimen collection",
            "Chain-of-custody documentation",
            "Legally defensible result reporting",
            "International specimen coordination",
            "Sibling, grandparent, and avuncular testing",
            "Child support enforcement testing",
            "Mobile collection at government facilities",
            "Expert testimony and litigation support",
            "Electronic results delivery and tracking",
        ],
        "differentiators": [
            {"title": "EDWOSB sole-source eligible &mdash; up to $7M", "desc": "SBA-certified. Streamlined procurement for federal DNA testing contracts"},
            {"title": "AABB-accredited laboratory network", "desc": "Gold standard for immigration and legal DNA testing. Court-admissible results"},
            {"title": "Immigration testing expertise", "desc": "USCIS and embassy coordination. International specimen collection and transport"},
            {"title": "Proven prime/sub contract management model", "desc": "DDI manages compliance and chain-of-custody. Accredited labs execute analysis"},
            {"title": "Nationwide mobile collection", "desc": "On-site specimen collection at federal facilities, courts, and detention centers"},
        ],
        "past_performance": [
            {"title": "DNA Testing Program Administration", "desc": "Managing AABB-accredited DNA and paternity testing programs. Specimen collection, chain-of-custody, laboratory coordination, and legally defensible result reporting."},
            {"title": "Immigration DNA Coordination", "desc": "USCIS and embassy-coordinated testing for family reunification cases. International specimen collection and transport through accredited partners."},
            {"title": "Prime/Sub Contract Management", "desc": "Managing regulated testing operations as prime contractor. Compliance oversight, quality assurance, and reporting across multiple service locations."},
        ],
        "naics_detailed": [
            {"code": "621511", "desc": "Medical Laboratories"},
            {"code": "621999", "desc": "Miscellaneous Ambulatory Health"},
            {"code": "541380", "desc": "Testing Laboratories"},
            {"code": "541990", "desc": "Other Professional Services"},
        ],
        "cert_badges": [
            {"text": "EDWOSB", "cls": "gold"},
            {"text": "WOSB", "cls": "gold"},
            {"text": "WBENC WBE", "cls": ""},
            {"text": "MBE", "cls": ""},
            {"text": "SBE", "cls": ""},
            {"text": "E-Verify", "cls": "accent"},
            {"text": "AABB Network", "cls": "accent"},
        ],
        "footer_extra": "",
        "naics": "621511 | 621999 | 541380 | 541990",
    },
    "janitorial": {
        "service_model": "Assess &rarr; Plan &rarr; Deploy &rarr; Execute &rarr; Inspect &rarr; Report",
        "header_tag": "Facilities Maintenance &bull; Grounds &bull; Janitorial &bull; Contract Management",
        "header_creds": [
            *DEFAULT_HEADER_CREDS,
        ],
        "gold_bar_title": "FACILITIES MAINTENANCE &amp; GROUNDS SERVICES",
        "overview": (
            '<strong>EDWOSB-Certified &bull; SBA Verified &bull; Woman-Owned Small Business</strong> &mdash; '
            'Dee Davis Inc. (DDI) is an EDWOSB-certified contract management firm providing janitorial, grounds '
            'maintenance, landscaping, and facility support services for federal, state, and municipal clients. '
            'DDI manages the full service lifecycle as prime contractor&mdash;scheduling, quality inspections, '
            'compliance reporting, and performance management&mdash;through vetted, regionally licensed service partners.'
        ),
        "competencies_header": "CORE COMPETENCIES",
        "competencies": [
            {"title": "Janitorial &amp; Custodial", "desc": "Daily, weekly, and periodic cleaning. Floor care, restroom sanitation, trash removal, window cleaning. Federal and commercial facilities.", "style": "c-primary"},
            {"title": "Grounds &amp; Landscaping", "desc": "Mowing, trimming, edging, leaf removal, snow/ice management, irrigation, and seasonal planting. Multi-acre campus coverage.", "style": "c-light1"},
            {"title": "Facility Support", "desc": "Pressure washing, parking lot maintenance, pest control coordination, minor repairs, and preventive maintenance scheduling.", "style": "c-light2"},
            {"title": "DDI Service Model", "desc": "DDI primes the contract, manages scheduling, quality inspections, and compliance reporting. Licensed regional partners execute the work. Single point of accountability.", "style": "c-light3"},
        ],
        "service_capabilities": [
            "Daily janitorial and custodial services",
            "Floor care (strip, wax, buff, carpet cleaning)",
            "Restroom sanitation and supply management",
            "Grounds mowing, trimming, and edging",
            "Snow and ice removal",
            "Landscaping and seasonal planting",
            "Pressure washing (buildings, walkways, lots)",
            "Trash and recycling removal",
            "Window cleaning (interior and exterior)",
            "Pest control coordination",
            "Quality inspection and compliance reporting",
            "Emergency and after-hours response",
        ],
        "differentiators": [
            {"title": "EDWOSB sole-source eligible &mdash; up to $7M", "desc": "SBA-certified. Streamlined procurement for federal facility maintenance contracts"},
            {"title": "Proven prime/sub contract management model", "desc": "DDI manages compliance, scheduling, and quality. Licensed regional partners execute the work"},
            {"title": "Quality inspection program", "desc": "Regular site inspections, photographic documentation, performance scorecards, and corrective action tracking"},
            {"title": "Multi-facility scalability", "desc": "Manage multiple locations through single contract. Consistent standards across all sites"},
            {"title": "Emergency response capability", "desc": "After-hours and emergency service activation. Snow/ice response within contracted SLA windows"},
        ],
        "past_performance": [
            {"title": "Facility Maintenance Operations", "desc": "Managing janitorial, grounds, and facility support contracts as prime contractor. Scheduling, quality inspections, compliance reporting, and performance management through vetted regional partners."},
            {"title": "Multi-Location Service Delivery", "desc": "Coordinating service operations across multiple facilities. Consistent quality standards, SLA compliance, and single-point-of-contact management."},
            {"title": "Prime/Sub Contract Management", "desc": "Active prime contractor on federal supply and service contracts. Full VAAR/FAR compliance, CO/COR communication, monthly performance reporting, and quality assurance oversight."},
        ],
        "naics_detailed": [
            {"code": "561720", "desc": "Janitorial Services"},
            {"code": "561730", "desc": "Landscaping Services"},
            {"code": "561790", "desc": "Other Services to Buildings"},
            {"code": "561210", "desc": "Facilities Support Services"},
        ],
        "cert_badges": [
            {"text": "EDWOSB", "cls": "gold"},
            {"text": "WOSB", "cls": "gold"},
            {"text": "WBENC WBE", "cls": ""},
            {"text": "MBE", "cls": ""},
            {"text": "SBE", "cls": ""},
            {"text": "E-Verify", "cls": "accent"},
        ],
        "footer_extra": "",
        "naics": "561720 | 561730 | 561790 | 561210",
    },
    "industrial": {
        "service_model": "Source &rarr; Quote &rarr; Procure &rarr; Deliver &rarr; Inspect &rarr; Invoice",
        "header_tag": "Industrial Supplies &bull; Equipment &bull; Federal Supply Contracts",
        "header_creds": [
            *DEFAULT_HEADER_CREDS,
        ],
        "gold_bar_title": "INDUSTRIAL SUPPLIES &amp; EQUIPMENT",
        "overview": (
            '<strong>EDWOSB-Certified &bull; SBA Verified &bull; Woman-Owned Small Business</strong> &mdash; '
            'Dee Davis Inc. (DDI) is an EDWOSB-certified prime contractor delivering industrial supplies, '
            'equipment, safety products, and commodity materials for federal, state, and municipal clients. '
            'DDI sources competitively from manufacturer and distributor networks, manages procurement logistics, '
            'and delivers to specification&mdash;on time, to location, with full documentation.'
        ),
        "competencies_header": "CORE COMPETENCIES",
        "competencies": [
            {"title": "Federal Supply Contracts", "desc": "DLA, GSA, and agency-direct supply contracts. FAR/DFAR compliant procurement. CLIN-based pricing and delivery.", "style": "c-primary"},
            {"title": "Industrial &amp; Safety Products", "desc": "PPE, tools, fasteners, electrical, plumbing, HVAC, janitorial supplies, fleet parts, and MRO commodities.", "style": "c-light1"},
            {"title": "Sourcing &amp; Logistics", "desc": "Competitive multi-supplier sourcing. Freight coordination. Delivery scheduling. Inspection and acceptance documentation.", "style": "c-light2"},
            {"title": "DDI Service Model", "desc": "DDI primes the contract, sources from manufacturer/distributor networks, manages logistics, and delivers with full compliance documentation.", "style": "c-light3"},
        ],
        "service_capabilities": [
            "Federal supply contract execution (DLA, GSA, VA)",
            "Industrial supplies and MRO commodities",
            "Safety and PPE products",
            "Fleet parts and automotive supplies",
            "Electrical, plumbing, and HVAC materials",
            "Fasteners, hardware, and tools",
            "Competitive multi-supplier sourcing",
            "Freight coordination and delivery scheduling",
            "Inspection and acceptance documentation",
            "CLIN-based pricing and invoicing",
            "Packaging, labeling, and shipping compliance",
            "Warranty and return management",
        ],
        "differentiators": [
            {"title": "EDWOSB sole-source eligible &mdash; up to $7M", "desc": "SBA-certified. Streamlined procurement for federal supply contracts"},
            {"title": "Competitive multi-supplier sourcing", "desc": "DDI sources from manufacturer and distributor networks to deliver best value pricing"},
            {"title": "Full compliance documentation", "desc": "Packing slips, COCs, MTRs, inspection reports, and WAWF/iRAPT invoicing"},
            {"title": "On-time delivery track record", "desc": "Freight coordination, delivery scheduling, and proactive shipment tracking"},
            {"title": "Proven contract management model", "desc": "DDI primes the contract, manages sourcing and logistics, delivers to specification"},
        ],
        "past_performance": [
            {"title": "Federal Supply Contracts", "desc": "Active prime contractor on DLA and VA supply contracts. Industrial supplies, safety products, and commodity materials. Full FAR/DFAR compliance, WAWF invoicing."},
            {"title": "Municipal Procurement", "desc": "Sourcing and delivering industrial supplies, fleet parts, and equipment for state and local government clients. Competitive pricing through multi-supplier networks."},
            {"title": "Logistics &amp; Delivery Management", "desc": "Freight coordination, delivery scheduling, inspection documentation, and acceptance reporting across multiple contract vehicles."},
        ],
        "naics_detailed": [
            {"code": "423450", "desc": "Medical Equipment Wholesale"},
            {"code": "423840", "desc": "Industrial Supplies Wholesale"},
            {"code": "423510", "desc": "Metal Service Centers"},
            {"code": "423710", "desc": "Hardware Wholesale"},
            {"code": "423490", "desc": "Other Professional Equipment"},
        ],
        "cert_badges": [
            {"text": "EDWOSB", "cls": "gold"},
            {"text": "WOSB", "cls": "gold"},
            {"text": "WBENC WBE", "cls": ""},
            {"text": "MBE", "cls": ""},
            {"text": "SBE", "cls": ""},
            {"text": "E-Verify", "cls": "accent"},
        ],
        "footer_extra": "",
        "naics": "423450 | 423840 | 423510 | 423710 | 423490 | 332510",
    },
    "courier": {
        "service_model": "Receive &rarr; Route &rarr; Dispatch &rarr; Deliver &rarr; Confirm &rarr; Invoice",
        "header_tag": "Courier &amp; Express Delivery &bull; Medical Specimen Transport &bull; Logistics",
        "header_creds": [
            *DEFAULT_HEADER_CREDS,
            "US DOT: 4250594", "MC: 1647572",
        ],
        "gold_bar_title": "COURIER &amp; EXPRESS DELIVERY SERVICES",
        "overview": (
            '<strong>EDWOSB-Certified &bull; SBA Verified &bull; Woman-Owned Small Business</strong> &mdash; '
            'Dee Davis Inc. (DDI) is an EDWOSB-certified contract management firm providing medical specimen '
            'courier, pharmaceutical delivery, express courier, and time-critical logistics for federal, state, '
            'and commercial clients. With active DOT and MC authority, DDI manages the full delivery lifecycle '
            'through vetted, regionally licensed courier and logistics partners.'
        ),
        "competencies_header": "CORE COMPETENCIES",
        "competencies": [
            {"title": "Medical Specimen Courier", "desc": "Temperature-controlled specimen transport. Chain-of-custody documentation. HIPAA-compliant handling. Scheduled and STAT routes.", "style": "c-primary"},
            {"title": "Express &amp; Time-Critical Delivery", "desc": "Same-day, next-day, and scheduled recurring delivery. Government mail and document courier. Hot-shot and on-demand dispatch.", "style": "c-light1"},
            {"title": "Pharmaceutical &amp; Supply Delivery", "desc": "Pharmacy distribution, medical supply delivery, lab supply replenishment. Temperature monitoring and compliance documentation.", "style": "c-light2"},
            {"title": "DDI Service Model", "desc": "DDI primes the contract, manages routing, dispatch, and compliance. Vetted regional courier partners execute deliveries. Single point of accountability.", "style": "c-light3"},
        ],
        "service_capabilities": [
            "Medical specimen and lab courier",
            "Pharmaceutical and medical supply delivery",
            "Temperature-controlled transport",
            "Chain-of-custody specimen handling",
            "Same-day and STAT delivery",
            "Recurring scheduled route management",
            "Government mail and document courier",
            "Hot-shot and on-demand dispatch",
            "HIPAA-compliant documentation and reporting",
            "Electronic proof of delivery and tracking",
            "Route optimization and fleet coordination",
            "After-hours and weekend delivery capability",
        ],
        "differentiators": [
            {"title": "EDWOSB sole-source eligible &mdash; up to $7M", "desc": "SBA-certified. Streamlined procurement for federal courier contracts"},
            {"title": "Active US DOT (4250594) and MC (1647572) authority", "desc": "Federally registered motor carrier. Interstate and intrastate transport"},
            {"title": "Temperature-controlled capability", "desc": "Specimen and pharmaceutical transport with monitoring, documentation, and chain-of-custody compliance"},
            {"title": "Proven prime/sub contract management model", "desc": "DDI manages routing, compliance, and reporting. Vetted regional couriers execute deliveries"},
            {"title": "Electronic tracking and proof of delivery", "desc": "Real-time shipment tracking, electronic POD, and automated reporting to contracting officers"},
        ],
        "past_performance": [
            {"title": "Gideon Logistics (Jan 2023 &ndash; Present)", "desc": "Courier services, logistics documentation &amp; regulatory filings, biometric fingerprinting, workforce management &amp; recruitment support, and DOT compliance."},
            {"title": "Medical Specimen Transport", "desc": "Temperature-controlled courier services for laboratory specimens, pharmaceuticals, and medical supplies. Chain-of-custody documentation. HIPAA compliance."},
            {"title": "Prime/Sub Contract Management", "desc": "Managing multi-route courier operations as prime contractor. Scheduling, dispatch coordination, compliance oversight, and electronic reporting."},
        ],
        "naics_detailed": [
            {"code": "492110", "desc": "Couriers &amp; Express Delivery"},
            {"code": "484110", "desc": "General Freight Trucking, Local"},
            {"code": "484230", "desc": "Specialized Freight, Long-Distance"},
            {"code": "492210", "desc": "Local Messengers &amp; Delivery"},
        ],
        "cert_badges": [
            {"text": "EDWOSB", "cls": "gold"},
            {"text": "WOSB", "cls": "gold"},
            {"text": "WBENC WBE", "cls": ""},
            {"text": "MBE", "cls": ""},
            {"text": "SBE", "cls": ""},
            {"text": "E-Verify", "cls": "accent"},
            {"text": "US DOT", "cls": "accent"},
            {"text": "MC Authority", "cls": "accent"},
        ],
        "footer_extra": "US DOT: 4250594 &nbsp;|&nbsp; MC: 1647572",
        "naics": "492110 | 484110 | 484230 | 492210",
    },
}


def _get_sector_content(sector: str) -> Dict:
    return SECTOR_CONTENT.get(sector, SECTOR_CONTENT["main"])


def _get_sector_colors(sector: str) -> Dict:
    return SECTOR_COLORS.get(sector, SECTOR_COLORS["main"])


# ═══════════════════════════════════════════════════════════════════════════════
# IMAGE UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def _img_to_base64(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    suffix = p.suffix.lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "webp": "webp"}.get(suffix, "png")
    with open(p, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{mime};base64,{encoded}"


def _get_logo_base64() -> str:
    for name in ["DDI Logo.png", "DEE-DAVIS-INC-black-2.png", "DEE-DAVIS-INC-black.png"]:
        p = ESSENTIALS_DIR / name
        if p.exists():
            return _img_to_base64(str(p))
    bids_dir = Path(__file__).parent / "BIDS:RESOURCES"
    for html_file in bids_dir.rglob("*Capability_Statement*.html"):
        try:
            content = html_file.read_text(errors="ignore")
            match = re.search(r'<img[^>]+src="(data:image/png;base64,[A-Za-z0-9+/=]{100,})"[^>]+class="h-logo-img"', content)
            if match:
                return match.group(1)
            match = re.search(r'class="h-logo-img"[^>]*src="(data:image/[^"]+)"', content)
            if match:
                return match.group(1)
            match = re.search(r'<img[^>]+src="(data:image/png;base64,[A-Za-z0-9+/=]{100,})"[^>]+alt="DDI"', content)
            if match:
                return match.group(1)
        except Exception:
            continue
    return ""


# ═══════════════════════════════════════════════════════════════════════════════
# HTML BUILDERS — match NEMT reference format exactly
# ═══════════════════════════════════════════════════════════════════════════════

def build_service_model_html(model_text: str, color: str) -> str:
    if not model_text:
        return ""
    return (
        f'<p style="font-size:0.58rem;margin-top:0.15rem;color:{color};font-weight:600;">'
        f'SERVICE MODEL: {model_text}</p>'
    )


def build_header_creds_html(creds: List[str]) -> str:
    return "\n        ".join(f"<span>{c}</span>" for c in creds)


def build_competencies_html(competencies: List[Dict]) -> str:
    parts = []
    for comp in competencies:
        style = comp.get("style", "c-light1")
        parts.append(
            f'      <div class="c {style}">\n'
            f'        <h4>{comp["title"]}</h4>\n'
            f'        <p>{comp["desc"]}</p>\n'
            f'      </div>'
        )
    return "\n".join(parts)


def build_service_capabilities_html(items: List[str]) -> str:
    mid = (len(items) + 1) // 2
    left = items[:mid]
    right = items[mid:]
    left_html = "      <ul class=\"svc\">\n" + "\n".join(f"        <li>{s}</li>" for s in left) + "\n      </ul>"
    right_html = "      <ul class=\"svc\">\n" + "\n".join(f"        <li>{s}</li>" for s in right) + "\n      </ul>"
    return left_html + "\n" + right_html


def build_differentiators_html(items: List[Dict]) -> str:
    return "\n".join(
        f'      <li><strong>{item["title"]}</strong> &mdash; {item["desc"]}</li>'
        for item in items
    )


def build_pp_grid_html(items: List[Dict]) -> str:
    parts = []
    for item in items:
        parts.append(
            f'      <div class="pp">\n'
            f'        <h4>{item["title"]}</h4>\n'
            f'        <p>{item["desc"]}</p>\n'
            f'      </div>'
        )
    return "\n".join(parts)


def build_naics_strip_html(naics_list: List[Dict]) -> str:
    pills = "\n      ".join(
        f'<span class="naics-pill"><span class="nc">{n["code"]}</span> {n["desc"]}</span>'
        for n in naics_list
    )
    return (
        '    <div class="naics-strip">\n'
        '      <span class="nlbl">NAICS:</span>\n'
        f'      {pills}\n'
        '    </div>'
    )


def build_cert_badges_html(badges: List[Dict]) -> str:
    parts = []
    for b in badges:
        cls = f' {b["cls"]}' if b.get("cls") else ""
        parts.append(f'      <span class="cert-badge{cls}">{b["text"]}</span>')
    return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def generate_capability_statement(
    sector: str = "main",
    agency_name: Optional[str] = None,
    solicitation_number: Optional[str] = None,
    service_description: Optional[str] = None,
    custom_overview: Optional[str] = None,
    custom_competencies: Optional[List[Dict]] = None,
    custom_past_performance: Optional[List[Dict]] = None,
    custom_differentiators: Optional[List[Dict]] = None,
    custom_service_capabilities: Optional[List[str]] = None,
    custom_naics: Optional[str] = None,
    custom_naics_detailed: Optional[List[Dict]] = None,
    custom_header_tag: Optional[str] = None,
    custom_cert_badges: Optional[List[Dict]] = None,
    custom_footer_extra: Optional[str] = None,
    custom_service_model: Optional[str] = None,
    output_path: Optional[str] = None,
) -> str:
    colors = _get_sector_colors(sector)
    content = _get_sector_content(sector)
    logo_b64 = _get_logo_base64()

    template_path = Path(__file__).parent / "capability_statement_template.html"
    template = template_path.read_text()

    footer_extra = custom_footer_extra if custom_footer_extra is not None else content.get("footer_extra", "")
    if agency_name and not footer_extra:
        footer_extra = f"Prepared for {agency_name}"
    if agency_name and solicitation_number and not custom_footer_extra:
        footer_extra = f"Prepared for {agency_name} &mdash; {solicitation_number}"

    replacements = {
        "{{PRIMARY_COLOR}}": colors["primary"],
        "{{SECONDARY_COLOR}}": colors["secondary"],
        "{{ACCENT_COLOR}}": colors["accent"],
        "{{ACCENT_COLOR_DARK}}": colors["accent_dark"],
        "{{COMP_COLUMNS}}": str(colors["comp_columns"]),
        "{{LOGO_BASE64}}": logo_b64,
        "{{HEADER_TAG}}": custom_header_tag or content.get("header_tag", "Contract Management"),
        "{{HEADER_CREDS_HTML}}": build_header_creds_html(content.get("header_creds", DEFAULT_HEADER_CREDS)),
        "{{GOLD_BAR_TITLE}}": service_description or content["gold_bar_title"],
        "{{OVERVIEW_HTML}}": custom_overview or content["overview"],
        "{{SERVICE_MODEL_HTML}}": build_service_model_html(
            content.get("service_model", "") if custom_service_model is None else custom_service_model,
            colors["primary"],
        ),
        "{{COMPETENCIES_HEADER}}": content.get("competencies_header", "CORE COMPETENCIES"),
        "{{COMPETENCIES_GRID_HTML}}": build_competencies_html(custom_competencies or content["competencies"]),
        "{{SERVICE_CAPABILITIES_HTML}}": build_service_capabilities_html(custom_service_capabilities or content.get("service_capabilities", [])),
        "{{DIFFERENTIATORS_HTML}}": build_differentiators_html(custom_differentiators or content["differentiators"]),
        "{{PAST_PERFORMANCE_HTML}}": build_pp_grid_html(custom_past_performance or content["past_performance"]),
        "{{NAICS_STRIP_HTML}}": build_naics_strip_html(custom_naics_detailed or content.get("naics_detailed", [])),
        "{{CERT_BADGES_ROW_HTML}}": build_cert_badges_html(custom_cert_badges or content.get("cert_badges", [])),
        "{{FOOTER_EXTRA_HTML}}": footer_extra,
    }

    html = template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    if output_path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(html)

    return html


AVAILABLE_SECTORS = [
    {"key": "main", "label": "Main — Contract Management TPA (All Sectors)"},
    {"key": "nemt", "label": "NEMT / Personal Care TPA / MCO Contract Management"},
    {"key": "haven", "label": "HAVEN — Disaster Response / Member Relocation"},
    {"key": "drug_testing", "label": "Drug & Alcohol Testing / TPA"},
    {"key": "fingerprinting", "label": "Fingerprinting / Background Screening / FBI Appendix F"},
    {"key": "courier", "label": "Courier / Delivery / Logistics"},
    {"key": "dna_testing", "label": "DNA / Paternity / Genetic Testing"},
    {"key": "janitorial", "label": "Janitorial / Grounds Maintenance / Facilities"},
    {"key": "industrial", "label": "Industrial Supplies / Equipment / Parts"},
    {"key": "notary", "label": "Notary / Signing Agent / Legal / Title Services"},
    {"key": "professional", "label": "Professional Services / Consulting / Staffing"},
    {"key": "georgia", "label": "Georgia State Agencies (State Override)"},
]
