#!/usr/bin/env python3
"""
NEXUS ADVISOR — THE TEACHING ENGINE
======================================
Contextual education that runs across EVERY NEXUS system.
Not a separate screen — embedded knowledge that shows up while Dee works.

SYSTEMS COVERED:
  GPSS    — Government bids, proposals, compliance, pricing
  ATLAS   — Project management, RFP response, WBS, change orders
  COMPASS — Post-award operations, deliverables, compliance, CO comms
  VERTEX  — Financial management, invoicing, P&L, cash flow
  GBIS    — Grant intelligence, applications, story library
  DDCSS   — Corporate sales, client avatars, blueprints
  LBPC    — Surplus recovery, lead mining, document generation
  PRISM   — Field service, dispatch, inspection, agent management
  COMMAND — Agenda, workflow, task execution

THREE FUNCTIONS:
  1. TEACH   — Contextual education triggered by user actions
  2. DEBRIEF — Lessons learned from outcomes (win/loss/complete)
  3. BRIEF   — Periodic summaries of growth, patterns, and industry updates

PHILOSOPHY:
  NEXUS makes DDI operate at the level of $50M WOSBs while Dee learns the craft.
  Every action is an opportunity to teach. Every outcome is a lesson.
  The system doesn't hide the knowledge — it surfaces it.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

ADVISOR_DB_PATH = Path(os.environ.get(
    'NEXUS_ADVISOR_DB',
    '/Users/deedavis/NEXUS BACKEND/nexus_advisor_db.json'
))

# ─── KNOWLEDGE BASE: Contextual education per system + action ────────────────

KNOWLEDGE_BASE = {
    # ══════════════════════════════════════════════════════════════════════════
    # GPSS — Government Prime Sales System
    # ══════════════════════════════════════════════════════════════════════════
    'gpss': {
        'system_name': 'GPSS — Government Prime Sales System',
        'actions': {
            'opportunity_discovered': {
                'teach': 'Every opportunity on SAM.gov has a NAICS code that determines who can bid. '
                         'DDI\'s EDWOSB certification means you get access to set-aside contracts where '
                         'only woman-owned small businesses can compete — drastically fewer competitors. '
                         'Always check: Is it a set-aside? What\'s the NAICS? Is it in a DDI service lane?',
                'key_concept': 'Set-Aside Advantage',
                'far_reference': 'FAR 19.15 — Women-Owned Small Business Program',
            },
            'go_decision': {
                'teach': 'A Go/No-Go decision should never be emotional. Score it: Do you have the '
                         'capability? Past performance? Price competitiveness? Relationship with the buyer? '
                         'Resource availability? If 3 of 5 are weak, it\'s a No-Go — no matter how '
                         'exciting the contract looks. Bidding costs time and money. Be disciplined.',
                'key_concept': 'Go/No-Go Discipline',
                'far_reference': None,
            },
            'proposal_created': {
                'teach': 'Government evaluators use Section M to score your proposal. They don\'t read '
                         'it like a story — they check boxes. Each evaluation factor has subfactors, and '
                         'each gets an adjectival rating: Outstanding, Good, Acceptable, Marginal, or '
                         'Unacceptable. One Unacceptable on a critical factor = eliminated. Mirror the '
                         'RFP structure EXACTLY. If Section L says 3 volumes, you submit 3 volumes.',
                'key_concept': 'Section M Evaluation',
                'far_reference': 'FAR 15.305 — Proposal Evaluation',
            },
            'proposal_scored': {
                'teach': 'Your evaluator score predicts how a CO will rate your proposal. '
                         'Outstanding (10/10) means you exceeded requirements with innovation. '
                         'Good (8/10) means solid with some strengths. Acceptable (6/10) meets minimum — '
                         'but "minimum" rarely wins Best Value. Marginal (4/10) means gaps that create doubt. '
                         'Focus improvement effort on the HIGHEST WEIGHTED factors first — a 2-point gain '
                         'on a 40% factor is worth more than perfecting a 10% factor.',
                'key_concept': 'Weighted Score Optimization',
                'far_reference': 'FAR 15.101 — Best Value Continuum',
            },
            'rfq_sent_to_supplier': {
                'teach': 'Never reveal the end buyer to suppliers. If they know it\'s a government '
                         'contract for Agency X, they can look up the bid and cut you out. Use DDI-YYYY-### '
                         'format. Say "Michigan municipal client." Give them a deadline 3-5 days before '
                         'the government deadline. This protects your margin and your business.',
                'key_concept': 'Buyer Protection',
                'far_reference': None,
            },
            'bid_submitted': {
                'teach': 'After submission, document everything: what you bid, your pricing, your '
                         'technical approach, who you subbed. Win or lose, this data is gold. '
                         'If you win, it becomes past performance for next time. If you lose, '
                         'request a debrief — it\'s your right under FAR 15.506. Debriefs tell you '
                         'exactly where you scored low so you can fix it.',
                'key_concept': 'Post-Submission Documentation',
                'far_reference': 'FAR 15.506 — Post-Award Debriefing',
            },
            'bid_won': {
                'teach': 'Congratulations — but the real work starts now. Within 10 days of award, '
                         'expect a post-award conference. Have your subcontractors ready, insurance current, '
                         'and a transition plan. The CO will want to see you can actually perform. '
                         'Your CPARS rating starts from day one — every late delivery, every quality issue, '
                         'every communication gap gets documented. Manage the contract like your reputation '
                         'depends on it — because it does.',
                'key_concept': 'Post-Award Execution',
                'far_reference': 'FAR 42.15 — Contractor Performance Information (CPARS)',
            },
            'bid_lost': {
                'teach': 'Request a debrief. Under FAR 15.506, you have 3 days after notification to '
                         'request one. The CO must tell you: your rating on each factor, the awardee\'s '
                         'rating (not their price), and why you lost. This is the most valuable '
                         'information you can get. Document the debrief, update your approach, and '
                         'bid the recompete smarter. Every loss is tuition.',
                'key_concept': 'Debrief & Learn',
                'far_reference': 'FAR 15.506 — Post-Award Debriefing of Offerors',
            },
            'markup_set': {
                'teach': 'Your markup has to balance three things: winning the bid, covering your costs, '
                         'and making profit. For subcontracted services, 12-18% is typical. For products, '
                         '15-25%. LPTA contracts are price wars — go aggressive. Best Value contracts '
                         'let you price higher if your technical is strong. EDWOSB set-asides have less '
                         'competition, so you can hold a higher margin. Track your win/loss at different '
                         'markup levels — the data will tell you your sweet spot.',
                'key_concept': 'Markup Strategy',
                'far_reference': None,
            },
            'compliance_check': {
                'teach': 'Compliance isn\'t sexy but it wins contracts. COs use a checklist: Did they '
                         'include all required forms? Correct format? Page limits followed? Required '
                         'certifications attached? One missing signature or wrong font size can get your '
                         'proposal thrown out before anyone reads your brilliant technical approach. '
                         'Build your compliance matrix from Section L BEFORE writing a single word.',
                'key_concept': 'Compliance Matrix',
                'far_reference': 'FAR 15.2 — Solicitation and Receipt of Proposals',
            },
            'subcontractor_vetted': {
                'teach': 'As the prime contractor, YOU are responsible for everything the sub does. '
                         'If they fail, YOUR CPARS takes the hit. Vet them with the 6 pillars: '
                         'VET (qualifications), PROTECT (NDA/Non-Compete), INSURE (COI with DDI as '
                         'additional insured), PLAN (staffing/work plan), COMMUNICATE (reporting cadence), '
                         'MANAGE (performance tracking). NDA before information. Non-Compete before details. '
                         'COI before work. Always.',
                'key_concept': 'Subcontractor Risk Management',
                'far_reference': 'FAR 44 — Subcontracting Policies and Procedures',
            },
            'capstat_generated': {
                'teach': 'Your capability statement is DDI\'s resume. Tailor it to EVERY opportunity — '
                         'a generic cap statement is a wasted opportunity. Mirror the buyer\'s language from '
                         'the RFP. Use their agency name 3+ times. Match the sector color scheme. '
                         'Include EDWOSB prominently — it\'s your competitive weapon. A CO should scan '
                         'your cap statement in 30 seconds and think "this company understands our mission."',
                'key_concept': 'Tailored Capability Statements',
                'far_reference': None,
            },
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # ATLAS — Project Management System
    # ══════════════════════════════════════════════════════════════════════════
    'atlas': {
        'system_name': 'ATLAS — Project Management',
        'actions': {
            'project_created': {
                'teach': 'Every government contract should have a project plan within 5 days of award. '
                         'Break the SOW into a Work Breakdown Structure (WBS) — each deliverable gets '
                         'its own task with an owner, deadline, and quality standard. The CO expects a '
                         'project management plan at the kickoff meeting. Show them you\'re organized.',
                'key_concept': 'Work Breakdown Structure',
                'far_reference': None,
            },
            'rfp_analyzed': {
                'teach': 'Every section of an RFP has a purpose. Section A = admin info. B = what to price. '
                         'C = what to do (SOW). L = how to format your proposal. M = how they\'ll score it. '
                         'Read Section L and M FIRST — they tell you exactly what the evaluator is looking '
                         'for and how to organize your response. Then read Section C to understand the work.',
                'key_concept': 'RFP Section Anatomy',
                'far_reference': 'Uniform Contract Format (UCF) — FAR 15.204',
            },
            'task_completed': {
                'teach': 'Document task completion with evidence — photos, reports, sign-offs. '
                         'Government contracts often require monthly progress reports. If you can\'t prove '
                         'you did it, you didn\'t do it. Keep a delivery log for every task. '
                         'This becomes your evidence for invoicing AND future past performance.',
                'key_concept': 'Performance Documentation',
                'far_reference': 'FAR 42.11 — Production Surveillance and Reporting',
            },
            'change_order_created': {
                'teach': 'Change orders are how contracts get modified after award. The government CANNOT '
                         'ask you to do work outside the original scope without a modification. If a CO asks '
                         'for extra work verbally, respond in writing: "Per our discussion, this appears '
                         'to be outside the current scope. Please issue a contract modification." '
                         'Never do free work. Protect your contract.',
                'key_concept': 'Contract Modifications',
                'far_reference': 'FAR 43 — Contract Modifications',
            },
            'wbs_generated': {
                'teach': 'A WBS breaks the contract into manageable pieces. Level 1 = the whole contract. '
                         'Level 2 = major deliverables. Level 3 = tasks within each deliverable. '
                         'Every task at the lowest level should have: an owner, a deadline, hours estimated, '
                         'and acceptance criteria. This is how you track whether you\'re on schedule and '
                         'on budget — and it\'s what the CO expects to see in status reports.',
                'key_concept': 'WBS Methodology',
                'far_reference': None,
            },
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # VERTEX — Financial Command Center
    # ══════════════════════════════════════════════════════════════════════════
    'vertex': {
        'system_name': 'VERTEX — Financial Command Center',
        'actions': {
            'invoice_created': {
                'teach': 'Government invoices follow strict rules. Most federal contracts use the '
                         'Wide Area Workflow (WAWF) system for invoicing. Invoices must match the CLIN '
                         'structure exactly — bill what the contract says, not what you think you did. '
                         'Include period of performance, CLIN number, quantity, unit price, and total. '
                         'Net 30 is standard but track payment dates — if they\'re late past 30 days, '
                         'you\'re entitled to interest under the Prompt Payment Act.',
                'key_concept': 'Government Invoicing',
                'far_reference': 'FAR 32.9 — Prompt Payment',
            },
            'expense_recorded': {
                'teach': 'Track every contract-related expense separately. Direct costs go against '
                         'specific contracts. Indirect costs (rent, admin, insurance) get allocated '
                         'across all contracts. If you ever do cost-reimbursable work, the government '
                         'can audit your books. Keep them clean. A good expense tracking system now '
                         'prevents painful audits later.',
                'key_concept': 'Direct vs Indirect Costs',
                'far_reference': 'FAR 31 — Contract Cost Principles',
            },
            'pl_generated': {
                'teach': 'Your P&L tells the real story. Revenue minus direct costs = gross profit. '
                         'Gross profit minus overhead = net profit. If your net margin on government '
                         'work is below 8%, you\'re working too hard for too little. Track margin by '
                         'contract type — products vs services have very different profiles. '
                         'Use this data to decide which contracts to pursue more aggressively.',
                'key_concept': 'Profit Margin Analysis',
                'far_reference': None,
            },
            'financial_health_checked': {
                'teach': 'Cash flow kills more small contractors than bad proposals. You might win '
                         'a $500K contract but not get paid for 45 days after invoicing. Meanwhile, '
                         'you\'re paying subs within 30 days. That gap is where companies fail. '
                         'Maintain a cash reserve of at least 2 months of operating expenses. '
                         'Consider a line of credit before you need one — banks lend when you don\'t '
                         'need it, not when you do.',
                'key_concept': 'Cash Flow Management',
                'far_reference': None,
            },
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # GBIS — Grant Business Intelligence System
    # ══════════════════════════════════════════════════════════════════════════
    'gbis': {
        'system_name': 'GBIS — Grant Intelligence',
        'actions': {
            'grant_discovered': {
                'teach': 'Grants are free money — but they\'re not free effort. A grant application '
                         'can take 40-100 hours to prepare. Focus on grants where DDI has a natural '
                         'advantage: EDWOSB-focused grants, small business development grants, '
                         'Michigan economic development funds. The ROI is best when the grant aligns '
                         'with what you\'re already doing — don\'t chase grants that require you to '
                         'become a different company.',
                'key_concept': 'Grant ROI Assessment',
                'far_reference': None,
            },
            'application_generated': {
                'teach': 'Grant applications are scored by reviewers with rubrics — similar to '
                         'government proposals. Address every criterion. Use their exact language. '
                         'Include measurable outcomes ("will serve 200 clients" not "will serve many"). '
                         'The story library lets you reuse strong narratives across applications. '
                         'A good application tells a story: here\'s the problem, here\'s our approach, '
                         'here\'s the evidence it works, here\'s the measurable impact.',
                'key_concept': 'Grant Application Strategy',
                'far_reference': None,
            },
            'score_calculated': {
                'teach': 'Your qualification score estimates how competitive your application will be. '
                         'A score below 60 means you\'re missing key elements — don\'t submit until '
                         'you\'ve addressed the gaps. Above 80 means strong position. '
                         'Focus effort on the highest-weighted scoring criteria first.',
                'key_concept': 'Qualification Scoring',
                'far_reference': None,
            },
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # DDCSS — Corporate Sales System
    # ══════════════════════════════════════════════════════════════════════════
    'ddcss': {
        'system_name': 'DDCSS — Corporate Sales',
        'actions': {
            'prospect_qualified': {
                'teach': 'Corporate sales is different from government. There\'s no public solicitation — '
                         'you create the opportunity. DDI\'s corporate clients need the same services as '
                         'government: drug testing, fingerprinting, notary, DNA collection, phlebotomy, '
                         'medical courier. The difference is pricing (no FAR, market rates), contracting '
                         '(MSA instead of government contract), and volume (often recurring). '
                         'When a corporate client is won, it flows into ATLAS for project management '
                         'and PRISM for field service delivery — same quality pipeline as government work.',
                'key_concept': 'Corporate Field Service Sales',
                'far_reference': None,
            },
            'blueprint_generated': {
                'teach': 'The 6-sector blueprint maps DDI\'s capabilities to market opportunities. '
                         'Each sector has different buyers, different cycles, and different margins. '
                         'Government is steady but slow. Corporate is faster but less predictable. '
                         'Diversifying across sectors reduces risk — if government contracts slow down, '
                         'corporate fills the gap.',
                'key_concept': 'Sector Diversification',
                'far_reference': None,
            },
            'pitchmap_created': {
                'teach': 'A pitchmap is your talk track turned into a system. Every objection has a '
                         'response. Every question has an answer. The goal is to never be caught off guard. '
                         'Record what works and what doesn\'t — the system learns which approaches '
                         'convert and which fall flat.',
                'key_concept': 'Sales Process Systematization',
                'far_reference': None,
            },
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # LBPC — Surplus Recovery System
    # ══════════════════════════════════════════════════════════════════════════
    'lbpc': {
        'system_name': 'LBPC — Surplus Recovery',
        'actions': {
            'lead_mined': {
                'teach': 'County surplus lists are public records. The key is volume and speed — '
                         'the faster you identify and contact property owners, the more likely '
                         'they sign with you before another firm reaches them. Quality the lead first: '
                         'Is the surplus amount worth pursuing? Is the property owner reachable? '
                         'Is there a valid claim? Don\'t spend time on $50 recoveries.',
                'key_concept': 'Lead Volume & Speed',
                'far_reference': None,
            },
            'document_generated': {
                'teach': 'The three documents in surplus recovery — Initial Notice, Engagement Agreement, '
                         'and Power of Attorney — must be legally compliant for the specific state. '
                         'Each state has different unclaimed property laws and fee caps. '
                         'Always verify state-specific requirements before sending documents.',
                'key_concept': 'State-Specific Compliance',
                'far_reference': None,
            },
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # PRISM — Field Service Command Center
    # ══════════════════════════════════════════════════════════════════════════
    'prism': {
        'system_name': 'PRISM — Field Service Operations',
        'actions': {
            'order_dispatched': {
                'teach': 'DDI delivers field services through PRISM: notary signings, drug testing '
                         '(DOT and non-DOT), DNA collection, phlebotomy, fingerprinting/livescan, and '
                         'medical courier. Each service type has different compliance requirements. '
                         'DOT drug tests follow 49 CFR Part 40 — a single fatal flaw voids the entire test. '
                         'Notary orders require seal, ID verification, and state-specific journal entries. '
                         'DNA collections require AABB chain of custody. Every dispatched order should have '
                         'the service type, compliance checklist, and agent qualifications confirmed.',
                'key_concept': 'Service-Specific Dispatch',
                'far_reference': '49 CFR Part 40 (DOT Drug Testing)',
            },
            'scanback_inspected': {
                'teach': 'Scanback inspection is your quality gate — and each service type has different '
                         'rules. Drug tests: verify CCF 5-copy form, donor signature, collector certification, '
                         'specimen temp. Notary: verify seal/stamp, signer ID, journal entry, correct venue. '
                         'DNA: verify chain of custody, photo ID match, buccal swab packaging. '
                         'Fingerprints: verify FBI CJIS quality standards, all 10 prints captured. '
                         'One bad document submitted to the government triggers a performance issue. '
                         'PRISM\'s 7-point inspection checklist catches errors before they leave your hands.',
                'key_concept': 'Service-Specific Quality Control',
                'far_reference': None,
            },
            'agent_assigned': {
                'teach': 'Field agents are independent contractors who represent DDI in the field. '
                         'Each service type requires specific credentials: drug test collectors need '
                         'DOT certification. Notaries need active commission + E&O insurance. DNA collectors '
                         'need AABB training. Fingerprint technicians need livescan certification. '
                         'Phlebotomists need state certification + CPT codes. Before assigning any agent, '
                         'verify: NDA signed, insurance current, credentials match the service type, '
                         'background check cleared. A reliable agent network is DDI\'s most valuable '
                         'asset for scaling service contracts.',
                'key_concept': 'Credentialed Agent Network',
                'far_reference': None,
            },
            'contract_registered': {
                'teach': 'When DDI wins a field service contract through GPSS, PRISM auto-registers it. '
                         'The contract flows: GPSS (win) → ATLAS (project management) → PRISM (service delivery) '
                         '→ VERTEX (invoicing). Your job in PRISM is to break the contract into individual '
                         'orders, assign qualified agents, inspect every scanback, and bill through VERTEX. '
                         'The government CO sees the final product — make sure every order meets the SOW.',
                'key_concept': 'Contract-to-Dispatch Flow',
                'far_reference': None,
            },
            'drug_test_completed': {
                'teach': 'DOT drug testing under 49 CFR Part 40 has specific fatal flaws that void the test '
                         'entirely: no collector signature, wrong specimen temperature, broken chain of custody, '
                         'incorrect CCF form. Non-DOT tests have more flexibility but still require proper '
                         'documentation. After collection, specimens go to a SAMHSA-certified lab. Track '
                         'the full chain: collection → courier to lab → MRO review → result to employer. '
                         'DDI\'s role is ensuring every step is documented and every agent is DOT-certified.',
                'key_concept': 'Drug Testing Compliance (49 CFR 40)',
                'far_reference': '49 CFR Part 40 — Procedures for Transportation Workplace Drug Testing',
            },
            'notary_completed': {
                'teach': 'Notary compliance varies by state — and DDI operates in multiple states. '
                         'Every state has different rules on: journal requirements, ID verification methods, '
                         'remote online notarization (RON), seal/stamp format, and venue (county vs state). '
                         'Common errors: missing seal, wrong venue, expired commission, no journal entry, '
                         'signer not personally present. PRISM\'s inspection engine has 31 notary-specific '
                         'rules from PCS CommonErrors data. One bad notarization can void an entire document.',
                'key_concept': 'State-Specific Notary Compliance',
                'far_reference': None,
            },
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # COMPASS — Post-Award Contract Operations
    # ══════════════════════════════════════════════════════════════════════════
    'compass': {
        'system_name': 'COMPASS — Post-Award Operations',
        'actions': {
            'contract_activated': {
                'teach': 'The moment a contract is awarded, you become responsible for execution. '
                         'First 10 days: expect a post-award conference where the CO verifies you can perform. '
                         'Have your subs ready, insurance current, staffing plan finalized, and transition plan documented. '
                         'COMPASS tracks everything from here — deliverables, payments, compliance, and CO communications. '
                         'Your CPARS rating starts accumulating from day one. Every missed deadline, every communication '
                         'gap, every quality issue gets recorded. Treat the contract like your reputation depends on it — because it does.',
                'key_concept': 'Post-Award Activation',
                'far_reference': 'FAR 42.5 — Post-Award Orientation',
            },
            'deliverable_completed': {
                'teach': 'Every deliverable completion needs documentation: what was delivered, when, and evidence '
                         'of quality. Government CORs verify deliverables against the SOW before approving payment. '
                         'If you submit a report and it doesn\'t match the CDRL format or misses a required section, '
                         'it gets rejected and you don\'t get paid until it\'s fixed. Build a checklist from the SOW '
                         'for each deliverable type — check every box before submitting.',
                'key_concept': 'Deliverable Documentation',
                'far_reference': 'FAR 46 — Quality Assurance',
            },
            'co_communication_logged': {
                'teach': 'Document every single interaction with the CO and COR. Emails, phone calls, meetings — '
                         'all of it. If the CO asks for something verbally, follow up in writing: "Per our conversation '
                         'today, you requested X. We will deliver Y by Z date. Please confirm." This protects DDI '
                         'from scope creep, verbal-only changes, and "he said / she said" situations. The paper trail '
                         'is your insurance policy.',
                'key_concept': 'Communication Documentation',
                'far_reference': 'FAR 1.602 — Contracting Officers',
            },
            'modification_logged': {
                'teach': 'Contract modifications are formal changes to the contract terms. There are two types: '
                         'bilateral (both parties agree) and unilateral (the government changes it — usually admin). '
                         'If the CO asks for work outside the original scope, NEVER do it without a signed modification. '
                         'Respond in writing: "This appears outside the current scope. Please issue a contract modification '
                         'under FAR 43." Free work sets a precedent and reduces your profit. Mods can add value (option years, '
                         'scope expansion) or reduce it (partial termination). Track every mod — the cumulative changes '
                         'affect your contract ceiling and profit margin.',
                'key_concept': 'Contract Modifications',
                'far_reference': 'FAR 43 — Contract Modifications',
            },
            'report_generated': {
                'teach': 'Monthly performance reports are your chance to show the CO that DDI is executing well. '
                         'Include: deliverables completed, upcoming milestones, any issues and resolution plans, '
                         'financial status (invoiced vs. paid), and subcontractor performance. A consistent, '
                         'professional report builds trust and directly influences your CPARS rating. COs remember '
                         'contractors who communicate proactively. Don\'t wait for them to ask what\'s happening.',
                'key_concept': 'Performance Reporting',
                'far_reference': 'FAR 42.15 — Contractor Performance Information (CPARS)',
            },
            'health_checked': {
                'teach': 'Contract health is a composite: are deliverables on time? Is payment flowing? '
                         'Is the burn rate sustainable? Are there overdue items? A "Green" score (85+) means you\'re '
                         'on track for a Satisfactory or better CPARS. "Yellow" (65-84) means there are gaps that '
                         'need attention before they become issues. "Red" (below 65) means the CO is likely already '
                         'noticing problems. Fix Yellow before it turns Red. Fix Red before it hits CPARS.',
                'key_concept': 'Contract Health Monitoring',
                'far_reference': 'FAR 42.15 — CPARS',
            },
        },
    },

    # ══════════════════════════════════════════════════════════════════════════
    # COMMAND — Agenda & Workflow
    # ══════════════════════════════════════════════════════════════════════════
    'command': {
        'system_name': 'COMMAND — Agenda & Workflow',
        'actions': {
            'task_completed': {
                'teach': 'Consistency wins in government contracting. The companies pulling $50M+ '
                         'in contracts don\'t do it with one big win — they do it by executing '
                         'hundreds of small steps correctly every day. Your agenda is the engine. '
                         'Clear it daily. Follow up on every outreach. Submit every bid on time. '
                         'The compound effect of consistent execution is what builds a $10M pipeline.',
                'key_concept': 'Execution Consistency',
                'far_reference': None,
            },
            'email_sent': {
                'teach': 'Every email to a contracting officer is a micro-impression. They remember '
                         'the companies that were professional, responsive, and showed they did homework. '
                         'Use their name. Reference their specific solicitation. Ask smart questions. '
                         'Attach a tailored cap statement. Be the company they want to award to.',
                'key_concept': 'Buyer Relationship Building',
                'far_reference': None,
            },
        },
    },
}

# ─── DEBRIEF TEMPLATES (triggered by outcomes) ──────────────────────────────

DEBRIEF_TEMPLATES = {
    'bid_won': {
        'title': 'BID WON — Post-Award Debrief',
        'prompts': [
            'What was your evaluator score? Which factors were strongest?',
            'What markup did you use? Was it in the competitive range?',
            'Did you use a subcontractor? How was their performance during proposal prep?',
            'What buyer language did you mirror from the RFP?',
            'What would you do differently to score even higher?',
        ],
        'next_actions': [
            'Update past performance record with this contract',
            'Request and file the official award notice',
            'Prepare for post-award kickoff meeting',
            'Ensure subcontractor has NDA/COI/Teaming Agreement finalized',
            'Set up project in ATLAS with WBS from the proposal',
        ],
    },
    'bid_lost': {
        'title': 'BID LOST — Lessons Learned',
        'prompts': [
            'Request a debrief within 3 days (FAR 15.506)',
            'What was your evaluator score vs. the winner?',
            'Which factor was your weakest? Why?',
            'Was price the deciding factor or technical?',
            'What would make this proposal competitive next time?',
        ],
        'next_actions': [
            'Schedule debrief with CO',
            'Document lessons in learning engine',
            'Update evaluator model with outcome',
            'Review pricing against the winner if debrief reveals it',
            'Flag this opportunity for recompete tracking',
        ],
    },
    'contract_complete': {
        'title': 'CONTRACT COMPLETE — Performance Review',
        'prompts': [
            'Did you meet all deliverables on time?',
            'What was your actual margin vs. proposed margin?',
            'How did the subcontractor perform?',
            'Were there any change orders? How were they handled?',
            'What CPARS rating are you expecting?',
        ],
        'next_actions': [
            'Verify CPARS rating is posted (check in 30-60 days)',
            'Update past performance library',
            'Log final financials in VERTEX',
            'Evaluate subcontractor for future work',
            'Check for recompete or follow-on opportunities',
        ],
    },
}

# ─── GROWTH MILESTONES ──────────────────────────────────────────────────────

MILESTONES = [
    {'id': 'first_bid', 'name': 'First Bid Submitted', 'description': 'DDI submitted its first government bid'},
    {'id': 'first_win', 'name': 'First Contract Won', 'description': 'DDI won its first government contract'},
    {'id': 'first_100k', 'name': '$100K Contract', 'description': 'DDI won a contract valued at $100K+'},
    {'id': 'first_500k', 'name': '$500K Contract', 'description': 'DDI won a contract valued at $500K+'},
    {'id': 'first_1m', 'name': '$1M Contract', 'description': 'DDI won a contract valued at $1M+'},
    {'id': '5_bids', 'name': '5 Bids Submitted', 'description': 'DDI has submitted 5 government bids'},
    {'id': '10_bids', 'name': '10 Bids Submitted', 'description': 'DDI is becoming a consistent bidder'},
    {'id': '25_bids', 'name': '25 Bids Submitted', 'description': 'DDI is a serious government contractor'},
    {'id': 'first_sub_managed', 'name': 'First Subcontractor Managed', 'description': 'DDI primed a contract with a managed sub'},
    {'id': 'first_debrief', 'name': 'First Debrief Requested', 'description': 'DDI requested a post-award debrief — smart move'},
    {'id': 'win_rate_25', 'name': '25% Win Rate', 'description': 'DDI wins 1 in 4 bids — industry competitive'},
    {'id': 'win_rate_33', 'name': '33% Win Rate', 'description': 'DDI wins 1 in 3 bids — above industry average'},
    {'id': 'first_cpars', 'name': 'First CPARS Rating', 'description': 'DDI received its first CPARS evaluation'},
    {'id': 'multi_system', 'name': 'Multi-System Revenue', 'description': 'DDI has revenue from 2+ NEXUS systems'},
    {'id': 'pipeline_500k', 'name': '$500K Pipeline', 'description': 'DDI\'s active bid pipeline exceeds $500K'},
    {'id': 'pipeline_1m', 'name': '$1M Pipeline', 'description': 'DDI\'s active bid pipeline exceeds $1M'},
]


class NexusAdvisor:
    """
    Teaching engine that runs across all NEXUS systems.
    Surfaces contextual education, debriefs outcomes, and tracks growth.
    """

    def __init__(self):
        self._db = self._load_db()

    def _load_db(self) -> Dict:
        if ADVISOR_DB_PATH.exists():
            try:
                return json.loads(ADVISOR_DB_PATH.read_text())
            except Exception:
                pass
        return {
            'lessons_delivered': [],
            'milestones_achieved': [],
            'growth_stats': {
                'bids_submitted': 0,
                'bids_won': 0,
                'bids_lost': 0,
                'total_contract_value': 0,
                'total_outreach_emails': 0,
                'subs_managed': 0,
                'debriefs_requested': 0,
                'proposals_scored': 0,
                'invoices_created': 0,
                'grants_applied': 0,
            },
            'system_usage': defaultdict(int),
            'topics_encountered': [],
            'created_at': datetime.now().isoformat(),
        }

    def _save_db(self):
        db_copy = dict(self._db)
        if isinstance(db_copy.get('system_usage'), defaultdict):
            db_copy['system_usage'] = dict(db_copy['system_usage'])
        try:
            ADVISOR_DB_PATH.write_text(json.dumps(db_copy, indent=2, default=str))
        except Exception as e:
            print(f"Advisor DB save error: {e}")

    # ─── 1. TEACH — Contextual education triggered by actions ────────────────

    def teach(self, system: str, action: str, context: Dict = None) -> Dict:
        """
        Get contextual education for a specific action in a specific system.
        Returns teaching content, key concept, and optional FAR reference.
        """
        system_kb = KNOWLEDGE_BASE.get(system, {})
        action_kb = system_kb.get('actions', {}).get(action, {})

        if not action_kb:
            return {'has_advice': False}

        lesson_id = f"{system}_{action}_{datetime.now().strftime('%Y%m%d')}"
        is_new_topic = action not in self._db.get('topics_encountered', [])

        if is_new_topic:
            if 'topics_encountered' not in self._db:
                self._db['topics_encountered'] = []
            self._db['topics_encountered'].append(action)

        self._db['lessons_delivered'].append({
            'system': system,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'context': context,
        })
        if len(self._db['lessons_delivered']) > 500:
            self._db['lessons_delivered'] = self._db['lessons_delivered'][-300:]

        if isinstance(self._db.get('system_usage'), dict):
            self._db['system_usage'] = defaultdict(int, self._db['system_usage'])
        elif not isinstance(self._db.get('system_usage'), defaultdict):
            self._db['system_usage'] = defaultdict(int)
        self._db['system_usage'][system] += 1
        self._save_db()

        related_prompts = []
        try:
            from govcon_prompt_library import suggest_prompts
            suggestions = suggest_prompts(action)
            for s in suggestions[:2]:
                related_prompts.append({'id': s['id'], 'name': s['name'], 'prompt': s['prompt']})
        except Exception:
            pass

        result = {
            'has_advice': True,
            'system': system_kb.get('system_name', system),
            'action': action,
            'teach': action_kb.get('teach', ''),
            'key_concept': action_kb.get('key_concept', ''),
            'far_reference': action_kb.get('far_reference'),
            'is_new_topic': is_new_topic,
            'related_prompts': related_prompts,
        }

        if is_new_topic:
            result['new_topic_message'] = f"New concept: {action_kb.get('key_concept', action)}. This is important for DDI's growth."

        return result

    # ─── 2. DEBRIEF — Lessons learned from outcomes ──────────────────────────

    def debrief(self, outcome_type: str, context: Dict = None) -> Dict:
        """
        Generate a debrief based on an outcome (win, loss, contract complete).
        Returns structured prompts and next actions.
        """
        template = DEBRIEF_TEMPLATES.get(outcome_type, {})
        if not template:
            return {'has_debrief': False}

        stats = self._db.get('growth_stats', {})
        if outcome_type == 'bid_won':
            stats['bids_won'] = stats.get('bids_won', 0) + 1
            if context and context.get('contract_value'):
                stats['total_contract_value'] = stats.get('total_contract_value', 0) + context['contract_value']
        elif outcome_type == 'bid_lost':
            stats['bids_lost'] = stats.get('bids_lost', 0) + 1
        self._db['growth_stats'] = stats

        milestones_earned = self._check_milestones()
        self._save_db()

        total_bids = stats.get('bids_won', 0) + stats.get('bids_lost', 0)
        win_rate = round(stats.get('bids_won', 0) / max(total_bids, 1) * 100, 1)

        ai_prompts = []
        try:
            from govcon_prompt_library import get_prompts_by_context
            debrief_prompts = get_prompts_by_context('learning')
            for cat in debrief_prompts:
                for p in cat.get('prompts', [])[:3]:
                    ai_prompts.append({'id': p['id'], 'name': p['name'], 'prompt': p['prompt']})
        except Exception:
            pass

        return {
            'has_debrief': True,
            'title': template['title'],
            'prompts': template['prompts'],
            'next_actions': template['next_actions'],
            'ai_prompts': ai_prompts,
            'current_record': {
                'total_bids': total_bids,
                'wins': stats.get('bids_won', 0),
                'losses': stats.get('bids_lost', 0),
                'win_rate': win_rate,
                'total_value': stats.get('total_contract_value', 0),
            },
            'milestones_earned': milestones_earned,
        }

    # ─── 3. BRIEF — Periodic summary of growth and patterns ─────────────────

    def brief(self) -> Dict:
        """
        Generate a periodic briefing on DDI's growth, patterns, and status.
        """
        stats = self._db.get('growth_stats', {})
        milestones = self._db.get('milestones_achieved', [])
        usage = dict(self._db.get('system_usage', {}))
        topics = self._db.get('topics_encountered', [])
        total_lessons = len(self._db.get('lessons_delivered', []))

        total_bids = stats.get('bids_won', 0) + stats.get('bids_lost', 0)
        win_rate = round(stats.get('bids_won', 0) / max(total_bids, 1) * 100, 1) if total_bids > 0 else 0

        most_used = sorted(usage.items(), key=lambda x: x[1], reverse=True)[:3] if usage else []
        least_used = [s for s in KNOWLEDGE_BASE.keys() if s not in usage or usage.get(s, 0) < 3]

        all_milestones = {m['id']: m for m in MILESTONES}
        achieved_ids = [m['id'] for m in milestones]
        next_milestones = [m for m in MILESTONES if m['id'] not in achieved_ids][:3]

        total_actions_available = sum(
            len(sys_data.get('actions', {}))
            for sys_data in KNOWLEDGE_BASE.values()
        )
        knowledge_coverage = round(len(topics) / max(total_actions_available, 1) * 100, 1)

        patterns = []
        if total_bids >= 3 and win_rate >= 25:
            patterns.append(f"Your {win_rate}% win rate is competitive. Industry average for small business is 15-25%.")
        elif total_bids >= 3:
            patterns.append(f"Your {win_rate}% win rate is below the 25% target. Focus on set-asides where DDI has an edge.")
        if stats.get('debriefs_requested', 0) == 0 and stats.get('bids_lost', 0) > 0:
            patterns.append("You haven't requested a debrief yet. Every loss is wasted without one. FAR 15.506 gives you the right.")
        if usage.get('gpss', 0) > 10 and usage.get('vertex', 0) < 3:
            patterns.append("You're active in GPSS but not tracking financials in VERTEX. Know your margins.")
        if len(least_used) >= 3:
            patterns.append(f"Underutilized systems: {', '.join(s.upper() for s in least_used[:3])}. These have tools that can help.")

        return {
            'generated_at': datetime.now().isoformat(),
            'growth_stats': stats,
            'win_rate': win_rate,
            'total_bids': total_bids,
            'milestones_achieved': milestones,
            'milestones_next': next_milestones,
            'system_usage': dict(usage),
            'most_used_systems': most_used,
            'underutilized_systems': least_used,
            'knowledge_coverage': knowledge_coverage,
            'topics_learned': len(topics),
            'total_topics_available': total_actions_available,
            'total_lessons_delivered': total_lessons,
            'patterns': patterns,
        }

    # ─── 4. LOG — Track growth events ────────────────────────────────────────

    def log_event(self, event_type: str, metadata: Dict = None) -> Dict:
        """Log a growth event (bid submitted, email sent, invoice created, etc.)."""
        stats = self._db.get('growth_stats', {})

        event_to_stat = {
            'bid_submitted': 'bids_submitted',
            'email_sent': 'total_outreach_emails',
            'sub_managed': 'subs_managed',
            'debrief_requested': 'debriefs_requested',
            'proposal_scored': 'proposals_scored',
            'invoice_created': 'invoices_created',
            'grant_applied': 'grants_applied',
        }

        stat_key = event_to_stat.get(event_type)
        if stat_key:
            stats[stat_key] = stats.get(stat_key, 0) + 1
            self._db['growth_stats'] = stats

        milestones_earned = self._check_milestones()
        self._save_db()

        return {
            'logged': True,
            'event_type': event_type,
            'new_milestones': milestones_earned,
            'current_stats': stats,
        }

    # ─── MILESTONE CHECKING ─────────────────────────────────────────────────

    def _check_milestones(self) -> List[Dict]:
        stats = self._db.get('growth_stats', {})
        achieved_ids = {m['id'] for m in self._db.get('milestones_achieved', [])}
        new_milestones = []

        checks = {
            'first_bid': stats.get('bids_submitted', 0) >= 1,
            '5_bids': stats.get('bids_submitted', 0) >= 5,
            '10_bids': stats.get('bids_submitted', 0) >= 10,
            '25_bids': stats.get('bids_submitted', 0) >= 25,
            'first_win': stats.get('bids_won', 0) >= 1,
            'first_100k': stats.get('total_contract_value', 0) >= 100000,
            'first_500k': stats.get('total_contract_value', 0) >= 500000,
            'first_1m': stats.get('total_contract_value', 0) >= 1000000,
            'first_sub_managed': stats.get('subs_managed', 0) >= 1,
            'first_debrief': stats.get('debriefs_requested', 0) >= 1,
            'first_cpars': False,  # Manual trigger
        }

        total_decided = stats.get('bids_won', 0) + stats.get('bids_lost', 0)
        if total_decided >= 4:
            wr = stats.get('bids_won', 0) / total_decided
            checks['win_rate_25'] = wr >= 0.25
            checks['win_rate_33'] = wr >= 0.33

        for milestone in MILESTONES:
            if milestone['id'] not in achieved_ids and checks.get(milestone['id'], False):
                milestone_record = {
                    **milestone,
                    'achieved_at': datetime.now().isoformat(),
                }
                self._db.setdefault('milestones_achieved', []).append(milestone_record)
                new_milestones.append(milestone_record)

        return new_milestones

    def get_milestones(self) -> Dict:
        achieved = self._db.get('milestones_achieved', [])
        achieved_ids = {m['id'] for m in achieved}
        upcoming = [m for m in MILESTONES if m['id'] not in achieved_ids]
        return {
            'achieved': achieved,
            'upcoming': upcoming,
            'total_achieved': len(achieved),
            'total_possible': len(MILESTONES),
        }


# ─── SINGLETON ───────────────────────────────────────────────────────────────

_advisor = None


def get_advisor() -> NexusAdvisor:
    global _advisor
    if _advisor is None:
        _advisor = NexusAdvisor()
    return _advisor


# ─── CONVENIENCE FUNCTIONS (for other modules to call) ───────────────────────

def advise(system: str, action: str, context: Dict = None) -> Dict:
    """Get contextual teaching for an action. Call from any NEXUS module."""
    return get_advisor().teach(system, action, context)


def debrief(outcome_type: str, context: Dict = None) -> Dict:
    """Generate a debrief for an outcome."""
    return get_advisor().debrief(outcome_type, context)


def brief() -> Dict:
    """Generate a periodic growth briefing."""
    return get_advisor().brief()


def log_growth(event_type: str, metadata: Dict = None) -> Dict:
    """Log a growth event."""
    return get_advisor().log_event(event_type, metadata)
