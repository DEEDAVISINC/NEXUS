"""
GBIS Small Business Grant Miner
================================
Mines and seeds small business grants ($500 – $100K) for Dee Davis Inc.
Target profile: Woman-owned, EDWOSB, service-based, Michigan-based.

ALL FREE sources only — no paid subscriptions, no application fees unless noted.
Fees noted explicitly where they exist (e.g., Amber Grant $15).

Sources covered (53 total):
  Daily aggregators    — Hello Alice, Grants.gov, Nav, SBA, SCORE
  Monthly grants       — Amber Grant ($15 fee), IFundWomen, Comcast RISE
  Corporate programs   — Bank of America, Chase, Google, Walmart, FedEx, AT&T, etc.
  Michigan-specific    — MEDC, Michigan SBDC, DEGC, Community Foundations
  Women-focused        — WBENC, NAWBO, Tory Burch, Cartier, InnovateHER, SBA
  Veteran-adjacent     — DAV, VFW, HIRE Vets
  Rolling/always-open  — Many corporate grants are rolling year-round
  Fellowship/Builder   — O'Shaughnessy ($100K), Soma Scholars ($30K), Women Who Tech,
                         AT&T She's Connected ($50K), Proposium, Funding Findr, Merge Grant
                         DDI qualifies as creator of NEXUS + FleetFlow TMS (AI platforms)

Tables written to: GBIS OPPORTUNITIES
Grant Category tag:  'Small Business Grant'
Applicant Entity:    'DDI'

Run daily via:     POST /gbis/mine-small-grants
Seed all via:      POST /gbis/mine-small-grants/seed
Seed free only:    POST /gbis/mine-small-grants/seed-free
Daily digest:      GET  /gbis/mine-small-grants/daily-digest
"""

import re
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

try:
    from nexus_backend import AirtableClient
except ImportError:
    raise ImportError("Run from NEXUS BACKEND root directory.")

from gbis_airtable_helpers import (
    create_grant_opportunity,
    priority_to_recommendation,
    today_iso,
)


# ---------------------------------------------------------------------------
# FREE SMALL GRANT SOURCES — ALL 46
#
# Fee field: True = has application or membership fee (noted in Notes)
#            False = 100% free to apply
# ---------------------------------------------------------------------------

SMALL_GRANT_SOURCES: List[Dict] = [

    # =========================================================================
    # TIER 1: BEST FREE AGGREGATORS — Check these DAILY
    # These are platforms/databases that list many grants in one place.
    # =========================================================================

    {
        'Grant Name':          'Hello Alice Small Business Grants',
        'Funder Organization': 'Hello Alice',
        'Funder Type':         'Grant Aggregator Platform',
        'Funding Type':        'Multiple — Corporate + Foundation',
        'Grant URL':           'https://helloalice.com/grants',
        'Eligibility':         'Woman-owned, BIPOC, or veteran-owned. Revenue $0–$10M. US-based. Free account.',
        'Grant Amount':        '$500 – $50,000 (varies by program)',
        'Cycle':               'Rolling — 5-10 new grants added per month',
        'Priority Level':      'Critical (90-100)',
        'Qualification Score': 98,
        'Application Time':    '5–30 minutes (1-click after profile setup)',
        'Fee':                 False,
        'Notes': (
            'HIGHEST PRIORITY. #1 free aggregator for women/BIPOC-owned businesses. '
            'Complete profile once → auto-matched to all eligible grants. '
            'Active programs rotate constantly: Visa Back to Business ($10K), '
            'Amazon Business Grant ($25K–$50K), Mastercard Empowered ($10K), '
            'Bank of America, JPMorgan Chase, AT&T, and dozens more. '
            'FREE to join. FREE to apply. No fees ever. '
            'CHECK EVERY DAY — new grants appear with no announcement.'
        ),
        'Action Required': 'REGISTER NOW at helloalice.com. Complete full business profile. Apply to ALL visible grants.',
        'Check Frequency':     'Daily',
    },
    {
        'Grant Name':          'Nav Business Grants Database',
        'Funder Organization': 'Nav / Multiple Corporate Sponsors',
        'Funder Type':         'Grant Aggregator',
        'Funding Type':        'Multiple',
        'Grant URL':           'https://www.nav.com/resource/small-business-grants/',
        'Eligibility':         'Varies — woman-owned, minority, veteran, all small biz.',
        'Grant Amount':        '$500 – $100,000 (varies)',
        'Cycle':               'Updated continuously — rolling programs',
        'Priority Level':      'Critical (90-100)',
        'Qualification Score': 94,
        'Application Time':    '5 min to browse, varies per grant',
        'Fee':                 False,
        'Notes': (
            'FREE. Aggregates 40+ small business grants updated continuously. '
            'Strong woman-owned and EDWOSB-eligible grant coverage. '
            'Best for finding grants that just launched unexpectedly. '
            'No account required — just bookmark and check.'
        ),
        'Action Required': 'Bookmark nav.com/resource/small-business-grants/ — check every Monday.',
        'Check Frequency':     'Weekly (Mondays)',
    },
    {
        'Grant Name':          'SCORE Grant Resources',
        'Funder Organization': 'SCORE / SBA',
        'Funder Type':         'Federal / Nonprofit',
        'Funding Type':        'Grant Directory + Mentorship',
        'Grant URL':           'https://www.score.org/resource/business-grants-women',
        'Eligibility':         'Any small business. US-based. Free to access.',
        'Grant Amount':        'Directory of grants (varies)',
        'Cycle':               'Updated monthly',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 86,
        'Application Time':    '5 min to browse',
        'Fee':                 False,
        'Notes': (
            'FREE. SCORE (SBA partner) maintains a running list of open grants for women. '
            'Also provides FREE mentors who know about local/state grants before they post publicly. '
            'Request a free SCORE mentor — they are a goldmine of grant intelligence. '
            'SCORE mentors are former executives who know funders personally.'
        ),
        'Action Required': 'Register for free SCORE mentor at score.org. Check grant list monthly.',
        'Check Frequency':     'Monthly',
    },
    {
        'Grant Name':          'SBA Small Business Grants',
        'Funder Organization': 'U.S. Small Business Administration',
        'Funder Type':         'Federal Government',
        'Funding Type':        'Federal Grant',
        'Grant URL':           'https://www.sba.gov/funding-programs/grants',
        'Eligibility':         'Small business per SBA size standards. Various requirements by program.',
        'Grant Amount':        '$2,500 – $500,000 (varies)',
        'Cycle':               'Multiple rolling programs + periodic NOFOs',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 87,
        'Application Time':    '30 min – 4 hours',
        'Fee':                 False,
        'Notes': (
            'FREE. SBA manages SBIR/STTR (federal R&D grants $50K–$1M), '
            'partners with WBCs for InnovateHER, and announces state programs. '
            'Subscribe to SBA email newsletter for instant notifications. '
            'Also check SBA.gov/events for free grant webinars.'
        ),
        'Action Required': 'Subscribe to SBA email at sba.gov. Monitor weekly.',
        'Check Frequency':     'Weekly',
    },
    {
        'Grant Name':          'Grants.gov Federal Database',
        'Funder Organization': 'U.S. Federal Government',
        'Funder Type':         'Federal Government',
        'Funding Type':        'Federal Grant',
        'Grant URL':           'https://www.grants.gov',
        'Eligibility':         'Varies widely. Filter: small business, women-owned, nonprofits.',
        'Grant Amount':        '$1,000 – $10,000,000 (all sizes)',
        'Cycle':               'Continuously updated — all 26 federal agencies',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 88,
        'Application Time':    '1–40 hours (varies enormously)',
        'Fee':                 False,
        'Notes': (
            'FREE. Official federal grants clearinghouse. '
            'Set up a saved search: keyword "women-owned" OR "WOSB" + your NAICS codes. '
            'Enable email alerts — new grants notify you immediately. '
            'NEXUS also mines this via API automatically.'
        ),
        'Action Required': 'Create account at grants.gov. Set saved search with email alert.',
        'Check Frequency':     'Automated via NEXUS GBIS miner',
    },
    {
        'Grant Name':          'Business.gov Small Business Grants',
        'Funder Organization': 'U.S. Government',
        'Funder Type':         'Federal Government',
        'Funding Type':        'Federal / State Grants Directory',
        'Grant URL':           'https://www.usa.gov/government-grants-small-business',
        'Eligibility':         'US-based small business.',
        'Grant Amount':        'Varies',
        'Cycle':               'Directory — updated quarterly',
        'Priority Level':      'Medium (70-79)',
        'Qualification Score': 72,
        'Application Time':    '5 min to browse',
        'Fee':                 False,
        'Notes': (
            'FREE. Official government guide to small business grants. '
            'Organized by category: women, minority, veteran, rural, technology.'
        ),
        'Action Required': 'Bookmark and check quarterly.',
        'Check Frequency':     'Quarterly',
    },

    # =========================================================================
    # TIER 2: WOMEN-OWNED SPECIFIC — Apply Monthly or As Open
    # =========================================================================

    {
        'Grant Name':          'Amber Grant for Women — Monthly',
        'Funder Organization': 'WomensNet / Amber Grant Foundation',
        'Funder Type':         'Women-Focused Foundation',
        'Funding Type':        'Foundation Grant',
        'Grant URL':           'https://ambergrantsforwomen.com',
        'Eligibility':         'Woman-owned business. Any stage. Any industry. US or international.',
        'Grant Amount':        '$10,000 monthly + $25,000 annual winner',
        'Cycle':               'Monthly (12 winners/year + 1 annual $25K winner)',
        'Priority Level':      'Critical (90-100)',
        'Qualification Score': 95,
        'Application Time':    '20–30 minutes',
        'Fee':                 True,
        'Notes': (
            'APPLICATION FEE: $15 per application. '
            'Apply EVERY MONTH — previous applicants can reapply. '
            'Annual $25K winner selected from monthly winners — momentum compounds. '
            'Simple one-page application. Set calendar reminder for 1st of each month. '
            'One of the most accessible women\'s grants available — $15 is the only barrier.'
        ),
        'Action Required': 'Apply now at ambergrantsforwomen.com ($15). Set monthly calendar reminder.',
        'Check Frequency':     'Monthly (1st of month)',
    },
    {
        'Grant Name':          'IFundWomen Universal Grant — Quarterly',
        'Funder Organization': 'IFundWomen',
        'Funder Type':         'Women-Focused Platform',
        'Funding Type':        'Corporate Grant',
        'Grant URL':           'https://ifundwomen.com/universal-grant',
        'Eligibility':         'Woman-owned or women-led. US-based. All stages. All industries.',
        'Grant Amount':        '$10,000',
        'Cycle':               'Quarterly',
        'Priority Level':      'Critical (90-100)',
        'Qualification Score': 91,
        'Application Time':    '45 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. No crowdfunding required (simpler than other IFW programs). '
            'Free coaching for applicants. Apply every quarter. '
            'Also check IFundWomen corporate partner grants: '
            'Google for Startups, Visa, JPMorgan Chase, AT&T — all rotating, all free.'
        ),
        'Action Required': 'Apply at ifundwomen.com/universal-grant. Set quarterly calendar reminder.',
        'Check Frequency':     'Quarterly',
    },
    {
        'Grant Name':          'Comcast RISE — Rolling',
        'Funder Organization': 'Comcast / NBCUniversal',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant (In-Kind Services)',
        'Grant URL':           'https://www.comcastrise.com',
        'Eligibility':         'Women or BIPOC-owned (51%+). 50 or fewer employees. 3+ years. US-based.',
        'Grant Amount':        'Marketing + tech services ($25K–$100K value)',
        'Cycle':               'Rolling — apply anytime',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 86,
        'Application Time':    '30 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. In-kind: marketing campaigns, website design, tech upgrades, media buys. '
            'Not cash — but real business value. EDWOSB + women-owned = strong fit. '
            'No deadline pressure. Apply when DDI needs marketing or tech services.'
        ),
        'Action Required': 'Apply at comcastrise.com any time.',
        'Check Frequency':     'Rolling — apply when ready',
    },
    {
        'Grant Name':          'InnovateHER Challenge — SBA Annual',
        'Funder Organization': 'U.S. Small Business Administration',
        'Funder Type':         'Federal Government',
        'Funding Type':        'Federal Competition Grant',
        'Grant URL':           'https://www.sba.gov/local-assistance/resource-partners/womens-business-centers/innovateher-challenge',
        'Eligibility':         'Woman-owned (51%+). Innovative product or service. US-based.',
        'Grant Amount':        '$30,000 – $70,000 (3 national winners)',
        'Cycle':               'Annual — opens Fall/Winter',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 89,
        'Application Time':    '2–3 hours',
        'Fee':                 False,
        'Notes': (
            'FREE. SBA-backed competition — winner recognition goes on DDI cap statement. '
            'Strengthens federal proposals and relationships with SBA offices. '
            'Start at local WBC (Women\'s Business Center) — they run local rounds that feed to nationals.'
        ),
        'Action Required': 'Monitor SBA.gov for InnovateHER opening (Fall). Apply annually.',
        'Check Frequency':     'Annual (Fall)',
    },
    {
        'Grant Name':          'Cartier Women\'s Initiative — Annual',
        'Funder Organization': 'Cartier',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant',
        'Grant URL':           'https://www.cartierwomensinitiative.com',
        'Eligibility':         'Woman founder/co-founder. 3+ years in operation. Impact mission. Revenue generating.',
        'Grant Amount':        '$30,000 – $100,000',
        'Cycle':               'Annual — opens Q1',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 82,
        'Application Time':    '2–3 hours',
        'Fee':                 False,
        'Notes': (
            'FREE. Prestigious $100K no-equity grant. Global recognition + PR value. '
            'Worth the 2–3 hour effort. Apply annually when opens Q1. '
            'Frame Cause We Care + DDI community health work as the impact narrative.'
        ),
        'Action Required': 'Apply in Q1 at cartierwomensinitiative.com.',
        'Check Frequency':     'Annual (Q1)',
    },
    {
        'Grant Name':          'Eileen Fisher Women-Owned Business Grant',
        'Funder Organization': 'Eileen Fisher Foundation',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant',
        'Grant URL':           'https://www.eileenfisher.com/grants',
        'Eligibility':         'Woman-owned (51%+). 3+ years in operation. Revenue $75K–$1M. Social/environmental impact.',
        'Grant Amount':        '$40,000 – $100,000 (10 winners/year)',
        'Cycle':               'Annual — opens Q1/Q2',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 81,
        'Application Time':    '2–3 hours',
        'Fee':                 False,
        'Notes': (
            'FREE. 10 winners/year = better odds than single-winner grants. '
            'Multi-year potential — previous winners can reapply. '
            'Frame DDI community health + Cause We Care as the impact angle.'
        ),
        'Action Required': 'Apply in Q1/Q2 at eileenfisher.com/grants.',
        'Check Frequency':     'Annual (Q1/Q2)',
    },
    {
        'Grant Name':          'Tory Burch Foundation Fellowship',
        'Funder Organization': 'Tory Burch Foundation',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant + Fellowship',
        'Grant URL':           'https://www.toryburchfoundation.org/fellowship',
        'Eligibility':         'Woman entrepreneur. US-based. Revenue-generating. 2+ years.',
        'Grant Amount':        '$5,000 cash + education ($10K value)',
        'Cycle':               'Annual cohorts',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 77,
        'Application Time':    '1–2 hours',
        'Fee':                 False,
        'Notes': (
            'FREE. Cash + mentorship + network access. Long-term alumni community. '
            'Apply annually. Great for growth-stage visibility.'
        ),
        'Action Required': 'Monitor toryburchfoundation.org for fellowship opening.',
        'Check Frequency':     'Annual',
    },
    {
        'Grant Name':          'WBENC Member Grants & Corporate Partners',
        'Funder Organization': 'WBENC / Corporate Partners',
        'Funder Type':         'Trade Association',
        'Funding Type':        'Corporate Grant',
        'Grant URL':           'https://www.wbenc.org/resources/grants/',
        'Eligibility':         'WBENC-certified members. Woman-owned (51%+). DDI is already certified.',
        'Grant Amount':        '$2,500 – $50,000 (varies by program)',
        'Cycle':               'Rolling + periodic announcements',
        'Priority Level':      'Critical (90-100)',
        'Qualification Score': 96,
        'Application Time':    '30–60 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE — DDI is already WBENC certified. This is an unlocked resource. '
            'Corporate partners (AT&T, Walmart, JPMorgan, Dell, etc.) run exclusive '
            'grant programs ONLY for WBENC members. Not public-facing. '
            'Log in to WBENC member portal and check the grants section monthly. '
            'Also check WBENC regional events — local grants announced at meetings.'
        ),
        'Action Required': 'Log into WBENC member portal monthly. Check grants/programs section.',
        'Check Frequency':     'Monthly',
    },
    {
        'Grant Name':          'NAWBO National + Local Chapter Grants',
        'Funder Organization': 'National Association of Women Business Owners',
        'Funder Type':         'Trade Association',
        'Funding Type':        'Association Grant',
        'Grant URL':           'https://nawbo.org',
        'Eligibility':         'Woman-owned business. NAWBO member preferred (not required for some).',
        'Grant Amount':        '$1,000 – $25,000 (chapter-level varies)',
        'Cycle':               'Rolling + chapter-based',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 83,
        'Application Time':    '30–60 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE to check. NAWBO local chapters (Michigan chapter = Detroit area) '
            'often run grant programs funded by corporate sponsors. '
            'Not always publicly announced — attend local NAWBO meetings to hear about them first. '
            'Also check NAWBO national corporate partner programs on nawbo.org.'
        ),
        'Action Required': 'Contact Michigan NAWBO chapter. Attend local meeting for grant intel.',
        'Check Frequency':     'Monthly (attend chapter meetings)',
    },

    # =========================================================================
    # TIER 3: CORPORATE GRANTS — All Free to Apply
    # =========================================================================

    {
        'Grant Name':          'FedEx Small Business Grant Contest',
        'Funder Organization': 'FedEx',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant',
        'Grant URL':           'https://smallbusinessgrant.fedex.com',
        'Eligibility':         'Small business (fewer than 99 employees). US-based. Operating 6+ months.',
        'Grant Amount':        '$5,000 – $50,000 (10 total winners)',
        'Cycle':               'Annual — opens Spring',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 84,
        'Application Time':    '45–60 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. 10 winners per year = better odds. Public voting phase (mobilize network). '
            'Women-owned gets bonus points. Free shipping credit for all applicants. '
            'Opens Spring — set reminder for March.'
        ),
        'Action Required': 'Monitor smallbusinessgrant.fedex.com. Apply when opens (Spring).',
        'Check Frequency':     'Annual (Spring)',
    },
    {
        'Grant Name':          'Bank of America Small Business Grant',
        'Funder Organization': 'Bank of America',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant',
        'Grant URL':           'https://about.bankofamerica.com/en/making-an-impact/small-business-grants',
        'Eligibility':         'Small business. Community impact focus. Woman/minority-owned preferred.',
        'Grant Amount':        '$5,000 – $25,000',
        'Cycle':               'Multiple programs annually — Rolling',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 88,
        'Application Time':    '30–60 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. Bank of America runs multiple grant programs throughout the year: '
            'Small Business Spotlight ($25K), Neighborhood Builders, '
            'Minority Business Development, Women\'s Economic Empowerment. '
            'Also available through Hello Alice — apply via both channels. '
            'Michigan-based businesses have regional advantage.'
        ),
        'Action Required': 'Check about.bankofamerica.com/grants and Hello Alice. Apply as programs open.',
        'Check Frequency':     'Monthly',
    },
    {
        'Grant Name':          'JPMorgan Chase Small Business Forward Grant',
        'Funder Organization': 'JPMorgan Chase',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant',
        'Grant URL':           'https://www.jpmorganchase.com/impact/small-business',
        'Eligibility':         'Small business. Minority/woman-owned preferred. Community impact.',
        'Grant Amount':        '$10,000 – $150,000',
        'Cycle':               'Rolling programs throughout year',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 85,
        'Application Time':    '30–60 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. JPMorgan Chase runs several programs: '
            'Advancing Black Pathways, Small Business Forward, Workforce Initiative. '
            'Also administers grants through Hello Alice and IFundWomen — '
            'completing Hello Alice profile gives you automatic access. '
            'Troy/Detroit Michigan presence is a regional advantage.'
        ),
        'Action Required': 'Apply via Hello Alice profile + check jpmorganchase.com/impact.',
        'Check Frequency':     'Monthly',
    },
    {
        'Grant Name':          'Google for Startups — Various Programs',
        'Funder Organization': 'Google',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant + Services',
        'Grant URL':           'https://startup.google.com/programs/',
        'Eligibility':         'Small business / startup. Woman-owned, Black-owned, Latino-owned preferred.',
        'Grant Amount':        '$10,000 – $100,000 cash + Google Cloud credits',
        'Cycle':               'Multiple rolling programs',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 82,
        'Application Time':    '30–60 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. Google runs dedicated programs: '
            'Google for Startups Black Founders Fund, '
            'Google for Startups Women Founders Fund, '
            'Google for Startups Latino Founders Fund. '
            'Awards include cash ($50K–$100K) + Google Cloud credits + mentorship. '
            'Also available through IFundWomen.'
        ),
        'Action Required': 'Check startup.google.com/programs monthly for open cohorts.',
        'Check Frequency':     'Monthly',
    },
    {
        'Grant Name':          'AT&T Small Business Grant',
        'Funder Organization': 'AT&T',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant',
        'Grant URL':           'https://helloalice.com/grants',
        'Eligibility':         'Small business. Woman/minority-owned preferred.',
        'Grant Amount':        '$5,000 – $25,000',
        'Cycle':               'Rolling through Hello Alice',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 84,
        'Application Time':    '15–30 minutes via Hello Alice',
        'Fee':                 False,
        'Notes': (
            'FREE. AT&T funds multiple small business grant programs through Hello Alice. '
            'Creating a Hello Alice profile auto-matches you to AT&T grants. '
            'AT&T also runs: AT&T Dream in Black, Connect to Thrive, '
            'and various community grant programs announced throughout the year.'
        ),
        'Action Required': 'Complete Hello Alice profile — AT&T grants appear automatically.',
        'Check Frequency':     'Via Hello Alice (daily)',
    },
    {
        'Grant Name':          'Walmart Foundation Community Grant',
        'Funder Organization': 'Walmart Foundation',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant',
        'Grant URL':           'https://walmart.org/how-we-give/local-community-grants',
        'Eligibility':         '501(c)(3) nonprofits OR for-profits with community programs. US-based.',
        'Grant Amount':        '$250 – $5,000 (local store grants)',
        'Cycle':               'Rolling — apply through local Walmart store manager',
        'Priority Level':      'Medium (70-79)',
        'Qualification Score': 74,
        'Application Time':    '30 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. Two tiers: '
            '1. Local grants ($250–$5K) — apply through local Walmart store manager. '
            '2. Spark Good (national) — apply through walmartspark.org for larger grants. '
            'Community health angle (Cause We Care) is the strongest fit. '
            'Simple application, fast turnaround.'
        ),
        'Action Required': 'Apply via walmartspark.org and local Walmart store community grants.',
        'Check Frequency':     'Rolling',
    },
    {
        'Grant Name':          'Target Circle Community Grant',
        'Funder Organization': 'Target Corporation',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant',
        'Grant URL':           'https://corporate.target.com/sustainability-governance/our-communities',
        'Eligibility':         '501(c)(3) or small business with community impact. Local focus.',
        'Grant Amount':        '$1,000 – $10,000',
        'Cycle':               'Periodic — quarterly to annual',
        'Priority Level':      'Medium (70-79)',
        'Qualification Score': 73,
        'Application Time':    '30 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. Target runs community grants through Target Circle rewards program. '
            'Cause We Care (nonprofit) is the strongest applicant. '
            'Michigan/SE Michigan focus gives local advantage.'
        ),
        'Action Required': 'Monitor target.com/circle/community for open grant cycles.',
        'Check Frequency':     'Quarterly',
    },
    {
        'Grant Name':          'Visa Everywhere Initiative',
        'Funder Organization': 'Visa',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant',
        'Grant URL':           'https://usa.visa.com/everywhere-initiative',
        'Eligibility':         'Early to growth-stage. US-based. Innovative business model.',
        'Grant Amount':        '$50,000 – $100,000',
        'Cycle':               'Annual + regional competitions',
        'Priority Level':      'Medium (70-79)',
        'Qualification Score': 75,
        'Application Time':    '2–3 hours (pitch deck)',
        'Fee':                 False,
        'Notes': (
            'FREE. Apply if DDI has a tech/innovation angle. '
            'Visa also funds grants through Hello Alice (Back to Business, $10K) — '
            'those are rolling and much easier. Apply to both.'
        ),
        'Action Required': 'Apply via Hello Alice for rolling Visa grants. Annual competition separately.',
        'Check Frequency':     'Annual + rolling via Hello Alice',
    },
    {
        'Grant Name':          'Tito\'s Vodka Love, Tito\'s Grant',
        'Funder Organization': 'Tito\'s Handmade Vodka',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant',
        'Grant URL':           'https://www.titosvodka.com/love-titos-grants',
        'Eligibility':         '501(c)(3) or for-profit with community/social impact. US-based.',
        'Grant Amount':        '$5,000 – $50,000',
        'Cycle':               'Quarterly',
        'Priority Level':      'Medium (70-79)',
        'Qualification Score': 74,
        'Application Time':    '30–45 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. Quarterly cycle. Community impact angle = strong fit. '
            'Cause We Care (nonprofit) is the best applicant entity. '
            'DDI community health work also qualifies as for-profit with social mission.'
        ),
        'Action Required': 'Apply quarterly at titosvodka.com/love-titos-grants.',
        'Check Frequency':     'Quarterly',
    },
    {
        'Grant Name':          'Spanx Foundation Leg Up Grant',
        'Funder Organization': 'Spanx by Sara Blakely Foundation',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant',
        'Grant URL':           'https://spanx.com/pages/leg-up',
        'Eligibility':         'Woman entrepreneur. Early to growth stage. All industries. US-based.',
        'Grant Amount':        '$5,000',
        'Cycle':               'Rolling / as announced',
        'Priority Level':      'Medium (70-79)',
        'Qualification Score': 76,
        'Application Time':    '30 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. Woman entrepreneur focus. Simple application. '
            'Monitor website + set email alert for when grant opens.'
        ),
        'Action Required': 'Monitor spanx.com/pages/leg-up. Apply when open.',
        'Check Frequency':     'Monthly check',
    },
    {
        'Grant Name':          'Lowe\'s Spring Scholarship + Business Grant',
        'Funder Organization': 'Lowe\'s Companies',
        'Funder Type':         'Corporate Foundation',
        'Funding Type':        'Corporate Grant',
        'Grant URL':           'https://newsroom.lowes.com/our-communities/',
        'Eligibility':         'Small business. Home improvement/community focus preferred.',
        'Grant Amount':        '$5,000 – $25,000',
        'Cycle':               'Annual — Spring',
        'Priority Level':      'Medium (70-79)',
        'Qualification Score': 71,
        'Application Time':    '30–45 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. Lowe\'s runs periodic small business and community grants. '
            'Facilities/grounds/community focus = good fit for DDI services. '
            'Monitor Lowe\'s newsroom for announcements.'
        ),
        'Action Required': 'Monitor newsroom.lowes.com/our-communities/ for grant openings.',
        'Check Frequency':     'Annual (Spring)',
    },

    # =========================================================================
    # TIER 4: MICHIGAN-SPECIFIC — Highest geographic advantage
    # =========================================================================

    {
        'Grant Name':          'Michigan SBDC Small Business Grants',
        'Funder Organization': 'Michigan Small Business Development Center',
        'Funder Type':         'State Government / SBA Partner',
        'Funding Type':        'State Grant',
        'Grant URL':           'https://www.michigansbdc.org/programs',
        'Eligibility':         'Michigan-based small business. Free to access. Woman-owned advantage.',
        'Grant Amount':        '$1,000 – $25,000 (varies by program)',
        'Cycle':               'Rolling + periodic program announcements',
        'Priority Level':      'Critical (90-100)',
        'Qualification Score': 92,
        'Application Time':    '30–60 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. Michigan SBDC advisors know about grants BEFORE they post publicly. '
            'Free advisor appointment = insider grant intelligence. '
            'They also help write grant applications at no cost. '
            'Troy location (Oakland County) = East Michigan SBDC region. '
            'FASTEST path to Michigan state-level grants.'
        ),
        'Action Required': 'Call Michigan SBDC to schedule FREE advisor appointment. Ask about current grants.',
        'Check Frequency':     'Monthly (meet with advisor)',
    },
    {
        'Grant Name':          'Michigan Economic Development Corporation (MEDC) Programs',
        'Funder Organization': 'Michigan Economic Development Corporation',
        'Funder Type':         'State Government',
        'Funding Type':        'State Grant + Incentive',
        'Grant URL':           'https://www.michiganbusiness.org/services/small-business/',
        'Eligibility':         'Michigan-based business. Various programs. Women/minority advantage.',
        'Grant Amount':        '$5,000 – $500,000 (varies by program)',
        'Cycle':               'Multiple rolling programs',
        'Priority Level':      'Critical (90-100)',
        'Qualification Score': 93,
        'Application Time':    '1–4 hours',
        'Fee':                 False,
        'Notes': (
            'FREE. MEDC programs include: '
            'Pure Michigan Business Connect (procurement matchmaking), '
            'Michigan Business Growth Fund, '
            'Entrepreneurs in Residence, '
            'Michigan Microenterprise Grant. '
            'EDWOSB + Michigan-based = maximum advantage for these programs. '
            'Register at michiganbusiness.org and set email alerts for new programs.'
        ),
        'Action Required': 'Register at michiganbusiness.org. Subscribe to MEDC newsletter.',
        'Check Frequency':     'Monthly',
    },
    {
        'Grant Name':          'Detroit Economic Growth Corporation (DEGC) Grants',
        'Funder Organization': 'Detroit Economic Growth Corporation',
        'Funder Type':         'Local Government / Economic Development',
        'Funding Type':        'Local Grant',
        'Grant URL':           'https://www.degc.org',
        'Eligibility':         'Detroit-area businesses. Woman/minority-owned priority. Small business.',
        'Grant Amount':        '$2,500 – $50,000',
        'Cycle':               'Rolling programs',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 88,
        'Application Time':    '30–60 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. DEGC manages multiple Detroit/SE Michigan economic development grant programs. '
            'EDWOSB + woman-owned + Southeast Michigan location = maximum fit. '
            'Programs include: Small Business Support, Façade Improvement, '
            'Detroit Means Business, neighborhood business grants. '
            'Troy/Oakland County = Metro Detroit service area qualifies.'
        ),
        'Action Required': 'Register at degc.org. Subscribe to newsletter.',
        'Check Frequency':     'Monthly',
    },
    {
        'Grant Name':          'Community Foundation for Southeast Michigan (CFSEM)',
        'Funder Organization': 'Community Foundation for Southeast Michigan',
        'Funder Type':         'Regional Foundation',
        'Funding Type':        'Foundation Grant',
        'Grant URL':           'https://cfsem.org/grants/',
        'Eligibility':         '501(c)(3) serving Wayne, Oakland, Macomb, Washtenaw, Monroe, St. Clair, or Livingston.',
        'Grant Amount':        '$25,000 – $200,000',
        'Cycle':               'Quarterly',
        'Priority Level':      'Critical (90-100)',
        'Qualification Score': 95,
        'Application Time':    '1–2 hours',
        'Fee':                 False,
        'Notes': (
            'FREE. FASTEST path to first foundation grant win. '
            'Quarterly cycle, smaller competition pool than national foundations. '
            'Cause We Care (501c3) is the applicant — SE Michigan presence = direct fit. '
            'Apply Q2 2026. Register on CFSEM portal NOW. '
            'Also check CFSEM rapid-response and emergency grants.'
        ),
        'Action Required': 'PRIORITY — Register Cause We Care on CFSEM portal. Apply Q2 2026.',
        'Check Frequency':     'Quarterly',
    },
    {
        'Grant Name':          'Michigan Health Endowment Fund (MHEF)',
        'Funder Organization': 'Michigan Health Endowment Fund',
        'Funder Type':         'Michigan Foundation',
        'Funding Type':        'Foundation Grant',
        'Grant URL':           'https://mihealthfund.org/funding',
        'Eligibility':         '501(c)(3) organizations serving Michigan residents. Community health focus.',
        'Grant Amount':        '$50,000 – $500,000',
        'Cycle':               'Q2 and Q4 annually',
        'Priority Level':      'Critical (90-100)',
        'Qualification Score': 92,
        'Application Time':    '2–4 hours',
        'Fee':                 False,
        'Notes': (
            'FREE. DDI MDHHS MIBridges Community Partner status = direct credibility. '
            'Cause We Care community health programming is a direct fit. '
            'Apply Q2 2026 cycle. Register on MHEF portal first.'
        ),
        'Action Required': 'Register Cause We Care on MHEF portal. Confirm Q2 deadline.',
        'Check Frequency':     'Twice yearly (Q2, Q4)',
    },
    {
        'Grant Name':          'Oakland County Small Business Grant Programs',
        'Funder Organization': 'Oakland County, Michigan',
        'Funder Type':         'County Government',
        'Funding Type':        'Local Grant',
        'Grant URL':           'https://www.oakgov.com/business',
        'Eligibility':         'Oakland County-based business. Small business. Woman/minority-owned advantage.',
        'Grant Amount':        '$1,000 – $25,000',
        'Cycle':               'Various — rolling and periodic',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 87,
        'Application Time':    '30–60 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. DDI is based in Troy (Oakland County) — maximum geographic advantage. '
            'Oakland County runs periodic small business support programs, '
            'women\'s entrepreneurship grants, and ARPA-funded business recovery grants. '
            'Also check Oakland County One Stop Shop for consolidated programs.'
        ),
        'Action Required': 'Monitor oakgov.com/business for grant announcements.',
        'Check Frequency':     'Monthly',
    },

    # =========================================================================
    # TIER 5: FEDERAL AGENCY PROGRAMS — All Free
    # =========================================================================

    {
        'Grant Name':          'USDA Rural Business Development Grant',
        'Funder Organization': 'U.S. Department of Agriculture',
        'Funder Type':         'Federal Government',
        'Funding Type':        'Federal Grant',
        'Grant URL':           'https://www.rd.usda.gov/programs-services/business-programs/rural-business-development-grants',
        'Eligibility':         'Rural businesses and nonprofits. Community-focused programs.',
        'Grant Amount':        '$10,000 – $500,000',
        'Cycle':               'Annual NOFO on Grants.gov',
        'Priority Level':      'Medium (70-79)',
        'Qualification Score': 71,
        'Application Time':    '2–6 hours',
        'Fee':                 False,
        'Notes': (
            'FREE. Applies if DDI serves any rural Michigan communities. '
            'Cause We Care could qualify for rural community development programming. '
            'Monitor Grants.gov for USDA Rural Development NOFOs.'
        ),
        'Action Required': 'Monitor Grants.gov for USDA Rural Development grants.',
        'Check Frequency':     'Annual via Grants.gov alerts',
    },
    {
        'Grant Name':          'Minority Business Development Agency (MBDA) Grants',
        'Funder Organization': 'U.S. Minority Business Development Agency',
        'Funder Type':         'Federal Government',
        'Funding Type':        'Federal Grant',
        'Grant URL':           'https://www.mbda.gov/programs',
        'Eligibility':         'Minority-owned businesses. Woman-owned with minority status. US-based.',
        'Grant Amount':        '$25,000 – $250,000',
        'Cycle':               'Annual program cycles',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 85,
        'Application Time':    '1–3 hours',
        'Fee':                 False,
        'Notes': (
            'FREE. MBDA Business Centers provide free services + grant access. '
            'Detroit MBDA Business Center = local resource for SE Michigan businesses. '
            'MBE certification = direct eligibility for MBDA programs. '
            'Also check MBDA Capital Readiness Program.'
        ),
        'Action Required': 'Contact Detroit MBDA Business Center. Register at mbda.gov.',
        'Check Frequency':     'Monthly',
    },
    {
        'Grant Name':          'EDA Economic Development Grants',
        'Funder Organization': 'U.S. Economic Development Administration',
        'Funder Type':         'Federal Government',
        'Funding Type':        'Federal Grant',
        'Grant URL':           'https://www.eda.gov/funding/programs',
        'Eligibility':         'Economic development projects. Small business + community focus.',
        'Grant Amount':        '$100,000 – $3,000,000',
        'Cycle':               'Continuous on Grants.gov',
        'Priority Level':      'Medium (70-79)',
        'Qualification Score': 73,
        'Application Time':    '4–20 hours',
        'Fee':                 False,
        'Notes': (
            'FREE. Large grants for economic development projects. '
            'More suited for Cause We Care + DDI partnership applications. '
            'Troy/Detroit economic development angle is the hook. '
            'Best pursued with MEDC or MBDA as co-applicants.'
        ),
        'Action Required': 'Monitor eda.gov/funding for relevant NOFOs.',
        'Check Frequency':     'Monthly',
    },
    {
        'Grant Name':          'HUD CDBG Small Business Assistance',
        'Funder Organization': 'U.S. Department of Housing and Urban Development',
        'Funder Type':         'Federal Government',
        'Funding Type':        'Federal Subgrant',
        'Grant URL':           'https://www.hud.gov/program_offices/comm_planning/cdbg',
        'Eligibility':         'Businesses in HUD Community Development Block Grant areas. Low/moderate income communities.',
        'Grant Amount':        '$5,000 – $50,000 (via local grantees)',
        'Cycle':               'Annual through local municipalities',
        'Priority Level':      'Medium (70-79)',
        'Qualification Score': 74,
        'Application Time':    '1–2 hours',
        'Fee':                 False,
        'Notes': (
            'FREE. CDBG funds flow through local governments to small businesses. '
            'Apply through Detroit, Troy, or Oakland County CDBG programs. '
            'Check with Oakland County Community Development office. '
            'Community health + SE Michigan service area = strong fit.'
        ),
        'Action Required': 'Contact Oakland County or Detroit CDBG office for small business assistance.',
        'Check Frequency':     'Annual (local municipality cycle)',
    },

    # =========================================================================
    # TIER 6: SOCIAL / EMAIL / COMMUNITY MONITORING — Free discovery tools
    # =========================================================================

    {
        'Grant Name':          'LinkedIn Grant Announcements — Daily Monitor',
        'Funder Organization': 'Multiple Corporate Sponsors',
        'Funder Type':         'Social Media Discovery',
        'Funding Type':        'Multiple',
        'Grant URL':           'https://www.linkedin.com/search/results/content/?keywords=small+business+grant+women+owned',
        'Eligibility':         'Varies',
        'Grant Amount':        'Varies',
        'Cycle':               'New grants announced daily',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 85,
        'Application Time':    '5 min to scan',
        'Fee':                 False,
        'Notes': (
            'FREE. Many corporate grant programs are announced FIRST on LinkedIn '
            'before they appear on other platforms. '
            'Search daily: "small business grant women" "WOSB grant" "EDWOSB grant" '
            '"women owned business grant 2026". '
            'Follow: Hello Alice, IFundWomen, WBENC, SBA, SCORE, NAWBO, '
            'Bank of America Small Business, JPMorgan Chase Business. '
            'Turn on post notifications for these accounts.'
        ),
        'Action Required': 'Follow key accounts on LinkedIn. Search grant keywords daily.',
        'Check Frequency':     'Daily',
    },
    {
        'Grant Name':          'Facebook Groups — Small Business Grants for Women',
        'Funder Organization': 'Community / Peer Network',
        'Funder Type':         'Community Monitor',
        'Funding Type':        'Multiple',
        'Grant URL':           'https://www.facebook.com/groups/smallbusinessgrantsforwomen',
        'Eligibility':         'Members share grants as they find them',
        'Grant Amount':        'Varies',
        'Cycle':               'Multiple posts daily from community members',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 83,
        'Application Time':    '5 min to scan',
        'Fee':                 False,
        'Notes': (
            'FREE. Facebook groups where members share grant opportunities as they find them. '
            'Key groups to join: '
            '"Small Business Grants for Women", '
            '"Grants for Black Women Business Owners", '
            '"Woman Business Owner Grant Opportunities", '
            '"Small Business Support Network". '
            'Community members post grants that haven\'t hit mainstream platforms yet. '
            'Check once daily — takes 2 minutes.'
        ),
        'Action Required': 'Join the Facebook groups listed. Check daily feed.',
        'Check Frequency':     'Daily',
    },
    {
        'Grant Name':          'SBA Email Newsletter + Alerts',
        'Funder Organization': 'U.S. Small Business Administration',
        'Funder Type':         'Federal Government Email',
        'Funding Type':        'Alert Service',
        'Grant URL':           'https://www.sba.gov/about-sba/sba-newsroom/press-releases-media-advisories',
        'Eligibility':         'Anyone can subscribe',
        'Grant Amount':        'N/A — alert service',
        'Cycle':               'Email alerts as opportunities arise',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 84,
        'Application Time':    '2 min to subscribe',
        'Fee':                 False,
        'Notes': (
            'FREE. Subscribe to SBA email list for immediate notification of: '
            'new grant programs, InnovateHER openings, SBIR solicitations, '
            'disaster relief grants, and special WOSB/EDWOSB programs. '
            'Also subscribe to SBA Michigan District Office list for state-specific programs.'
        ),
        'Action Required': 'Subscribe at sba.gov/about-sba/sba-newsroom. Also subscribe to SBA Michigan District.',
        'Check Frequency':     'Passive — email alerts',
    },
    {
        'Grant Name':          'Hello Alice Email Alerts',
        'Funder Organization': 'Hello Alice',
        'Funder Type':         'Grant Aggregator',
        'Funding Type':        'Alert Service',
        'Grant URL':           'https://helloalice.com',
        'Eligibility':         'Free registered users',
        'Grant Amount':        'N/A — alert service',
        'Cycle':               'Alerts as new grants added',
        'Priority Level':      'Critical (90-100)',
        'Qualification Score': 97,
        'Application Time':    '2 min to configure',
        'Fee':                 False,
        'Notes': (
            'FREE. After creating Hello Alice account, enable email notifications. '
            'You will be alerted the MOMENT a new grant you match becomes available. '
            'This is the single most important free alert to configure. '
            'Hello Alice adds grants 24/7 from dozens of corporate partners.'
        ),
        'Action Required': 'Enable email notifications in Hello Alice account settings.',
        'Check Frequency':     'Passive — email alerts',
    },

    # =========================================================================
    # TIER 7: FELLOWSHIP / BUILDER / TECH INNOVATION — DDI as Creator of NEXUS + FleetFlow
    # DDI built two proprietary AI platforms (NEXUS, FleetFlow TMS). These grants
    # recognize technology builders, not just traditional small businesses.
    # Pitch: "We built the AI infrastructure that allows a 5-person firm to compete
    # at the level of a 50-person organization in federal contracting."
    # =========================================================================

    {
        'Grant Name':          "O'Shaughnessy Fellowships & Grants",
        'Funder Organization': "O'Shaughnessy Ventures",
        'Funder Type':         'Private Venture — Fellowship',
        'Funding Type':        'Fellowship Grant ($100K) + Grant ($10K+)',
        'Grant URL':           'https://www.osvfellowship.com/',
        'Eligibility':         'Anyone 18+, global. Builders, researchers, creatives advancing civilization. No equity taken.',
        'Grant Amount':        '$10,000 – $100,000',
        'Cycle':               'Annual — Jan 1 to Apr 30 deadline',
        'Priority Level':      'Critical (90-100)',
        'Qualification Score': 92,
        'Application Time':    '1–2 hours',
        'Fee':                 False,
        'Notes': (
            'FREE. No equity. No corporate oversight. No thesis. No committee approvals. '
            '10 Fellowships at $100K + up to 20 Grants at $10K+. '
            'DDI pitch: Built NEXUS (9-module AI platform for federal contracting) and FleetFlow TMS '
            'from scratch — 5-person firm operating with Fortune 500-level capacity. '
            '7 years traction, live government contracts, 100% IP owned by DDI. '
            'Apply as Dieasha D. Davis / Dee Davis Inc. — same entity, same work. '
            'Single application considered for both Fellowship and Grant. '
            '2026 deadline: April 30, 2026. Rolling reviews — apply ASAP. '
            'Apply: https://forms.osv.llc/fellowships2026'
        ),
        'Action Required': 'APPLY NOW — deadline April 30, 2026. Use NEXUS + FleetFlow as the project. Apply at forms.osv.llc/fellowships2026',
        'Check Frequency':     'Annual — apply by April 30',
    },
    {
        'Grant Name':          'Soma Scholars Grant',
        'Funder Organization': 'Soma Capital',
        'Funder Type':         'Venture Capital — Non-Dilutive Grant',
        'Funding Type':        'Grant',
        'Grant URL':           'https://merge.club/program/soma-scholars',
        'Eligibility':         'Ambitious builders globally. Any domain. Rolling admissions. 2-minute application.',
        'Grant Amount':        '$30,000',
        'Cycle':               'Rolling — no fixed deadline',
        'Priority Level':      'Critical (90-100)',
        'Qualification Score': 90,
        'Application Time':    '30 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. $30,000 completely equity-free. No strings attached. '
            'Rolling admissions — 2-minute application. '
            'Also includes access to NYC + SF offices and network of founders of 30+ unicorns '
            '(Rippling, Deel, Ramp). '
            'DDI pitch: NEXUS and FleetFlow are live AI platforms built by DDI — '
            'active government contracts, 7 years operational, no investors. '
            'Strong "self-directed builder" narrative. '
            'Apply: somacap.com/scholars'
        ),
        'Action Required': 'Apply at somacap.com/scholars — rolling, apply anytime. Fast 2-minute form.',
        'Check Frequency':     'Rolling — apply now',
    },
    {
        'Grant Name':          "Women Who Tech Startup Grants",
        'Funder Organization': 'Women Who Tech',
        'Funder Type':         'Nonprofit Foundation',
        'Funding Type':        'Grant',
        'Grant URL':           'https://womenwhotech.org/grants-program',
        'Eligibility':         'Women-led tech startups. Overlooked founders. US-based. Rolling cycles.',
        'Grant Amount':        '$3,000 – $15,000',
        'Cycle':               'Rolling — multiple cycles per year',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 88,
        'Application Time':    '45–60 minutes',
        'Fee':                 False,
        'Notes': (
            'FREE. Equity-free grants for tech startups led by women. '
            'Explicitly targets overlooked founders — EDWOSB + Black woman-owned = strong fit. '
            'Multiple cycles per year with different themes. '
            'Sign up for alerts at womenwhotech.org for when next cycle opens. '
            'DDI pitch: AI platform company (NEXUS, FleetFlow) run by a Black woman-owned EDWOSB. '
            'Apply: womenwhotech.org/grants-program'
        ),
        'Action Required': 'Sign up for alerts at womenwhotech.org. Apply when next cycle opens.',
        'Check Frequency':     'Monthly — check for new cycles',
    },
    {
        'Grant Name':          "AT&T She's Connected $50K Grant",
        'Funder Organization': 'AT&T',
        'Funder Type':         'Corporate — Technology',
        'Funding Type':        'Grant',
        'Grant URL':           'https://www.att.com/smallbusiness/shesconnected/',
        'Eligibility':         'Woman-owned US business. 50 employees or fewer. Any sector.',
        'Grant Amount':        '$50,000',
        'Cycle':               'Annual — typically opens Spring/Summer',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 85,
        'Application Time':    '1–2 hours',
        'Fee':                 False,
        'Notes': (
            'FREE. $50,000 + media exposure + mentorship for woman-owned businesses. '
            'Annual program — 2025 cycle closed September 30; watch for 2026 opening. '
            'Technology and connectivity focus makes DDI a strong fit (NEXUS, FleetFlow). '
            'No equity taken. One grand prize + runner-up grants. '
            'Monitor AT&T small business page for 2026 opening announcement. '
            'Also available via Hello Alice when cycle opens.'
        ),
        'Action Required': 'Monitor att.com/smallbusiness/shesconnected for 2026 cycle opening. Set calendar reminder for Spring 2026.',
        'Check Frequency':     'Annual — watch for Spring 2026 opening',
    },
    {
        'Grant Name':          'Proposium Grant Discovery Platform',
        'Funder Organization': 'Proposium',
        'Funder Type':         'Grant Aggregator / AI Matching',
        'Funding Type':        'Multiple — AI-Matched Grants',
        'Grant URL':           'https://proposium.ai/',
        'Eligibility':         'Any business — AI matches grants to your profile',
        'Grant Amount':        'Varies — monitors $750B+ in funding',
        'Cycle':               'Daily monitoring',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 84,
        'Application Time':    '10 min to set up profile',
        'Fee':                 False,
        'Notes': (
            'FREE tier available. Monitors $750B+ in funding daily. '
            'Weekly grant digests tailored to DDI profile. '
            'Pro plan ($9/month) adds daily alerts and unlimited matching. '
            'Specifically surfaces fellowship-style and innovation grants that '
            'standard aggregators (Hello Alice) miss. '
            'Strong for finding O\'Shaughnessy-style opportunities as they emerge. '
            'Set up DDI profile with: EDWOSB, woman-owned, Black-owned, AI technology, '
            'government contracting, logistics, healthcare compliance.'
        ),
        'Action Required': 'Create free account at proposium.ai. Set DDI profile with tech + EDWOSB filters.',
        'Check Frequency':     'Weekly digest (free) or daily alerts (Pro)',
    },
    {
        'Grant Name':          'Funding Findr — Founder + Creator Grants',
        'Funder Organization': 'Funding Findr',
        'Funder Type':         'Grant Aggregator — Founders / Creators',
        'Funding Type':        'Multiple — Curated Grants',
        'Grant URL':           'https://www.fundingfindr.co/',
        'Eligibility':         'Entrepreneurs, creators, nonprofits. US-based.',
        'Grant Amount':        'Varies + $250 monthly microgrant',
        'Cycle':               'Daily updates + rolling microgrant',
        'Priority Level':      'High (80-89)',
        'Qualification Score': 83,
        'Application Time':    '5 min to browse, $3 trial',
        'Fee':                 True,
        'Notes': (
            'LOW FEE ($3 trial). Hand-curated grant database for founders, creators, nonprofits. '
            'Specifically surfaces fellowship-style grants that Hello Alice misses. '
            'Runs its own $250 monthly microgrant (rolling). '
            'Strong for surfacing O\'Shaughnessy-type opportunities. '
            'Use alongside Hello Alice — different grant types, complementary coverage.'
        ),
        'Action Required': 'Try $3 trial at fundingfindr.co. Set up DDI profile. Check weekly.',
        'Check Frequency':     'Weekly',
    },
    {
        'Grant Name':          'Merge Grant — Builder Microgrant',
        'Funder Organization': 'Merge Club',
        'Funder Type':         'Private — Builder Community',
        'Funding Type':        'Microgrant',
        'Grant URL':           'https://merge.club/grant',
        'Eligibility':         'Any builder globally. Young or first-time builders preferred.',
        'Grant Amount':        '$100 – $1,000',
        'Cycle':               'Rolling — ~10 day turnaround',
        'Priority Level':      'Medium (70-79)',
        'Qualification Score': 72,
        'Application Time':    '15-minute interview',
        'Fee':                 False,
        'Notes': (
            'FREE. Fast microgrant ($100–$1K) for builders. '
            '~10 day average funding timeline. Short application + 15-min interview. '
            'Low dollar amount but builds grant track record and network access. '
            'Comes with $800K in service credits (AWS, Stripe, etc.). '
            'Good for documenting DDI as a builder org in grant databases. '
            'Apply: merge.club/grant'
        ),
        'Action Required': 'Apply at merge.club/grant — rolling, fast turnaround. Good track record builder.',
        'Check Frequency':     'Rolling — apply anytime',
    },
]

# DDI priority seeds (March 2026 GBIS fix list) — merged into main list
DDI_PRIORITY_GRANT_SOURCES: List[Dict] = [
    {
        'Grant Name': 'Amber Grant for Women — WomensNet',
        'Funder Organization': 'WomensNet',
        'Funder Type': 'Women-Focused Foundation',
        'Funding Type': 'Foundation Grant',
        'Grant URL': 'https://ambergrantsforwomen.com',
        'Eligibility': 'Woman-owned business. US-based.',
        'Grant Amount': '$10,000 monthly + $50,000 annual',
        'Cycle': 'Monthly rolling',
        'Priority Level': 'Critical (90-100)',
        'Qualification Score': 96,
        'Application Time': '20–30 minutes',
        'Fee': True,
        'Notes': 'Apply every month. Women owned. Rolling deadline. $15 application fee per entry.',
        'Action Required': 'Apply monthly at ambergrantsforwomen.com.',
        'Check Frequency': 'Monthly',
        'Entity': 'BOTH',
        'Recommendation': 'Auto-Pursue',
    },
    {
        'Grant Name': 'Michigan Women Forward Microloan',
        'Funder Organization': 'Michigan Women Forward',
        'Funder Type': 'CDFI',
        'Funding Type': 'Loan / capital (grant-like access)',
        'Grant URL': 'https://miwf.org/business-loans',
        'Eligibility': 'Michigan women-owned businesses; flexible credit.',
        'Grant Amount': '$2,500 - $50,000',
        'Cycle': 'Rolling',
        'Priority Level': 'Critical (90-100)',
        'Qualification Score': 93,
        'Application Time': 'Varies',
        'Fee': False,
        'Notes': 'CDFI. Flexible underwriting. Sub-optimal credit may qualify.',
        'Action Required': 'Start application at miwf.org.',
        'Check Frequency': 'Rolling',
        'Entity': 'DDI',
        'Recommendation': 'Auto-Pursue',
    },
    {
        'Grant Name': 'Goldman Sachs One Million Black Women',
        'Funder Organization': 'Goldman Sachs',
        'Funder Type': 'Corporate',
        'Funding Type': 'Capital / grant programs',
        'Grant URL': 'https://www.goldmansachs.com/citizenship/10000-small-businesses/US/one-million-black-women',
        'Eligibility': 'Black women entrepreneurs; all industries.',
        'Grant Amount': '$25,000 - $250,000',
        'Cycle': 'Annual',
        'Priority Level': 'Critical (90-100)',
        'Qualification Score': 94,
        'Application Time': 'Varies',
        'Fee': False,
        'Notes': 'Black women entrepreneurs. All industries.',
        'Action Required': 'Monitor program page for next cycle.',
        'Check Frequency': 'Annual',
        'Entity': 'DDI',
        'Recommendation': 'Auto-Pursue',
    },
    {
        'Grant Name': 'MEDC Inclusive Entrepreneurship Support Grant',
        'Funder Organization': 'Michigan Economic Development Corporation',
        'Funder Type': 'State Government',
        'Funding Type': 'State Grant',
        'Grant URL': 'https://www.michiganbusiness.org',
        'Eligibility': 'Michigan small businesses; EDWOSB/MBE priority when programs open.',
        'Grant Amount': 'Varies',
        'Cycle': 'Annual',
        'Priority Level': 'High (80-89)',
        'Qualification Score': 85,
        'Application Time': 'Varies',
        'Fee': False,
        'Notes': 'Michigan EDWOSB MBE priority. Watch for next cycle.',
        'Action Required': 'Subscribe to MEDC / michiganbusiness.org alerts.',
        'Check Frequency': 'Monthly',
        'Entity': 'BOTH',
        'Recommendation': 'Review',
    },
    {
        'Grant Name': "Olga's Kitchen Foundation",
        'Funder Organization': "Olga's Kitchen Foundation",
        'Funder Type': 'Foundation',
        'Funding Type': 'Foundation Grant',
        'Grant URL': 'https://olgaskitchenfoundation.org',
        'Eligibility': 'Michigan women business owners; financial need statement.',
        'Grant Amount': 'Up to $10,000',
        'Cycle': 'Annual',
        'Priority Level': 'Critical (90-100)',
        'Qualification Score': 91,
        'Application Time': 'Varies',
        'Fee': False,
        'Notes': 'Michigan women business owners. Financial need statement required.',
        'Action Required': 'Watch for annual application window.',
        'Check Frequency': 'Annual',
        'Entity': 'DDI',
        'Recommendation': 'Auto-Pursue',
    },
    {
        'Grant Name': 'Entrepreneurs of Color Fund',
        'Funder Organization': 'Detroit Future City / partner CDFIs',
        'Funder Type': 'CDFI / philanthropic',
        'Funding Type': 'Grant / loan hybrid',
        'Grant URL': 'https://detroitfuturecity.com',
        'Eligibility': 'Detroit Metro women- and minority-owned businesses.',
        'Grant Amount': '$10,000 - $300,000',
        'Cycle': 'Rolling',
        'Priority Level': 'Critical (90-100)',
        'Qualification Score': 92,
        'Application Time': 'Varies',
        'Fee': False,
        'Notes': 'Detroit Metro. Women and minority owned. Cash flow gaps.',
        'Action Required': 'Inquire via Detroit Future City / fund partners.',
        'Check Frequency': 'Rolling',
        'Entity': 'DDI',
        'Recommendation': 'Auto-Pursue',
    },
]

SMALL_GRANT_SOURCES.extend(DDI_PRIORITY_GRANT_SOURCES)


# ---------------------------------------------------------------------------
# DAILY CHECK URLS — for human monitoring
# ---------------------------------------------------------------------------

DAILY_CHECK_URLS = [
    {
        'name':        'Hello Alice Grants',
        'url':         'https://helloalice.com/grants',
        'method':      'daily_check + email_alert',
        'frequency':   'Daily',
        'description': 'Best free aggregator for woman-owned businesses. New grants appear 24/7.',
        'fee':         False,
    },
    {
        'name':        'Nav Business Grants',
        'url':         'https://www.nav.com/resource/small-business-grants/',
        'method':      'manual',
        'frequency':   'Weekly (Mondays)',
        'description': 'Aggregates 40+ rolling small business grant programs.',
        'fee':         False,
    },
    {
        'name':        'Grants.gov',
        'url':         'https://www.grants.gov',
        'method':      'automated + email_alert',
        'frequency':   'Automated via NEXUS GBIS miner',
        'description': 'Federal grants database. NEXUS mines this automatically.',
        'fee':         False,
    },
    {
        'name':        'SBA Grants',
        'url':         'https://www.sba.gov/funding-programs/grants',
        'method':      'email_alert + manual',
        'frequency':   'Weekly + email alerts',
        'description': 'SBA programs including SBIR/STTR and InnovateHER.',
        'fee':         False,
    },
    {
        'name':        'Michigan SBDC',
        'url':         'https://www.michigansbdc.org/programs',
        'method':      'manual + advisor',
        'frequency':   'Monthly advisor meeting',
        'description': 'State grants. Free SBDC advisor has grant intel before it posts.',
        'fee':         False,
    },
    {
        'name':        'Michigan Business (MEDC)',
        'url':         'https://www.michiganbusiness.org/services/small-business/',
        'method':      'email_alert + manual',
        'frequency':   'Monthly',
        'description': 'Michigan state programs and economic development grants.',
        'fee':         False,
    },
    {
        'name':        'WBENC Member Portal',
        'url':         'https://www.wbenc.org',
        'method':      'manual',
        'frequency':   'Monthly',
        'description': 'Exclusive grants for WBENC-certified businesses. DDI is already certified.',
        'fee':         False,
    },
    {
        'name':        'LinkedIn Grant Search',
        'url':         'https://www.linkedin.com',
        'method':      'manual + notifications',
        'frequency':   'Daily',
        'description': 'Corporate grant announcements often appear on LinkedIn first.',
        'fee':         False,
    },
    {
        'name':        'Facebook Grant Groups',
        'url':         'https://www.facebook.com/groups',
        'method':      'manual',
        'frequency':   'Daily (2 min scan)',
        'description': 'Community members share grants as they find them.',
        'fee':         False,
    },
]


class GBISSmallGrantsMiner:
    """
    Seeds and monitors small business grant sources for Dee Davis Inc.
    Targets woman-owned, EDWOSB, service-based, Michigan-based businesses.
    ALL sources are free unless explicitly marked Fee: True.
    """

    def __init__(self):
        self.airtable = AirtableClient()

    # -----------------------------------------------------------------------
    # SEED ALL SOURCES
    # -----------------------------------------------------------------------

    def seed_all_sources(self) -> Dict:
        """Seeds all sources. Safe to re-run — skips duplicates."""
        return self._seed_sources(SMALL_GRANT_SOURCES, label="all sources")

    def seed_free_sources_only(self) -> Dict:
        """Seeds only 100% free sources (no application fees)."""
        free = [s for s in SMALL_GRANT_SOURCES if not s.get('Fee', False)]
        return self._seed_sources(free, label="free-only sources")

    def _seed_sources(self, sources: List[Dict], label: str = "sources") -> Dict:
        print("=" * 60)
        print(f"GBIS SMALL BUSINESS GRANT MINER — {label.upper()}")
        print(f"Seeding {len(sources)} sources")
        print(f"Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)

        imported = 0
        skipped  = 0

        for source in sources:
            try:
                if self._is_duplicate(source['Grant Name']):
                    print(f"   ⏭️  Already tracked: {source['Grant Name'][:65]}")
                    skipped += 1
                    continue

                fee_note = " [FEE REQUIRED]" if source.get('Fee') else " [FREE]"
                # Pack supplemental info into NOTES since those fields aren't in the table
                ent = source.get('Entity') or 'DDI'
                rec_label = source.get('Recommendation') or priority_to_recommendation(source.get('Priority Level', ''))
                notes_parts = [
                    source.get('Notes', ''),
                    f"Amount: {source.get('Grant Amount', 'Varies')}",
                    f"Priority: {source['Priority Level']} | Score: {source['Qualification Score']}",
                    f"Cycle: {source.get('Cycle', '')}",
                    f"Time: {source.get('Application Time', '')} | Freq: {source.get('Check Frequency', '')}",
                    f"Action: {source.get('Action Required', '')}",
                    f"Type: {source['Funder Type']} | Funding: {source.get('Funding Type', '')}",
                    f"Lane: Small Business Grants | Entity: {ent}",
                    fee_note,
                ]
                record = {
                    'Grant Name': source['Grant Name'],
                    'Funder Organization': source['Funder Organization'],
                    'Grant URL': source['Grant URL'],
                    'Eligibility': source['Eligibility'],
                    'Notes': '\n'.join(p for p in notes_parts if p.strip()),
                    'Entity': ent,
                    'Grant Source Type': 'TRACKED SOURCE',
                    'Recommendation': rec_label,
                    'Priority Level': source.get('Priority Level', ''),
                    'Last Source Check': today_iso(),
                }
                if ent == 'BOTH':
                    record['DDI Strategy Note'] = (
                        'Cause We Care may apply where nonprofit eligibility applies; '
                        'Dee Davis Inc. as EDWOSB prime for contract delivery where applicable.'
                    )

                create_grant_opportunity(self.airtable, record)
                print(f"   ✅ {source['Grant Name'][:65]}{fee_note}")
                print(f"      {source.get('Grant Amount', 'Varies')} | {source['Priority Level']} | {source.get('Check Frequency', '')}")
                imported += 1

            except Exception as e:
                print(f"   ❌ Error: {source['Grant Name'][:50]}: {e}")

        print(f"\n📊 {label}: {imported} added, {skipped} already tracked")
        return {
            'imported': imported,
            'skipped':  skipped,
            'total':    len(sources),
        }

    # -----------------------------------------------------------------------
    # DAILY DIGEST
    # -----------------------------------------------------------------------

    def daily_digest(self) -> Dict:
        """
        Returns today's prioritized grant action checklist.
        Called by NEXUS daily briefing.
        """
        today        = datetime.now()
        day_of_week  = today.weekday()   # 0 = Monday
        day_of_month = today.day

        actions = []

        # ── Every day ─────────────────────────────────────────────────────
        actions.append({
            'priority': 'EVERY DAY',
            'source':   'Hello Alice',
            'action':   'Check for new grants (takes 2 minutes)',
            'url':      'https://helloalice.com/grants',
            'time':     '2–5 min',
            'fee':      'FREE',
        })
        actions.append({
            'priority': 'EVERY DAY',
            'source':   'LinkedIn',
            'action':   'Search: "small business grant women" in LinkedIn feed',
            'url':      'https://www.linkedin.com/search/results/content/?keywords=small+business+grant+women+owned',
            'time':     '2 min',
            'fee':      'FREE',
        })

        # ── Every Monday ──────────────────────────────────────────────────
        if day_of_week == 0:
            actions.append({
                'priority': 'EVERY MONDAY',
                'source':   'Nav Business Grants',
                'action':   'Scan nav.com for new small business grants added this week',
                'url':      'https://www.nav.com/resource/small-business-grants/',
                'time':     '10 min',
                'fee':      'FREE',
            })
            actions.append({
                'priority': 'EVERY MONDAY',
                'source':   'Michigan SBDC',
                'action':   'Check for new Michigan state programs',
                'url':      'https://www.michigansbdc.org/programs',
                'time':     '5 min',
                'fee':      'FREE',
            })
            actions.append({
                'priority': 'EVERY MONDAY',
                'source':   'MEDC Michigan',
                'action':   'Check michiganbusiness.org for new programs',
                'url':      'https://www.michiganbusiness.org/services/small-business/',
                'time':     '5 min',
                'fee':      'FREE',
            })

        # ── 1st of month ──────────────────────────────────────────────────
        if day_of_month == 1:
            actions.append({
                'priority': 'MONTHLY — DO TODAY',
                'source':   'Amber Grant for Women',
                'action':   'APPLY NOW — $10K monthly grant',
                'url':      'https://ambergrantsforwomen.com',
                'time':     '20–30 min',
                'fee':      '$15 application fee',
            })
            actions.append({
                'priority': 'MONTHLY — DO TODAY',
                'source':   'IFundWomen',
                'action':   'Check ifundwomen.com for open grant programs this month',
                'url':      'https://ifundwomen.com/grants',
                'time':     '15 min',
                'fee':      'FREE',
            })
            actions.append({
                'priority': 'MONTHLY — DO TODAY',
                'source':   'WBENC Member Portal',
                'action':   'Log in and check member grants section',
                'url':      'https://www.wbenc.org',
                'time':     '10 min',
                'fee':      'FREE (already certified)',
            })
            actions.append({
                'priority': 'MONTHLY — DO TODAY',
                'source':   'Bank of America',
                'action':   'Check for new Bank of America small business grant programs',
                'url':      'https://about.bankofamerica.com/en/making-an-impact/small-business-grants',
                'time':     '5 min',
                'fee':      'FREE',
            })

        # ── Q1 (Jan–Mar) ───────────────────────────────────────────────────
        if today.month in (1, 2, 3):
            actions.append({
                'priority': 'ANNUAL — Q1 OPEN NOW',
                'source':   'Cartier Women\'s Initiative',
                'action':   'Check if application is open for this year',
                'url':      'https://www.cartierwomensinitiative.com',
                'time':     '2–3 hours if applying',
                'fee':      'FREE',
            })
            actions.append({
                'priority': 'ANNUAL — Q1 OPEN NOW',
                'source':   'Eileen Fisher Grant',
                'action':   'Check if Q1/Q2 application cycle is open',
                'url':      'https://www.eileenfisher.com/grants',
                'time':     '2–3 hours if applying',
                'fee':      'FREE',
            })

        # ── Spring (Mar–May) ───────────────────────────────────────────────
        if today.month in (3, 4, 5):
            actions.append({
                'priority': 'ANNUAL — SPRING',
                'source':   'FedEx Small Business Grant',
                'action':   'Check if FedEx contest is open this year',
                'url':      'https://smallbusinessgrant.fedex.com',
                'time':     '45–60 min if applying',
                'fee':      'FREE',
            })

        # ── Fall (Sep–Nov) ─────────────────────────────────────────────────
        if today.month in (9, 10, 11):
            actions.append({
                'priority': 'ANNUAL — FALL',
                'source':   'SBA InnovateHER Challenge',
                'action':   'Apply to SBA InnovateHER — strong EDWOSB fit',
                'url':      'https://www.sba.gov/local-assistance/resource-partners/womens-business-centers/innovateher-challenge',
                'time':     '2–3 hours',
                'fee':      'FREE',
            })

        return {
            'date':              today.strftime('%Y-%m-%d'),
            'day_of_week':       today.strftime('%A'),
            'actions':           actions,
            'total_actions':     len(actions),
            'daily_check_urls':  DAILY_CHECK_URLS,
            'total_sources':     len(SMALL_GRANT_SOURCES),
            'free_sources':      len([s for s in SMALL_GRANT_SOURCES if not s.get('Fee')]),
            'fee_sources':       len([s for s in SMALL_GRANT_SOURCES if s.get('Fee')]),
        }

    # -----------------------------------------------------------------------
    # HELPERS
    # -----------------------------------------------------------------------

    def _is_duplicate(self, grant_name: str) -> bool:
        try:
            from gbis_airtable_helpers import grant_name_from_fields

            records = self.airtable.get_all_records('GRANT OPPORTUNITIES')
            g = grant_name.lower().strip()
            for r in records:
                if grant_name_from_fields(r.get('fields', {})).lower() == g:
                    return True
            return False
        except Exception:
            return False

    def get_critical_sources(self) -> List[Dict]:
        """Returns only Critical (90-100) sources sorted by score."""
        return sorted(
            [s for s in SMALL_GRANT_SOURCES if s['Priority Level'].startswith('Critical')],
            key=lambda x: x['Qualification Score'],
            reverse=True,
        )

    def get_free_sources(self) -> List[Dict]:
        """Returns only 100% free sources."""
        return [s for s in SMALL_GRANT_SOURCES if not s.get('Fee', False)]


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    miner = GBISSmallGrantsMiner()

    free_count = len(miner.get_free_sources())
    total_count = len(SMALL_GRANT_SOURCES)
    print(f"\n📊 Sources: {total_count} total | {free_count} completely FREE | {total_count - free_count} have fees")

    print("\n📋 TODAY'S GRANT ACTIONS:")
    digest = miner.daily_digest()
    for action in digest['actions']:
        fee_label = f"  [{action['fee']}]" if action.get('fee') else "  [FREE]"
        print(f"\n  [{action['priority']}] {action['source']}{fee_label}")
        print(f"  → {action['action']}")
        print(f"  → {action['url']}")

    print(f"\n\n📋 DAILY CHECK LIST:")
    for url in DAILY_CHECK_URLS:
        print(f"  {'✅ FREE' if not url['fee'] else '💰 PAID'} | {url['frequency']:25s} | {url['name']} — {url['url']}")

    confirm = input("\n\nSeed all sources into GBIS? (all/free/no): ").strip().lower()
    if confirm == 'all':
        miner.seed_all_sources()
    elif confirm == 'free':
        miner.seed_free_sources_only()
    else:
        print("\nSeed skipped. Run via API: POST /gbis/mine-small-grants/seed")
