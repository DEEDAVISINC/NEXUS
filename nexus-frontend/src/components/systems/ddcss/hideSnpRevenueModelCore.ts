/** DDI NEMT HIDE SNP Revenue Model — shared calc (DDCSS + PRISM) */

export const TARGET_FLOOR = 20.0;
export const RIDER_RATE = 0.25;
export const DAYS_PER_MONTH = 30;
export const AVG_RIDE_TAB1 = 46.5;

export type McoRow = {
  name: string;
  current: number;
  eligible: number;
  active: boolean;
};

export const HIDE_SNP_MCOS: McoRow[] = [
  { name: 'HAP CareSource', current: 5990, eligible: 24400, active: true },
  { name: 'Meridian / WellCare', current: 10300, eligible: 41900, active: false },
  { name: 'Molina', current: 10300, eligible: 41900, active: false },
  { name: 'Priority Health', current: 10300, eligible: 41900, active: false },
  { name: 'UnitedHealthcare', current: 10300, eligible: 41900, active: false },
  { name: 'Humana', current: 9000, eligible: 36700, active: false },
  { name: 'Aetna Better Health', current: 8650, eligible: 35200, active: false },
  { name: 'UPHP', current: 4710, eligible: 19200, active: false },
  { name: 'AmeriHealth Caritas', current: 4150, eligible: 16900, active: false },
];

export type RateInputs = {
  sedanBase: number;
  wcBase: number;
  mileRate: number;
  avgMiles: number;
  wcPct: number;
  ulo: number;
  umid: number;
  uhi: number;
  ridesPerDay: number;
};

export const DEFAULT_RATE_INPUTS: RateInputs = {
  sedanBase: 28,
  wcBase: 35,
  mileRate: 1.85,
  avgMiles: 10,
  wcPct: 20,
  ulo: 5,
  umid: 14,
  uhi: 24,
  ridesPerDay: 4.5,
};

export function fmt(n: number): string {
  return Math.round(n).toLocaleString();
}

export function fmtM(n: number): string {
  return `$${(n / 1e6).toFixed(2)}M`;
}

export function fmtK(n: number): string {
  return n >= 1e6 ? fmtM(n) : `$${Math.round(n / 1000)}K`;
}

export function fmtD(n: number): string {
  return `${n < 0 ? '-$' : '$'}${Math.abs(n).toFixed(2)}`;
}

export function blendedRate(inputs: RateInputs): number {
  const wcP = inputs.wcPct / 100;
  const sedR = inputs.sedanBase + inputs.avgMiles * inputs.mileRate;
  const wcR = inputs.wcBase + inputs.avgMiles * inputs.mileRate;
  return wcP * wcR + (1 - wcP) * sedR;
}

export type RiderRow = {
  mco: McoRow;
  enrolled: number;
  dailyRiders: number;
  halfPctRiders: number;
  onePctRiders: number;
  halfRidesMo: number;
  oneRidesMo: number;
  halfRevYr: number;
  oneRevYr: number;
};

export function calcRiderBreakdown(
  scen: 'current' | 'expansion',
  rpd = 4.5
): { rows: RiderRow[]; totals: Record<string, number> } {
  const rows = HIDE_SNP_MCOS.map((mco) => {
    const enrolled = scen === 'current' ? mco.current : mco.eligible;
    const dailyRiders = Math.round(enrolled * RIDER_RATE);
    const halfPctRiders = Math.round(dailyRiders * 0.005);
    const onePctRiders = Math.round(dailyRiders * 0.01);
    const halfRidesMo = Math.round(halfPctRiders * rpd * DAYS_PER_MONTH);
    const oneRidesMo = Math.round(onePctRiders * rpd * DAYS_PER_MONTH);
    const halfRevYr = halfPctRiders * rpd * DAYS_PER_MONTH * 12 * AVG_RIDE_TAB1;
    const oneRevYr = onePctRiders * rpd * DAYS_PER_MONTH * 12 * AVG_RIDE_TAB1;
    return {
      mco,
      enrolled,
      dailyRiders,
      halfPctRiders,
      onePctRiders,
      halfRidesMo,
      oneRidesMo,
      halfRevYr,
      oneRevYr,
    };
  });
  const totals = rows.reduce(
    (acc, r) => ({
      enrolled: acc.enrolled + r.enrolled,
      dailyRiders: acc.dailyRiders + r.dailyRiders,
      halfPctRiders: acc.halfPctRiders + r.halfPctRiders,
      onePctRiders: acc.onePctRiders + r.onePctRiders,
      halfRevYr: acc.halfRevYr + r.halfRevYr,
      oneRevYr: acc.oneRevYr + r.oneRevYr,
    }),
    { enrolled: 0, dailyRiders: 0, halfPctRiders: 0, onePctRiders: 0, halfRevYr: 0, oneRevYr: 0 }
  );
  return { rows, totals };
}

export type SpreadRow = {
  mco: McoRow;
  ddiRiders: number;
  ridesMo: number;
  grossYr: number;
  costYr: number;
  netYr: number;
  marginPct: number;
};

export function calcSpreadTable(
  scen: 'current' | 'expansion',
  pct: 'half' | 'one',
  inputs: RateInputs
): {
  rows: SpreadRow[];
  totals: { ddiRiders: number; ridesMo: number; grossYr: number; costYr: number; netYr: number; marginPct: number };
  blend: number;
  spLo: number;
  spMid: number;
  spHi: number;
} {
  const pm = pct === 'half' ? 0.005 : 0.01;
  const blend = blendedRate(inputs);
  const spLo = blend - inputs.ulo;
  const spMid = blend - inputs.umid;
  const spHi = blend - inputs.uhi;
  const rows = HIDE_SNP_MCOS.map((mco) => {
    const enr = scen === 'current' ? mco.current : mco.eligible;
    const ddiRiders = Math.round(Math.round(enr * RIDER_RATE) * pm);
    const ridesMo = Math.round(ddiRiders * inputs.ridesPerDay * DAYS_PER_MONTH);
    const ridesYr = ridesMo * 12;
    const grossYr = ridesYr * blend;
    const costYr = ridesYr * inputs.umid;
    const netYr = grossYr - costYr;
    const marginPct = grossYr ? (netYr / grossYr) * 100 : 0;
    return { mco, ddiRiders, ridesMo, grossYr, costYr, netYr, marginPct };
  });
  const totals = rows.reduce(
    (acc, r) => ({
      ddiRiders: acc.ddiRiders + r.ddiRiders,
      ridesMo: acc.ridesMo + r.ridesMo,
      grossYr: acc.grossYr + r.grossYr,
      costYr: acc.costYr + r.costYr,
      netYr: acc.netYr + r.netYr,
      marginPct: 0,
    }),
    { ddiRiders: 0, ridesMo: 0, grossYr: 0, costYr: 0, netYr: 0, marginPct: 0 }
  );
  totals.marginPct = totals.grossYr ? (totals.netYr / totals.grossYr) * 100 : 0;
  return { rows, totals, blend, spLo, spMid, spHi };
}

export function calcNegotiation(inputs: RateInputs, offeredSedan: number, offeredWc: number) {
  const mileRev = inputs.avgMiles * inputs.mileRate;
  const minBase = (u: number) => TARGET_FLOOR + u - mileRev;
  const oSedRate = offeredSedan + mileRev;
  const oWcRate = offeredWc + mileRev;
  const wcP = inputs.wcPct / 100;
  const blend = wcP * oWcRate + (1 - wcP) * oSedRate;
  const spMid = blend - inputs.umid;
  const above = spMid - TARGET_FLOOR;
  const minSedMid = minBase(inputs.umid);
  const sedGap = offeredSedan - minSedMid;
  const cls = above >= 2 ? 'ok' : above >= -2 ? 'warn' : 'bad';
  return { mileRev, blend, spMid, above, minSedMid, sedGap, cls, minBase };
}
