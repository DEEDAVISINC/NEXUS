import React, { useMemo, useState } from 'react';
import './HideSnpRevenueModel.css';
import { ViewType } from '../../Header';
import {
  TARGET_FLOOR,
  DEFAULT_RATE_INPUTS,
  RateInputs,
  calcNegotiation,
  calcRiderBreakdown,
  calcSpreadTable,
  fmt,
  fmtD,
  fmtK,
  fmtM,
} from './hideSnpRevenueModelCore';

type TabId = 'riders' | 'spread' | 'floor' | 'negotiate';

interface Props {
  /** Inside DDCSS/PRISM — hide duplicate NEXUS chrome */
  embedded?: boolean;
  onNavigate?: (system: ViewType, initialTab?: string) => void;
}

const TABS: { id: TabId; label: string }[] = [
  { id: 'riders', label: '01  MCO Rider Breakdown' },
  { id: 'spread', label: '02  Spread Margin Model' },
  { id: 'floor', label: '03  $20 Floor Tracker' },
  { id: 'negotiate', label: '04  Negotiation Solver' },
];

function ToggleBtn({ on, label, onClick }: { on: boolean; label: string; onClick: () => void }) {
  return (
    <button type="button" className={`tb${on ? ' on' : ''}`} onClick={onClick}>
      {label}
    </button>
  );
}

function SliderRow({
  label,
  value,
  min,
  max,
  step,
  display,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  display: string;
  onChange: (v: number) => void;
}) {
  return (
    <div className="ctrl-row">
      <span className="ctrl-lbl">{label}</span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
      />
      <span className="ctrl-val">{display}</span>
    </div>
  );
}

function Metrics({ items }: { items: { ml: string; mv: string; ms: string }[] }) {
  return (
    <div className="summary-row" style={{ gridTemplateColumns: `repeat(${items.length}, 1fr)` }}>
      {items.map((d) => (
        <div key={d.ml} className="met">
          <div className="ml">{d.ml}</div>
          <div className="mv">{d.mv}</div>
          <div className="ms">{d.ms}</div>
        </div>
      ))}
    </div>
  );
}

const HideSnpRevenueModel: React.FC<Props> = ({ embedded = false, onNavigate }) => {
  const [tab, setTab] = useState<TabId>('riders');
  const [r1Scen, setR1Scen] = useState<'current' | 'expansion'>('current');
  const [r1Pct, setR1Pct] = useState<'both' | 'half' | 'one'>('both');
  const [r2Scen, setR2Scen] = useState<'current' | 'expansion'>('current');
  const [r2Pct, setR2Pct] = useState<'half' | 'one'>('half');
  const [r3Scen, setR3Scen] = useState<'current' | 'expansion'>('current');
  const [r3Pct, setR3Pct] = useState<'half' | 'one'>('half');
  const [rates, setRates] = useState<RateInputs>(DEFAULT_RATE_INPUTS);
  const [offeredSedan, setOfferedSedan] = useState(28);
  const [offeredWc, setOfferedWc] = useState(35);

  const patch = (p: Partial<RateInputs>) => setRates((r) => ({ ...r, ...p }));

  const timestamp = useMemo(
    () =>
      `Last updated: ${new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })} · ${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`,
    []
  );

  const riderData = useMemo(() => calcRiderBreakdown(r1Scen), [r1Scen]);
  const spreadData = useMemo(() => calcSpreadTable(r2Scen, r2Pct, rates), [r2Scen, r2Pct, rates]);
  const floorData = useMemo(() => calcSpreadTable(r3Scen, r3Pct, rates), [r3Scen, r3Pct, rates]);
  const neg = useMemo(() => calcNegotiation(rates, offeredSedan, offeredWc), [rates, offeredSedan, offeredWc]);

  const uCols = [5, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28];
  const sedRows = [20, 22, 24, 25, 26, 27, 28, 29, 30, 32, 34, 36, 38, 40, 42, 45];

  const rateControls = (
    <>
      <div className="ctrl-card">
        <div className="ctrl-title">MCO rates — what DDI collects</div>
        <SliderRow label="Sedan base rate" value={rates.sedanBase} min={20} max={45} step={1} display={`$${rates.sedanBase}`} onChange={(v) => patch({ sedanBase: v })} />
        <SliderRow label="Wheelchair base rate" value={rates.wcBase} min={25} max={60} step={1} display={`$${rates.wcBase}`} onChange={(v) => patch({ wcBase: v })} />
        <SliderRow label="Per-mile rate (both)" value={rates.mileRate} min={1} max={3.5} step={0.05} display={`$${rates.mileRate.toFixed(2)}`} onChange={(v) => patch({ mileRate: v })} />
        <SliderRow label="Avg trip miles" value={rates.avgMiles} min={3} max={20} step={1} display={`${rates.avgMiles} mi`} onChange={(v) => patch({ avgMiles: v })} />
        <SliderRow label="% wheelchair rides" value={rates.wcPct} min={0} max={60} step={5} display={`${rates.wcPct}%`} onChange={(v) => patch({ wcPct: v })} />
        {tab === 'floor' && (
          <SliderRow label="Rides per member/day" value={rates.ridesPerDay} min={2} max={7} step={0.5} display={rates.ridesPerDay.toFixed(1)} onChange={(v) => patch({ ridesPerDay: v })} />
        )}
      </div>
      <div className="ctrl-card">
        <div className="ctrl-title">Fulfillment cost — what DDI pays</div>
        <SliderRow label="Best case" value={rates.ulo} min={5} max={20} step={1} display={`$${rates.ulo}`} onChange={(v) => patch({ ulo: v })} />
        <SliderRow label="Planning / expected" value={rates.umid} min={5} max={28} step={1} display={`$${rates.umid}`} onChange={(v) => patch({ umid: v })} />
        <SliderRow label="Worst case" value={rates.uhi} min={10} max={30} step={1} display={`$${rates.uhi}`} onChange={(v) => patch({ uhi: v })} />
        {tab === 'spread' && (
          <SliderRow label="Rides per member/day" value={rates.ridesPerDay} min={2} max={7} step={0.5} display={rates.ridesPerDay.toFixed(1)} onChange={(v) => patch({ ridesPerDay: v })} />
        )}
      </div>
    </>
  );

  return (
    <div className={`hsrm-root${embedded ? ' hsrm-embedded' : ''}`}>
      {!embedded && (
        <div className="mod-header">
          <div className="mod-topbar">
            <div>
              NEXUS COMMAND CENTER &nbsp;·&nbsp; <span>DEE DAVIS INC.</span> &nbsp;·&nbsp; INTERNAL USE ONLY — CONFIDENTIAL
            </div>
            <div>{timestamp}</div>
          </div>
          <div className="mod-titlebar">
            <div className="mod-title-left">
              <div>
                <div className="mod-eyebrow">DDI NEMT TPA &nbsp;·&nbsp; Healthcare Transportation</div>
                <div className="mod-name">
                  HIDE SNP &nbsp;<span>Revenue Model</span>
                </div>
                <div className="mod-sub">
                  MICH Region 10 &nbsp;·&nbsp; 9 MCOs &nbsp;·&nbsp; $20 Target Floor &nbsp;·&nbsp; .5%–1% Rule &nbsp;·&nbsp; CY2026
                </div>
              </div>
            </div>
            <div className="mod-badges">
              <div className="mbadge">HAP CARESOURCE — ACTIVE</div>
              <div className="mbadge">EDWOSB · WOSB · MBE · WBE</div>
              <div className="mbadge">CAGE 8UMX3 · UEI HJB4KNYJVGZ1</div>
            </div>
          </div>
        </div>
      )}

      <nav className="mod-nav">
        {TABS.map((t) => (
          <div key={t.id} className={`nav-tab${tab === t.id ? ' active' : ''}`} onClick={() => setTab(t.id)} role="button" tabIndex={0}>
            {t.label}
          </div>
        ))}
      </nav>

      {embedded && onNavigate && (
        <div className="hsrm-module-links">
          <span className="hsrm-links-label">Connected in NEXUS:</span>
          <button type="button" className="hsrm-link-btn" onClick={() => onNavigate('ddcss', 'pipeline')}>
            DDCSS Pipeline
          </button>
          <button type="button" className="hsrm-link-btn" onClick={() => onNavigate('opportunity-hunter')}>
            NOVA Hunter
          </button>
          <button type="button" className="hsrm-link-btn" onClick={() => onNavigate('prism')}>
            PRISM NEMT Ops
          </button>
          <button type="button" className="hsrm-link-btn" onClick={() => onNavigate('vertex')}>
            VERTEX Billing
          </button>
        </div>
      )}

      <div className="mod-body">
        {tab === 'riders' && (
          <div className="tool-panel active">
            <div className="sec-label">MCO Rider Breakdown</div>
            <div className="tog-row">
              <span className="tog-lbl">Scenario:</span>
              <ToggleBtn on={r1Scen === 'current'} label="Current enrollment" onClick={() => setR1Scen('current')} />
              <ToggleBtn on={r1Scen === 'expansion'} label="Full eligible pool" onClick={() => setR1Scen('expansion')} />
              <span style={{ marginLeft: 14 }} className="tog-lbl">
                DDI Ask:
              </span>
              <ToggleBtn on={r1Pct === 'both'} label=".5% and 1%" onClick={() => setR1Pct('both')} />
              <ToggleBtn on={r1Pct === 'half'} label=".5% only" onClick={() => setR1Pct('half')} />
              <ToggleBtn on={r1Pct === 'one'} label="1% only" onClick={() => setR1Pct('one')} />
            </div>
            <Metrics
              items={[
                { ml: 'Total enrolled', mv: fmt(riderData.totals.enrolled), ms: r1Scen === 'current' ? 'CY2026 baseline' : 'Full eligible pool' },
                { ml: 'Est. daily riders', mv: fmt(riderData.totals.dailyRiders), ms: '25% utilization' },
                ...(r1Pct !== 'one' ? [{ ml: 'DDI at .5% — est rev/yr', mv: fmtM(riderData.totals.halfRevYr), ms: `${fmt(riderData.totals.halfPctRiders)} riders` }] : []),
                ...(r1Pct !== 'half' ? [{ ml: 'DDI at 1% — est rev/yr', mv: fmtM(riderData.totals.oneRevYr), ms: `${fmt(riderData.totals.onePctRiders)} riders` }] : []),
              ]}
            />
            <div className="tbl-wrap">
              <table>
                <thead>
                  <tr>
                    <th>MCO</th>
                    <th>Enrolled</th>
                    <th>Daily riders (25%)</th>
                    {r1Pct !== 'one' && <th className="am">.5% DDI riders</th>}
                    {r1Pct !== 'half' && <th className="gr">1% DDI riders</th>}
                    {r1Pct !== 'one' && <th className="am">.5% rides/mo</th>}
                    {r1Pct !== 'half' && <th className="gr">1% rides/mo</th>}
                    {r1Pct !== 'one' && <th className="am">.5% est rev/yr</th>}
                    {r1Pct !== 'half' && <th className="gr">1% est rev/yr</th>}
                  </tr>
                </thead>
                <tbody>
                  {riderData.rows.map((r) => (
                    <tr key={r.mco.name} className={r.mco.active ? 'hap' : ''}>
                      <td>
                        {r.mco.name}
                        <span className={`badge ${r.mco.active ? 'ba' : 'bp'}`}>{r.mco.active ? 'Active' : 'Outreach'}</span>
                      </td>
                      <td>{fmt(r.enrolled)}</td>
                      <td>{fmt(r.dailyRiders)}</td>
                      {r1Pct !== 'one' && <td className="am">{fmt(r.halfPctRiders)}</td>}
                      {r1Pct !== 'half' && <td className="gr">{fmt(r.onePctRiders)}</td>}
                      {r1Pct !== 'one' && <td className="am">{fmt(r.halfRidesMo)}</td>}
                      {r1Pct !== 'half' && <td className="gr">{fmt(r.oneRidesMo)}</td>}
                      {r1Pct !== 'one' && <td className="am">{fmtK(r.halfRevYr)}</td>}
                      {r1Pct !== 'half' && <td className="gr">{fmtK(r.oneRevYr)}</td>}
                    </tr>
                  ))}
                  <tr className="total-row">
                    <td>Total — all 9 MCOs</td>
                    <td>{fmt(riderData.totals.enrolled)}</td>
                    <td>{fmt(riderData.totals.dailyRiders)}</td>
                    {r1Pct !== 'one' && <td className="am">{fmt(riderData.totals.halfPctRiders)}</td>}
                    {r1Pct !== 'half' && <td className="gr">{fmt(riderData.totals.onePctRiders)}</td>}
                    {r1Pct !== 'one' && <td className="am">{fmt(Math.round(riderData.totals.halfPctRiders * 4.5 * 30))}</td>}
                    {r1Pct !== 'half' && <td className="gr">{fmt(Math.round(riderData.totals.onePctRiders * 4.5 * 30))}</td>}
                    {r1Pct !== 'one' && <td className="am">{fmtM(riderData.totals.halfRevYr)}</td>}
                    {r1Pct !== 'half' && <td className="gr">{fmtM(riderData.totals.oneRevYr)}</td>}
                  </tr>
                </tbody>
              </table>
            </div>
            <div className="caveat">
              Enrollment: public data Feb 2026. Internal planning only — DDCSS / PRISM module. Fulfillment partners not named in buyer-facing materials.
            </div>
          </div>
        )}

        {(tab === 'spread' || tab === 'floor') && (
          <div className="tool-panel active">
            <div className="sec-label">{tab === 'spread' ? 'Spread Margin Model' : '$20 Target Floor Tracker'}</div>
            {tab === 'floor' && (
              <div className="target-banner">
                <div className="target-big">$20.00</div>
                <div className="target-desc">
                  <strong>DDI minimum net spread per ride.</strong> Adjust inputs below. Model confirms hit/miss vs $20 floor across all 9 MCOs.
                </div>
              </div>
            )}
            <div className="tog-row">
              <span className="tog-lbl">Scenario:</span>
              <ToggleBtn on={(tab === 'spread' ? r2Scen : r3Scen) === 'current'} label="Current enrollment" onClick={() => (tab === 'spread' ? setR2Scen('current') : setR3Scen('current'))} />
              <ToggleBtn on={(tab === 'spread' ? r2Scen : r3Scen) === 'expansion'} label="Full eligible pool" onClick={() => (tab === 'spread' ? setR2Scen('expansion') : setR3Scen('expansion'))} />
              <span style={{ marginLeft: 14 }} className="tog-lbl">
                DDI Ask:
              </span>
              <ToggleBtn on={(tab === 'spread' ? r2Pct : r3Pct) === 'half'} label=".5%" onClick={() => (tab === 'spread' ? setR2Pct('half') : setR3Pct('half'))} />
              <ToggleBtn on={(tab === 'spread' ? r2Pct : r3Pct) === 'one'} label="1%" onClick={() => (tab === 'spread' ? setR2Pct('one') : setR3Pct('one'))} />
            </div>
            <div className="controls-grid">{rateControls}</div>
            {tab === 'spread' && (
              <>
                <div className="bar-section">
                  <div className="sec-label">Per-ride spread — cost vs margin</div>
                  {[
                    { lbl: 'Sedan — best case', rate: spreadData.blend, cost: rates.ulo },
                    { lbl: 'Sedan — worst case', rate: spreadData.blend, cost: rates.uhi },
                  ].map((b) => {
                    const sp = b.rate - b.cost;
                    const cw = Math.round((b.cost / b.rate) * 100);
                    return (
                      <div key={b.lbl} className="ride-row">
                        <div className="rt-label">{b.lbl}</div>
                        <div className="bar-track">
                          <div className="bar-cost" style={{ width: `${cw}%`, background: '#7a2020', color: '#e87c73' }}>
                            {cw > 15 ? fmtD(b.cost) : ''}
                          </div>
                          <div className="bar-spread" style={{ width: `${100 - cw}%`, background: '#0f6e56', color: '#5DCAA5' }}>
                            {100 - cw > 12 ? fmtD(sp) : ''}
                          </div>
                        </div>
                        <div className="rt-total">{fmtD(b.rate)}</div>
                        <div className={`rt-margin ${sp >= 0 ? 'gr' : 'co'}`}>{sp >= 0 ? '+' : ''}{fmtD(sp)}</div>
                      </div>
                    );
                  })}
                </div>
                <Metrics
                  items={[
                    { ml: 'Blended rate / ride', mv: fmtD(spreadData.blend), ms: `${rates.wcPct}% wc mix` },
                    { ml: 'Net — best case', mv: fmtD(spreadData.spLo), ms: `fulfillment at $${rates.ulo}` },
                    { ml: 'Net — planning', mv: fmtD(spreadData.spMid), ms: `fulfillment at $${rates.umid}` },
                    { ml: 'Net — worst case', mv: fmtD(spreadData.spHi), ms: `fulfillment at $${rates.uhi}` },
                  ]}
                />
              </>
            )}
            {tab === 'floor' && (
              <>
                <div className="hit-note">
                  Max fulfillment to protect $20 floor: <strong>{fmtD(Math.max(0, floorData.blend - TARGET_FLOOR))}</strong> per ride.
                  Planning net: <strong>{fmtD(floorData.spMid)}</strong> {floorData.spMid >= TARGET_FLOOR ? '✓' : '✗'}
                </div>
                <Metrics
                  items={[
                    { ml: 'Blended rate / ride', mv: fmtD(floorData.blend), ms: `${rates.wcPct}% wc mix` },
                    { ml: 'Max fulfillment to hit $20', mv: fmtD(Math.max(0, floorData.blend - TARGET_FLOOR)), ms: 'ceiling per ride' },
                    { ml: 'Net / ride (planning)', mv: fmtD(floorData.spMid), ms: floorData.spMid >= TARGET_FLOOR ? '✓ above floor' : '✗ below floor' },
                    { ml: 'Total net / yr', mv: fmtM(floorData.totals.netYr), ms: `${fmt(floorData.totals.ddiRiders)} DDI riders` },
                  ]}
                />
              </>
            )}
            <div className="tbl-wrap">
              <table>
                <thead>
                  <tr>
                    <th>MCO</th>
                    <th>DDI riders</th>
                    <th>Rides/mo</th>
                    <th className="bl">Gross/yr</th>
                    <th className="co">Cost/yr</th>
                    <th className="gr">Net/yr</th>
                    {tab === 'spread' ? <th>Margin %</th> : (
                      <>
                        <th>$/ride net</th>
                        <th>Status</th>
                      </>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {(tab === 'spread' ? spreadData : floorData).rows.map((r) => {
                    const nr = floorData.blend - rates.umid;
                    const hit = nr >= TARGET_FLOOR;
                    return (
                      <tr key={r.mco.name} className={r.mco.active ? 'hap' : ''}>
                        <td>
                          {r.mco.name}
                          <span className={`badge ${r.mco.active ? 'ba' : 'bp'}`}>{r.mco.active ? 'Active' : 'Outreach'}</span>
                        </td>
                        <td>{fmt(r.ddiRiders)}</td>
                        <td>{fmt(r.ridesMo)}</td>
                        <td className="bl">{fmtK(r.grossYr)}</td>
                        <td className="co">({fmtK(r.costYr)})</td>
                        <td className={r.netYr >= 0 ? 'gr' : 'co'}>{fmtK(r.netYr)}</td>
                        {tab === 'spread' ? (
                          <td className={r.netYr >= 0 ? 'gr' : 'co'}>{r.marginPct.toFixed(0)}%</td>
                        ) : (
                          <>
                            <td className={hit ? 'gr' : 'co'}>{fmtD(nr)}</td>
                            <td>
                              <span className={`spill ${hit ? 'spill-ok' : 'spill-bad'}`}>{hit ? '✓ hits $20' : '✗ below $20'}</span>
                            </td>
                          </>
                        )}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {tab === 'negotiate' && (
          <div className="tool-panel active">
            <div className="sec-label">Negotiation Floor Solver</div>
            <div className="target-banner">
              <div className="target-big">$20 floor</div>
              <div className="target-desc">
                <strong>Reverse solver.</strong> Set fulfillment cost and trip parameters — minimum MCO base before walk-away.
              </div>
            </div>
            <div className="controls-grid">
              <div className="ctrl-card">
                <div className="ctrl-title">Your operating assumptions</div>
                <SliderRow label="Avg trip miles" value={rates.avgMiles} min={3} max={20} step={1} display={`${rates.avgMiles} mi`} onChange={(v) => patch({ avgMiles: v })} />
                <SliderRow label="Per-mile rate (MCO)" value={rates.mileRate} min={1} max={3.5} step={0.05} display={`$${rates.mileRate.toFixed(2)}`} onChange={(v) => patch({ mileRate: v })} />
                <SliderRow label="% wheelchair rides" value={rates.wcPct} min={0} max={60} step={5} display={`${rates.wcPct}%`} onChange={(v) => patch({ wcPct: v })} />
                <SliderRow label="Rides per member/day" value={rates.ridesPerDay} min={2} max={7} step={0.5} display={rates.ridesPerDay.toFixed(1)} onChange={(v) => patch({ ridesPerDay: v })} />
              </div>
              <div className="ctrl-card">
                <div className="ctrl-title">MCO offer on the table</div>
                <SliderRow label="Fulfillment — planning" value={rates.umid} min={5} max={28} step={1} display={`$${rates.umid}`} onChange={(v) => patch({ umid: v })} />
                <SliderRow label="Offered sedan base" value={offeredSedan} min={15} max={50} step={1} display={`$${offeredSedan}`} onChange={setOfferedSedan} />
                <SliderRow label="Offered wheelchair base" value={offeredWc} min={20} max={65} step={1} display={`$${offeredWc}`} onChange={setOfferedWc} />
              </div>
            </div>
            <div className={`answer-block ${neg.cls}`}>
              <div className="answer-grid">
                <div className="answer-item">
                  <div className="answer-lbl">Blended rate collected</div>
                  <div className="answer-val">{fmtD(neg.blend)}</div>
                  <div className="answer-sub">{rates.wcPct}% wc mix</div>
                </div>
                <div className="answer-item">
                  <div className="answer-lbl">Net spread at planning cost</div>
                  <div className={`answer-val ${neg.spMid >= TARGET_FLOOR ? 'gr' : 'co'}`}>{fmtD(neg.spMid)}</div>
                  <div className="answer-sub">vs $20 floor</div>
                </div>
                <div className="answer-item">
                  <div className="answer-lbl">{neg.above >= 0 ? 'Cushion above floor' : 'Gap below floor'}</div>
                  <div className={`answer-val ${neg.above >= 0 ? 'gr' : 'co'}`}>{fmtD(Math.abs(neg.above))}</div>
                  <div className="answer-sub">{neg.above >= 0 ? 'protected' : 'must negotiate'}</div>
                </div>
              </div>
              <div className="verdict">
                {neg.spMid >= TARGET_FLOOR ? (
                  <>
                    At planning fulfillment <strong>{fmtD(rates.umid)}</strong>, offered rates clear $20 with <strong>{fmtD(neg.above)}</strong> cushion/ride. Min sedan base <strong>{fmtD(neg.minSedMid)}</strong>. Accept.
                  </>
                ) : (
                  <>
                    Does not clear $20 — nets <strong>{fmtD(neg.spMid)}</strong>/ride. Counter sedan base to at least <strong>{fmtD(neg.minSedMid)}</strong>.
                  </>
                )}
              </div>
            </div>
            <div className="matrix-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Sedan base ↓ / Fulfillment →</th>
                    {uCols.map((u) => (
                      <th key={u}>${u}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {sedRows.map((sed) => (
                    <tr key={sed} style={Math.round(offeredSedan) === sed ? { fontWeight: 700 } : undefined}>
                      <td>
                        {fmtD(sed)}
                        {Math.round(offeredSedan) === sed ? ' ←' : ''}
                      </td>
                      {uCols.map((u) => {
                        const rate = sed + neg.mileRev;
                        const diff = rate - u - TARGET_FLOOR;
                        const cls = diff >= 2 ? 'cell-ok' : diff >= 0 ? 'cell-edge' : 'cell-bad';
                        return (
                          <td
                            key={u}
                            className={cls}
                            style={Math.round(offeredSedan) === sed ? { outline: '1.5px solid var(--gold)', outlineOffset: -2 } : undefined}
                          >
                            {diff >= 0 ? '+' : ''}
                            {diff.toFixed(0)}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {!embedded && (
        <div className="mod-footer">
          <div>
            NEXUS · <span>DEE DAVIS INC.</span> · DDI NEMT TPA · HIDE SNP REVENUE MODEL · CONFIDENTIAL
          </div>
          <div>
            CAGE <span>8UMX3</span> · UEI <span>HJB4KNYJVGZ1</span> · info@deedavis.biz
          </div>
        </div>
      )}
    </div>
  );
};

export default HideSnpRevenueModel;
