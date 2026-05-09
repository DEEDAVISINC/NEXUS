# FREIGHT & LOGISTICS OPPORTUNITY SEARCH STRATEGY

**Created:** May 8, 2026  
**Purpose:** Find ALL freight/shipping contracts — volume builds cash flow, larger ones are priority

---

## SAM.GOV SAVED SEARCH — FREIGHT/LOGISTICS

### Search URL (Bookmark This)

```
https://sam.gov/search/?keywords=freight%20OR%20shipping%20OR%20logistics%20OR%20LTL%20OR%20transportation%20of%20goods%20OR%20trucking&sort=-modifiedDate&index=opp&is_active=true&page=1
```

### Filters to Apply

| Filter | Setting |
|---|---|
| **NAICS Codes** | 488510, 484110, 484121, 488999 |
| **Set-Aside** | WOSB, EDWOSB, Small Business, Total Small Business |
| **Notice Type** | Solicitation, Combined Synopsis/Solicitation, Sources Sought |
| **Active Only** | Yes |

### Keywords to Search

**Primary:**
- freight
- shipping
- logistics
- LTL
- transportation of goods
- trucking
- freight forwarding

**Secondary (larger contracts):**
- 3PL (Third Party Logistics)
- freight management
- transportation services
- distribution services
- supply chain
- intermodal

---

## CONTRACT PRIORITIZATION

**HIGH PRIORITY (larger recurring revenue):**
- **IDIQ contracts** — Indefinite Delivery, Indefinite Quantity = recurring revenue
- **Multi-year contracts** — Base + option years
- **3PL / Managed freight** — Program-level logistics management
- **Regional freight programs** — Multiple shipments over time
- **Agency-wide freight contracts** — GSA, DLA, VA blanket freight needs

**STILL PURSUE (volume play — builds past performance + cash flow):**
- Individual equipment shipping
- Single-item moves
- Small parts shipments
- One-time shipments

**Strategy:** Capture everything. Smaller wins build track record and keep revenue flowing. Larger IDIQ/multi-year contracts are the priority targets.

---

## TOP AGENCIES FOR FREIGHT CONTRACTS

| Agency | Why |
|---|---|
| **DLA (Defense Logistics Agency)** | Huge freight volume, multiple programs |
| **TRANSCOM** | All DoD transportation |
| **SDDC (Surface Deployment & Distribution Command)** | Army freight |
| **GSA** | Civilian agency freight programs |
| **VA** | Medical equipment, supplies shipping |
| **USDA** | Agricultural shipments |

---

## USASPENDING SEARCH — EXPIRING FREIGHT CONTRACTS

Search for freight contracts expiring in 6-12 months → email the CO before recompete.

**URL:**
```
https://www.usaspending.gov/search/?hash=FREIGHT_SEARCH
```

**Filters:**
- NAICS: 488510, 484110, 484121
- End Date: Next 6-12 months
- Award Amount: Any (capture all, prioritize larger)

---

## NEXUS AUTO-MINE INTEGRATION

Add these NAICS codes to the auto-miner:

```python
FREIGHT_NAICS = [
    "488510",  # Freight Transportation Arrangement
    "484110",  # General Freight Trucking, Local
    "484121",  # General Freight Trucking, Long-Distance, Truckload
    "484122",  # General Freight Trucking, Long-Distance, LTL
    "488999",  # All Other Support Activities for Transportation
]
```

---

## WEEKLY CHECK ROUTINE

Every Monday:
1. Run SAM.gov saved search
2. Filter for WOSB/EDWOSB set-asides
3. **Capture ALL opportunities** — small ones add up, big ones are priority
4. **Flag IDIQ and multi-year contracts** as high priority
5. Check USASpending for expiring contracts in target NAICS

**Approach:** Take the volume (smaller contracts build track record and cash flow), prioritize the larger IDIQ/multi-year programs.

---

## DDI FREIGHT POSITIONING

**Value prop:** DDI is a Contract Management TPA that can broker freight through Uber Freight — no asset ownership, flexible capacity, competitive rates.

**Best fit contracts:**
- LTL programs (multiple smaller shipments over time)
- Equipment returns / reverse logistics
- Regional distribution (Michigan/Midwest)
- Government surplus/disposal shipping
- Medical equipment transport

---

*Run this search weekly. Capture everything — small wins add up, big wins are the goal.*
