import React, { useState } from 'react';
import BuyerPipelineTab, { type PipelineImportFilter } from './jeta/BuyerPipelineTab';
import DealManagerTab from './jeta/DealManagerTab';
import DocumentsTab from './jeta/DocumentsTab';
import OutreachCenterTab from './jeta/OutreachCenterTab';
import DashboardTab from './jeta/DashboardTab';
import JetaFaaImportPanel from './jeta/JetaFaaImportPanel';

export interface JETASystemProps {
  onBackToNexus: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TABS: { id: string; label: string }[] = [
  { id: 'dashboard', label: '📊 Dashboard' },
  { id: 'buyer-pipeline', label: '🛫 Buyer Pipeline' },
  { id: 'deal-manager', label: '📋 Deal Manager' },
  { id: 'outreach-center', label: '📧 Outreach Center' },
  { id: 'documents', label: '📁 Documents' },
];

/** Simplified wholesale → retail stack; broker fee is part of the final commercial margin. */
const JETA_PRICE_STACK_LINES = [
  'Crude Oil Price',
  '+ Refining Cost',
  '= Refinery Gate Price (wholesale)',
  '+ Pipeline/Transport Cost',
  '= Terminal Rack Price (what marketers pay)',
  '+ Marketer Margin',
  '= What your buyer pays',
];

function MarketRefRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5 text-[11px] text-amber-100/95">
      <span className="text-amber-200/85">{label}</span>
      <span className="font-mono tabular-nums text-amber-50">{value}</span>
    </div>
  );
}

function JetaTouch1EmailExampleCard() {
  const [copied, setCopied] = useState(false);
  const clipboardText = `Subject: ${JETA_TOUCH1_EMAIL_EXAMPLE_SUBJECT}\n\n${JETA_TOUCH1_EMAIL_EXAMPLE_BODY}`;

  const copyFull = async () => {
    try {
      await navigator.clipboard.writeText(clipboardText);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      alert('Could not copy to clipboard.');
    }
  };

  return (
    <div
      className="mt-4 rounded-lg border border-cyan-800/40 bg-gradient-to-br from-cyan-950/25 to-black/30 px-4 py-3 ring-1 ring-cyan-900/20"
      role="region"
      aria-label="Example Touch 1 email for charter operator at KPTK"
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-cyan-300/90">
          Touch 1 email (example — pairs with prospect above)
        </p>
        <button
          type="button"
          onClick={() => void copyFull()}
          className="shrink-0 rounded border border-cyan-600/50 bg-cyan-950/40 px-2.5 py-1 text-[10px] font-medium text-cyan-100/95 hover:bg-cyan-900/50"
        >
          {copied ? 'Copied' : 'Copy full email'}
        </button>
      </div>
      <p className="mt-3 text-[11px] font-semibold text-cyan-100/95">
        Subject: {JETA_TOUCH1_EMAIL_EXAMPLE_SUBJECT}
      </p>
      <pre className="mt-2 max-h-[22rem] overflow-y-auto whitespace-pre-wrap font-sans text-[11px] leading-relaxed text-cyan-50/95">
        {JETA_TOUCH1_EMAIL_EXAMPLE_BODY}
      </pre>
      <p className="mt-3 text-[10px] text-cyan-400/70">
        Replace <span className="font-mono text-cyan-200/85">[Name]</span> from the contact row; send from your outreach identity and log Touch 1 in
        Outreach Center.
      </p>
    </div>
  );
}

type JetaChokepointRow = { label: string; value: string };

type JetaChokepoint = {
  id: string;
  title: string;
  rows: JetaChokepointRow[];
};

const JETA_CHOKEPOINTS: JetaChokepoint[] = [
  {
    id: 'hormuz',
    title: 'STRAIT OF HORMUZ — Most Critical',
    rows: [
      { label: 'Location', value: 'Persian Gulf entrance' },
      { label: 'Volume', value: '20% of ALL global oil passes here' },
      { label: 'Countries', value: 'Iran controls one side' },
      { label: 'Risk', value: 'Iran threatens closure regularly' },
      { label: 'Price impact', value: 'Closure = $50-100/bbl spike overnight' },
    ],
  },
  {
    id: 'suez',
    title: 'SUEZ CANAL',
    rows: [
      { label: 'Location', value: 'Egypt — connects Red Sea to Med' },
      { label: 'Volume', value: '12% of global trade' },
      { label: 'Risk', value: 'Houthi attacks ongoing 2024-2026' },
      {
        label: 'Price impact',
        value: 'Diversions add weeks and cost\nAlready adding $4-8/bbl currently',
      },
    ],
  },
  {
    id: 'bosphorus',
    title: 'STRAIT OF BOSPHORUS',
    rows: [
      { label: 'Location', value: 'Turkey — Black Sea to Med' },
      { label: 'Volume', value: 'Russian oil export route' },
      { label: 'Risk', value: 'Ukraine war disruption' },
      {
        label: 'Price impact',
        value: 'Russian supply disruptions\nalready baked into current prices',
      },
    ],
  },
  {
    id: 'scs',
    title: 'SOUTH CHINA SEA',
    rows: [
      { label: 'Location', value: 'Asia Pacific' },
      { label: 'Volume', value: '$3T trade annually passes here' },
      { label: 'Risk', value: 'China-Taiwan tension' },
      {
        label: 'Price impact',
        value: 'Disruption would spike\nAsian and West Coast US prices',
      },
    ],
  },
];

type JetaPriceRiskStructure = {
  id: string;
  title: string;
  bullets: string[];
};

const JETA_PRICE_RISK_STRUCTURES: JetaPriceRiskStructure[] = [
  {
    id: 'futures',
    title: 'FUTURES CONTRACT',
    bullets: [
      'Buyer locks in a price today for fuel delivered in 3–6 months',
      'Protects against price spikes',
      'Common for airlines',
    ],
  },
  {
    id: 'options',
    title: 'OPTIONS',
    bullets: [
      'Buyer buys the RIGHT to purchase fuel at a set price',
      'If price goes up — they exercise',
      'If price drops — they let it expire',
      'More flexible than futures',
    ],
  },
  {
    id: 'fixed',
    title: 'FIXED PRICE SUPPLY AGREEMENT',
    bullets: [
      'Buyer and seller agree on a fixed price for a term',
      'Your brokered deal could include this structure',
      'Seller takes the price risk',
    ],
  },
  {
    id: 'floating-cap',
    title: 'FLOATING PRICE + CAP',
    bullets: [
      'Price floats with market',
      'But capped at a maximum',
      'Buyer has upside protection',
      'Most common in term contracts',
    ],
  },
];

const JETA_SUSTAINED_HIGH_PRICE_EFFECTS = [
  'Higher prices = buyers get squeezed',
  'Airlines cut routes, reduce flying',
  'FBOs see less traffic',
];

const JETA_SUSTAINED_HIGH_PRICE_LOCK_IN =
  'Some buyers lock into long-term\ncontracts for price certainty\n— harder to break in as new broker';

const JETA_IATA_FEE_ESCALATION_CLAUSE =
  '"JETA COURTIÈRE fee shall be $0.02/gallon\nat IATA benchmark pricing of $200/bbl or below.\nFor every $25/bbl increase above $200/bbl,\nJETA COURTIÈRE fee increases by $0.005/gallon."';

const JETA_IATA_FEE_ESCALATION_EXAMPLES: { benchmark: string; fee: string }[] = [
  { benchmark: '$250/bbl', fee: '$0.03/gallon' },
  { benchmark: '$300/bbl', fee: '$0.04/gallon' },
  { benchmark: '$350/bbl', fee: '$0.05/gallon' },
];

/** Long-form agreement template — two consecutive weeks above/below $25/bbl bands; symmetric fee reductions. */
const JETA_FUEL_PRICE_ESCALATION_CLAUSE_FULL = `FUEL PRICE ESCALATION CLAUSE

Base JETA COURTIÈRE fee of $[X.XX] per gallon is established at an IATA jet fuel benchmark price of $[XXX.XX] per barrel (the "Base Benchmark") as of the date of this Agreement.

In the event the weekly IATA Jet Fuel Price Monitor benchmark exceeds the Base Benchmark by more than twenty-five dollars ($25.00) per barrel for two (2) consecutive weeks, the JETA COURTIÈRE per-gallon fee shall automatically increase as follows:

  $25.01 - $50.00 above Base:
  Fee increases by $0.005/gallon

  $50.01 - $75.00 above Base:
  Fee increases by $0.010/gallon

  $75.01 - $100.00 above Base:
  Fee increases by $0.015/gallon

  Above $100.00 above Base:
  Parties agree to renegotiate within 5 business days

Fee adjustments are calculated on the first business day following the second consecutive week of threshold breach and applied to all gallons delivered thereafter.

JETA COURTIÈRE shall provide written notice to all parties within 48 hours of any fee adjustment trigger.

Fee reductions shall apply symmetrically if the IATA benchmark falls more than $25.00/bbl below the Base Benchmark for two consecutive weeks.`;

/** Spot-oriented benchmark anchoring + 15% move right to adjust fee before delivery. */
const JETA_MARKET_PRICE_ADJUSTMENT_CLAUSE = `MARKET PRICE ADJUSTMENT

This fee agreement is established at current IATA benchmark pricing of $[XXX.XX]/bbl as of [DATE].

For spot transactions, JETA COURTIÈRE reserves the right to adjust the agreed fee if the IATA benchmark moves more than 15% from the date of this agreement to the date of fuel delivery. Adjusted fee will be communicated in writing prior to delivery confirmation.

Buyer/Seller acknowledges that jet fuel pricing is subject to global market conditions including geopolitical events, supply disruptions, and currency fluctuations beyond the control of any party.`;

/** Term deals over 90 days: annual 52-week review, force majeure renegotiation, optional war surcharge. */
const JETA_MULTI_YEAR_PRICE_ESCALATION_PROVISION = `MULTI-YEAR PRICE ESCALATION PROVISION

For term agreements exceeding ninety (90) days, the following escalation structure applies:

ANNUAL REVIEW
On each anniversary of this Agreement, JETA COURTIÈRE fee shall be reviewed against the trailing 52-week average IATA benchmark. If the annual average has increased more than 10% from the prior year average, JETA COURTIÈRE fee shall increase proportionally, not to exceed $0.02/gallon per annual adjustment.

FORCE MAJEURE PRICING EVENT
A Force Majeure Pricing Event is declared when:
  (a) Any major oil transit chokepoint (Strait of Hormuz, Suez Canal, Strait of Bosphorus) is officially closed or restricted by governmental or military action, OR
  (b) IATA benchmark exceeds the Base Benchmark by more than $75.00/bbl for any period exceeding 14 days

Upon declaration of a Force Majeure Pricing Event, all parties agree to renegotiate fee terms within 10 business days. JETA COURTIÈRE fee during renegotiation period shall default to the Version A escalation schedule above.

WAR SURCHARGE
In the event of declared armed conflict directly impacting petroleum production or transport in any OPEC member nation, JETA COURTIÈRE may apply a war surcharge not to exceed $0.02/gallon for the duration of the conflict impact period, with 5 business days written notice to all parties.`;

/** Hormuz stress scenario — ties Dashboard banner, deal monitoring, AI notices, and clause economics. */
const JETA_HORMUZ_SCENARIO_STEPS: { line: string; sub?: string }[] = [
  { line: 'War breaks out near Hormuz' },
  {
    line: 'Dee updates NEXUS JETA_MarketData',
    sub: 'hormuz_status = Restricted · geopolitical_risk_level = High · supply_disruption_alert = checked',
  },
  { line: 'Dashboard immediately shows ORANGE alert banner' },
  { line: 'NEXUS checks all active deals against escalation thresholds' },
  { line: 'Deals above threshold are flagged' },
  {
    line: 'Dee clicks “Send Counterparty Notices”',
    sub: 'AI drafts professional notice letters for buyers (sellers via your CRM if not in NEXUS)',
  },
  {
    line: 'Fee adjustments follow the clause already in each executed agreement',
    sub: 'Review & send — NEXUS does not auto-bill; increases are contractual',
  },
  {
    line: 'JETA COURTIÈRE earns more while competitors scramble',
    sub: 'Escalation + spot premia when you have supply access',
  },
];

const JETA_BROKER_VALUE_WAR_LINES = 'Finding ANY supply\nat ANY reasonable price';

const JETA_BROKER_VALUE_CERTAINTY =
  'Buyers will pay more for\ncertainty of supply than\nfor competitive pricing';

const JETA_VOLATILITY_BAD_FOR = [
  'Airlines and FBOs paying the bill',
  'Long-term fixed contracts without escalation clauses',
  "Brokers who don't adapt their fee structure",
];

const JETA_VOLATILITY_GOOD_FOR = [
  'Brokers with supply diversity access',
  'Brokers with escalation clauses built in',
  'Brokers who can find supply when normal channels are disrupted',
  'SAF pipeline owners',
];

const JETA_NEXUS_POSITIONING_LINES = [
  'Price escalation clauses in every agreement',
  'Supply diversity across all 50 states + Canada',
  'SAF pipeline as hedge against oil volatility',
  'Real-time market monitoring on dashboard',
  'Geopolitical risk flagging in system',
];

/** Illustrative Buyer Pipeline row — how NEXUS ranks and surfaces a high-value prospect. */
const JETA_NEXUS_PROSPECT_SURFACE_EXAMPLE: { label: string; value: string }[] = [
  { label: 'Priority score', value: '87 — HIGH VALUE' },
  { label: 'Company', value: 'Midwest Charter Air' },
  { label: 'Location', value: 'Pontiac, MI (KPTK)' },
  { label: 'Based aircraft', value: '12 jets' },
  { label: 'Supplier status', value: 'Open (no branded program)' },
  { label: 'Contact', value: 'Director of Operations' },
  { label: 'Email', value: 'On file from FAA database' },
  { label: 'Touch 1', value: 'Due today' },
];

/** Touch 1 template paired with the Midwest / KPTK prospect example above. */
const JETA_TOUCH1_EMAIL_EXAMPLE_SUBJECT = 'Competitive Jet-A Sourcing — Pontiac Operations';

const JETA_TOUCH1_EMAIL_EXAMPLE_BODY = `Mr. [Name],

JETA COURTIÈRE sources competitive Jet-A 
pricing for charter operators across Michigan 
and the Midwest. Given your operation at KPTK 
I'd like to understand your current fuel 
program and explore whether there's a fit.

Are you open to a 15-minute conversation 
this week?

Dee Davis
JETA COURTIÈRE | DEE DAVIS INC
jeta@deedavis.biz
EDWOSB · WBE · MBE`;

const JETA_VOLATILITY_BROKER_OPPORTUNITY: string[] = [
  `Higher prices = more urgency to find\ncompetitive supply\n\nBuyers who can't afford spot market\nprices desperately need brokers\nwho can find better deals`,
  `Price volatility = more frequent\nbuying decisions\nInstead of annual contracts,\nbuyers shop quarterly or monthly\nMore opportunities for brokers`,
  `Supply chain disruption =\nregional supply gaps\nTerminals in some areas run low\nBuyers need alternative sourcing\nThat's exactly what you do`,
];

function JetaChokepointCard({ cp }: { cp: JetaChokepoint }) {
  return (
    <div className="rounded-lg border border-amber-700/30 bg-black/20 px-3 py-2.5">
      <p className="text-[10px] font-bold tracking-wide text-orange-300/95">{cp.title}</p>
      <div className="mt-2 space-y-1.5">
        {cp.rows.map((row, ri) => (
          <div
            key={`${cp.id}-row-${ri}`}
            className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5 text-[11px] text-amber-100/95"
          >
            <span className="text-amber-200/85">{row.label}</span>
            <span
              className={`max-w-[15rem] text-right font-mono text-[11px] leading-snug text-amber-50 ${
                row.value.includes('\n') ? 'whitespace-pre-line' : ''
              }`}
            >
              {row.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function JetaPriceRiskStructureCard({ block }: { block: JetaPriceRiskStructure }) {
  return (
    <div className="rounded-lg border border-amber-700/30 bg-black/20 px-3 py-2.5">
      <p className="text-[10px] font-bold tracking-wide text-orange-300/95">{block.title}</p>
      <ul className="mt-2 list-disc space-y-1 pl-4 text-[11px] leading-snug text-amber-100/90 marker:text-amber-500/65">
        {block.bullets.map((b, i) => (
          <li key={`${block.id}-b-${i}`}>{b}</li>
        ))}
      </ul>
    </div>
  );
}

const JETA_PRICE_DRIVERS_UP = [
  'Crude oil rises',
  'Geopolitical tension (Middle East, Russia)',
  'Refinery outages',
  'Hurricane season (Gulf Coast = PADD 3)',
  'High travel demand (summer, holidays)',
];

const JETA_PRICE_DRIVERS_DOWN = [
  'Crude falls',
  'Demand drops (recessions, pandemics)',
  'Refinery capacity increases',
  'Strong US dollar',
];

/** Geopolitical shock → pass-through to jet; $/gal fee unchanged but notional deal size moves. */
const JETA_GEO_SHOCK_CHAIN_BEFORE_PAYERS = [
  'War breaks out near oil region',
  'Crude oil supply threatened',
  'Crude price spikes',
  'Refinery input costs rise',
  'Jet fuel price spikes',
];

const JETA_GEO_SHOCK_PAYERS = 'Airlines, FBOs, operators\npay more per gallon';

const JETA_WAR_PREMIUM_CONFLICTS = 'Middle East (ongoing)\nRussia-Ukraine (ongoing)';
const JETA_WAR_PREMIUM_CURRENT_PRICE = '$209/bbl — already\nelevated vs historical norm';

type JetaFeeTier = {
  id: string;
  title: string;
  tagline: string;
  volume: string;
  fee: string;
  whyLabel: string;
  whyLines: string[];
};

type JetaFeeLens = {
  id: string;
  n: number;
  question: string;
  bullets: string[];
  callout?: string;
};

/** Questions to size fee before quoting (urgency, supply exclusivity, broker chain). */
type JetaYearOnePhase = {
  id: string;
  period: string;
  bullets: string[];
  income?: string;
};

/** Illustrative first-year ramp — not a forecast guarantee. */
const JETA_YEAR_ONE_PHASES: JetaYearOnePhase[] = [
  {
    id: 'm1-2',
    period: 'MONTH 1-2',
    bullets: ['Learning the process', 'Building pipeline in NEXUS', 'Making first outreach contacts'],
    income: 'Income: $0 (investment phase)',
  },
  {
    id: 'm3',
    period: 'MONTH 3',
    bullets: ['First deal closes — small FBO', '30,000 gal x $0.03 = $900/month'],
    income: 'Income: $900',
  },
  {
    id: 'm4-5',
    period: 'MONTH 4-5',
    bullets: ['Two more small FBOs close', '90,000 gal x $0.03 = $2,700/month'],
    income: 'Income: $2,700',
  },
  {
    id: 'm6',
    period: 'MONTH 6',
    bullets: [
      'First term contract — charter operator',
      '150,000 gal x $0.02 = $3,000/month',
      'Running total: 4 deals',
    ],
    income: 'Income: $5,700/month',
  },
  {
    id: 'm8',
    period: 'MONTH 8',
    bullets: [
      'First municipal RFP win',
      '500,000 gal/year = 41,667 gal/month',
      'At $0.03/gal = $1,250/month guaranteed',
    ],
    income: 'Income: $6,950/month',
  },
  {
    id: 'm10-12',
    period: 'MONTH 10-12',
    bullets: ['Pipeline mature, outreach automated', '8-10 active deals running'],
    income: 'Income: $12,000 - $18,000/month',
  },
  {
    id: 'y1-end',
    period: 'END OF YEAR 1',
    bullets: [],
    income: 'Annual total: approximately $120,000 - $180,000',
  },
];

type JetaMultiYearLine = { id: string; title: string; bullets: string[] };

const JETA_MANUAL_BROKER_ADMIN_TASKS = [
  'Writing emails manually',
  'Generating documents manually',
  'Tracking follow-ups in spreadsheets',
  'Chasing signatures manually',
  'Monitoring RFPs manually',
];

const JETA_NEXUS_AUTOMATIONS = [
  'All outreach sequences',
  'All document generation',
  'All follow-up tracking',
  'All RFP monitoring',
  'All fraud detection',
  'All pipeline management',
];

const JETA_STARTUP_COST_LINES: { label: string; value: string }[] = [
  { label: 'DBA Filing (Oakland County)', value: '$10' },
  { label: 'SAM.gov 425120 addition', value: '$0 (free)' },
  { label: 'Email setup jeta@deedavis.biz', value: '$0 (existing domain)' },
  { label: 'Airtable (existing DDI plan)', value: '$0 (add tables)' },
  { label: 'NEXUS development (Cursor)', value: 'Your time' },
  { label: 'FAA database download', value: '$0 (free)' },
  { label: 'NAV CANADA database', value: '$0 (free)' },
  { label: 'IATA tools', value: '$0 (free)' },
  { label: 'ICC Publication 769 E (NCNDA)', value: '~$150' },
  { label: 'Business cards / one-pager', value: '~$100' },
];

const JETA_GROWTH_TRAJECTORY: { year: string; deals: number; monthly: string; annual: string }[] = [
  { year: 'Year 1', deals: 15, monthly: '$25,000', annual: '$300,000' },
  { year: 'Year 2', deals: 50, monthly: '$75,000', annual: '$900,000' },
  { year: 'Year 3', deals: 100, monthly: '$160,000', annual: '$1,920,000' },
];

const JETA_MULTI_YEAR_ROADMAP: JetaMultiYearLine[] = [
  {
    id: 'road-y1',
    title: 'Year 1',
    bullets: ['Build conventional pipeline, learn the process'],
  },
  {
    id: 'road-y2',
    title: 'Year 2',
    bullets: ['Add SAF track in NEXUS, register on IATA SAF Matchmaker'],
  },
  {
    id: 'road-y3',
    title: 'Year 3',
    bullets: [
      'Convert 20% of pipeline to SAF deals',
      '20% SAF at 4x fee = same revenue as 80% conventional',
    ],
  },
];

const JETA_FEE_LENSES: JetaFeeLens[] = [
  {
    id: 'urgency',
    n: 1,
    question: 'How urgent is the buyer?',
    bullets: ['Urgent = charge more', 'Planning ahead = standard rate'],
  },
  {
    id: 'supply',
    n: 2,
    question: 'How locked in is the supply?',
    bullets: ['Exclusive supply = charge more', 'Competitive market = standard rate'],
  },
  {
    id: 'chain',
    n: 3,
    question: 'How many brokers are in the chain?',
    bullets: ['Just you = keep full fee', 'Multiple brokers = split fee via IMFPA'],
    callout: 'Never let the chain eat your margin below $0.01/gal.',
  },
];

const JETA_FEE_TIERS: JetaFeeTier[] = [
  {
    id: 'spot',
    title: 'SPOT DEALS',
    tagline: 'One-time, urgent, small volume',
    volume: 'Under 100,000 gallons',
    fee: '$0.03 – $0.08/gallon',
    whyLabel: 'Why higher',
    whyLines: ['Urgency premium, less competition,', 'buyer needs fuel fast'],
  },
  {
    id: 'term',
    title: 'TERM DEALS',
    tagline: 'Recurring, contracted volume',
    volume: '100,000 – 1,000,000 gal/month',
    fee: '$0.015 – $0.03/gallon',
    whyLabel: 'Why lower',
    whyLines: ['Volume makes up for thinner margin,', 'predictable recurring income'],
  },
  {
    id: 'large',
    title: 'LARGE VOLUME',
    tagline: 'Airlines, major cargo',
    volume: '1,000,000+ gal/month',
    fee: '$0.005 – $0.015/gallon',
    whyLabel: 'Why lower',
    whyLines: ['These buyers have leverage,', 'but volume is enormous'],
  },
  {
    id: 'municipal',
    title: 'MUNICIPAL RFP',
    tagline: 'Government contract',
    volume: 'Varies — 50K to 2M gal/year',
    fee: '$0.02 – $0.05/gallon',
    whyLabel: 'Why solid',
    whyLines: ['Fixed term, predictable,', 'diversity certifications help you win'],
  },
];

function JetaMultiYearBlock({ row }: { row: JetaMultiYearLine }) {
  return (
    <div className="border-t border-amber-700/30 pt-3 first:border-t-0 first:pt-0">
      <p className="text-[10px] font-bold uppercase tracking-wide text-orange-300/95">{row.title}</p>
      <ul className="mt-2 list-disc space-y-1 pl-4 text-[11px] leading-snug text-amber-100/90 marker:text-amber-500/70">
        {row.bullets.map((b, i) => (
          <li key={`${row.id}-b-${i}`}>{b}</li>
        ))}
      </ul>
    </div>
  );
}

function JetaYearOnePhaseBlock({ phase }: { phase: JetaYearOnePhase }) {
  return (
    <div className="border-t border-amber-700/30 pt-3 first:border-t-0 first:pt-0">
      <p className="text-[10px] font-bold uppercase tracking-wide text-orange-300/95">{phase.period}</p>
      {phase.bullets.length > 0 ? (
        <ul className="mt-2 list-disc space-y-1 pl-4 text-[11px] leading-snug text-amber-100/90 marker:text-amber-500/70">
          {phase.bullets.map((b, i) => (
            <li key={`${phase.id}-b-${i}`}>{b}</li>
          ))}
        </ul>
      ) : null}
      {phase.income ? (
        <p className="mt-2 font-mono text-[11px] text-amber-200/95">{phase.income}</p>
      ) : null}
    </div>
  );
}

function JetaExampleSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border-t border-amber-700/30 pt-3 first:border-t-0 first:pt-0">
      <p className="text-[10px] font-bold uppercase tracking-wide text-orange-300/95">{title}</p>
      <div className="mt-2 space-y-1.5">{children}</div>
    </div>
  );
}

function JetaFeeLensCard({ lens }: { lens: JetaFeeLens }) {
  return (
    <div className="rounded-md border border-amber-700/25 bg-black/15 px-3 py-2.5">
      <p className="text-[11px] font-semibold text-amber-200/95">
        <span className="mr-1.5 font-mono text-orange-300/90">{lens.n}.</span>
        {lens.question}
      </p>
      <ul className="mt-2 list-none space-y-1.5 text-[11px] text-amber-100/90">
        {lens.bullets.map((b, i) => (
          <li key={`${lens.id}-b-${i}`} className="flex gap-2 pl-0">
            <span className="text-amber-500/70" aria-hidden>
              •
            </span>
            <span>{b}</span>
          </li>
        ))}
      </ul>
      {lens.callout ? (
        <p className="mt-2 border-t border-amber-700/30 pt-2 text-[11px] font-medium text-amber-200/95">
          {lens.callout}
        </p>
      ) : null}
    </div>
  );
}

function JetaFeeTierCard({ tier }: { tier: JetaFeeTier }) {
  return (
    <div className="rounded-md border border-amber-700/30 bg-black/20 px-3 py-2.5">
      <p className="text-[10px] font-bold tracking-wide text-orange-300/95">{tier.title}</p>
      <p className="mt-0.5 text-[10px] text-amber-400/80">{tier.tagline}</p>
      <div className="mt-2 space-y-1 text-[11px] text-amber-100/95">
        <div className="flex flex-wrap gap-x-2 gap-y-0.5">
          <span className="text-amber-300/80">Volume:</span>
          <span className="font-mono text-amber-50">{tier.volume}</span>
        </div>
        <div className="flex flex-wrap gap-x-2 gap-y-0.5">
          <span className="text-amber-300/80">Your fee:</span>
          <span className="font-mono text-amber-200/95">{tier.fee}</span>
        </div>
        <div className="pt-1">
          <span className="text-amber-300/85">{tier.whyLabel}:</span>
          {tier.whyLines.map((line, i) => (
            <span key={`${tier.id}-why-${i}`} className="block pl-0 text-amber-100/90">
              {line}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

const JETASystem: React.FC<JETASystemProps> = ({ onBackToNexus: _onBackToNexus, activeTab, setActiveTab }) => {
  const [buyerPipelineImportFilter, setBuyerPipelineImportFilter] = useState<PipelineImportFilter | null>(null);
  const [buyerPipelineRefreshKey, setBuyerPipelineRefreshKey] = useState(0);

  return (
    <div className="relative">
      {/* Module identity — above tab bar (navigation: global Header) */}
      <div className="border-b border-amber-900/40 bg-gradient-to-r from-amber-950/80 via-gray-900 to-amber-950/80">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div>
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-amber-400 to-orange-400">
              JETA COURTIÈRE
            </h2>
            <p className="mt-1 text-sm font-medium text-amber-200/90">Aviation Fuel Brokerage</p>
            <p className="mt-1 text-xs text-amber-300/75">
              Fraud detection & deal integrity — counterparty scoring, terminology blacklist (e.g. JP54), ICC 769 E–aligned NCNDA
              workflow, stage gates. Buyer Pipeline auto-ranks prospects by{' '}
              <span className="text-amber-200/90">priority score (0–130)</span> from based aircraft, supplier status, geography
              (Michigan home base), Gulf supply proximity (PADD 3), and email. Deal Manager &amp; Buyer Pipeline:{' '}
              <span className="text-amber-200/90">All / Conventional / SAF</span> fuel filters. ICAO supplier lookup →{' '}
              <code className="text-amber-200/80">JETA_SupplierDirectory</code>. API:{' '}
              <code className="text-amber-200/80">/jeta/fraud-log</code>, <code className="text-amber-200/80">/jeta/import-log</code>,{' '}
              <code className="text-amber-200/80">/jeta/events</code>.
            </p>
            <p className="mt-2 text-xs uppercase tracking-widest text-gray-500">Division of DEE DAVIS INC</p>

            <div className="mt-4 flex flex-col gap-4 lg:flex-row lg:items-stretch lg:gap-6">
              <div
                className="max-w-xl flex-1 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
                role="region"
                aria-label="Jet fuel price stack from crude to buyer"
              >
                <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">Price stack (wholesale chain)</p>
                <div className="mt-2 font-mono text-[11px] leading-6 text-amber-100/95">
                  {JETA_PRICE_STACK_LINES.map((line, i) => (
                    <div key={line}>
                      {i > 0 && <div className="text-center text-amber-500/80 select-none">↓</div>}
                      <div>{line}</div>
                    </div>
                  ))}
                  <div className="mt-2 border-t border-amber-700/30 pt-2 text-amber-200/95 italic">
                    Your fee sits inside this final margin.
                  </div>
                </div>
              </div>

              <div
                className="max-w-xl flex-1 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
                role="region"
                aria-label="Crude, IATA benchmark, and FBO price reference"
              >
                <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">Market reference (illustrative)</p>
                <div className="mt-3 space-y-2">
                  <MarketRefRow label="Crude oil (Brent)" value="~$75/bbl" />
                  <MarketRefRow
                    label="Jet premium over crude (refining + margin)"
                    value="~$25–35/bbl"
                  />
                  <div className="my-2 border-t border-amber-600/40" />
                  <MarketRefRow label="IATA benchmark (example day)" value="$209/bbl" />
                  <MarketRefRow label="÷ 42 gal per barrel → wholesale" value="$4.98/gal" />
                  <div className="my-2 border-t border-amber-600/40" />
                  <MarketRefRow label="FBO pays (marketer / terminal)" value="$5.20 – $5.80/gal" />
                  <MarketRefRow label="FBO charges pilots (retail rack)" value="$6.00 – $9.00/gal" />
                </div>
                <p className="mt-3 text-[10px] text-amber-400/75">Retail rack varies by location and contract.</p>
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-cyan-800/40 bg-gradient-to-br from-cyan-950/30 to-black/30 px-4 py-3 ring-1 ring-cyan-900/25"
              role="region"
              aria-label="Example prospect surfaced by NEXUS Buyer Pipeline priority scoring"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-cyan-300/90">
                NEXUS surfaces a prospect (example)
              </p>
              <div className="mt-3 space-y-1.5">
                {JETA_NEXUS_PROSPECT_SURFACE_EXAMPLE.map((row) => (
                  <MarketRefRow key={row.label} label={row.label} value={row.value} />
                ))}
              </div>
              <p className="mt-3 text-[10px] text-cyan-400/70">
                Scores and touch due dates come from <span className="font-mono text-cyan-200/80">JETA_Buyers</span> + outreach
                rules — open Buyer Pipeline to work the row.
              </p>
            </div>

            <JetaTouch1EmailExampleCard />

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="Factors that push jet fuel prices up or down"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">What moves jet prices</p>
              <div className="mt-3 grid gap-4 sm:grid-cols-2">
                <div className="rounded-md border-l-2 border-emerald-500/55 bg-emerald-950/20 pl-3 pr-1 py-1">
                  <p className="text-[11px] font-semibold text-emerald-200/95">UP when</p>
                  <ul className="mt-2 list-disc space-y-1.5 pl-4 text-[11px] leading-snug text-amber-100/90 marker:text-emerald-500/80">
                    {JETA_PRICE_DRIVERS_UP.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
                <div className="rounded-md border-l-2 border-sky-500/50 bg-slate-950/30 pl-3 pr-1 py-1">
                  <p className="text-[11px] font-semibold text-sky-200/95">DOWN when</p>
                  <ul className="mt-2 list-disc space-y-1.5 pl-4 text-[11px] leading-snug text-amber-100/90 marker:text-sky-500/70">
                    {JETA_PRICE_DRIVERS_DOWN.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-rose-900/35 bg-rose-950/15 px-4 py-3"
              role="region"
              aria-label="How regional conflict passes through to jet prices and deal gross value"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-rose-300/90">
                Shock chain (geopolitical → jet)
              </p>
              <div className="mt-2 font-mono text-[11px] leading-6 text-amber-100/95">
                {JETA_GEO_SHOCK_CHAIN_BEFORE_PAYERS.map((line, i) => (
                  <div key={line}>
                    {i > 0 && <div className="text-center text-rose-500/75 select-none">↓</div>}
                    <div>{line}</div>
                  </div>
                ))}
                <div className="text-center text-rose-500/75 select-none">↓</div>
                <div className="whitespace-pre-line text-center">{JETA_GEO_SHOCK_PAYERS}</div>
                <div className="mt-2 border-t border-rose-800/40 pt-2 text-center italic text-amber-200/95">
                  Your fee stays the same per gallon
                </div>
                <div className="mt-1 text-center font-semibold text-orange-200/95">BUT the gross deal value explodes</div>
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-rose-900/30 bg-black/20 px-4 py-3"
              role="region"
              aria-label="March 2022 era crude and jet fuel spike reference"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-rose-300/85">
                Historical parallel — crude spike (2022 reference)
              </p>
              <div className="mt-3 space-y-1.5">
                <MarketRefRow label="Pre-war crude" value="$75/bbl" />
                <MarketRefRow label="Peak crude" value="$139/bbl (March 2022)" />
                <MarketRefRow label="Spike" value="+85% in weeks" />
                <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5 text-[11px] text-amber-100/95">
                  <span className="text-amber-200/85">Jet fuel peak</span>
                  <span className="max-w-[14rem] text-right font-mono text-[11px] leading-snug text-amber-50 whitespace-pre-line">
                    {'$7.50 - $8.00/gallon\nvs $2.50 pre-war'}
                  </span>
                </div>
                <MarketRefRow label="Duration" value="Elevated 18+ months" />
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-800/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="Active conflicts and built-in war premium versus historical crude range"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Current backdrop — war premium (illustrative)
              </p>
              <div className="mt-3 space-y-2">
                <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5 text-[11px] text-amber-100/95">
                  <span className="text-amber-200/85">Active conflicts</span>
                  <span className="max-w-[16rem] text-right font-mono text-[11px] leading-snug text-amber-50 whitespace-pre-line">
                    {JETA_WAR_PREMIUM_CONFLICTS}
                  </span>
                </div>
                <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5 text-[11px] text-amber-100/95">
                  <span className="text-amber-200/85">Current price</span>
                  <span className="max-w-[16rem] text-right font-mono text-[11px] leading-snug text-amber-50 whitespace-pre-line">
                    {JETA_WAR_PREMIUM_CURRENT_PRICE}
                  </span>
                </div>
                <MarketRefRow label="Pre-conflict historical avg" value="$140–160/bbl" />
                <MarketRefRow label="Current premium" value="~$50–70/bbl war risk built in" />
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="Global oil and trade chokepoints reference"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Global chokepoints (reference)
              </p>
              <div className="mt-3 grid gap-3 sm:grid-cols-2">
                {JETA_CHOKEPOINTS.map((cp) => (
                  <JetaChokepointCard key={cp.id} cp={cp} />
                ))}
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-orange-800/40 bg-orange-950/15 px-4 py-3"
              role="region"
              aria-label="Operational flow when Hormuz is restricted and market intel goes orange"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-orange-300/90">
                Live ops loop — Hormuz scenario (NEXUS Dashboard)
              </p>
              <p className="mt-1 text-[10px] text-orange-200/70">
                From market data → alert banner → deal monitoring → AI counterparty notices → clause-aligned economics.
              </p>
              <div className="mt-3 space-y-0 font-mono text-[11px] leading-relaxed text-amber-100/95">
                {JETA_HORMUZ_SCENARIO_STEPS.map((step, i) => (
                  <div key={step.line}>
                    {i > 0 && <div className="py-1 text-center text-orange-500/80 select-none">↓</div>}
                    <div className="rounded border border-orange-900/35 bg-black/25 px-2 py-1.5">
                      <span className="text-orange-200/90">{step.line}</span>
                      {step.sub ? (
                        <p className="mt-1 text-[10px] leading-snug text-amber-100/75">{step.sub}</p>
                      ) : null}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-800/30 bg-amber-950/15 px-4 py-3"
              role="region"
              aria-label="Effects of sustained high fuel prices on buyers and broker entry"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                When prices stay high (second-order effects)
              </p>
              <ul className="mt-3 list-disc space-y-1.5 pl-5 text-[11px] leading-snug text-amber-100/90 marker:text-amber-500/70">
                {JETA_SUSTAINED_HIGH_PRICE_EFFECTS.map((line, i) => (
                  <li key={`high-price-${i}`}>{line}</li>
                ))}
              </ul>
              <p className="mt-3 border-l-2 border-amber-600/50 pl-3 font-mono text-[11px] leading-snug text-amber-100/95 whitespace-pre-line">
                {JETA_SUSTAINED_HIGH_PRICE_LOCK_IN}
              </p>
            </div>

            <div
              className="mt-4 rounded-lg border border-emerald-900/35 bg-emerald-950/10 px-4 py-3"
              role="region"
              aria-label="Why price stress and volatility can increase broker opportunity"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-emerald-400/90">
                Counterweight — same environment, broker upside
              </p>
              <div className="mt-3 space-y-4">
                {JETA_VOLATILITY_BROKER_OPPORTUNITY.map((chunk, i) => (
                  <p
                    key={`vol-opp-${i}`}
                    className={`font-mono text-[11px] leading-relaxed text-amber-100/95 whitespace-pre-line ${
                      i > 0 ? 'border-t border-emerald-800/30 pt-4' : ''
                    }`}
                  >
                    {chunk}
                  </p>
                ))}
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="Example broker fee versus deal gross value"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">Broker economics (example)</p>
              <div className="mt-3 grid gap-4 md:grid-cols-2 md:gap-8">
                <div className="space-y-2">
                  <p className="text-[11px] leading-relaxed text-amber-100/95">
                    Seller sells <span className="font-mono text-amber-50">500,000</span> gallons to buyer
                    <br />
                    At <span className="font-mono text-amber-50">$5.40/gallon</span>
                  </p>
                  <MarketRefRow label="Deal gross value" value="$2,700,000" />
                </div>
                <div className="space-y-2 border-t border-amber-700/25 pt-3 md:border-t-0 md:border-l md:pl-8 md:pt-0">
                  <MarketRefRow label="Your fee" value="$0.02/gallon" />
                  <MarketRefRow label="Your take" value="$10,000" />
                </div>
              </div>
              <div className="mt-4 border-t border-amber-600/35 pt-3 text-[11px] leading-relaxed text-amber-100/95">
                <p>You never saw $2.7M.</p>
                <p className="mt-1">
                  You collected <span className="font-mono font-semibold text-amber-200">$10,000</span> for making the introduction and
                  managing the paperwork.
                </p>
              </div>
            </div>

            <div className="mt-4 grid gap-4 md:grid-cols-2 md:items-stretch">
              <div
                className="rounded-lg border border-amber-800/40 bg-amber-950/20 px-4 py-3"
                role="region"
                aria-label="Typical manual broker time allocation"
              >
                <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">Manual broker (baseline)</p>
                <p className="mt-2 text-[11px] leading-relaxed text-amber-100/95">Manages 5–10 deals at once.</p>
                <p className="mt-3 text-[11px] font-semibold text-amber-200/95">Spends 60% of time on:</p>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-[11px] leading-snug text-amber-100/90 marker:text-amber-500/70">
                  {JETA_MANUAL_BROKER_ADMIN_TASKS.map((t, i) => (
                    <li key={`manual-task-${i}`}>{t}</li>
                  ))}
                </ul>
                <p className="mt-3 border-t border-amber-700/30 pt-3 text-[11px] font-medium text-amber-200/95">
                  40% of time actually closing deals
                </p>
              </div>
              <div
                className="rounded-lg border border-orange-600/45 bg-gradient-to-br from-orange-950/35 to-amber-950/25 px-4 py-3"
                role="region"
                aria-label="NEXUS-enabled broker workload and automation"
              >
                <p className="text-[10px] font-semibold uppercase tracking-wider text-orange-300/95">NEXUS-enabled broker (you)</p>
                <p className="mt-2 text-[11px] leading-relaxed text-amber-100/95">Manages 50–100 deals at once.</p>
                <p className="mt-3 text-[11px] font-semibold text-amber-200/95">Automates:</p>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-[11px] leading-snug text-amber-100/90 marker:text-orange-400/70">
                  {JETA_NEXUS_AUTOMATIONS.map((t, i) => (
                    <li key={`nexus-auto-${i}`}>{t}</li>
                  ))}
                </ul>
                <p className="mt-3 border-t border-orange-700/35 pt-3 text-[11px] font-medium text-amber-100/95">
                  You spend 90% of time on relationships and closes
                </p>
              </div>
            </div>

            <div className="mt-4">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Revenue at capacity (illustrative — same $/deal/month)
              </p>
              <div className="mt-3 grid gap-4 md:grid-cols-2 md:items-stretch">
                <div
                  className="rounded-lg border border-slate-600/45 bg-slate-950/40 px-4 py-3"
                  role="region"
                  aria-label="Revenue without NEXUS at capacity"
                >
                  <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400/95">Without NEXUS</p>
                  <div className="mt-3 space-y-1.5">
                    <MarketRefRow label="Capacity" value="10 deals" />
                    <MarketRefRow label="Avg monthly per deal" value="$2,000" />
                    <MarketRefRow label="Monthly" value="$20,000" />
                    <MarketRefRow label="Annual" value="$240,000" />
                  </div>
                </div>
                <div
                  className="rounded-lg border border-orange-600/45 bg-gradient-to-br from-orange-950/35 to-amber-950/25 px-4 py-3"
                  role="region"
                  aria-label="Revenue with NEXUS at capacity"
                >
                  <p className="text-[10px] font-bold uppercase tracking-wider text-orange-300/95">With NEXUS</p>
                  <div className="mt-3 space-y-1.5">
                    <MarketRefRow label="Capacity" value="75 deals" />
                    <MarketRefRow label="Avg monthly per deal" value="$2,000" />
                    <MarketRefRow label="Monthly" value="$150,000" />
                    <MarketRefRow label="Annual" value="$1,800,000" />
                  </div>
                </div>
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="JETA startup costs estimate"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">Startup costs</p>
              <div className="mt-3 space-y-1.5">
                {JETA_STARTUP_COST_LINES.map((row) => (
                  <MarketRefRow key={row.label} label={row.label} value={row.value} />
                ))}
              </div>
              <div className="my-3 border-t border-dashed border-amber-600/50" aria-hidden />
              <MarketRefRow label="Total hard cash to launch" value="~$260" />
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="JETA monthly overhead and break-even on first deal"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">Overhead &amp; break-even</p>
              <div className="mt-3 space-y-1.5">
                <MarketRefRow label="Monthly overhead added for JETA" value="~$0" />
                <p className="text-[10px] italic text-amber-400/80">(runs on existing DDI infrastructure)</p>
                <MarketRefRow label="First deal needed to break even" value="1 small FBO spot deal" />
                <p className="pt-1 font-mono text-[11px] text-amber-100/95">At $0.03/gallon x 10,000 gallons = $300</p>
                <p className="pt-2 text-[11px] font-medium text-amber-200/95">You&apos;re profitable on deal one.</p>
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="Typical fee ranges by deal type"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">Fee ranges by deal type (illustrative)</p>
              <div className="mt-3 grid gap-3 sm:grid-cols-2">
                {JETA_FEE_TIERS.map((tier) => (
                  <JetaFeeTierCard key={tier.id} tier={tier} />
                ))}
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="Questions to price your fee"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">Pricing your fee</p>
              <div className="mt-3 space-y-3">
                {JETA_FEE_LENSES.map((lens) => (
                  <JetaFeeLensCard key={lens.id} lens={lens} />
                ))}
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="Worked example: buyer savings spread and broker fee"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Spread economics (example — Michigan FBO)
              </p>
              <div className="mt-3 space-y-0">
                <JetaExampleSection title="Buyer">
                  <MarketRefRow label="Company" value="Small Michigan FBO" />
                  <MarketRefRow label="Volume" value="30,000 gallons/month" />
                  <MarketRefRow label="Current PPG" value="$5.60/gallon" />
                  <MarketRefRow label="Paying" value="$168,000/month for fuel" />
                </JetaExampleSection>
                <JetaExampleSection title="Your move">
                  <MarketRefRow label="Find a supply source at" value="$5.30/gallon" />
                  <MarketRefRow label="Offer buyer" value="$5.45/gallon" />
                  <MarketRefRow label="Buyer saves" value="$0.15/gallon vs current" />
                  <MarketRefRow label="Buyer saves" value="$4,500/month — they love you" />
                </JetaExampleSection>
                <JetaExampleSection title="Your fee structure">
                  <MarketRefRow label="Supply cost" value="$5.30/gallon (seller gets this)" />
                  <MarketRefRow label="Buyer pays" value="$5.45/gallon" />
                  <MarketRefRow label="Your gross" value="$0.15/gallon spread" />
                  <MarketRefRow label="Your fee" value="$0.03/gallon (agreed in fee agreement)" />
                  <MarketRefRow label="Seller margin" value="$0.12/gallon (their take)" />
                </JetaExampleSection>
                <JetaExampleSection title="Your monthly income from this deal">
                  <p className="text-[11px] font-mono text-amber-100/95">30,000 gallons x $0.03 = $900/month</p>
                </JetaExampleSection>
                <JetaExampleSection title="Annual from this one deal">
                  <p className="text-[11px] font-mono text-amber-200/95">$900 x 12 = $10,800/year</p>
                </JetaExampleSection>
              </div>
            </div>

            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <div
                className="rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
                role="region"
                aria-label="Regional airport term contract example"
              >
                <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                  Regional airport term (example)
                </p>
                <div className="mt-3 space-y-1.5">
                  <MarketRefRow label="Airport" value="Small regional — 2 runways" />
                  <MarketRefRow label="Annual volume" value="600,000 gallons Jet-A" />
                  <MarketRefRow label="Your fee" value="$0.025/gallon" />
                  <MarketRefRow label="Annual income" value="$15,000" />
                  <MarketRefRow label="Contract term" value="2 years" />
                  <MarketRefRow label="Total value" value="$30,000 guaranteed" />
                </div>
              </div>
              <div
                className="rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
                role="region"
                aria-label="County airport term contract example"
              >
                <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                  County airport term (example)
                </p>
                <div className="mt-3 space-y-1.5">
                  <MarketRefRow label="Airport" value="County airport — active FBO" />
                  <MarketRefRow label="Annual volume" value="1,500,000 gallons" />
                  <MarketRefRow label="Your fee" value="$0.02/gallon" />
                  <MarketRefRow label="Annual income" value="$30,000" />
                  <MarketRefRow label="Contract term" value="3 years" />
                  <MarketRefRow label="Total value" value="$90,000 guaranteed" />
                </div>
              </div>
            </div>

            <div className="mt-4">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Conventional Jet-A vs SAF (illustrative)
              </p>
              <p className="mt-1 text-[10px] text-amber-400/70">Same volume, same buyer — fee tier differs.</p>
              <div className="mt-3 grid gap-4 md:grid-cols-2">
                <div
                  className="rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
                  role="region"
                  aria-label="Conventional Jet-A fee example"
                >
                  <p className="text-[10px] font-bold uppercase tracking-wide text-orange-300/95">Conventional Jet-A</p>
                  <div className="mt-3 space-y-1.5">
                    <MarketRefRow label="Volume" value="500,000 gal/month" />
                    <MarketRefRow label="Your fee" value="$0.02/gallon" />
                    <MarketRefRow label="Monthly income" value="$10,000" />
                    <MarketRefRow label="Annual" value="$120,000" />
                  </div>
                </div>
                <div
                  className="rounded-lg border border-emerald-900/40 bg-emerald-950/15 px-4 py-3"
                  role="region"
                  aria-label="SAF fee example same volume"
                >
                  <p className="text-[10px] font-bold uppercase tracking-wide text-emerald-300/95">SAF (same volume, same buyer)</p>
                  <div className="mt-3 space-y-1.5">
                    <MarketRefRow label="Volume" value="500,000 gal/month" />
                    <MarketRefRow label="Your fee" value="$0.08/gallon" />
                    <MarketRefRow label="Monthly income" value="$40,000" />
                    <MarketRefRow label="Annual" value="$480,000" />
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-4">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Normal market vs war market (illustrative)
              </p>
              <p className="mt-1 text-[10px] text-amber-400/70">
                Same volume &amp; $0.02/gal fee — deal value moves with price; your cash take unchanged.
              </p>
              <div className="mt-3 grid gap-4 md:grid-cols-2">
                <div
                  className="rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
                  role="region"
                  aria-label="Normal market deal notional versus broker fee"
                >
                  <p className="text-[10px] font-bold uppercase tracking-wide text-orange-300/95">Normal market</p>
                  <div className="mt-3 space-y-1.5">
                    <MarketRefRow label="Volume" value="500,000 gal/month" />
                    <MarketRefRow label="Price/gallon" value="$4.98" />
                    <MarketRefRow label="Deal value" value="$2,490,000/month" />
                    <MarketRefRow label="Your fee $0.02" value="$10,000/month" />
                    <MarketRefRow label="Annual" value="$120,000" />
                  </div>
                </div>
                <div
                  className="rounded-lg border border-rose-900/40 bg-rose-950/15 px-4 py-3"
                  role="region"
                  aria-label="War market deal notional with 60 percent price spike"
                >
                  <p className="text-[10px] font-bold uppercase tracking-wide text-rose-300/95">
                    War market (price spikes 60%)
                  </p>
                  <div className="mt-3 space-y-1.5">
                    <MarketRefRow label="Volume" value="500,000 gal/month" />
                    <MarketRefRow label="Price/gallon" value="$7.97" />
                    <MarketRefRow label="Deal value" value="$3,985,000/month" />
                    <MarketRefRow label="Your fee $0.02" value="$10,000/month" />
                    <MarketRefRow label="Annual" value="$120,000" />
                  </div>
                </div>
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="Example IATA-linked fee escalation clause and stepped fees"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Fee escalation — IATA benchmark (example clause)
              </p>
              <p className="mt-2 text-[10px] text-amber-400/80">Standard language:</p>
              <blockquote className="mt-2 border-l-2 border-amber-600/55 pl-3 font-mono text-[11px] leading-relaxed text-amber-100/95 whitespace-pre-line">
                {JETA_IATA_FEE_ESCALATION_CLAUSE}
              </blockquote>
              <p className="mt-3 text-[10px] font-semibold uppercase tracking-wide text-amber-400/75">
                Stepped fee examples
              </p>
              <div className="mt-2 space-y-1.5">
                {JETA_IATA_FEE_ESCALATION_EXAMPLES.map((row) => (
                  <MarketRefRow key={row.benchmark} label={`At ${row.benchmark}`} value={`your fee = ${row.fee}`} />
                ))}
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/30 px-4 py-3"
              role="region"
              aria-label="Full fuel price escalation clause template for agreements"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Fuel price escalation clause — full template
              </p>
              <p className="mt-2 text-[10px] text-amber-400/75">
                Replace <span className="font-mono text-amber-200/90">$[X.XX]</span> with your base per-gallon fee and{' '}
                <span className="font-mono text-amber-200/90">$[XXX.XX]</span> with the IATA $/bbl Base Benchmark at signing.
              </p>
              <p className="mt-2 text-[10px] text-sky-300/85">
                <span className="font-semibold text-sky-200/90">PDF generator (Documents tab):</span> Fee Agreement PDFs
                auto-insert Version A / B / C from <span className="text-sky-100/90">Deal Type</span> &amp;{' '}
                <span className="text-sky-100/90">Term Length</span>, populate benchmark from latest{' '}
                <span className="font-mono text-sky-200/80">JETA_MarketData</span>, and store the clause version on{' '}
                <span className="font-mono text-sky-200/80">JETA_Documents</span>.
              </p>
              <blockquote className="mt-3 max-h-[min(28rem,55vh)] overflow-y-auto border-l-2 border-amber-600/50 pl-3 font-mono text-[11px] leading-relaxed text-amber-100/95 whitespace-pre-line">
                {JETA_FUEL_PRICE_ESCALATION_CLAUSE_FULL}
              </blockquote>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/30 px-4 py-3"
              role="region"
              aria-label="Market price adjustment clause for spot transactions"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Market price adjustment — template
              </p>
              <p className="mt-2 text-[10px] text-amber-400/75">
                Replace <span className="font-mono text-amber-200/90">$[XXX.XX]</span> with the IATA $/bbl at agreement and{' '}
                <span className="font-mono text-amber-200/90">[DATE]</span> with the effective date. Use for spot deals where
                benchmark may move materially before delivery.
              </p>
              <blockquote className="mt-3 border-l-2 border-amber-600/50 pl-3 font-mono text-[11px] leading-relaxed text-amber-100/95 whitespace-pre-line">
                {JETA_MARKET_PRICE_ADJUSTMENT_CLAUSE}
              </blockquote>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/30 px-4 py-3"
              role="region"
              aria-label="Multi-year price escalation provision for term agreements over ninety days"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Multi-year price escalation — template
              </p>
              <p className="mt-2 text-[10px] text-amber-400/75">
                For agreements over 90 days. Tie &quot;Version A escalation schedule&quot; to your{' '}
                <span className="font-semibold text-amber-200/85">Fuel price escalation clause</span> block above, or define
                Version A inline in the executed agreement.
              </p>
              <blockquote className="mt-3 max-h-[min(26rem,50vh)] overflow-y-auto border-l-2 border-amber-600/50 pl-3 font-mono text-[11px] leading-relaxed text-amber-100/95 whitespace-pre-line">
                {JETA_MULTI_YEAR_PRICE_ESCALATION_PROVISION}
              </blockquote>
            </div>

            <div
              className="mt-4 rounded-lg border border-rose-900/35 bg-rose-950/10 px-4 py-3"
              role="region"
              aria-label="Spot fee ranges in normal versus high-urgency war markets"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-rose-300/90">
                Spot urgency — fee bands (illustrative)
              </p>
              <div className="mt-3 space-y-1.5">
                <MarketRefRow label="Normal spot fee" value="$0.03 – $0.05/gallon" />
                <MarketRefRow label="War urgency fee" value="$0.08 – $0.15/gallon" />
                <MarketRefRow label="Buyer choice" value="Pay your premium or ground aircraft" />
              </div>
              <p className="mt-3 border-t border-rose-800/35 pt-3 text-center text-[11px] font-semibold text-amber-200/95">
                They pay.
              </p>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="Broker value proposition in normal versus stressed markets"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Broker value — normal vs stress market
              </p>
              <div className="mt-3 space-y-2">
                <MarketRefRow label="Normal market broker value" value="Competitive pricing" />
                <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5 text-[11px] text-amber-100/95">
                  <span className="text-amber-200/85">War market broker value</span>
                  <span className="max-w-[16rem] text-right font-mono text-[11px] leading-snug text-amber-50 whitespace-pre-line">
                    {JETA_BROKER_VALUE_WAR_LINES}
                  </span>
                </div>
                <p className="mt-3 border-t border-amber-700/35 pt-3 text-center font-mono text-[11px] leading-relaxed text-amber-100/95 whitespace-pre-line">
                  {JETA_BROKER_VALUE_CERTAINTY}
                </p>
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="Who loses and who wins when prices spike or supply tightens"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Volatility — bad vs good
              </p>
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                <div
                  className="rounded-lg border border-rose-900/40 bg-rose-950/10 px-3 py-2.5"
                  role="region"
                  aria-label="Parties hurt by fuel price volatility"
                >
                  <p className="text-[10px] font-bold uppercase tracking-wide text-rose-300/95">Bad for</p>
                  <ul className="mt-2 list-disc space-y-1 pl-4 text-[11px] leading-snug text-amber-100/90 marker:text-rose-500/60">
                    {JETA_VOLATILITY_BAD_FOR.map((line) => (
                      <li key={line}>{line}</li>
                    ))}
                  </ul>
                </div>
                <div
                  className="rounded-lg border border-emerald-900/40 bg-emerald-950/10 px-3 py-2.5"
                  role="region"
                  aria-label="Parties positioned to benefit from volatility"
                >
                  <p className="text-[10px] font-bold uppercase tracking-wide text-emerald-300/95">Good for</p>
                  <ul className="mt-2 list-disc space-y-1 pl-4 text-[11px] leading-snug text-amber-100/90 marker:text-emerald-500/55">
                    {JETA_VOLATILITY_GOOD_FOR.map((line) => (
                      <li key={line}>{line}</li>
                    ))}
                  </ul>
                </div>
              </div>
              <div
                className="mt-3 rounded-lg border border-orange-900/35 bg-black/20 px-3 py-2.5"
                role="region"
                aria-label="JETA COURTIÈRE positioning with NEXUS"
              >
                <p className="text-[10px] font-bold uppercase tracking-wide text-orange-300/95">
                  JETA COURTIÈRE with NEXUS
                </p>
                <ul className="mt-2 space-y-1.5 text-[11px] leading-snug text-amber-100/95">
                  {JETA_NEXUS_POSITIONING_LINES.map((line) => (
                    <li key={line} className="flex gap-2">
                      <span className="shrink-0 font-semibold text-emerald-400/95" aria-hidden>
                        ✓
                      </span>
                      <span>{line}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="Price risk and hedging structures for fuel buyers"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Price risk structures (reference)
              </p>
              <div className="mt-3 grid gap-3 sm:grid-cols-2">
                {JETA_PRICE_RISK_STRUCTURES.map((block) => (
                  <JetaPriceRiskStructureCard key={block.id} block={block} />
                ))}
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-emerald-900/35 bg-emerald-950/10 px-4 py-3"
              role="region"
              aria-label="Why SAF broker fees often run higher than conventional Jet-A"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-emerald-400/90">
                Why SAF fees trend higher
              </p>
              <dl className="mt-3 space-y-3 text-[11px] leading-snug text-amber-100/90">
                <div>
                  <dt className="font-semibold text-emerald-200/95">Supply is scarce</dt>
                  <dd className="mt-0.5 pl-0 text-amber-100/85">Few producers currently</dd>
                </div>
                <div>
                  <dt className="font-semibold text-emerald-200/95">Buyer urgency</dt>
                  <dd className="mt-0.5 pl-0 text-amber-100/85">Airlines have ESG commitments</dd>
                </div>
                <div>
                  <dt className="font-semibold text-emerald-200/95">Regulatory push</dt>
                  <dd className="mt-0.5 pl-0 text-amber-100/85">Government mandates increasing</dd>
                </div>
                <div>
                  <dt className="font-semibold text-emerald-200/95">Complexity premium</dt>
                  <dd className="mt-0.5 pl-0 text-amber-100/85">
                    Documentation heavier — brokers who know it get paid more
                  </dd>
                </div>
              </dl>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="Illustrative year one income ramp"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Year 1 ramp (illustrative — not a guarantee)
              </p>
              <div className="mt-3 space-y-0">
                {JETA_YEAR_ONE_PHASES.map((phase) => (
                  <JetaYearOnePhaseBlock key={phase.id} phase={phase} />
                ))}
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="Multi-year conventional and SAF roadmap"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Multi-year roadmap (strategy)
              </p>
              <div className="mt-3 space-y-0">
                {JETA_MULTI_YEAR_ROADMAP.map((row) => (
                  <JetaMultiYearBlock key={row.id} row={row} />
                ))}
              </div>
            </div>

            <div
              className="mt-4 rounded-lg border border-amber-700/35 bg-black/25 px-4 py-3"
              role="region"
              aria-label="Deals and income by year"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-400/90">
                Growth trajectory (illustrative)
              </p>
              <div className="mt-3 overflow-x-auto">
                <table className="w-full min-w-[280px] border-collapse text-left text-[11px] text-amber-100/95">
                  <caption className="sr-only">Deals, monthly and annual income by year</caption>
                  <thead>
                    <tr className="border-b border-amber-700/40 text-[10px] font-semibold uppercase tracking-wide text-amber-400/90">
                      <th scope="col" className="pb-2 pr-3 font-semibold">
                        Year
                      </th>
                      <th scope="col" className="pb-2 pr-3 text-right font-semibold">
                        Deals
                      </th>
                      <th scope="col" className="pb-2 pr-3 text-right font-semibold">
                        Monthly
                      </th>
                      <th scope="col" className="pb-2 text-right font-semibold">
                        Annual
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {JETA_GROWTH_TRAJECTORY.map((row) => (
                      <tr key={row.year} className="border-b border-amber-800/25 last:border-b-0">
                        <th scope="row" className="py-2 pr-3 font-medium text-amber-200/95">
                          {row.year}
                        </th>
                        <td className="py-2 pr-3 text-right font-mono tabular-nums text-amber-50">{row.deals}</td>
                        <td className="py-2 pr-3 text-right font-mono tabular-nums text-amber-50">{row.monthly}</td>
                        <td className="py-2 text-right font-mono tabular-nums text-amber-100/95">{row.annual}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System tabs — same pattern as GPSS / PRISM */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1 overflow-x-auto">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 text-sm font-semibold rounded-t-lg transition whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-amber-600 to-orange-700 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6">
        {activeTab === 'dashboard' && <DashboardTab setActiveTab={setActiveTab} />}
        {activeTab === 'buyer-pipeline' && (
          <div className="space-y-6">
            <JetaFaaImportPanel
              onImportSuccess={() => setBuyerPipelineRefreshKey((k) => k + 1)}
              onViewAllImported={() => setBuyerPipelineImportFilter('csv_imports')}
            />
            <BuyerPipelineTab
              pipelineImportFilter={buyerPipelineImportFilter}
              onClearPipelineImportFilter={() => setBuyerPipelineImportFilter(null)}
              refreshKey={buyerPipelineRefreshKey}
            />
          </div>
        )}
        {activeTab === 'deal-manager' && <DealManagerTab />}
        {activeTab === 'outreach-center' && <OutreachCenterTab />}
        {activeTab === 'documents' && <DocumentsTab />}
      </div>
    </div>
  );
};

export default JETASystem;
