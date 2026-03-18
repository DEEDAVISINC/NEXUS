#!/usr/bin/env python3
"""
DDI Capability Statement Generator
Uses clean HTML design + PDF master content + partner logos
Tailors content per solicitation while keeping the look identical
"""

import os
import sys

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

def load_img(name):
    with open(os.path.join(ASSETS_DIR, f'capimg_{name}.txt'), 'r') as f:
        return f.read()

LOGO = load_img('ddi')
PHOTO = load_img('dee_davis')
EDWOSB_BADGE = load_img('edwosb')
WBENC_BADGE = load_img('wbenc')
TWIC_BADGE = load_img('twic')
QUEST_LOGO = load_img('quest')
DDC_LOGO = load_img('ddc')
INK3D_LOGO = load_img('3d_ink')
CHAMPION_LOGO = load_img('champion')
MDHHS_LOGO = load_img('mdhhs')


def generate(config):
    primary = config['primary']
    accent = config['accent']
    sol_number = config.get('sol_number', '')
    sol_agency = config.get('sol_agency', '')
    sol_service = config.get('sol_service', '')
    sol_naics = config.get('sol_naics', '')
    competencies = config.get('competencies', DEFAULT_COMPETENCIES)
    past_performance = config.get('past_performance', DEFAULT_PAST_PERFORMANCE)
    differentiators = config.get('differentiators', DEFAULT_DIFFERENTIATORS)
    overview = config.get('overview', DEFAULT_OVERVIEW)
    
    comp_html = ''
    classes = ['c-primary','c-accent','c-light1','c-light2','c-primary','c-accent','c-light1','c-light2']
    for i, (title, desc) in enumerate(competencies):
        cls = classes[i % len(classes)]
        comp_html += f'    <div class="comp-box {cls}"><h4>{title}</h4><p>{desc}</p></div>\n'
    
    pp_html = ''
    for metric, desc in past_performance:
        pp_html += f'          <li><span class="wt">{metric}</span><br><span class="wd">{desc}</span></li>\n'
    
    diff_html = ''
    for title, desc in differentiators:
        diff_html += f'          <li><span class="wt">{title}</span><br><span class="wd">{desc}</span></li>\n'

    naics_list = config.get('naics', DEFAULT_NAICS)
    naics_html = ''
    for code in naics_list:
        if code == sol_naics:
            naics_html += f'<strong style="color:{primary};">{code} &#9733;</strong> &nbsp; '
        else:
            naics_html += f'{code} &nbsp; '

    footer_ref = f'Prepared for {sol_agency} &mdash; {sol_number} &mdash; {sol_service} | March 2026' if sol_number else ''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DEE DAVIS INC &mdash; Capability Statement{" &mdash; " + sol_number if sol_number else ""}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
* {{ margin:0; padding:0; box-sizing:border-box; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
body {{ font-family:'Inter',sans-serif; background:#fff; color:#1e293b; }}
.page {{ width:8.5in; min-height:11in; margin:0 auto; padding:0.35in 0.45in; display:flex; flex-direction:column; }}

.header {{ display:flex; align-items:center; gap:0.6rem; margin-bottom:0.35rem; }}
.h-logo img {{ width:70px; height:70px; object-fit:contain; }}
.h-text {{ flex:1; }}
.h-text h1 {{ font-size:1.5rem; font-weight:900; color:{primary}; letter-spacing:-0.5px; line-height:1; }}
.h-text .sub {{ font-size:0.72rem; font-weight:700; color:{accent}; margin-top:0.1rem; }}
.h-creds {{ display:flex; gap:0.5rem; font-size:0.52rem; font-weight:700; color:#475569; margin-top:0.25rem; flex-wrap:wrap; }}
.h-creds span {{ background:#f1f5f9; padding:0.1rem 0.4rem; border-radius:3px; }}
.h-eligible {{ font-size:0.56rem; color:{primary}; font-weight:700; margin-top:0.15rem; }}

.who-row {{ display:flex; gap:0.6rem; align-items:center; margin-bottom:0.3rem; padding:0.4rem 0.5rem; background:linear-gradient(135deg,#f8fafc,#f1f5f9); border-radius:6px; border-left:4px solid {primary}; }}
.who-photo img {{ width:62px; height:62px; border-radius:50%; object-fit:cover; border:2px solid {accent}; }}
.who-text {{ flex:1; font-size:0.63rem; line-height:1.55; color:#334155; }}
.who-text strong {{ color:{primary}; }}

.exec-bar {{ background:linear-gradient(135deg,{primary},{accent}); color:#fff; text-align:center; padding:0.25rem; border-radius:4px; font-size:0.58rem; font-weight:700; letter-spacing:0.5px; margin-bottom:0.35rem; }}

.sh {{ font-size:0.65rem; font-weight:800; color:{primary}; border-bottom:2px solid {primary}; padding-bottom:0.1rem; margin-bottom:0.3rem; text-transform:uppercase; letter-spacing:0.5px; }}

.comp-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:0.3rem; margin-bottom:0.35rem; }}
.comp-box {{ border-radius:4px; padding:0.3rem 0.4rem; }}
.comp-box h4 {{ font-size:0.58rem; font-weight:700; margin-bottom:0.05rem; }}
.comp-box p {{ font-size:0.52rem; line-height:1.4; color:#475569; }}
.c-primary {{ background:{primary}10; border-left:3px solid {primary}; }}
.c-primary h4 {{ color:{primary}; }}
.c-accent {{ background:{accent}10; border-left:3px solid {accent}; }}
.c-accent h4 {{ color:{accent}; }}
.c-light1 {{ background:#f8fafc; border-left:3px solid #94a3b8; }}
.c-light1 h4 {{ color:#475569; }}
.c-light2 {{ background:#f8fafc; border-left:3px solid #64748b; }}
.c-light2 h4 {{ color:#334155; }}

.cols {{ display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; margin-bottom:0.3rem; }}
.wl {{ list-style:none; padding:0; }}
.wl li {{ font-size:0.54rem; padding:0.2rem 0; border-bottom:1px solid #f1f5f9; }}
.wt {{ font-weight:700; color:{primary}; }}
.wd {{ color:#64748b; }}

.cert-strip {{ display:flex; align-items:center; justify-content:center; gap:0.6rem; padding:0.25rem 0; margin-bottom:0.25rem; border-top:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0; }}
.cert-strip img {{ height:30px; object-fit:contain; }}

.partners {{ display:flex; align-items:center; justify-content:center; gap:0.5rem; padding:0.2rem 0; margin-bottom:0.25rem; }}
.partners img {{ height:26px; object-fit:contain; filter:grayscale(30%); }}
.plbl {{ font-size:0.48rem; color:#94a3b8; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; }}

.bottom {{ display:grid; grid-template-columns:1fr 1fr; gap:0.4rem; margin-top:auto; }}
.naics-block {{ font-size:0.5rem; color:#475569; line-height:1.6; }}
.naics-label {{ font-size:0.52rem; font-weight:700; color:{primary}; margin-bottom:0.1rem; }}
.contact-block {{ }}
.cert-line {{ font-size:0.5rem; font-weight:700; color:{primary}; margin-bottom:0.1rem; }}
.contact-line {{ font-size:0.52rem; color:#1e293b; line-height:1.5; }}
.contact-line strong {{ color:{primary}; }}

.footer {{ background:linear-gradient(135deg,{primary},{accent}); color:#fff; padding:0.25rem 0.5rem; border-radius:4px; margin-top:0.25rem; text-align:center; }}
.footer p {{ font-size:0.48rem; }}
.footer .gold {{ color:#fde68a; font-weight:700; }}
.sol-ref {{ font-size:0.42rem; opacity:0.7; margin-top:0.1rem; }}

@media print {{ body {{ margin:0; }} .page {{ margin:0; padding:0.35in 0.45in; }} }}
</style>
</head>
<body>
<div class="page">

  <div class="header">
    <div class="h-logo"><img src="{LOGO}" alt="DDI"></div>
    <div class="h-text">
      <h1>DEE DAVIS INC.</h1>
      <div class="sub">CONTRACT MANAGEMENT FIRM</div>
      <div class="h-creds">
        <span>CAGE: 8UMX3</span><span>UEI: HJB4KNYJVGZ1</span><span>DUNS: 002636755</span><span>SAM.gov: ACTIVE</span><span>Est. 2018</span>
      </div>
      <div class="h-eligible">Federal &bull; State &bull; Commercial &bull; Sole-Source Eligible Up to $7M</div>
    </div>
  </div>

  <div class="who-row">
    <div class="who-photo"><img src="{PHOTO}" alt="Dee Davis"></div>
    <div class="who-text">{overview}</div>
  </div>

  <div class="exec-bar">EXECUTION FRAMEWORK: Identify &rarr; Pursue &rarr; Build &rarr; Manage &rarr; Deliver &rarr; Sustain</div>

  <div class="sh">&#9670; CORE COMPETENCIES &mdash; PROVEN CONTRACT SECTORS</div>
  <div class="comp-grid">
{comp_html}  </div>

  <div class="cols">
    <div>
      <div class="sh">PAST PERFORMANCE &mdash; VERIFIED TRACK RECORD</div>
      <ul class="wl">
{pp_html}      </ul>
    </div>
    <div>
      <div class="sh">DIFFERENTIATORS</div>
      <ul class="wl">
{diff_html}      </ul>
    </div>
  </div>

  <div class="cert-strip">
    <img src="{EDWOSB_BADGE}" alt="EDWOSB">
    <img src="{WBENC_BADGE}" alt="WBENC">
    <img src="{TWIC_BADGE}" alt="TWIC">
  </div>

  <div class="partners">
    <span class="plbl">Strategic Alliance Partners:</span>
    <img src="{QUEST_LOGO}" alt="Quest" title="Quest Diagnostics">
    <img src="{DDC_LOGO}" alt="DDC" title="DNA Diagnostics Center">
    <img src="{INK3D_LOGO}" alt="3D Ink" title="3D Ink &amp; Livescan">
    <img src="{CHAMPION_LOGO}" alt="Champion" title="Champion Home Builders">
    <img src="{MDHHS_LOGO}" alt="MDHHS" title="MDHHS Community Partner">
  </div>

  <div class="bottom">
    <div class="naics-block">
      <div class="naics-label">NAICS CODES</div>
      {naics_html}
    </div>
    <div class="contact-block">
      <div class="cert-line">EDWOSB | WOSB | WBE | MBE | SBE | E-Verify | SWFT (DCSA) | TWIC (TSA)</div>
      <div class="contact-line">
        <strong>Dieasha D. Davis</strong> &mdash; President &amp; CEO<br>
        248.376.4550 &nbsp;|&nbsp; info@deedavis.biz<br>
        755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084
      </div>
    </div>
  </div>

  <div class="footer">
    <p><span class="gold">DEE DAVIS INC.</span> &mdash; "The Professionals' Professional" &mdash; <span class="gold">248.376.4550</span> &mdash; info@deedavis.biz</p>
    {"<p class='sol-ref'>" + footer_ref + "</p>" if footer_ref else ""}
  </div>

</div>
</body>
</html>'''
    
    return html


DEFAULT_OVERVIEW = '<strong>DEE DAVIS INC.</strong> is an <strong>SBA-certified EDWOSB prime contractor</strong> delivering end-to-end contract management across federal, state, and commercial sectors. With <strong>7+ years of proven performance</strong>, 5,100+ managed service locations nationwide, and <strong>zero compliance deficiencies</strong>, DDI executes complex, multi-stakeholder contracts through strategic alliance partners &mdash; from regulated healthcare operations and federal security credentialing to emergency logistics and business continuity. Multi-state licensed. CONUS/OCONUS deployment-ready.'

DEFAULT_COMPETENCIES = [
    ('Healthcare &amp; Compliance', 'DOT/FTA/SAMHSA drug &amp; alcohol programs, AABB-accredited DNA testing, medical specimen transport, NEMT, Medicaid provider operations'),
    ('Federal Security &amp; Credentialing', 'DCSA SWFT electronic fingerprinting, FBI NCHC submissions, TWIC-cleared facility access, personnel vetting'),
    ('Logistics &amp; Fleet Operations', 'Licensed freight brokerage (MC-1647572), DOT-regulated fleet coordination, time-critical delivery, chain-of-custody transport'),
    ('Government Procurement', 'Medical &amp; emergency equipment, industrial supply fulfillment, modified housing &amp; storage, commodity contract execution'),
    ('Professional &amp; Legal Services', 'Commissioned notary, Remote Online Notarization, CNTDA-certified document execution, surety bonds, signing agent services'),
    ('Workforce &amp; Training', 'Contract staffing, regulatory compliance training, supervisor certification programs, safety-sensitive personnel management'),
    ('Business Continuity', 'COOP execution, FEMA-coordinated disaster logistics, emergency supply chain activation, rapid contractor mobilization'),
    ('Management Consulting', 'Federal healthcare compliance, process optimization, logistics system design, operational risk assessment, BPM implementation'),
]

DEFAULT_PAST_PERFORMANCE = [
    ('DOT DRUG &amp; ALCOHOL PROGRAMS', 'TPA for transit authorities, utilities, federal agencies. Full 49 CFR Parts 40 &amp; 655 compliance.'),
    ('FEDERAL FINGERPRINTING &mdash; 4+ INSTALLATIONS', 'SWFT BPAs executed. DCSA/FBI electronic submissions. 24-48 hour turnaround.'),
    ('15+ ANNUAL MUNICIPAL CONTRACTS', 'County government commodity supply. On-time, on-budget, renewed annually.'),
    ('1,500+ REGULATED DELIVERIES', 'Chain-of-custody medical, pharmaceutical, specimen transport. Zero deficiencies.'),
    ('5,100+ MANAGED FACILITIES', 'Deployment-ready nationwide via eScreen/Quest Diagnostics partnership.'),
    ('MDHHS COMMUNITY PARTNER', 'Official recognition &mdash; State of Michigan Department of Health &amp; Human Services.'),
]

DEFAULT_DIFFERENTIATORS = [
    ('EDWOSB SOLE-SOURCE ELIGIBLE &mdash; UP TO $7M', 'SBA-certified. Streamlined procurement path. Reduces acquisition timeline by 60%+.'),
    ('5,100+ DEPLOYMENT-READY FACILITIES', 'Nationwide operational coverage through eScreen/Quest. Activate within 24 hours of award.'),
    ('SWFT AUTHORIZED &mdash; TOP 10% NATIONALLY', '3+ consecutive years DCSA authorization. Electronic submission to DCSA &amp; FBI CJIS.'),
    ('ZERO COMPLIANCE DEFICIENCIES', '1,500+ regulated deliveries across DOT, SAMHSA, HIPAA, and AABB environments. Fully auditable.'),
    ('TWIC-CLEARED SECURE ACCESS', 'Credentialed for ports, VA medical centers, DoD installations, and restricted federal facilities.'),
    ('MULTI-STATE, MULTI-SECTOR PRIME', '7+ years. Licensed in MI, GA, FL, MD. Active: SAM.gov, SIGMA, City of Detroit, BidNet, Oracle, Bonfire.'),
]

DEFAULT_NAICS = ['541611','541614','541618','541690','541990','621511','621999','561611','561612','485991','492110','484230','423450','485999']


if __name__ == '__main__':
    # State Dept Ride Share - TAILORED to transportation/rideshare
    state_dept = generate({
        'primary': '#6b21a8',
        'accent': '#0d9488',
        'sol_number': '19AQMM26N0154',
        'sol_agency': 'Department of State',
        'sol_service': 'Rideshare Services',
        'sol_naics': '485999',
        'naics': ['485999','485991','492110','484230','541611','541614','541618','541690','541990','561611','561612','621511','621999','423450'],
        'overview': '<strong>DEE DAVIS INC.</strong> is an <strong>SBA-certified EDWOSB prime contractor</strong> delivering end-to-end contract management across federal, state, and commercial sectors. With <strong>7+ years of proven performance</strong>, 5,100+ managed service locations nationwide, and <strong>zero compliance deficiencies</strong>, DDI executes complex, multi-stakeholder contracts through strategic alliance partners &mdash; from regulated healthcare operations and federal security credentialing to emergency logistics and business continuity. Multi-state licensed. CONUS/OCONUS deployment-ready.',
        'competencies': [
            ('Transportation &amp; Rideshare Management', 'On-demand 24/7 ride coordination, real-time GPS tracking, mobile app &amp; SMS dispatch, multi-platform integration (Lyft, Uber, regional providers)'),
            ('Fleet &amp; Logistics Operations', 'Licensed freight brokerage (MC-1647572), DOT-regulated fleet coordination, time-critical delivery, chain-of-custody transport, vehicle compliance tracking'),
            ('Federal Program Management', 'Dedicated program managers, COR coordination, IPP invoicing compliance, monthly/quarterly reporting, performance dashboards'),
            ('Data Security &amp; Compliance', 'Trip data restricted to authorized personnel, PII protection protocols, federal records management, audit-ready documentation'),
            ('Workforce &amp; Driver Management', 'Background-checked drivers, drug testing compliance, safety certifications, CDL qualification verification, personnel vetting'),
            ('Financial &amp; Invoice Management', 'Treasury IPP invoicing, automated cost reporting, spend analysis, quarterly review analysis, budget forecasting'),
            ('Healthcare &amp; Compliance', 'DOT/FTA/SAMHSA drug &amp; alcohol programs, AABB-accredited DNA testing, medical specimen transport, NEMT coordination'),
            ('Business Continuity', 'COOP execution, emergency transportation activation, rapid contractor mobilization, surge capacity coordination'),
        ],
        'past_performance': [
            ('DOT DRUG &amp; ALCOHOL PROGRAMS', 'TPA for transit authorities, utilities, federal agencies. Full 49 CFR Parts 40 &amp; 655 compliance.'),
            ('1,500+ REGULATED DELIVERIES', 'Chain-of-custody medical, pharmaceutical, specimen transport. Zero deficiencies.'),
            ('5,100+ MANAGED FACILITIES', 'Deployment-ready nationwide via eScreen/Quest Diagnostics partnership. Activate within 24 hours.'),
            ('LICENSED FREIGHT BROKERAGE', 'MC-1647572, DOT 4250594. Nationwide transportation coordination and fleet management.'),
            ('15+ ANNUAL MUNICIPAL CONTRACTS', 'County government service contracts. On-time, on-budget, renewed annually.'),
            ('MDHHS COMMUNITY PARTNER', 'Official recognition &mdash; State of Michigan Department of Health &amp; Human Services.'),
        ],
    })
    
    outpath = 'BIDS:RESOURCES/STATE DEPT RIDE SHARE/SEND_TO_BUYER/19AQMM26N0154_Ride_Share_Capability_Statement.html'
    with open(outpath, 'w') as f:
        f.write(state_dept)
    print(f'Generated: {outpath}')

    # USACE Palatka Custodial - TAILORED to facilities/custodial
    palatka = generate({
        'primary': '#166534',
        'accent': '#475569',
        'sol_number': 'W912EP26QA006',
        'sol_agency': 'USACE Jacksonville District',
        'sol_service': 'Palatka Custodial &amp; Mowing',
        'sol_naics': '561210',
        'naics': ['561210','561720','561730','561611','561612','541611','541614','541618','541690','541990','621511','621999','492110','484230'],
        'competencies': [
            ('Custodial &amp; Janitorial Services', 'Interior cleaning, restroom sanitation, floor care, trash removal, periodic deep cleaning, federal facility standards compliance'),
            ('Grounds Maintenance &amp; Mowing', 'Scheduled mowing, edging, trimming, debris removal, seasonal landscape care, stormwater area maintenance'),
            ('Quality Assurance &amp; Inspection', 'Performance tracking, corrective action procedures, USACE inspection alignment, documented QA protocols'),
            ('Federal Facility Compliance', 'Safety documentation, environmental compliance, OSHA adherence, contractor oversight, access control coordination'),
            ('Workforce &amp; Staffing', 'Vetted local subcontractors, background-checked personnel, contract staffing, safety-sensitive personnel management'),
            ('Equipment &amp; Supply Management', 'Cleaning supplies, grounds equipment, maintenance scheduling, inventory tracking, EPA-compliant products'),
            ('Management Consulting', 'Process optimization, operational risk assessment, logistics system design, BPM implementation'),
            ('Business Continuity', 'COOP execution, emergency contractor mobilization, rapid deployment, surge capacity coordination'),
        ],
        'past_performance': [
            ('15+ ANNUAL MUNICIPAL CONTRACTS', 'County government facility and commodity service contracts. On-time, on-budget, renewed annually.'),
            ('5,100+ MANAGED FACILITIES', 'Deployment-ready nationwide via eScreen/Quest Diagnostics partnership. Activate within 24 hours.'),
            ('ZERO COMPLIANCE DEFICIENCIES', '1,500+ regulated service deliveries across DOT, SAMHSA, HIPAA environments. Fully auditable.'),
            ('FEDERAL FINGERPRINTING &mdash; 4+ INSTALLATIONS', 'SWFT BPAs executed at federal installations. DCSA/FBI electronic submissions.'),
            ('DOT DRUG &amp; ALCOHOL PROGRAMS', 'TPA for transit authorities, utilities, federal agencies. Full compliance management.'),
            ('MDHHS COMMUNITY PARTNER', 'Official recognition &mdash; State of Michigan Department of Health &amp; Human Services.'),
        ],
    })
    
    outpath = 'BIDS:RESOURCES/USACE PALATKA CUSTODIAL/SEND_TO_BUYER/W912EP26QA006_Custodial_Capability_Statement.html'
    with open(outpath, 'w') as f:
        f.write(palatka)
    print(f'Generated: {outpath}')

    # Travis AFB TRAM Transport - TAILORED to transportation with driver
    travis = generate({
        'primary': '#6b21a8',
        'accent': '#0d9488',
        'sol_number': 'FA442726QZ022',
        'sol_agency': 'Travis AFB, 60th AMW',
        'sol_service': 'TRAM Transport Services with Driver',
        'sol_naics': '485999',
        'naics': ['485999','485991','492110','484230','541611','541614','541618','541690','541990','561611','561612','621511','621999','423450'],
        'competencies': [
            ('Passenger Transportation &amp; TRAM Services', 'Scheduling, routing, and dispatch for TRAM and shuttle services, on-base passenger transport, route optimization'),
            ('Licensed Driver Management', 'CDL-qualified drivers, background investigations, drug testing compliance, safety certifications, personnel vetting'),
            ('Fleet &amp; Vehicle Oversight', 'Inspection compliance, maintenance tracking, safety documentation, DOT-regulated fleet coordination (MC-1647572)'),
            ('Base Access &amp; Security Coordination', 'Installation security protocols, TWIC-cleared access, DoD facility experience, contractor badge management'),
            ('Real-Time Dispatch &amp; Tracking', 'On-demand scheduling, GPS monitoring, performance reporting, automated ridership data, dashboard access'),
            ('Federal Program Compliance', 'COR coordination, monthly/quarterly reporting, performance metrics, Air Force contract requirements adherence'),
            ('Workforce &amp; Training', 'Contract staffing, regulatory compliance training, supervisor certification programs, safety-sensitive personnel management'),
            ('Business Continuity', 'COOP execution, emergency transportation activation, rapid contractor mobilization, surge capacity planning'),
        ],
        'past_performance': [
            ('LICENSED FREIGHT BROKERAGE', 'MC-1647572, DOT 4250594. Nationwide transportation coordination and fleet management.'),
            ('DOT DRUG &amp; ALCOHOL PROGRAMS', 'TPA for transit authorities, utilities, federal agencies. Full 49 CFR Parts 40 &amp; 655 compliance.'),
            ('5,100+ MANAGED FACILITIES', 'Deployment-ready nationwide via eScreen/Quest Diagnostics partnership. Activate within 24 hours.'),
            ('FEDERAL FINGERPRINTING &mdash; 4+ INSTALLATIONS', 'SWFT BPAs executed at DoD/federal installations. DCSA/FBI electronic submissions.'),
            ('1,500+ REGULATED DELIVERIES', 'Chain-of-custody medical, pharmaceutical, specimen transport. Zero deficiencies.'),
            ('MDHHS COMMUNITY PARTNER', 'Official recognition &mdash; State of Michigan Department of Health &amp; Human Services.'),
        ],
    })
    
    outpath = 'BIDS:RESOURCES/TRAVIS AFB TRAM TRANSPORT/SEND_TO_BUYER/FA442726QZ022_Transport_Capability_Statement.html'
    with open(outpath, 'w') as f:
        f.write(travis)
    print(f'Generated: {outpath}')
