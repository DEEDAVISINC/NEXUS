"""
GBIS Community Health & Research Grant Miner
=============================================
Mines federal and foundation grants for the Community Health & Market Research lane.
Applies ResearchLaneDetector to tag grants and assigns Applicant Entity
(DDI vs Cause We Care) automatically.

Cause We Care Entity Info:
  Legal Name:  Cause We Care
  EIN:         92-3602670
  Type:        501(c)(3) Nonprofit
  Director:    Gary C. Felton Jr. (U.S. Army Veteran)
  Programs:    MIBridges (MDHHS), Hair Cuts for Vets, community health,
               veteran employment initiative

Funding channels covered:
  Federal:    NIH NIMHD, HRSA, SAMHSA, USDA FNS, HUD, ACF, HHS ASPE,
              DOL VETS (veteran employment grants)
  Veteran:    DAV Charitable Trust, VFW Foundation, Bob Woodruff Foundation,
              Gary Sinise Foundation, JPMorgan Chase Veteran Jobs Mission
  Michigan:   Michigan Health Endowment Fund, Kresge, W.K. Kellogg,
              Community Foundation for SE Michigan, Ralph C. Wilson Jr. Foundation
  Platform:   Grants.gov API

Tables written to:  GBIS OPPORTUNITIES
New fields used:    Service Lane, Research Subtype, Applicant Entity, Funding Type
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Import core NEXUS dependencies
try:
    from nexus_backend import AirtableClient, AnthropicClient, ResearchLaneDetector
except ImportError:
    raise ImportError("Run from NEXUS BACKEND root directory.")


# ---------------------------------------------------------------------------
# MICHIGAN FOUNDATION GRANT SOURCES
# These are manually monitored — no API, portal-based applications.
# Included here as seed records so GBIS tracks them and shows deadlines.
# ---------------------------------------------------------------------------

MICHIGAN_FOUNDATION_SOURCES = [
    {
        'Grant Name': 'Michigan Health Endowment Fund — Community Health',
        'Funder Organization': 'Michigan Health Endowment Fund',
        'Funder Type': 'Michigan Foundation',
        'Funding Type': 'Foundation Grant',
        'Grant URL': 'https://mihealthfund.org/funding',
        'Eligibility': '501(c)(3) organizations serving Michigan residents. Community health focus required.',
        'Typical Award': '$50,000 – $500,000',
        'Cycle': 'Q2 and Q4 annually',
        'Priority Level': 'Critical (90-100)',
        'Qualification Score': 92,
        'Service Lane': 'Community Health & Research',
        'Research Subtype': 'Community Health Assessment',
        'Applicant Entity': 'Cause We Care',
        'Notes': 'DDI MDHHS MIBridges Community Partner status highly relevant. '
                 'Cause We Care community health programming is direct fit. '
                 'Apply Q2 2026 cycle. Register on MHEF portal first.',
        'Action Required': 'Register Cause We Care on MHEF portal. Confirm Q2 deadline.',
    },
    {
        'Grant Name': 'Kresge Foundation — Health Equity Detroit',
        'Funder Organization': 'Kresge Foundation',
        'Funder Type': 'National Foundation (Detroit HQ)',
        'Funding Type': 'Foundation Grant',
        'Grant URL': 'https://kresge.org/grants-social-investments/how-to-apply/',
        'Eligibility': '501(c)(3) organizations. Detroit/SE Michigan focus preferred. '
                       'Health equity and community impact required.',
        'Typical Award': '$100,000 – $500,000',
        'Cycle': 'Rolling (invite-only for large grants; LOI process for new applicants)',
        'Priority Level': 'High (80-89)',
        'Qualification Score': 84,
        'Service Lane': 'Community Health & Research',
        'Research Subtype': 'Community Health Assessment',
        'Applicant Entity': 'Cause We Care',
        'Notes': 'Kresge is Detroit-based and actively funds SE Michigan health equity work. '
                 'Start with Letter of Inquiry (LOI). Reference MIBridges partnership, '
                 'Wayne Metro liaison role, lead testing coordination.',
        'Action Required': 'Submit LOI to Kresge Health Program. Reference MDHHS partnership.',
    },
    {
        'Grant Name': "W.K. Kellogg Foundation — Michigan Community Health",
        'Funder Organization': 'W.K. Kellogg Foundation',
        'Funder Type': 'National Foundation (Battle Creek HQ)',
        'Funding Type': 'Foundation Grant',
        'Grant URL': 'https://wkkf.org/grants/apply',
        'Eligibility': '501(c)(3). Michigan focus strong advantage. Child welfare, '
                       'community health, racial equity priorities.',
        'Typical Award': '$100,000 – $750,000',
        'Cycle': 'Annual (typically opens Q1)',
        'Priority Level': 'High (80-89)',
        'Qualification Score': 81,
        'Service Lane': 'Community Health & Research',
        'Research Subtype': 'Program Evaluation',
        'Applicant Entity': 'Cause We Care',
        'Notes': 'Strong Michigan roots, child welfare + community health = '
                 'direct Cause We Care alignment. Apply 2027 after MHEF win establishes track record.',
        'Action Required': 'Monitor for 2027 cycle. Build track record with MHEF first.',
    },
    {
        'Grant Name': 'Robert Wood Johnson Foundation — Health Equity',
        'Funder Organization': 'Robert Wood Johnson Foundation',
        'Funder Type': 'National Foundation',
        'Funding Type': 'Foundation Grant',
        'Grant URL': 'https://rwjf.org/en/grants/how-we-fund.html',
        'Eligibility': '501(c)(3). Social determinants of health, health equity, '
                       'community-based research.',
        'Typical Award': '$200,000 – $1,000,000',
        'Cycle': 'Rolling by program area',
        'Priority Level': 'High (80-89)',
        'Qualification Score': 78,
        'Service Lane': 'Community Health & Research',
        'Research Subtype': 'Community Health Assessment',
        'Applicant Entity': 'Cause We Care',
        'Notes': 'Large national foundation. Competitive. Best approached after '
                 'establishing 1-2 Michigan foundation wins. MIBridges + MDHHS = strong SDOH narrative.',
        'Action Required': 'Target 2027. Monitor RWJF call for proposals by program area.',
    },
    {
        'Grant Name': 'Community Foundation for Southeast Michigan — Community Health',
        'Funder Organization': 'Community Foundation for Southeast Michigan',
        'Funder Type': 'Regional Foundation',
        'Funding Type': 'Foundation Grant',
        'Grant URL': 'https://cfsem.org/grants/',
        'Eligibility': '501(c)(3) serving Wayne, Oakland, Macomb, Washtenaw, '
                       'Monroe, St. Clair, or Livingston counties.',
        'Typical Award': '$25,000 – $200,000',
        'Cycle': 'Quarterly',
        'Priority Level': 'Critical (90-100)',
        'Qualification Score': 95,
        'Service Lane': 'Community Health & Research',
        'Research Subtype': 'Community Health Assessment',
        'Applicant Entity': 'Cause We Care',
        'Notes': 'FASTEST path to first grant win. Quarterly cycle, regional focus, '
                 'smaller competition pool than national foundations. '
                 'Cause We Care SE Michigan presence = direct fit. Apply Q2 2026.',
        'Action Required': 'PRIORITY — Apply Q2 2026. Register on CFSEM portal NOW.',
    },
    {
        'Grant Name': 'Ralph C. Wilson Jr. Foundation — SE Michigan Community Impact',
        'Funder Organization': 'Ralph C. Wilson Jr. Foundation',
        'Funder Type': 'Regional Foundation',
        'Funding Type': 'Foundation Grant',
        'Grant URL': 'https://rcwjr.org/apply/',
        'Eligibility': '501(c)(3). SE Michigan (Detroit region) focus. '
                       'Youth, aging, sports/recreation, caregiving priorities.',
        'Typical Award': '$50,000 – $500,000',
        'Cycle': 'Annual',
        'Priority Level': 'High (80-89)',
        'Qualification Score': 79,
        'Service Lane': 'Community Health & Research',
        'Research Subtype': 'Program Evaluation',
        'Applicant Entity': 'Cause We Care',
        'Notes': 'Caregiving angle fits Cause We Care mission well. '
                 'Less direct fit than MHEF/CFSEM but worth pursuing in year 2.',
        'Action Required': 'Monitor for next cycle. Apply 2027.',
    },
]

# ---------------------------------------------------------------------------
# VETERAN GRANT SOURCES
# Unlocked by: Gary C. Felton Jr. (Army Veteran, Board Director) +
#              DDI/CWC veteran hiring initiative + Hair Cuts for Vets program
# Applicant: Cause We Care (for community grants) or DDI (for employer grants)
# ---------------------------------------------------------------------------

VETERAN_GRANT_SOURCES = [
    {
        'Grant Name': 'DOL VETS — Homeless Veterans Reintegration Program (HVRP)',
        'Funder Organization': 'U.S. Department of Labor — VETS',
        'Funder Type': 'Federal Government',
        'Funding Type': 'Federal Grant',
        'Grant URL': 'https://www.dol.gov/agencies/vets/programs/hvrp',
        'Eligibility': '501(c)(3), state/local government, tribal orgs. '
                       'Programs providing employment and training services to homeless veterans.',
        'Typical Award': '$100,000 – $1,000,000',
        'Cycle': 'Annual (typically opens Q1–Q2)',
        'Priority Level': 'Critical (90-100)',
        'Qualification Score': 90,
        'Service Lane': 'Community Health & Research',
        'Research Subtype': 'Program Evaluation',
        'Applicant Entity': 'Cause We Care',
        'Notes': 'DIRECT FIT. Cause We Care works with homeless systems (Coordinated Entry '
                 'certificate). Gary Felton Jr. (Army Veteran, Director) provides veteran '
                 'community credibility. Hair Cuts for Vets demonstrates existing veteran '
                 'engagement. This is a strong first federal grant target.',
        'Action Required': 'PRIORITY after CWC SAM registration. Watch grants.gov for HVRP NOFO.',
    },
    {
        'Grant Name': 'DAV (Disabled American Veterans) Charitable Trust Grant',
        'Funder Organization': 'DAV Charitable Trust',
        'Funder Type': 'Veteran Foundation',
        'Funding Type': 'Foundation Grant',
        'Grant URL': 'https://www.dav.org/learn-more/charitable-service-trust/',
        'Eligibility': '501(c)(3). Programs that directly benefit disabled veterans '
                       'and their families.',
        'Typical Award': '$5,000 – $50,000',
        'Cycle': 'Rolling / quarterly review',
        'Priority Level': 'Critical (90-100)',
        'Qualification Score': 91,
        'Service Lane': 'Community Health & Research',
        'Research Subtype': 'Program Evaluation',
        'Applicant Entity': 'Cause We Care',
        'Notes': 'FASTEST veteran grant path. Small enough for first application, '
                 'strong alignment with Hair Cuts for Vets + veteran hiring initiative. '
                 'Gary Felton Jr. as Army Veteran Director is a direct credibility signal. '
                 'Apply as soon as CWC SAM registration is complete.',
        'Action Required': 'APPLY FIRST. Rolling applications. Reference Gary Felton, '
                           'Hair Cuts for Vets, and veteran hiring program.',
    },
    {
        'Grant Name': 'Bob Woodruff Foundation — Veteran Reintegration',
        'Funder Organization': 'Bob Woodruff Foundation',
        'Funder Type': 'Veteran Foundation',
        'Funding Type': 'Foundation Grant',
        'Grant URL': 'https://bobwoodrufffoundation.org/how-to-apply/',
        'Eligibility': '501(c)(3). Programs focused on post-9/11 veteran and '
                       'caregiver reintegration into communities.',
        'Typical Award': '$50,000 – $500,000',
        'Cycle': 'Annual (LOI process)',
        'Priority Level': 'High (80-89)',
        'Qualification Score': 83,
        'Service Lane': 'Community Health & Research',
        'Research Subtype': 'Program Evaluation',
        'Applicant Entity': 'Cause We Care',
        'Notes': 'Veteran employment initiative + Gary Felton community engagement = '
                 'strong narrative. Mid-tier foundation — more competitive than DAV '
                 'but larger awards. Target year 2 after DAV win establishes track record.',
        'Action Required': 'Submit LOI in 2027 after DAV win.',
    },
    {
        'Grant Name': 'VFW Foundation — Community Veteran Support',
        'Funder Organization': 'VFW Foundation',
        'Funder Type': 'Veteran Foundation',
        'Funding Type': 'Foundation Grant',
        'Grant URL': 'https://www.vfw.org/community/vfw-foundation',
        'Eligibility': '501(c)(3). Community programs supporting veterans and their families.',
        'Typical Award': '$10,000 – $30,000',
        'Cycle': 'Annual',
        'Priority Level': 'High (80-89)',
        'Qualification Score': 82,
        'Service Lane': 'Community Health & Research',
        'Research Subtype': 'Program Evaluation',
        'Applicant Entity': 'Cause We Care',
        'Notes': 'Hair Cuts for Vets is exactly the type of community program VFW Foundation '
                 'supports. Modest award but fast and high probability. '
                 'Gary Felton Jr. veteran director = credibility.',
        'Action Required': 'Apply Q3 2026. Reference Hair Cuts for Vets + veteran hiring.',
    },
    {
        'Grant Name': "Gary Sinise Foundation — Veteran Employment & Community",
        'Funder Organization': 'Gary Sinise Foundation',
        'Funder Type': 'Veteran Foundation',
        'Funding Type': 'Foundation Grant',
        'Grant URL': 'https://garysinisefoundation.org/',
        'Eligibility': '501(c)(3). Programs supporting veterans, first responders, '
                       'and their families. Employment and community integration focus.',
        'Typical Award': '$25,000 – $100,000',
        'Cycle': 'Annual',
        'Priority Level': 'High (80-89)',
        'Qualification Score': 80,
        'Service Lane': 'Community Health & Research',
        'Research Subtype': 'Program Evaluation',
        'Applicant Entity': 'Cause We Care',
        'Notes': 'Veteran employment initiative at DDI + Cause We Care is the hook. '
                 'Gary Felton Jr. on board adds authenticity.',
        'Action Required': 'Apply 2027 cycle.',
    },
    {
        'Grant Name': 'JPMorgan Chase — Veteran Jobs Mission',
        'Funder Organization': 'JPMorgan Chase Foundation',
        'Funder Type': 'Corporate Foundation',
        'Funding Type': 'Corporate Grant',
        'Grant URL': 'https://www.jpmorganchase.com/impact/people/military-and-veterans',
        'Eligibility': 'Organizations that train, employ, or support veterans in the workforce. '
                       '501(c)(3) preferred but for-profit with veteran hiring programs considered.',
        'Typical Award': '$50,000 – $250,000',
        'Cycle': 'Rolling / annual',
        'Priority Level': 'High (80-89)',
        'Qualification Score': 78,
        'Service Lane': 'Community Health & Research',
        'Research Subtype': 'SB/Diversity Research',
        'Applicant Entity': 'DDI + Cause We Care (Teaming)',
        'Notes': 'Unique: DDI (for-profit with veteran hiring policy) + Cause We Care '
                 '(veteran community programs) can apply together. '
                 'HIRE Vets Medallion + Gary Felton + veteran hiring = strong application.',
        'Action Required': 'Apply after HIRE Vets Medallion is awarded to DDI.',
    },
    {
        'Grant Name': 'HIRE Vets Medallion — DOL Recognition Program',
        'Funder Organization': 'U.S. Department of Labor',
        'Funder Type': 'Federal Recognition Program',
        'Funding Type': 'Federal Grant',
        'Grant URL': 'https://hirevets.dol.gov/',
        'Eligibility': 'Any U.S. employer. Gold/Platinum based on veteran hiring percentage, '
                       'retention, and support programs.',
        'Typical Award': 'Not a grant — federal recognition award (free)',
        'Cycle': 'Annual (applications open January, awards in November)',
        'Priority Level': 'Critical (90-100)',
        'Qualification Score': 95,
        'Service Lane': 'Community Health & Research',
        'Research Subtype': 'SB/Diversity Research',
        'Applicant Entity': 'DDI',
        'Notes': 'THIS IS THE FIRST STEP IN THE VETERAN STRATEGY. Free to apply. '
                 'Federal recognition. Goes on every DDI capability statement and proposal. '
                 'Requirement: document veteran hires at DDI. Gary Felton Jr. as Director '
                 'at Cause We Care helps but DDI needs documented W-2 or 1099 veteran hires. '
                 'Apply January 2027 for the 2027 cycle (need veteran hire data for 2026 first).',
        'Action Required': 'START HIRING VETERANS AT DDI IN 2026. Track data. '
                           'Apply for HIRE Vets Medallion January 2027.',
    },
]


# ---------------------------------------------------------------------------
# FEDERAL GRANT SOURCES (Grants.gov API)
# ---------------------------------------------------------------------------

FEDERAL_RESEARCH_CFDA_NUMBERS = [
    '93.307',   # NIH NIMHD minority health disparities
    '93.910',   # HRSA community health
    '93.243',   # SAMHSA behavioral health
    '10.561',   # USDA FNS SNAP outreach
    '14.218',   # HUD CDBG community development
    '93.647',   # ACF family support
    '93.239',   # HHS ASPE policy research
]

FEDERAL_RESEARCH_KEYWORDS = [
    'community health needs assessment',
    'health disparities research',
    'social determinants of health',
    'SNAP outreach enrollment',
    'benefits access barriers',
    'program evaluation behavioral health',
    'medicaid access community',
    'minority health research',
    'underserved community health',
    'food insecurity research',
]


class GBISCommunityHealthMiner:
    """
    Mines and tracks grant opportunities for the Community Health & Research lane.
    Writes to GBIS OPPORTUNITIES table with full Research Lane tagging.
    """

    def __init__(self):
        self.airtable = AirtableClient()
        self.detector = ResearchLaneDetector()

    # -----------------------------------------------------------------------
    # SEED MICHIGAN FOUNDATION SOURCES
    # -----------------------------------------------------------------------

    def seed_all_sources(self) -> Dict:
        """
        Seeds GBIS OPPORTUNITIES with ALL grant sources:
        Michigan foundations + veteran grant sources.
        Run once to populate the pipeline. Skips existing records.
        """
        print("🌱 Seeding all Community Health & Veteran grant sources into GBIS...")
        mich = self.seed_michigan_foundations()
        vets = self.seed_veteran_sources()
        return {
            'michigan_foundations': mich,
            'veteran_sources': vets,
            'total_imported': mich['imported'] + vets['imported'],
            'total_skipped': mich['skipped'] + vets['skipped'],
        }

    def seed_veteran_sources(self) -> Dict:
        """
        Seeds GBIS OPPORTUNITIES with veteran grant sources.
        Unlocked by Gary C. Felton Jr. (Army Veteran, Board Director) +
        DDI/CWC veteran hiring initiative.
        """
        print("\n🎖️  Seeding veteran grant sources into GBIS...")
        imported = 0
        skipped = 0

        for source in VETERAN_GRANT_SOURCES:
            try:
                if self._is_duplicate_grant(source['Grant Name']):
                    print(f"   ⏭️  Already exists: {source['Grant Name'][:60]}")
                    skipped += 1
                    continue

                notes = '\n'.join(filter(None, [
                    source['Notes'],
                    f"Amount: {source['Typical Award']} | Priority: {source['Priority Level']} | Score: {source['Qualification Score']}",
                    f"Type: {source['Funder Type']} | Funding: {source['Funding Type']}",
                    f"Lane: {source['Service Lane']} | Subtype: {source['Research Subtype']}",
                    f"Applicant: {source['Applicant Entity']}",
                    f"Action: {source.get('Action Required', '')}",
                ]))
                record = {
                    'GRANT NAME':          source['Grant Name'],
                    'FUNDER ORGANIZATION': source['Funder Organization'],
                    'GRANT URL':           source['Grant URL'],
                    'ELIGIBILITY':         source['Eligibility'],
                    'NOTES':               notes,
                }

                self.airtable.create_record('GRANT OPPORTUNITIES', record)
                print(f"   ✅ {source['Grant Name'][:60]}")
                print(f"      Applicant: {source['Applicant Entity']} | {source['Priority Level']}")
                imported += 1

            except Exception as e:
                print(f"   ❌ Error: {source['Grant Name'][:40]}: {e}")

        print(f"\n📊 Veteran grants: {imported} added, {skipped} skipped")
        return {'imported': imported, 'skipped': skipped}

    def seed_michigan_foundations(self) -> Dict:
        """
        Seeds GBIS OPPORTUNITIES with Michigan foundation grant sources.
        Run once to populate the pipeline. Skips existing records.
        """
        print("🏛️  Seeding Michigan foundation grant sources into GBIS...")
        imported = 0
        skipped = 0

        for source in MICHIGAN_FOUNDATION_SOURCES:
            try:
                if self._is_duplicate_grant(source['Grant Name']):
                    print(f"   ⏭️  Already exists: {source['Grant Name'][:60]}")
                    skipped += 1
                    continue

                notes = '\n'.join(filter(None, [
                    source['Notes'],
                    f"Amount: {source['Typical Award']} | Priority: {source['Priority Level']} | Score: {source['Qualification Score']}",
                    f"Type: {source['Funder Type']} | Funding: {source['Funding Type']}",
                    f"Lane: {source['Service Lane']} | Subtype: {source['Research Subtype']}",
                    f"Applicant: {source['Applicant Entity']}",
                    f"Action: {source.get('Action Required', '')}",
                ]))
                record = {
                    'GRANT NAME':          source['Grant Name'],
                    'FUNDER ORGANIZATION': source['Funder Organization'],
                    'GRANT URL':           source['Grant URL'],
                    'ELIGIBILITY':         source['Eligibility'],
                    'NOTES':               notes,
                }

                self.airtable.create_record('GRANT OPPORTUNITIES', record)
                print(f"   ✅ Added: {source['Grant Name'][:60]}")
                print(f"      Applicant: {source['Applicant Entity']} | Priority: {source['Priority Level']}")
                imported += 1

            except Exception as e:
                print(f"   ❌ Error adding {source['Grant Name'][:40]}: {e}")

        print(f"\n📊 Foundation seeds: {imported} added, {skipped} skipped")
        return {'imported': imported, 'skipped': skipped}

    # -----------------------------------------------------------------------
    # GRANTS.GOV API MINING
    # -----------------------------------------------------------------------

    def mine_grants_gov_research(self) -> Dict:
        """
        Searches Grants.gov for community health and research grants.
        Filters by CFDA numbers and keywords. Tags with ResearchLaneDetector.
        """
        print("🔍 Mining Grants.gov for Community Health & Research grants...")

        api_url = 'https://apply07.grants.gov/grantsws/rest/opportunities/search/'
        imported = 0
        found = 0

        for keyword in FEDERAL_RESEARCH_KEYWORDS[:5]:  # Start with top 5
            try:
                payload = {
                    'keyword': keyword,
                    'oppStatuses': 'forecasted|posted',
                    'rows': 25,
                    'sortBy': 'openDate|desc',
                }

                response = requests.post(api_url, json=payload,
                                         headers={'Content-Type': 'application/json'},
                                         timeout=30)
                response.raise_for_status()
                data = response.json()
                opportunities = data.get('oppHits', [])
                found += len(opportunities)

                for opp in opportunities:
                    try:
                        grant_id = opp.get('id', '')
                        if self._is_duplicate_grant_id(grant_id):
                            continue

                        title = opp.get('title', '')
                        agency = opp.get('agency', '')
                        description = opp.get('description', '')

                        # Tag with Research Lane
                        research_tags = self.detector.detect(
                            title=title,
                            description=description,
                            agency=agency,
                        )

                        # Assign applicant entity
                        applicant = self.detector.assign_applicant_entity(
                            funder=agency,
                            description=description,
                        )

                        close_date = opp.get('closeDate', '')

                        notes_parts = [
                            f"GRANT ID: {grant_id}",
                            f"Type: Federal Government | Funding: Federal Grant",
                            f"Priority: High (80-89) | Score: 80",
                            f"Lane: {research_tags.get('Service Lane', 'Community Health & Research')} | Subtype: {research_tags.get('Research Subtype', 'Survey / Market Research')}",
                            f"Applicant: {applicant}",
                            f"Source: Grants.gov API — Research Lane",
                            f"Deadline: {close_date}" if close_date else '',
                            f"Amount: Up to ${opp['awardCeiling']:,}" if opp.get('awardCeiling') else '',
                        ]
                        record = {
                            'GRANT NAME':          title[:255],
                            'FUNDER ORGANIZATION': agency,
                            'GRANT URL':           f"https://www.grants.gov/search-results-detail/{grant_id}",
                            'ELIGIBILITY':         opp.get('eligibility', ''),
                            'NOTES':               '\n'.join(p for p in notes_parts if p),
                        }

                        self.airtable.create_record('GRANT OPPORTUNITIES', record)
                        imported += 1
                        print(f"   ✅ {title[:60]} | {applicant}")

                    except Exception as e:
                        print(f"   ⚠️  Error processing grant: {str(e)[:80]}")

            except Exception as e:
                print(f"   ❌ Keyword '{keyword}' search failed: {e}")

        print(f"\n📊 Grants.gov: {found} found, {imported} imported to GBIS")
        return {'found': found, 'imported': imported, 'source': 'Grants.gov'}

    # -----------------------------------------------------------------------
    # RUN ALL
    # -----------------------------------------------------------------------

    def run_full_pipeline(self) -> Dict:
        """
        Seeds Michigan foundations + veteran grants + mines Grants.gov.
        Call this on first run and then on a weekly schedule.
        """
        print("=" * 60)
        print("GBIS COMMUNITY HEALTH & RESEARCH GRANT MINER")
        print("Cause We Care EIN: 92-3602670")
        print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)

        results = {}

        # 1. Seed Michigan foundations (idempotent — skips existing)
        results['michigan_foundations'] = self.seed_michigan_foundations()

        # 2. Seed veteran grant sources
        results['veteran_sources'] = self.seed_veteran_sources()

        # 3. Mine Grants.gov for live federal health grants
        results['grants_gov'] = self.mine_grants_gov_research()

        total_new = (
            results['michigan_foundations']['imported'] +
            results['veteran_sources']['imported'] +
            results['grants_gov']['imported']
        )

        print(f"\n✅ GBIS pipeline complete — {total_new} new records added")
        print("   Community Health & Research: GBIS OPPORTUNITIES → Service Lane filter")
        print("   Veteran Grants: Filter by Funder Type = 'Veteran Foundation'")
        print("   Cause We Care applicant: Filter Applicant Entity = 'Cause We Care'")
        return results

    # -----------------------------------------------------------------------
    # HELPERS
    # -----------------------------------------------------------------------

    def _is_duplicate_grant(self, grant_name: str) -> bool:
        try:
            records = self.airtable.get_all_records('GRANT OPPORTUNITIES')
            return any(r['fields'].get('GRANT NAME', '').lower() == grant_name.lower()
                       for r in records)
        except:
            return False

    def _is_duplicate_grant_id(self, grant_id: str) -> bool:
        if not grant_id:
            return False
        try:
            records = self.airtable.get_all_records('GRANT OPPORTUNITIES')
            return any(r['fields'].get('GRANT ID') == grant_id for r in records)
        except:
            return False


# ---------------------------------------------------------------------------
# AIRTABLE SCHEMA SETUP GUIDE
# ---------------------------------------------------------------------------

AIRTABLE_SETUP_INSTRUCTIONS = """
AIRTABLE FIELDS TO ADD — GBIS OPPORTUNITIES TABLE
==================================================
Add these fields before running this script for the first time:

Field Name         | Type            | Options
-------------------|-----------------|------------------------------------------
Service Lane       | Single Select   | Community Health & Research, General Business Grant, Other
Research Subtype   | Single Select   | Community Health Assessment, Program Evaluation,
                   |                 | Benefits Access Research, SB/Diversity Research,
                   |                 | Survey / Market Research
Applicant Entity   | Single Select   | DDI, Cause We Care, DDI + Cause We Care (Teaming)
Funding Type       | Single Select   | Federal Grant, Foundation Grant, State Subgrant, Corporate Grant
Grant Amount       | Single Line     | (text, e.g. "$50,000 – $200,000")

GPSS OPPORTUNITIES TABLE — ADD:
Field Name         | Type            | Options
Service Lane       | Single Select   | Community Health & Research, Drug Testing,
                   |                 | Fingerprinting, Grounds, NEMT, Supplies, Other
Research Subtype   | Single Select   | (same options as GBIS above)

AIRTABLE VIEW TO CREATE:
  In GBIS OPPORTUNITIES: New View → "Research Lane Pipeline"
    Filter: Service Lane = "Community Health & Research"
    Sort: Deadline ASC (earliest first)
    Group by: Applicant Entity
    
  In GPSS OPPORTUNITIES: New View → "Research Lane Contracts"
    Filter: Service Lane = "Community Health & Research"
    Sort: Deadline ASC
    Group by: Research Subtype
"""


# ---------------------------------------------------------------------------
# CAUSE WE CARE SAM.GOV REGISTRATION CHECKLIST
# ---------------------------------------------------------------------------

CWC_REGISTRATION_CHECKLIST = """
CAUSE WE CARE — FEDERAL REGISTRATION CHECKLIST
(Required before any federal grants can be received)
=======================================================

EIN:  92-3602670   ← confirmed
UEI:  VEJMFMVV6PQ1 ← EXISTS but EXPIRED — renew at sam.gov (1–3 days, not 7–10)
Board Director: Gary C. Felton Jr. (U.S. Army Veteran)

STEP 1: Renew SAM.gov registration  ⚠️  ACTION REQUIRED
  UEI VEJMFMVV6PQ1 already exists — just needs renewal
  □ Go to sam.gov → Sign In → Entity Registrations → Cause We Care → Renew
  □ Timeline: 1–3 business days (renewal, not new registration)
  □ This unlocks Grants.gov, federal grant eligibility, and federal contract teaming

STEP 2: Confirm EIN is active ✅
  EIN: 92-3602670 (confirmed via GiveButter 501c3 verification)
  □ Confirm 990 filings are current (2022, 2023, 2024)

STEP 2: Get UEI for Cause We Care (separate from DDI's UEI)
  □ Go to sam.gov → Register New Entity
  □ Select: Non-Federal Entity → Not a Federal Contractor
  □ This is a separate registration from Dee Davis Inc.
  □ Timeline: 1–3 business days for UEI
  □ Full SAM activation: 7–10 business days

STEP 3: Register on Grants.gov as an applicant
  □ Go to grants.gov → Register
  □ Use Cause We Care's EIN and new UEI
  □ Required for: NIH, HRSA, SAMHSA, USDA FNS, HUD, ACF

STEP 4: Register on Michigan foundation portals
  □ Community Foundation for SE Michigan: cfsem.org/grants
  □ Michigan Health Endowment Fund: mihealthfund.org/funding
  □ Kresge Foundation: kresge.org (LOI process — no portal)
  □ W.K. Kellogg: wkkf.org

STEP 5: Confirm nonprofit is in good standing with Michigan
  □ Michigan Annual Report current (LARA)
  □ Board minutes current
  □ 501(c)(3) status active (IRS)
  □ No outstanding state filings

TIMELINE: Complete Steps 1–3 within 2 weeks. Steps 4–5 within 1 month.
First grant application target: Community Foundation for SE Michigan, Q2 2026.
"""


if __name__ == '__main__':
    print(AIRTABLE_SETUP_INSTRUCTIONS)
    print(CWC_REGISTRATION_CHECKLIST)

    confirm = input("\nAirtable fields added and Cause We Care is registered? (yes/no): ")
    if confirm.lower() == 'yes':
        miner = GBISCommunityHealthMiner()
        miner.run_full_pipeline()
    else:
        print("\n⚠️  Complete Airtable setup and Cause We Care registration first.")
        print("   See AIRTABLE_SETUP_INSTRUCTIONS and CWC_REGISTRATION_CHECKLIST above.")
