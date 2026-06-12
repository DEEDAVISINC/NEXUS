# QC Contract Profile — [BUYER NAME]

**Contract ID:** [CTR-XXX]  
**Service lane(s):** [nemt / drug_testing / notary / …]  
**Period of performance:** [START] – [END]  
**Last updated:** [DATE]

---

## Buyer / plan contacts

| Role | Name | Email | Phone |
|------|------|-------|-------|
| QC / audit contact | | | |
| Contracting / vendor relations | | | |
| DDI owner | Dieasha D. Davis | info@deedavis.biz | 248.376.4550 |

---

## Registration

| Field | Value |
|-------|-------|
| Vendor ID | |
| NPI (if healthcare) | |
| COMPASS contract ID | |
| VERTEX client name | |

---

## Rate sheet → VERTEX

| CLIN / HCPCS | Description | DDI rate | VERTEX map |
|--------------|-------------|----------|------------|
| | | | |

---

## SLAs (plan-specific)

| Metric | Target | How measured | Module |
|--------|--------|--------------|--------|
| On-time performance | | PRISM timestamps | Pillar 3 |
| Member satisfaction | | Trip grades A–F | Pillar 6 |
| Grievance response | ≤ 48h | `nexus_qc_grievances.json` | Pillar 6 |
| Audit packet turnaround | ≤ 2 business days | MCO breakdown export | Pillar 9 |

---

## Subcontractors (if any)

| Sub | Service | 6-pillar status | COI expiry |
|-----|---------|-----------------|------------|
| | | | |

---

## Reporting cadence

| Deliverable | Frequency | Due | COMPASS owner |
|-------------|-----------|-----|---------------|
| | | | |

---

## MCO audit exports (quick reference)

| Plan asks for… | Export URL |
|----------------|------------|
| Full QC breakdown | `/nexus/qc/mco/breakdown.html?payer=[PLAN]` |
| Member trip grades | `/prism/nemt/satisfaction/mco-packet.html?payer=[PLAN]` |
| Match any request text | `/nexus/qc/mco/match?q=[query]` |
| Grievance log | `/nexus/qc/grievances?payer=[PLAN]` |

---

## Notes

[Contract-specific QC requirements from plan manual.]
