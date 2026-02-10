import React, { useState, useMemo } from "react";

// ─── NEXUS P&L + PRICING ENGINE v3.0 ─────────────────────────────────────────
// Universal Automated Pricing & Profit/Loss System
// Supports: Service-Based (Middleman/Broker) + Product-Based (Resell/Markup)
// Auto-calculates tax, overhead, and amortization
// DEE DAVIS INC | CAGE: 8UMX3
// Integrated into DocumentGenerator as Pricing Engine + P&L Tracker tabs
// ──────────────────────────────────────────────────────────────────────────────

// ─── FORMATTING HELPERS ──────────────────────────────────────────────────────

const fmt = (n: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(n);

const fmtShort = (n: number) => {
  if (Math.abs(n) >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
  if (Math.abs(n) >= 1e3) return `$${(n / 1e3).toFixed(1)}K`;
  return fmt(n);
};

const pct = (n: number) => `${(n * 100).toFixed(1)}%`;

// ─── AUTO TAX & RATE ENGINE ──────────────────────────────────────────────────

interface EntityType {
  id: string;
  label: string;
  taxRate: number;
  seTax: number;
  desc: string;
}

interface StateType {
  id: string;
  label: string;
  rate: number;
}

interface ContractTypeOption {
  id: string;
  label: string;
  overhead: number;
  ga: number;
  desc: string;
  amort?: number;
  contingency?: number;
  shipping?: number;
  storage?: number;
}

interface ProfitLevel {
  id: string;
  label: string;
  rate: number;
  desc: string;
  color: string;
}

const ENTITY_TYPES: EntityType[] = [
  { id: "scorp", label: "S-Corp", taxRate: 0.25, seTax: 0, desc: "Pass-through, salary + distributions" },
  { id: "ccorp", label: "C-Corp", taxRate: 0.21, seTax: 0, desc: "Federal corporate rate 21%" },
  { id: "llc_single", label: "LLC (Single Member)", taxRate: 0.22, seTax: 0.153, desc: "Self-employment + income tax" },
  { id: "llc_multi", label: "LLC (Multi-Member)", taxRate: 0.24, seTax: 0.153, desc: "Partnership taxation" },
  { id: "sole_prop", label: "Sole Proprietor", taxRate: 0.22, seTax: 0.153, desc: "Full self-employment tax applies" },
];

const STATES: StateType[] = [
  { id: "MI", label: "Michigan", rate: 0.06 },
  { id: "OH", label: "Ohio", rate: 0.0 },
  { id: "CA", label: "California", rate: 0.088 },
  { id: "TX", label: "Texas", rate: 0.0 },
  { id: "FL", label: "Florida", rate: 0.055 },
  { id: "NY", label: "New York", rate: 0.068 },
  { id: "IL", label: "Illinois", rate: 0.099 },
  { id: "GA", label: "Georgia", rate: 0.055 },
  { id: "PA", label: "Pennsylvania", rate: 0.0899 },
  { id: "NC", label: "North Carolina", rate: 0.025 },
  { id: "VA", label: "Virginia", rate: 0.06 },
  { id: "WA", label: "Washington", rate: 0.0 },
  { id: "MD", label: "Maryland", rate: 0.0575 },
  { id: "DC", label: "Washington D.C.", rate: 0.089 },
  { id: "NJ", label: "New Jersey", rate: 0.0663 },
  { id: "OTHER", label: "Other (enter rate)", rate: 0.05 },
];

const CONTRACT_TYPES: Record<string, ContractTypeOption[]> = {
  service: [
    { id: "broker", label: "Broker / Middleman", overhead: 0.1, ga: 0.05, amort: 0.03, contingency: 0.03, desc: "You coordinate between client and subcontractors" },
    { id: "consulting", label: "Consulting / Advisory", overhead: 0.08, ga: 0.06, amort: 0.04, contingency: 0.02, desc: "Professional services, expertise-based" },
    { id: "staffing", label: "Staffing / Labor", overhead: 0.12, ga: 0.05, amort: 0.02, contingency: 0.03, desc: "Providing personnel to client" },
    { id: "managed", label: "Managed Services", overhead: 0.1, ga: 0.06, amort: 0.04, contingency: 0.02, desc: "Ongoing service delivery and management" },
    { id: "transportation", label: "Transportation / Logistics", overhead: 0.12, ga: 0.05, amort: 0.03, contingency: 0.04, desc: "Fleet, NEMT, freight, delivery" },
    { id: "maintenance", label: "Maintenance / Facilities", overhead: 0.1, ga: 0.05, amort: 0.03, contingency: 0.03, desc: "Building, grounds, equipment upkeep" },
    { id: "custom_svc", label: "Custom Service Type", overhead: 0.1, ga: 0.05, amort: 0.03, contingency: 0.03, desc: "Define your own rates" },
  ],
  product: [
    { id: "resell", label: "Resell / Distribution", overhead: 0.08, ga: 0.04, shipping: 0.05, storage: 0.03, desc: "Buy wholesale, sell to end customer" },
    { id: "dropship", label: "Dropship / Pass-Through", overhead: 0.05, ga: 0.03, shipping: 0.0, storage: 0.0, desc: "Supplier ships direct, you take margin" },
    { id: "value_add", label: "Value-Added Resell", overhead: 0.1, ga: 0.05, shipping: 0.04, storage: 0.03, desc: "Customize/bundle products before resale" },
    { id: "equipment", label: "Equipment / Assets", overhead: 0.08, ga: 0.05, shipping: 0.06, storage: 0.04, desc: "Machinery, vehicles, technology hardware" },
    { id: "supplies", label: "Supplies / Consumables", overhead: 0.06, ga: 0.03, shipping: 0.04, storage: 0.02, desc: "Office, medical, industrial supplies" },
    { id: "custom_prod", label: "Custom Product Type", overhead: 0.08, ga: 0.04, shipping: 0.04, storage: 0.02, desc: "Define your own rates" },
  ],
};

const PROFIT_LEVELS: ProfitLevel[] = [
  { id: "competitive", label: "Competitive", rate: 0.08, desc: "Win on price, lower margin", color: "#F59E0B" },
  { id: "standard", label: "Standard", rate: 0.12, desc: "Balanced price and profit", color: "#10B981" },
  { id: "premium", label: "Premium", rate: 0.18, desc: "High value, higher margin", color: "#0A84E8" },
  { id: "emergency", label: "Emergency / Sole Source", rate: 0.25, desc: "Urgent need, maximum margin", color: "#7C3AED" },
];

// ─── SHARED STYLES ───────────────────────────────────────────────────────────

const labelStyle: React.CSSProperties = {
  color: "#666",
  fontSize: 10,
  textTransform: "uppercase",
  letterSpacing: 1,
  fontFamily: "'JetBrains Mono', monospace",
  display: "block",
};

const inputStyle: React.CSSProperties = {
  padding: "8px 12px",
  background: "#0a0a0a",
  border: "1px solid #222",
  borderRadius: 6,
  color: "#fff",
  fontSize: 13,
  fontFamily: "'JetBrains Mono', monospace",
  outline: "none",
};

const primaryBtnStyle: React.CSSProperties = {
  padding: "10px 28px",
  borderRadius: 6,
  border: "none",
  background: "#E8630A",
  color: "#000",
  cursor: "pointer",
  fontSize: 13,
  fontFamily: "'JetBrains Mono', monospace",
  fontWeight: 700,
};

const secondaryBtnStyle: React.CSSProperties = {
  padding: "10px 20px",
  borderRadius: 6,
  border: "1px solid #333",
  background: "transparent",
  color: "#888",
  cursor: "pointer",
  fontSize: 12,
  fontFamily: "'JetBrains Mono', monospace",
};

const pillStyle: React.CSSProperties = {
  display: "inline-block",
  padding: "4px 10px",
  borderRadius: 20,
  fontSize: 10,
  fontFamily: "'JetBrains Mono', monospace",
  fontWeight: 600,
  background: "#E8630A18",
  color: "#E8630A",
  border: "1px solid #E8630A33",
  marginRight: 6,
};

// ─── SHARED SUB-COMPONENTS ───────────────────────────────────────────────────

function ModeCard({
  title,
  icon,
  desc,
  examples,
  selected,
  onClick,
}: {
  title: string;
  icon: string;
  desc: string;
  examples: string;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: 24,
        borderRadius: 10,
        textAlign: "left",
        cursor: "pointer",
        border: selected ? "2px solid #E8630A" : "1px solid #222",
        background: selected ? "#E8630A08" : "#111",
        transition: "all 0.2s",
      }}
    >
      <div style={{ fontSize: 32, marginBottom: 12 }}>{icon}</div>
      <div
        style={{
          color: selected ? "#E8630A" : "#fff",
          fontSize: 16,
          fontWeight: 700,
          fontFamily: "'JetBrains Mono', monospace",
          marginBottom: 8,
        }}
      >
        {title}
      </div>
      <div
        style={{
          color: "#888",
          fontSize: 12,
          fontFamily: "'JetBrains Mono', monospace",
          lineHeight: 1.5,
          marginBottom: 10,
        }}
      >
        {desc}
      </div>
      <div
        style={{
          color: "#555",
          fontSize: 10,
          fontFamily: "'JetBrains Mono', monospace",
          fontStyle: "italic",
        }}
      >
        e.g. {examples}
      </div>
    </button>
  );
}

function MiniStat({ label, value, sub }: { label: string; value: string; sub: string }) {
  return (
    <div style={{ textAlign: "center" }}>
      <div
        style={{
          color: "#666",
          fontSize: 9,
          textTransform: "uppercase",
          letterSpacing: 1,
          fontFamily: "'JetBrains Mono', monospace",
          marginBottom: 4,
        }}
      >
        {label}
      </div>
      <div
        style={{
          color: "#E8630A",
          fontSize: 18,
          fontWeight: 700,
          fontFamily: "'JetBrains Mono', monospace",
        }}
      >
        {value}
      </div>
      <div style={{ color: "#444", fontSize: 9, marginTop: 2, fontFamily: "'JetBrains Mono', monospace" }}>{sub}</div>
    </div>
  );
}

function SectionHeader({ label }: { label: string }) {
  return (
    <h3
      style={{
        color: "#E8630A",
        fontSize: 13,
        textTransform: "uppercase",
        letterSpacing: 2,
        marginBottom: 16,
        fontFamily: "'JetBrains Mono', monospace",
      }}
    >
      ▸ {label}
    </h3>
  );
}

function InputField({
  label,
  value,
  onChange,
  prefix,
  suffix,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  prefix?: string;
  suffix?: string;
}) {
  return (
    <div style={{ marginBottom: 14 }}>
      <label style={{ ...labelStyle, marginBottom: 4 }}>{label}</label>
      <div style={{ position: "relative" }}>
        {prefix && (
          <span
            style={{
              position: "absolute",
              left: 10,
              top: "50%",
              transform: "translateY(-50%)",
              color: "#666",
              fontSize: 14,
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            {prefix}
          </span>
        )}
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
          style={{
            ...inputStyle,
            width: "100%",
            boxSizing: "border-box",
            paddingLeft: prefix ? 24 : 12,
            paddingRight: suffix ? 30 : 12,
          }}
          onFocus={(e) => (e.target.style.borderColor = "#E8630A")}
          onBlur={(e) => (e.target.style.borderColor = "#222")}
        />
        {suffix && (
          <span
            style={{
              position: "absolute",
              right: 10,
              top: "50%",
              transform: "translateY(-50%)",
              color: "#666",
              fontSize: 12,
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            {suffix}
          </span>
        )}
      </div>
    </div>
  );
}

function FormInput({
  label,
  value,
  onChange,
  text = false,
}: {
  label: string;
  value: string | number;
  onChange: (v: any) => void;
  text?: boolean;
}) {
  return (
    <div>
      <label style={labelStyle}>{label}</label>
      <input
        type={text ? "text" : "number"}
        value={value}
        onChange={(e) => onChange(text ? e.target.value : parseFloat(e.target.value) || 0)}
        style={{ ...inputStyle, width: "100%", boxSizing: "border-box", marginTop: 4 }}
        placeholder={text ? "Enter name..." : "0"}
      />
    </div>
  );
}

function SliderField({
  label,
  value,
  onChange,
  max = 0.2,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  max?: number;
}) {
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <label style={labelStyle}>{label}</label>
        <span style={{ color: "#E8630A", fontSize: 12, fontWeight: 700, fontFamily: "'JetBrains Mono', monospace" }}>
          {pct(value)}
        </span>
      </div>
      <input
        type="range"
        min={0}
        max={max}
        step={0.005}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        style={{ width: "100%", accentColor: "#E8630A", height: 4 }}
      />
    </div>
  );
}

function BuildupRow({
  label,
  value,
  color = "#fff",
  bold = false,
  dim = false,
}: {
  label: string;
  value: string;
  color?: string;
  bold?: boolean;
  dim?: boolean;
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        padding: "4px 0",
        fontSize: bold ? 13 : 11,
        fontWeight: bold ? 600 : 400,
        color: dim ? "#555" : color,
        fontFamily: "'JetBrains Mono', monospace",
      }}
    >
      <span>{label}</span>
      <span>{value}</span>
    </div>
  );
}

function MetricCard({
  label,
  value,
  sub,
  color,
}: {
  label: string;
  value: string;
  sub?: string;
  color: string;
}) {
  return (
    <div
      style={{
        background: "#111",
        borderRadius: 8,
        padding: 12,
        border: "1px solid #222",
        textAlign: "center",
      }}
    >
      <div style={{ ...labelStyle, marginBottom: 4, fontSize: 9 }}>{label}</div>
      <div style={{ color, fontSize: 20, fontWeight: 700, fontFamily: "'JetBrains Mono', monospace" }}>{value}</div>
      {sub && (
        <div style={{ color: "#555", fontSize: 9, marginTop: 2, fontFamily: "'JetBrains Mono', monospace" }}>{sub}</div>
      )}
    </div>
  );
}

function PnLLine({
  label,
  value,
  bold,
  color = "#fff",
  indent,
  divider,
  isPct,
}: {
  label: string;
  value: number;
  bold?: boolean;
  color?: string;
  indent?: boolean;
  divider?: boolean;
  isPct?: boolean;
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        padding: "6px 0",
        paddingLeft: indent ? 20 : 0,
        fontWeight: bold ? 700 : 400,
        fontSize: bold ? 14 : 12,
        color,
        fontFamily: "'JetBrains Mono', monospace",
        borderBottom: divider ? "1px solid #333" : "none",
        marginBottom: divider ? 8 : 0,
      }}
    >
      <span>{label}</span>
      <span>{isPct ? pct(value) : fmt(value)}</span>
    </div>
  );
}

function CellValue({ label, value, color = "#fff" }: { label: string; value: string; color?: string }) {
  return (
    <div style={{ textAlign: "right" }}>
      <div style={{ ...labelStyle, fontSize: 9 }}>{label}</div>
      <div style={{ color, fontSize: 13, fontWeight: 700, fontFamily: "'JetBrains Mono', monospace" }}>{value}</div>
    </div>
  );
}

function HealthCard({
  label,
  value,
  threshold,
  good,
  bad,
  invert = false,
}: {
  label: string;
  value: number;
  threshold: number;
  good: string;
  bad: string;
  invert?: boolean;
}) {
  const ok = invert ? value < threshold : value >= threshold;
  return (
    <div
      style={{
        background: "#111",
        borderRadius: 8,
        padding: 12,
        border: `1px solid ${ok ? "#10B98133" : "#EF444433"}`,
        textAlign: "center",
      }}
    >
      <div style={{ ...labelStyle, fontSize: 9, marginBottom: 4 }}>{label}</div>
      <div
        style={{
          color: ok ? "#10B981" : "#EF4444",
          fontSize: 18,
          fontWeight: 700,
          fontFamily: "'JetBrains Mono', monospace",
        }}
      >
        {pct(value)}
      </div>
      <div style={{ fontSize: 9, color: ok ? "#10B981" : "#EF4444", marginTop: 2, fontFamily: "'JetBrains Mono', monospace" }}>
        {ok ? `✓ ${good}` : `⚠ ${bad}`}
      </div>
    </div>
  );
}

// ─── AUTOMATED PRICING CALCULATOR ────────────────────────────────────────────

export function AutoPricingCalculator() {
  const [step, setStep] = useState(1);
  const [mode, setMode] = useState<string | null>(null);
  const [entityType, setEntityType] = useState("scorp");
  const [stateId, setStateId] = useState("MI");
  const [customStateRate, setCustomStateRate] = useState(0.05);
  const [annualRevenue, setAnnualRevenue] = useState(500000);
  const [contractName, setContractName] = useState("");
  const [contractType, setContractType] = useState("");
  const [directCost, setDirectCost] = useState(1000);
  const [costLabel, setCostLabel] = useState("unit/day");
  const [quantity, setQuantity] = useState(1);
  const [duration, setDuration] = useState(30);
  const [profitLevel, setProfitLevel] = useState("standard");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [overrides, setOverrides] = useState<Record<string, number | undefined>>({});

  const entity = ENTITY_TYPES.find((e) => e.id === entityType)!;
  const state = STATES.find((s) => s.id === stateId)!;
  const stateRate = stateId === "OTHER" ? customStateRate : state.rate;
  const ctType = mode ? CONTRACT_TYPES[mode]?.find((c) => c.id === contractType) : null;
  const profLevel = PROFIT_LEVELS.find((p) => p.id === profitLevel)!;

  const effectiveTaxRate = useMemo(() => {
    const federal = entity?.taxRate || 0.22;
    const se = entity?.seTax || 0;
    const st = stateRate;
    const effectiveSE = se * 0.9235;
    const combined = federal + st + effectiveSE;
    return Math.min(combined * 0.85, 0.45);
  }, [entity, stateRate]);

  const overheadScale = useMemo(() => {
    if (annualRevenue < 250000) return 1.2;
    if (annualRevenue < 500000) return 1.1;
    if (annualRevenue < 1000000) return 1.0;
    if (annualRevenue < 5000000) return 0.9;
    return 0.85;
  }, [annualRevenue]);

  const calc = useMemo(() => {
    if (!ctType) return null;

    const base = directCost;
    let oh: number, ga: number, tax: number, amort: number, cont: number, profit: number;

    if (mode === "service") {
      oh = overrides.overhead ?? ctType.overhead * overheadScale;
      ga = overrides.ga ?? ctType.ga;
      tax = overrides.tax ?? effectiveTaxRate;
      amort = overrides.amort ?? (ctType.amort || 0.03);
      cont = overrides.contingency ?? (ctType.contingency || 0.03);
      profit = overrides.profit ?? profLevel.rate;
    } else {
      oh = overrides.overhead ?? ctType.overhead * overheadScale;
      ga = overrides.ga ?? ctType.ga;
      tax = overrides.tax ?? effectiveTaxRate;
      const ship = overrides.shipping ?? (ctType.shipping || 0);
      const store = overrides.storage ?? (ctType.storage || 0);
      amort = ship + store;
      cont = overrides.contingency ?? 0.02;
      profit = overrides.profit ?? profLevel.rate;
    }

    const afterOH = base * (1 + oh);
    const afterGA = afterOH * (1 + ga);
    const afterTax = afterGA * (1 + tax);
    const afterAmort = afterTax * (1 + amort);
    const afterCont = afterAmort * (1 + cont);
    const proposedPrice = afterCont * (1 + profit);

    const totalMarkup = proposedPrice - base;
    const markupPct = base > 0 ? totalMarkup / base : 0;
    const grossMargin = proposedPrice > 0 ? totalMarkup / proposedPrice : 0;

    const ohDollars = base * oh;
    const gaDollars = afterOH * ga;
    const taxDollars = afterGA * tax;
    const amortDollars = afterTax * amort;
    const contDollars = afterAmort * cont;
    const profitDollars = afterCont * profit;

    const totalUnits = quantity * duration;
    const totalRevenue = proposedPrice * totalUnits;
    const totalCost = base * totalUnits;
    const totalProfit = totalMarkup * totalUnits;

    return {
      base, oh, ga, tax, amort, cont, profit,
      afterOH, afterGA, afterTax, afterAmort, afterCont, proposedPrice,
      totalMarkup, markupPct, grossMargin,
      ohDollars, gaDollars, taxDollars, amortDollars, contDollars, profitDollars,
      totalUnits, totalRevenue, totalCost, totalProfit,
    };
  }, [ctType, directCost, mode, overheadScale, effectiveTaxRate, profLevel, overrides, quantity, duration]);

  const resetOverrides = () => setOverrides({});

  // ─── STEP 1: Choose Mode ───
  if (step === 1) {
    return (
      <div style={{ maxWidth: 700, margin: "0 auto", paddingTop: 40 }}>
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <div style={{ fontSize: 11, color: "#E8630A", letterSpacing: 3, textTransform: "uppercase", marginBottom: 8 }}>
            Step 1 of 3
          </div>
          <h2 style={{ fontSize: 20, color: "#fff", margin: 0, fontFamily: "'JetBrains Mono', monospace" }}>
            What are you pricing?
          </h2>
          <p style={{ color: "#666", fontSize: 13, marginTop: 8, fontFamily: "'JetBrains Mono', monospace" }}>
            This determines how costs and margins are calculated
          </p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <ModeCard
            title="Service-Based"
            icon="⚙️"
            desc="Broker, middleman, consulting, staffing, managed services, transportation — you provide labor or coordination"
            examples="NEMT trips, freight brokerage, consulting SOWs, staffing contracts, maintenance"
            selected={mode === "service"}
            onClick={() => setMode("service")}
          />
          <ModeCard
            title="Product-Based"
            icon="📦"
            desc="Resell, distribute, dropship, or value-add physical goods — you buy and sell products"
            examples="Equipment resale, supply distribution, dropship, value-added bundling"
            selected={mode === "product"}
            onClick={() => setMode("product")}
          />
        </div>
        {mode && (
          <div style={{ textAlign: "center", marginTop: 32 }}>
            <button onClick={() => setStep(2)} style={primaryBtnStyle}>
              CONTINUE →
            </button>
          </div>
        )}
      </div>
    );
  }

  // ─── STEP 2: Business Setup ───
  if (step === 2) {
    return (
      <div style={{ maxWidth: 700, margin: "0 auto", paddingTop: 40 }}>
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <div style={{ fontSize: 11, color: "#E8630A", letterSpacing: 3, textTransform: "uppercase", marginBottom: 8 }}>
            Step 2 of 3
          </div>
          <h2 style={{ fontSize: 20, color: "#fff", margin: 0, fontFamily: "'JetBrains Mono', monospace" }}>
            Business Setup
          </h2>
          <p style={{ color: "#666", fontSize: 13, marginTop: 8, fontFamily: "'JetBrains Mono', monospace" }}>
            This auto-calculates your tax burden and overhead rates
          </p>
        </div>

        <div style={{ marginBottom: 24 }}>
          <label style={labelStyle}>Business Entity Type</label>
          <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 8 }}>
            {ENTITY_TYPES.map((e) => (
              <button
                key={e.id}
                onClick={() => setEntityType(e.id)}
                style={{
                  padding: "10px 14px",
                  borderRadius: 6,
                  textAlign: "left",
                  border: entityType === e.id ? "1px solid #E8630A" : "1px solid #222",
                  background: entityType === e.id ? "#E8630A10" : "#111",
                  cursor: "pointer",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <div
                    style={{
                      color: entityType === e.id ? "#E8630A" : "#ccc",
                      fontSize: 13,
                      fontWeight: 600,
                      fontFamily: "'JetBrains Mono', monospace",
                    }}
                  >
                    {e.label}
                  </div>
                  <div style={{ color: "#666", fontSize: 10, marginTop: 2, fontFamily: "'JetBrains Mono', monospace" }}>
                    {e.desc}
                  </div>
                </div>
                <div style={{ color: "#E8630A", fontSize: 12, fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 }}>
                  {pct(e.taxRate + e.seTax * 0.9235)}
                </div>
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: 24 }}>
          <label style={labelStyle}>State</label>
          <select
            value={stateId}
            onChange={(e) => setStateId(e.target.value)}
            style={{
              width: "100%",
              padding: "10px 12px",
              background: "#111",
              border: "1px solid #222",
              borderRadius: 6,
              color: "#fff",
              fontSize: 13,
              fontFamily: "'JetBrains Mono', monospace",
              marginTop: 8,
            }}
          >
            {STATES.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label} {s.rate > 0 ? `(${pct(s.rate)} state tax)` : "(No state income tax)"}
              </option>
            ))}
          </select>
          {stateId === "OTHER" && (
            <div style={{ marginTop: 8 }}>
              <InputField label="Custom State Tax Rate" value={customStateRate * 100} onChange={(v) => setCustomStateRate(v / 100)} suffix="%" />
            </div>
          )}
        </div>

        <div style={{ marginBottom: 24 }}>
          <label style={labelStyle}>Estimated Annual Revenue</label>
          <p
            style={{
              color: "#555",
              fontSize: 10,
              marginTop: 2,
              marginBottom: 8,
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            Used to auto-scale overhead rates (smaller businesses have proportionally higher overhead)
          </p>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {[100000, 250000, 500000, 1000000, 5000000, 10000000].map((v) => (
              <button
                key={v}
                onClick={() => setAnnualRevenue(v)}
                style={{
                  padding: "8px 14px",
                  borderRadius: 6,
                  border: annualRevenue === v ? "1px solid #E8630A" : "1px solid #222",
                  background: annualRevenue === v ? "#E8630A10" : "#111",
                  color: annualRevenue === v ? "#E8630A" : "#888",
                  cursor: "pointer",
                  fontSize: 12,
                  fontFamily: "'JetBrains Mono', monospace",
                  fontWeight: annualRevenue === v ? 700 : 400,
                }}
              >
                {fmtShort(v)}
              </button>
            ))}
          </div>
        </div>

        <div style={{ background: "#0a0a0a", borderRadius: 8, padding: 16, border: "1px solid #222", marginBottom: 24 }}>
          <div
            style={{
              fontSize: 11,
              color: "#E8630A",
              letterSpacing: 2,
              textTransform: "uppercase",
              marginBottom: 12,
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            ▸ Auto-Calculated Rates
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
            <MiniStat
              label="Effective Tax Rate"
              value={pct(effectiveTaxRate)}
              sub={`Federal ${pct(entity.taxRate)} + State ${pct(stateRate)}${entity.seTax > 0 ? ` + SE ${pct(entity.seTax)}` : ""}`}
            />
            <MiniStat label="Overhead Scale" value={`${(overheadScale * 100).toFixed(0)}%`} sub={`Based on ${fmtShort(annualRevenue)} revenue`} />
            <MiniStat label="Combined Burden" value={pct(effectiveTaxRate + 0.15 * overheadScale)} sub="Tax + estimated overhead" />
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 32 }}>
          <button onClick={() => setStep(1)} style={secondaryBtnStyle}>
            ← BACK
          </button>
          <button
            onClick={() => {
              setStep(3);
              if (!contractType) setContractType(mode === "service" ? "broker" : "resell");
            }}
            style={primaryBtnStyle}
          >
            CONTINUE →
          </button>
        </div>
      </div>
    );
  }

  // ─── STEP 3: Price It ───
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div>
          <span style={pillStyle}>{mode === "service" ? "⚙️ SERVICE" : "📦 PRODUCT"}</span>
          <span style={{ ...pillStyle, background: "#10B98118", color: "#10B981", borderColor: "#10B98133" }}>
            Tax: {pct(effectiveTaxRate)}
          </span>
          <span style={{ ...pillStyle, background: "#0A84E818", color: "#0A84E8", borderColor: "#0A84E833" }}>
            {entity.label} • {state.label}
          </span>
        </div>
        <button onClick={() => setStep(2)} style={{ ...secondaryBtnStyle, fontSize: 10, padding: "4px 10px" }}>
          ✎ EDIT SETUP
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 28 }}>
        {/* LEFT: Inputs */}
        <div>
          <SectionHeader label="Contract Details" />

          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>Contract Name</label>
            <input
              value={contractName}
              onChange={(e) => setContractName(e.target.value)}
              placeholder="e.g. Montgomery County NEMT, FEMA Logistics, Office Supply Order"
              style={{ ...inputStyle, marginTop: 6, width: "100%", boxSizing: "border-box" }}
              onFocus={(e) => (e.target.style.borderColor = "#E8630A")}
              onBlur={(e) => (e.target.style.borderColor = "#222")}
            />
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>{mode === "service" ? "Service Type" : "Product Type"}</label>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, marginTop: 6 }}>
              {(CONTRACT_TYPES[mode || "service"] || []).map((ct) => (
                <button
                  key={ct.id}
                  onClick={() => {
                    setContractType(ct.id);
                    resetOverrides();
                  }}
                  style={{
                    padding: "8px 10px",
                    borderRadius: 6,
                    textAlign: "left",
                    border: contractType === ct.id ? "1px solid #E8630A" : "1px solid #1a1a1a",
                    background: contractType === ct.id ? "#E8630A10" : "#111",
                    cursor: "pointer",
                  }}
                >
                  <div
                    style={{
                      color: contractType === ct.id ? "#E8630A" : "#aaa",
                      fontSize: 11,
                      fontWeight: 600,
                      fontFamily: "'JetBrains Mono', monospace",
                    }}
                  >
                    {ct.label}
                  </div>
                  <div style={{ color: "#555", fontSize: 9, marginTop: 2, fontFamily: "'JetBrains Mono', monospace" }}>
                    {ct.desc}
                  </div>
                </button>
              ))}
            </div>
          </div>

          <InputField label={`Direct Cost (per ${costLabel})`} value={directCost} onChange={setDirectCost} prefix="$" />

          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>Cost Unit</label>
            <div style={{ display: "flex", gap: 4, marginTop: 4, flexWrap: "wrap" }}>
              {(mode === "service"
                ? ["unit/day", "trip", "mile", "hour", "load", "engagement", "month"]
                : ["unit", "case", "pallet", "lot", "each", "order"]
              ).map((u) => (
                <button
                  key={u}
                  onClick={() => setCostLabel(u)}
                  style={{
                    padding: "4px 10px",
                    borderRadius: 4,
                    border: costLabel === u ? "1px solid #E8630A" : "1px solid #222",
                    background: costLabel === u ? "#E8630A10" : "#0a0a0a",
                    color: costLabel === u ? "#E8630A" : "#666",
                    cursor: "pointer",
                    fontSize: 10,
                    fontFamily: "'JetBrains Mono', monospace",
                    fontWeight: costLabel === u ? 700 : 400,
                  }}
                >
                  {u}
                </button>
              ))}
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <InputField label="Quantity" value={quantity} onChange={setQuantity} />
            <InputField label={mode === "service" ? "Duration (days)" : "Order Cycles"} value={duration} onChange={setDuration} />
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>Profit Target</label>
            <div style={{ display: "flex", gap: 6, marginTop: 6 }}>
              {PROFIT_LEVELS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => {
                    setProfitLevel(p.id);
                    setOverrides((o) => ({ ...o, profit: undefined }));
                  }}
                  style={{
                    flex: 1,
                    padding: "10px 8px",
                    borderRadius: 6,
                    textAlign: "center",
                    border: profitLevel === p.id ? `1px solid ${p.color}` : "1px solid #1a1a1a",
                    background: profitLevel === p.id ? `${p.color}10` : "#111",
                    cursor: "pointer",
                  }}
                >
                  <div
                    style={{
                      color: profitLevel === p.id ? p.color : "#888",
                      fontSize: 12,
                      fontWeight: 700,
                      fontFamily: "'JetBrains Mono', monospace",
                    }}
                  >
                    {pct(p.rate)}
                  </div>
                  <div
                    style={{
                      color: profitLevel === p.id ? p.color : "#555",
                      fontSize: 9,
                      marginTop: 2,
                      fontFamily: "'JetBrains Mono', monospace",
                    }}
                  >
                    {p.label}
                  </div>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            style={{
              background: "none",
              border: "none",
              color: "#555",
              cursor: "pointer",
              fontSize: 11,
              fontFamily: "'JetBrains Mono', monospace",
              padding: "8px 0",
              textDecoration: "underline",
              textUnderlineOffset: 3,
            }}
          >
            {showAdvanced ? "▾ Hide advanced overrides" : "▸ Show advanced overrides (optional)"}
          </button>

          {showAdvanced && (
            <div style={{ background: "#0a0a0a", borderRadius: 8, padding: 14, border: "1px solid #1a1a1a", marginTop: 8 }}>
              <div style={{ fontSize: 10, color: "#666", marginBottom: 10, fontFamily: "'JetBrains Mono', monospace" }}>
                Override any auto-calculated rate. Leave blank to use system defaults.
              </div>
              <SliderField
                label="Overhead"
                value={overrides.overhead ?? (ctType?.overhead || 0.1) * overheadScale}
                onChange={(v) => setOverrides({ ...overrides, overhead: v })}
              />
              <SliderField label="G&A" value={overrides.ga ?? (ctType?.ga || 0.05)} onChange={(v) => setOverrides({ ...overrides, ga: v })} />
              <SliderField
                label="Tax Burden"
                value={overrides.tax ?? effectiveTaxRate}
                onChange={(v) => setOverrides({ ...overrides, tax: v })}
                max={0.45}
              />
              {mode === "service" ? (
                <>
                  <SliderField
                    label="D&A"
                    value={overrides.amort ?? (ctType?.amort || 0.03)}
                    onChange={(v) => setOverrides({ ...overrides, amort: v })}
                    max={0.1}
                  />
                  <SliderField
                    label="Contingency"
                    value={overrides.contingency ?? (ctType?.contingency || 0.03)}
                    onChange={(v) => setOverrides({ ...overrides, contingency: v })}
                    max={0.1}
                  />
                </>
              ) : (
                <>
                  <SliderField
                    label="Shipping/Freight"
                    value={overrides.shipping ?? (ctType?.shipping || 0.04)}
                    onChange={(v) => setOverrides({ ...overrides, shipping: v })}
                    max={0.15}
                  />
                  <SliderField
                    label="Storage/Warehousing"
                    value={overrides.storage ?? (ctType?.storage || 0.02)}
                    onChange={(v) => setOverrides({ ...overrides, storage: v })}
                    max={0.1}
                  />
                </>
              )}
              <SliderField
                label="Profit Override"
                value={overrides.profit ?? profLevel.rate}
                onChange={(v) => setOverrides({ ...overrides, profit: v })}
                max={0.35}
              />
              <button onClick={resetOverrides} style={{ ...secondaryBtnStyle, fontSize: 10, padding: "4px 10px", marginTop: 4 }}>
                Reset to Auto
              </button>
            </div>
          )}
        </div>

        {/* RIGHT: Results */}
        <div>
          {calc ? (
            <>
              <SectionHeader label={`Pricing Buildup (Per ${costLabel})`} />

              <div style={{ background: "#111", borderRadius: 8, padding: 16, border: "1px solid #222" }}>
                <BuildupRow label="Direct Cost (Base)" value={fmt(calc.base)} bold />
                <BuildupRow label={`+ Overhead (${pct(calc.oh)})`} value={`+ ${fmt(calc.ohDollars)}`} dim />
                <BuildupRow label={`+ G&A (${pct(calc.ga)})`} value={`+ ${fmt(calc.gaDollars)}`} dim />
                <BuildupRow label={`+ Tax Burden (${pct(calc.tax)})`} value={`+ ${fmt(calc.taxDollars)}`} dim />
                {mode === "service" ? (
                  <>
                    <BuildupRow label={`+ D&A (${pct(calc.amort)})`} value={`+ ${fmt(calc.amortDollars)}`} dim />
                    <BuildupRow label={`+ Contingency (${pct(calc.cont)})`} value={`+ ${fmt(calc.contDollars)}`} dim />
                  </>
                ) : (
                  <>
                    <BuildupRow label={`+ Shipping & Storage (${pct(calc.amort)})`} value={`+ ${fmt(calc.amortDollars)}`} dim />
                    <BuildupRow label={`+ Contingency (${pct(calc.cont)})`} value={`+ ${fmt(calc.contDollars)}`} dim />
                  </>
                )}
                <BuildupRow label={`+ Profit (${pct(calc.profit)})`} value={`+ ${fmt(calc.profitDollars)}`} color="#E8630A" />

                <div
                  style={{
                    borderTop: "2px solid #E8630A",
                    marginTop: 12,
                    paddingTop: 12,
                    display: "flex",
                    justifyContent: "space-between",
                    fontWeight: 700,
                    fontSize: 20,
                    color: "#E8630A",
                    fontFamily: "'JetBrains Mono', monospace",
                  }}
                >
                  <span>SELL PRICE</span>
                  <span>{fmt(calc.proposedPrice)}</span>
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginTop: 14 }}>
                <MetricCard label="Total Markup" value={pct(calc.markupPct)} sub={fmt(calc.totalMarkup)} color="#E8630A" />
                <MetricCard
                  label="Gross Margin"
                  value={pct(calc.grossMargin)}
                  sub="Of sell price"
                  color={calc.grossMargin >= 0.25 ? "#10B981" : "#EF4444"}
                />
                <MetricCard label="Profit Per Unit" value={fmt(calc.profitDollars)} sub={`Per ${costLabel}`} color="#10B981" />
              </div>

              <div style={{ marginTop: 18, background: "#0a0a0a", borderRadius: 8, padding: 16, border: "1px solid #E8630A22" }}>
                <div style={{ ...labelStyle, marginBottom: 12, fontSize: 11, letterSpacing: 2 }}>
                  {mode === "service"
                    ? `Contract Projection — ${calc.totalUnits.toLocaleString()} ${costLabel}s`
                    : `Order Projection — ${calc.totalUnits.toLocaleString()} ${costLabel}s`}
                </div>
                <BuildupRow label="Total Revenue" value={fmt(calc.totalRevenue)} color="#E8630A" />
                <BuildupRow label="Total Direct Cost" value={fmt(calc.totalCost)} color="#EF4444" />
                <div
                  style={{
                    borderTop: "1px solid #333",
                    marginTop: 8,
                    paddingTop: 8,
                    display: "flex",
                    justifyContent: "space-between",
                    fontWeight: 700,
                    fontSize: 18,
                    color: calc.totalProfit > 0 ? "#10B981" : "#EF4444",
                    fontFamily: "'JetBrains Mono', monospace",
                  }}
                >
                  <span>TOTAL PROFIT</span>
                  <span>{fmt(calc.totalProfit)}</span>
                </div>
              </div>

              <div
                style={{
                  marginTop: 14,
                  padding: 12,
                  background: "#0a0a0a",
                  borderRadius: 6,
                  border: "1px solid #1a1a1a",
                  fontSize: 10,
                  color: "#444",
                  fontFamily: "'JetBrains Mono', monospace",
                  lineHeight: 1.8,
                }}
              >
                <span style={{ color: "#E8630A" }}>FORMULA:</span> Cost × (1+OH) × (1+G&A) × (1+Tax) ×
                (1+{mode === "service" ? "D&A" : "Ship+Store"}) × (1+Cont) × (1+Profit)
                <br />
                <span style={{ color: "#E8630A" }}>APPLIED:</span> {fmt(calc.base)} × {(1 + calc.oh).toFixed(3)} ×{" "}
                {(1 + calc.ga).toFixed(3)} × {(1 + calc.tax).toFixed(3)} × {(1 + calc.amort).toFixed(3)} ×{" "}
                {(1 + calc.cont).toFixed(3)} × {(1 + calc.profit).toFixed(3)} ={" "}
                <span style={{ color: "#E8630A" }}>{fmt(calc.proposedPrice)}</span>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 14 }}>
                <HealthCard label="Gross Margin" value={calc.grossMargin} threshold={0.25} good="≥ 25% ✓" bad="< 25% — Consider raising price" />
                <HealthCard label="Markup" value={calc.markupPct} threshold={0.35} good="≥ 35% ✓" bad="< 35% — Risk of loss after costs" />
              </div>

              {calc.grossMargin < 0.25 && (
                <div
                  style={{
                    marginTop: 14,
                    padding: 12,
                    background: "#EF444410",
                    borderRadius: 6,
                    border: "1px solid #EF444433",
                    fontSize: 11,
                    color: "#EF4444",
                    fontFamily: "'JetBrains Mono', monospace",
                    lineHeight: 1.6,
                  }}
                >
                  ⚠ <strong>WARNING:</strong> Your gross margin is below 25%. After taxes and overhead, you may be operating at a loss.
                  Consider increasing your sell price or negotiating lower direct costs.
                </div>
              )}
            </>
          ) : (
            <div style={{ padding: 60, textAlign: "center", color: "#333", fontFamily: "'JetBrains Mono', monospace" }}>
              ← Select a {mode === "service" ? "service" : "product"} type to see pricing
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── P&L STATEMENT TAB ──────────────────────────────────────────────────────

export function PnLStatement() {
  const [contracts, setContracts] = useState<any[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [nc, setNc] = useState({ name: "", revenue: 0, directCosts: 0, type: "service" });

  const autoCalc = (revenue: number, directCosts: number) => {
    const gross = revenue - directCosts;
    return {
      overhead: revenue * 0.1,
      ga: revenue * 0.05,
      tax: Math.max(gross * 0.25, 0),
      amort: revenue * 0.03,
      contingency: revenue * 0.02,
    };
  };

  const addContract = () => {
    if (!nc.name) return;
    const auto = autoCalc(nc.revenue, nc.directCosts);
    setContracts((p) => [...p, { ...nc, ...auto, id: Date.now() }]);
    setNc({ name: "", revenue: 0, directCosts: 0, type: "service" });
    setShowAdd(false);
  };

  const removeContract = (id: number) => setContracts((p) => p.filter((c) => c.id !== id));

  const totals = useMemo(() => {
    return contracts.reduce(
      (acc, c) => {
        const gross = c.revenue - c.directCosts;
        const opProfit = gross - c.overhead - c.ga;
        const net = opProfit - c.tax - c.amort - c.contingency;
        return {
          revenue: acc.revenue + c.revenue,
          directCosts: acc.directCosts + c.directCosts,
          grossProfit: acc.grossProfit + gross,
          overhead: acc.overhead + c.overhead,
          ga: acc.ga + c.ga,
          opProfit: acc.opProfit + opProfit,
          taxes: acc.taxes + c.tax,
          amortization: acc.amortization + c.amort,
          contingency: acc.contingency + c.contingency,
          netProfit: acc.netProfit + net,
        };
      },
      {
        revenue: 0,
        directCosts: 0,
        grossProfit: 0,
        overhead: 0,
        ga: 0,
        opProfit: 0,
        taxes: 0,
        amortization: 0,
        contingency: 0,
        netProfit: 0,
      }
    );
  }, [contracts]);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <SectionHeader label="Contracts & Engagements" />
        <button
          onClick={() => setShowAdd(!showAdd)}
          style={{
            padding: "6px 14px",
            borderRadius: 6,
            border: "1px solid #E8630A",
            background: showAdd ? "#E8630A" : "transparent",
            color: showAdd ? "#000" : "#E8630A",
            cursor: "pointer",
            fontSize: 12,
            fontFamily: "'JetBrains Mono', monospace",
            fontWeight: 700,
          }}
        >
          {showAdd ? "✕ CANCEL" : "+ ADD"}
        </button>
      </div>

      {showAdd && (
        <div style={{ background: "#111", borderRadius: 8, padding: 16, border: "1px solid #E8630A33", marginBottom: 20 }}>
          <p style={{ color: "#666", fontSize: 10, marginBottom: 12, fontFamily: "'JetBrains Mono', monospace" }}>
            Just enter the contract name, revenue, and direct costs. Overhead, taxes, and amortization are auto-calculated.
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: 12 }}>
            <FormInput label="Contract Name" value={nc.name} onChange={(v) => setNc({ ...nc, name: v })} text />
            <FormInput label="Revenue" value={nc.revenue} onChange={(v) => setNc({ ...nc, revenue: v })} />
            <FormInput label="Direct Costs" value={nc.directCosts} onChange={(v) => setNc({ ...nc, directCosts: v })} />
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
            {(["service", "product"] as const).map((t) => (
              <button
                key={t}
                onClick={() => setNc({ ...nc, type: t })}
                style={{
                  padding: "5px 12px",
                  borderRadius: 4,
                  border: nc.type === t ? "1px solid #E8630A" : "1px solid #222",
                  background: nc.type === t ? "#E8630A10" : "#0a0a0a",
                  color: nc.type === t ? "#E8630A" : "#666",
                  cursor: "pointer",
                  fontSize: 10,
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              >
                {t === "service" ? "⚙️ Service" : "📦 Product"}
              </button>
            ))}
          </div>
          <button onClick={addContract} style={{ ...primaryBtnStyle, marginTop: 12, fontSize: 11, padding: "8px 20px" }}>
            ADD TO P&L
          </button>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 24 }}>
        {contracts.map((c, i) => {
          const gross = c.revenue - c.directCosts;
          const net = gross - c.overhead - c.ga - c.tax - c.amort - c.contingency;
          const netPct = c.revenue > 0 ? net / c.revenue : 0;
          const color = ["#E8630A", "#0A84E8", "#7C3AED", "#059669", "#DC2626", "#B45309", "#EC4899", "#14B8A6"][i % 8];
          return (
            <div
              key={c.id}
              style={{
                background: "#111",
                borderRadius: 8,
                padding: 14,
                borderLeft: `3px solid ${color}`,
                display: "grid",
                gridTemplateColumns: "2fr 1fr 1fr 1fr auto",
                alignItems: "center",
                gap: 16,
              }}
            >
              <div>
                <div style={{ color: "#fff", fontSize: 13, fontWeight: 600, fontFamily: "'JetBrains Mono', monospace" }}>{c.name}</div>
                <div style={{ color: "#555", fontSize: 10, marginTop: 2, fontFamily: "'JetBrains Mono', monospace" }}>
                  {c.type === "service" ? "⚙️ Service" : "📦 Product"}
                </div>
              </div>
              <CellValue label="Revenue" value={fmt(c.revenue)} />
              <CellValue label="Net Profit" value={fmt(net)} color={net > 0 ? "#10B981" : "#EF4444"} />
              <CellValue label="Net %" value={pct(netPct)} color={netPct >= 0.08 ? "#10B981" : "#EF4444"} />
              <button
                onClick={() => removeContract(c.id)}
                style={{ background: "none", border: "none", color: "#444", cursor: "pointer", fontSize: 16, padding: 4 }}
              >
                ✕
              </button>
            </div>
          );
        })}
        {contracts.length === 0 && (
          <div
            style={{
              padding: 40,
              textAlign: "center",
              color: "#333",
              fontSize: 12,
              fontFamily: "'JetBrains Mono', monospace",
              border: "1px dashed #222",
              borderRadius: 8,
            }}
          >
            No contracts yet. Click "+ ADD" to build your P&L.
          </div>
        )}
      </div>

      {contracts.length > 0 && (
        <>
          <div style={{ background: "#0a0a0a", borderRadius: 10, padding: 24, border: "1px solid #222" }}>
            <SectionHeader label="Consolidated Profit & Loss" />
            <PnLLine label="REVENUE" value={totals.revenue} bold />
            <PnLLine label="Less: Direct Costs" value={-totals.directCosts} indent color="#EF4444" />
            <PnLLine label="GROSS PROFIT" value={totals.grossProfit} bold color="#10B981" divider />
            <PnLLine
              label="Gross Margin"
              value={totals.revenue > 0 ? totals.grossProfit / totals.revenue : 0}
              isPct
              color={totals.revenue > 0 && totals.grossProfit / totals.revenue >= 0.25 ? "#10B981" : "#F59E0B"}
            />
            <div style={{ height: 12 }} />
            <PnLLine label="Less: Overhead" value={-totals.overhead} indent color="#F59E0B" />
            <PnLLine label="Less: G&A" value={-totals.ga} indent color="#F59E0B" />
            <PnLLine label="OPERATING PROFIT" value={totals.opProfit} bold color="#10B981" divider />
            <div style={{ height: 12 }} />
            <PnLLine label="Less: Tax Reserve" value={-totals.taxes} indent color="#EF4444" />
            <PnLLine label="Less: D&A" value={-totals.amortization} indent color="#EF4444" />
            <PnLLine label="Less: Contingency" value={-totals.contingency} indent color="#EF4444" />
            <div
              style={{
                borderTop: "2px solid #E8630A",
                marginTop: 16,
                paddingTop: 16,
                display: "flex",
                justifyContent: "space-between",
                fontWeight: 700,
                fontSize: 20,
                color: totals.netProfit > 0 ? "#10B981" : "#EF4444",
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              <span>NET PROFIT</span>
              <span>{fmt(totals.netProfit)}</span>
            </div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontSize: 12,
                color: "#888",
                marginTop: 4,
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              <span>Net Margin</span>
              <span>{totals.revenue > 0 ? pct(totals.netProfit / totals.revenue) : "0.0%"}</span>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 12, marginTop: 20 }}>
            <HealthCard label="Gross Margin" value={totals.revenue > 0 ? totals.grossProfit / totals.revenue : 0} threshold={0.25} good="≥ 25%" bad="< 25%" />
            <HealthCard label="Net Margin" value={totals.revenue > 0 ? totals.netProfit / totals.revenue : 0} threshold={0.08} good="≥ 8%" bad="< 8%" />
            <HealthCard
              label="OH + G&A Ratio"
              value={totals.revenue > 0 ? (totals.overhead + totals.ga) / totals.revenue : 0}
              threshold={0.18}
              invert
              good="< 18%"
              bad="≥ 18%"
            />
            <HealthCard label="Tax Load" value={totals.revenue > 0 ? totals.taxes / totals.revenue : 0} threshold={0.2} invert good="< 20%" bad="≥ 20%" />
          </div>
        </>
      )}
    </div>
  );
}

// Components exported: AutoPricingCalculator, PnLStatement
// Integrated into DocumentGenerator as tabs
