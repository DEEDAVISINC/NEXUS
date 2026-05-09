"""
HAVEN Outreach Engine — Automated Partner & MCO Onboarding

The partner experience:
  1. Receives professional outreach package (email + one-pager PDF)
  2. Reviews the opportunity
  3. Signs NDA + Partnership Agreement via DocuSign
  4. Gets credentialed → Active in HAVEN network

DDI's experience:
  1. Click "Send Outreach" on a partner record
  2. System generates everything and stages for send
  3. Track status: Sent → Opened → Interested → NDA Signed → Agreement Signed → Active
  4. Partner auto-progresses through pipeline

No copy-pasting. No manual emails. No templates to fill in.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Optional

# ──────────────────────────────────────────────────────────────────────────
# OUTREACH PACKAGE GENERATION
# ──────────────────────────────────────────────────────────────────────────

DDI_INFO = {
    'company': 'Dee Davis Inc.',
    'owner': 'Dieasha D. Davis',
    'title': 'President & CEO',
    'display_name': 'Dee Davis',
    'phone': '248.376.4550',
    'email': 'info@deedavis.biz',
    'address': '755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084',
    'website': 'deedavis.biz',
    'cage': '8UMX3',
    'uei': 'HJB4KNYJVGZ1',
    'certs': 'EDWOSB | WOSB | WBENC | MBE | WBE | SBE',
}

HAVEN_STATES = ['FL', 'TX', 'LA', 'MI']
STATE_NAMES = {'FL': 'Florida', 'TX': 'Texas', 'LA': 'Louisiana', 'MI': 'Michigan'}


class OutreachPackage:
    """Represents a complete outreach package ready to send."""
    def __init__(self, partner_type: str, partner_name: str, partner_data: dict):
        self.partner_type = partner_type
        self.partner_name = partner_name
        self.partner_data = partner_data
        self.email_subject = ''
        self.email_body = ''
        self.one_pager_html = ''
        self.nda_ready = False
        self.agreement_ready = False
        self.generated_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            'partner_type': self.partner_type,
            'partner_name': self.partner_name,
            'email_subject': self.email_subject,
            'email_body': self.email_body,
            'one_pager_available': bool(self.one_pager_html),
            'nda_ready': self.nda_ready,
            'agreement_ready': self.agreement_ready,
            'generated_at': self.generated_at,
        }


class OutreachEngine:
    """
    Generates and manages automated outreach for HAVEN partners and MCOs.
    """

    def __init__(self):
        self.outreach_log: list[dict] = []

    # ─── TRANSPORT PARTNER OUTREACH ──────────────────────────────────

    def generate_transport_outreach(self, partner: dict) -> OutreachPackage:
        name = partner.get('company_name', 'Partner')
        contact = partner.get('contact_name', '')
        states = partner.get('states_served', [])
        if isinstance(states, str):
            states = [s.strip() for s in states.split(',')]
        state_str = ', '.join(states) if states else 'Gulf Coast / Southeast'
        greeting = f"Hi {contact}," if contact else "Hi,"

        pkg = OutreachPackage('transport', name, partner)
        pkg.email_subject = f"Disaster Response Transportation Network — Partnership Opportunity"
        pkg.email_body = f"""{greeting}

I'm reaching out because {name} has the kind of transportation capability that's critical for disaster response — and I'd like to talk about a partnership that puts your fleet to work during hurricane season and beyond.

Dee Davis Inc. is a federally certified EDWOSB building a credentialed disaster response network for Medicaid managed care organizations across {state_str}. When a hurricane or major disaster displaces members, MCOs need immediate, reliable transportation for evacuations, medical appointments, pharmacy runs, and relocation. That's where our transport partners come in.

HERE'S WHAT THE PARTNERSHIP LOOKS LIKE:

• DDI holds the MCO contracts — you never chase the business
• Pre-negotiated rates locked in before hurricane season
• Guaranteed dispatch volume during disaster activations
• All credentialing, compliance, and billing handled by DDI
• You provide vehicles and drivers — DDI handles everything else

WHAT WE'RE LOOKING FOR:

• Fleets operating in {state_str}
• Experience with medical transport, NEMT, or passenger services
• Ability to scale during disaster activations (24-48hr notice)
• Willingness to credential through DDI's network

We're finalizing our transport partner roster ahead of the 2026 hurricane season. Partners who sign early get priority dispatch during activations.

I've attached a one-page overview of the partnership structure and economics. If it makes sense, the next step is a quick 10-minute call — I'll walk you through how dispatch works and answer any questions.

The partnership agreement and NDA are available for electronic signature through DocuSign — no paperwork, no printing, no faxing.

Available any day after 12:00 PM ET.

Best regards,

{DDI_INFO['display_name']}
{DDI_INFO['title']}
{DDI_INFO['company']}
{DDI_INFO['address']}
{DDI_INFO['phone']} | {DDI_INFO['email']}
{DDI_INFO['certs']}"""

        pkg.one_pager_html = self._get_one_pager_path('transport')
        pkg.nda_ready = True
        pkg.agreement_ready = True
        return pkg

    # ─── HOUSING PARTNER OUTREACH ────────────────────────────────────

    def generate_housing_outreach(self, partner: dict) -> OutreachPackage:
        name = partner.get('property_name', partner.get('company_name', 'Partner'))
        contact = partner.get('contact_name', '')
        state = partner.get('state', '')
        state_name = STATE_NAMES.get(state, state) if state else 'Gulf Coast / Southeast'
        greeting = f"Hi {contact}," if contact else "Hi,"

        pkg = OutreachPackage('housing', name, partner)
        pkg.email_subject = f"Disaster Housing Network — Room Block Partnership"
        pkg.email_body = f"""{greeting}

When a hurricane displaces 50,000 Medicaid members overnight, the first question every managed care organization asks is: "Where do they sleep tonight?"

That's the problem Dee Davis Inc. solves — and {name} could be part of the answer.

DDI is building a pre-positioned disaster housing network for Medicaid MCOs across {state_name}. We're looking for hotel and extended-stay partners who can hold room blocks during disaster activations and provide safe, clean housing for displaced members and families.

HERE'S HOW IT WORKS:

• DDI contracts directly with MCOs — guaranteed payment, no chasing reimbursement
• Room blocks activated only during declared disasters (FEMA or state emergency)
• Pre-negotiated government/corporate rates locked in before hurricane season
• DDI handles member placement, check-in coordination, and billing
• Your property provides rooms — DDI handles everything else

WHAT MAKES A GOOD FIT:

• Properties in {state_name} (coastal or inland evacuation corridors)
• ADA accessible rooms available
• Ability to hold blocks of 10-50+ rooms on short notice
• Government/corporate billing accepted
• Extended stay capability preferred (7-30 day stays)

PARTNER ECONOMICS:

• Guaranteed occupancy during disaster periods (no vacancy risk)
• Government rates with reliable payment (DDI pays, not individuals)
• Extended stays = predictable revenue blocks
• Priority partnership for properties that commit early

The attached overview covers the full partnership structure. If it makes sense for {name}, the next step is a quick call — I'll explain how activations work and get you set up.

Everything is electronic — NDA and partnership agreement available via DocuSign. No paperwork.

Available any day after 12:00 PM ET.

Best regards,

{DDI_INFO['display_name']}
{DDI_INFO['title']}
{DDI_INFO['company']}
{DDI_INFO['address']}
{DDI_INFO['phone']} | {DDI_INFO['email']}
{DDI_INFO['certs']}"""

        pkg.one_pager_html = self._get_one_pager_path('housing')
        pkg.nda_ready = True
        pkg.agreement_ready = True
        return pkg

    # ─── MEDICAL PARTNER OUTREACH ────────────────────────────────────

    def generate_medical_outreach(self, partner: dict) -> OutreachPackage:
        name = partner.get('company_name', 'Partner')
        contact = partner.get('contact_name', '')
        partner_type = partner.get('partner_type', 'Medical Services')
        states = partner.get('states_served', [])
        if isinstance(states, str):
            states = [s.strip() for s in states.split(',')]
        state_str = ', '.join(states) if states else 'Gulf Coast / Southeast'
        greeting = f"Hi {contact}," if contact else "Hi,"

        pkg = OutreachPackage('medical', name, partner)
        pkg.email_subject = f"Disaster Medical Services Network — {partner_type} Partnership"
        pkg.email_body = f"""{greeting}

After a hurricane, displaced Medicaid members don't stop needing their medications, their home health visits, or their DME. But their usual providers are often unreachable. That gap in continuity of care is dangerous — and it's exactly what DDI's HAVEN network is built to fill.

Dee Davis Inc. is assembling a credentialed medical services network for Medicaid managed care organizations across {state_str}. We connect MCOs with pre-credentialed providers who can deliver continuity of care to displaced members during and after disaster events.

WE'RE LOOKING FOR {partner_type.upper()} PARTNERS WHO PROVIDE:

• Home health services (nursing, therapy, aide visits)
• DME delivery and setup
• Pharmacy delivery (Rx continuity for displaced members)
• Telehealth capability
• Wound care, chronic disease management
• Any medical service that displaced members need access to

THE DDI PARTNERSHIP MODEL:

• DDI contracts with the MCOs — you get dispatched through our network
• Pre-credentialed before hurricane season = immediate activation
• DDI handles care coordination, member intake, and MCO billing
• You provide the clinical services — DDI provides the patients and payment
• No cold calling, no sales, no insurance navigation

WHY SIGN NOW:

• Hurricane season starts June 1 — early partners get priority dispatch
• Pre-credentialing takes time — start now, be ready when it matters
• MCOs are actively seeking disaster-ready provider networks
• Partners who are credentialed and signed get first call during activations

The attached overview explains the full partnership model. If {name} is interested, the next step is a 10-minute call to review the scope and get your credentialing started.

NDA and partnership agreement available via DocuSign — completely electronic, no paperwork.

Available any day after 12:00 PM ET.

Best regards,

{DDI_INFO['display_name']}
{DDI_INFO['title']}
{DDI_INFO['company']}
{DDI_INFO['address']}
{DDI_INFO['phone']} | {DDI_INFO['email']}
{DDI_INFO['certs']}"""

        pkg.one_pager_html = self._get_one_pager_path('medical')
        pkg.nda_ready = True
        pkg.agreement_ready = True
        return pkg

    # ─── MCO OUTREACH ────────────────────────────────────────────────

    def generate_mco_outreach(self, mco: dict) -> OutreachPackage:
        name = mco.get('mco_name', 'MCO')
        contact = mco.get('contact_name', '')
        state = mco.get('state', '')
        state_name = STATE_NAMES.get(state, state) if state else 'your state'
        members = mco.get('member_count', 0)
        member_str = f"{members:,}" if members else 'your'
        greeting = f"Hi {contact}," if contact else "Hi,"

        pkg = OutreachPackage('mco', name, mco)
        pkg.email_subject = f"Disaster Response TPA — Pre-Built Network Ready for {name}"
        pkg.email_body = f"""{greeting}

When the next hurricane hits {state_name}, {name} will need to relocate, transport, and maintain medical continuity for {member_str} members — in 24 to 48 hours. The question isn't whether it will happen. The question is whether the infrastructure is already in place.

Dee Davis Inc. has built that infrastructure.

DDI is a federally certified EDWOSB operating as a disaster response Third Party Administrator. We've assembled a pre-credentialed network of transportation, housing, and medical service providers across Florida, Texas, Louisiana, and Michigan — specifically for Medicaid MCO disaster response.

WHAT DDI PROVIDES TO {name.upper()}:

• Pre-credentialed transport network (evacuation, medical transport, pharmacy runs)
• Pre-positioned housing partners (hotel room blocks, extended stay, ADA accessible)
• Medical continuity providers (home health, DME, pharmacy delivery, telehealth)
• Real-time disaster monitoring with FEMA + NWS integration
• Single point of contact for all disaster logistics
• HIPAA-compliant case management and member tracking
• Cost containment through pre-negotiated network rates
• Regulatory compliance documentation and reporting

THE ECONOMICS:

• No cost to {name} until activation — DDI maintains the network at our expense
• Per-member or per-service billing during disaster events
• Pre-negotiated rates 15-30% below emergency procurement costs
• Eliminates the scramble to find providers during a disaster
• Audit-ready documentation for CMS and state regulators

WHY NOW:

• Hurricane season begins June 1, 2026
• DDI's network is being finalized — {name} can shape the scope
• Partnering before a disaster = planning. Partnering during = panic pricing.
• FEMA declarations trigger immediate network activation

I'd like to schedule a 20-minute call to walk through our activation protocol and network map for {state_name}. Available any day after 12:00 PM ET.

Best regards,

{DDI_INFO['display_name']}
{DDI_INFO['title']}
{DDI_INFO['company']}
{DDI_INFO['address']}
{DDI_INFO['phone']} | {DDI_INFO['email']}
{DDI_INFO['certs']}

For immediate needs under $15,000, Dee Davis Inc. is available for direct micro-purchase — no competition required, SAM-registered and ready. For needs up to $350,000, we're available under simplified acquisition procedures with fast turnaround and reduced competition requirements."""

        pkg.one_pager_html = self._get_one_pager_path('mco')
        pkg.nda_ready = True
        pkg.agreement_ready = True
        return pkg

    # ─── FOLLOW-UP GENERATION ────────────────────────────────────────

    def generate_followup(self, partner_type: str, partner: dict, days_since: int = 7) -> OutreachPackage:
        name = partner.get('company_name', partner.get('property_name', partner.get('mco_name', 'Partner')))
        contact = partner.get('contact_name', '')
        greeting = f"Hi {contact}," if contact else "Hi,"

        pkg = OutreachPackage(partner_type, name, partner)

        if days_since <= 7:
            pkg.email_subject = f"Following Up — Disaster Response Network Partnership"
            pkg.email_body = f"""{greeting}

I wanted to follow up on my previous message about joining DDI's disaster response network.

We're finalizing our partner roster for the 2026 hurricane season. The partnership is straightforward — DDI brings the MCO contracts and dispatch volume, you provide the capacity. All credentialing, billing, and coordination is handled by DDI.

If you have 10 minutes this week, I'd love to walk through how it works. The whole onboarding process is electronic — NDA and agreement through DocuSign, no paperwork.

Available any day after 12:00 PM ET.

Best regards,

{DDI_INFO['display_name']}
{DDI_INFO['title']}
{DDI_INFO['company']}
{DDI_INFO['phone']} | {DDI_INFO['email']}"""

        elif days_since <= 14:
            pkg.email_subject = f"Hurricane Season Approaching — Last Call for Early Partner Roster"
            pkg.email_body = f"""{greeting}

Quick note — DDI is closing our early partner roster for the 2026 hurricane season. Partners who sign before June 1 get priority dispatch during activations.

The value proposition is simple: DDI holds the MCO contracts. When a disaster hits, our partners get dispatched first. No cold calling, no sales, no billing headaches — DDI handles all of that.

If {name} is interested, I can have the DocuSign package to you today. 10 minutes on a call is all we need to get started.

Available after 12:00 PM ET.

Best regards,

{DDI_INFO['display_name']}
{DDI_INFO['title']}
{DDI_INFO['company']}
{DDI_INFO['phone']} | {DDI_INFO['email']}"""

        else:
            pkg.email_subject = f"Still Open — Disaster Response Network Opportunity"
            pkg.email_body = f"""{greeting}

I reached out a few weeks ago about DDI's disaster response network for Medicaid managed care organizations. I know timing matters — if now isn't right, I completely understand.

If {name}'s capacity or priorities shift, the opportunity is still open. We're always looking for strong partners in the Gulf Coast and Southeast markets.

Feel free to reach out anytime.

Best regards,

{DDI_INFO['display_name']}
{DDI_INFO['title']}
{DDI_INFO['company']}
{DDI_INFO['phone']} | {DDI_INFO['email']}"""

        return pkg

    # ─── AGREEMENT GENERATION ────────────────────────────────────────

    def generate_nda_package(self, partner_type: str, partner: dict) -> dict:
        name = partner.get('company_name', partner.get('property_name', partner.get('mco_name', 'Partner')))
        today = datetime.now().strftime('%B %d, %Y')

        return {
            'document_type': 'NDA',
            'partner_name': name,
            'partner_type': partner_type,
            'generated_date': today,
            'status': 'Ready for DocuSign',
            'signers': [
                {'role': 'DDI', 'name': DDI_INFO['owner'], 'email': DDI_INFO['email']},
                {'role': 'Partner', 'name': partner.get('contact_name', ''), 'email': partner.get('contact_email', partner.get('email', ''))},
            ],
            'terms': {
                'confidentiality_period': '2 years after termination',
                'covers': 'All contract information, client identities, pricing, member data',
                'non_compete': '12 months post-contract in same service area',
                'no_end_run': 'Partner may not bid directly on DDI client contracts',
                'governing_law': 'State of Michigan',
            },
        }

    def generate_partnership_agreement(self, partner_type: str, partner: dict) -> dict:
        name = partner.get('company_name', partner.get('property_name', 'Partner'))
        today = datetime.now().strftime('%B %d, %Y')

        scope = {
            'transport': 'Disaster response transportation services including evacuation transport, medical appointment transport, pharmacy runs, and relocation assistance for displaced Medicaid members.',
            'housing': 'Temporary disaster housing including hotel room blocks, extended stay accommodations, and ADA-accessible units for displaced Medicaid members and families.',
            'medical': 'Medical continuity services including home health, DME delivery, pharmacy delivery, telehealth, and clinical services for displaced Medicaid members.',
        }

        return {
            'document_type': 'Partnership Agreement',
            'partner_name': name,
            'partner_type': partner_type,
            'generated_date': today,
            'status': 'Ready for DocuSign',
            'signers': [
                {'role': 'DDI (Prime)', 'name': DDI_INFO['owner'], 'email': DDI_INFO['email']},
                {'role': 'Partner (Sub)', 'name': partner.get('contact_name', ''), 'email': partner.get('contact_email', partner.get('email', ''))},
            ],
            'terms': {
                'scope': scope.get(partner_type, 'Disaster response services'),
                'service_area': ', '.join(partner.get('states_served', HAVEN_STATES)),
                'term': '1 year, auto-renewal',
                'payment': 'Net 30 from DDI upon MCO reimbursement',
                'insurance_required': 'General liability $1M/$2M, workers comp, auto if applicable',
                'ddi_as_additional_insured': True,
                'communication': 'All MCO/government communication through DDI only',
                'reporting': 'Weekly status during activations, monthly otherwise',
                'termination': '30 days written notice, immediate for cause',
            },
        }

    # ─── OUTREACH PIPELINE STATUS ────────────────────────────────────

    def get_pipeline_actions(self, partner: dict) -> list[dict]:
        """
        Returns the available automated actions for a partner based on their current status.
        """
        status = partner.get('agreement_status', partner.get('contract_status', 'Prospect'))
        actions = []

        if status == 'Prospect':
            actions.append({
                'action': 'send_outreach',
                'label': 'Send Outreach Package',
                'description': 'Generates professional email + one-pager and stages for send',
                'icon': '📧',
                'color': '#3b82f6',
                'available': True,
            })

        if status in ('Prospect', 'Outreach'):
            actions.append({
                'action': 'send_followup',
                'label': 'Send Follow-Up',
                'description': 'Auto-generates follow-up based on days since last contact',
                'icon': '🔄',
                'color': '#d97706',
                'available': True,
            })

        if status in ('Outreach', 'Negotiating'):
            actions.append({
                'action': 'send_nda',
                'label': 'Send NDA via DocuSign',
                'description': 'Generates NDA and sends for electronic signature',
                'icon': '🔒',
                'color': '#8b5cf6',
                'available': True,
            })

        if status in ('Negotiating', 'Signed'):
            actions.append({
                'action': 'send_agreement',
                'label': 'Send Partnership Agreement',
                'description': 'Generates partnership agreement and sends via DocuSign',
                'icon': '📝',
                'color': '#059669',
                'available': True,
            })

        if status == 'Signed':
            actions.append({
                'action': 'activate',
                'label': 'Activate Partner',
                'description': 'Mark partner as Active in the HAVEN network',
                'icon': '✅',
                'color': '#059669',
                'available': True,
            })

        return actions

    # ─── UTILITIES ───────────────────────────────────────────────────

    def _get_one_pager_path(self, partner_type: str) -> str:
        base = os.path.dirname(os.path.abspath(__file__))
        paths = {
            'transport': os.path.join(base, 'NEXUS_LEARNING', 'HAVEN_Transport_Partnership_OnePager.html'),
            'housing': os.path.join(base, 'NEXUS_LEARNING', 'HAVEN_Housing_Partnership_OnePager.html'),
            'medical': os.path.join(base, 'NEXUS_LEARNING', 'HAVEN_Medical_Partnership_OnePager.html'),
            'mco': os.path.join(base, 'NEXUS_LEARNING', 'HAVEN_MCO_Partnership_OnePager.html'),
        }
        path = paths.get(partner_type, '')
        return path if os.path.exists(path) else ''


# Singleton
_engine = OutreachEngine()

def generate_outreach(partner_type: str, partner: dict) -> dict:
    if partner_type == 'transport':
        return _engine.generate_transport_outreach(partner).to_dict()
    elif partner_type == 'housing':
        return _engine.generate_housing_outreach(partner).to_dict()
    elif partner_type == 'medical':
        return _engine.generate_medical_outreach(partner).to_dict()
    elif partner_type == 'mco':
        return _engine.generate_mco_outreach(partner).to_dict()
    else:
        raise ValueError(f"Unknown partner type: {partner_type}")

def generate_followup(partner_type: str, partner: dict, days_since: int = 7) -> dict:
    return _engine.generate_followup(partner_type, partner, days_since).to_dict()

def generate_nda(partner_type: str, partner: dict) -> dict:
    return _engine.generate_nda_package(partner_type, partner)

def generate_agreement(partner_type: str, partner: dict) -> dict:
    return _engine.generate_partnership_agreement(partner_type, partner)

def get_pipeline_actions(partner: dict) -> list[dict]:
    return _engine.get_pipeline_actions(partner)
