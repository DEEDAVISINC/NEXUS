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
| **NAICS Codes** | 484110, 484121, 484122, 484210, 484220, 484230, 488510, 488999, 492110, 493110, 493120 |
| **Set-Aside** | WOSB, EDWOSB, Small Business, Total Small Business |
| **Notice Type** | Solicitation, Combined Synopsis/Solicitation, Sources Sought |
| **Active Only** | Yes |

### Keywords to Search

**By Freight Lane — Run ALL:**

**General Freight (Dry Van):**
- freight, shipping, trucking, LTL, truckload, dry van, general freight, transportation of goods

**Refrigerated:**
- refrigerated transport, reefer, cold chain, temperature controlled, food distribution, commodity distribution, TEFAP, frozen transport, pharmaceutical transport

**Flatbed / Construction Materials:**
- flatbed, construction materials transport, steel transport, lumber transport, heavy equipment, step deck, building materials

**Heavy Haul / Oversize:**
- heavy haul, oversize, overweight, oversized load, specialized transport, wide load, lowboy, RGN, crane transport

**Auto Transport / Vehicle Hauling:**
- auto transport, vehicle transport, car hauling, fleet vehicle, GSA Fleet, PCS vehicle, vehicle relocation, driveaway

**Hotshot / Expedited:**
- hotshot, expedited freight, time-critical, urgent delivery, AOG, same-day freight, emergency shipment

**Tanker / Bulk Liquid:**
- tanker, bulk fuel, JP-8, fuel transport, fuel distribution, bulk liquid, petroleum transport, chemical transport, water transport

**Intermodal / Drayage:**
- intermodal, drayage, container hauling, port drayage, container transport, chassis, rail drayage

**Moving / Household Goods:**
- household goods, HHG, PCS move, military move, government relocation, office relocation, employee relocation, GBL

**3PL / Program-Level:**
- 3PL, third party logistics, freight management, transportation services, distribution services, supply chain, managed transportation

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

## TOP AGENCIES BY FREIGHT LANE

| Agency | Dry Van | Reefer | Flatbed | Heavy Haul | Auto | Hotshot | Tanker | Intermodal | Moving/HHG |
|---|---|---|---|---|---|---|---|---|---|
| **DLA** | ★★★ | ★★ | ★★ | ★ | | ★ | ★★★ | ★★ | |
| **TRANSCOM** | ★★★ | ★★ | ★★★ | ★★★ | ★★★ | ★★ | ★★ | ★★★ | ★★★ |
| **SDDC** | ★★ | ★★ | ★★★ | ★★★ | ★★★ | ★★ | ★★ | ★★★ | ★★★ |
| **GSA** | ★★ | ★ | ★ | | ★★★ | ★ | | ★ | ★★ |
| **VA** | ★★ | ★★★ | ★ | | | ★★ | | | |
| **USDA** | ★ | ★★★ | | | | | ★ | | |
| **USPS** | ★★★ | | | | | | | | |
| **FEMA** | ★★★ | ★★★ | ★★★ | ★★ | | ★★★ | ★★ | | |
| **USACE** | | | ★★★ | ★★★ | | ★★ | | | |
| **DOE** | | | ★★ | ★★★ | | ★ | ★★ | | |
| **State DOTs** | ★ | | ★★★ | ★★ | | ★ | | | |

★★★ = Major buyer | ★★ = Regular buyer | ★ = Occasional buyer

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
    # General Freight
    "484110",  # General Freight Trucking, Local
    "484121",  # General Freight Trucking, Long-Distance, Truckload
    "484122",  # General Freight Trucking, Long-Distance, LTL
    # Specialized Freight
    "484210",  # Used Household/Office Goods Moving (Military PCS/HHG)
    "484220",  # Specialized Freight Trucking, Long-Distance (heavy haul, tanker, oversize)
    "484230",  # Specialized Freight (auto transport, specialized cargo)
    # Support / Brokerage
    "488510",  # Freight Transportation Arrangement (brokerage)
    "488999",  # All Other Support Activities for Transportation
    # Courier / Expedited
    "492110",  # Couriers and Express Delivery (hotshot, expedited)
    # Warehousing (cross-dock/staging)
    "493110",  # General Warehousing and Storage
    "493120",  # Refrigerated Warehousing and Storage
]
```

### Lane-Specific Keyword Sets (for targeted mining)

```python
FREIGHT_LANE_KEYWORDS = {
    "reefer": ["refrigerated", "cold chain", "temperature controlled", "frozen", "TEFAP", "commodity distribution"],
    "flatbed": ["flatbed", "construction materials", "steel", "lumber", "step deck"],
    "heavy_haul": ["heavy haul", "oversize", "overweight", "lowboy", "RGN", "crane transport"],
    "auto_transport": ["auto transport", "vehicle transport", "car hauling", "GSA Fleet", "PCS vehicle", "driveaway"],
    "tanker": ["tanker", "bulk fuel", "JP-8", "fuel transport", "petroleum", "bulk liquid"],
    "intermodal": ["intermodal", "drayage", "container", "port drayage", "chassis"],
    "hhg": ["household goods", "HHG", "PCS move", "military move", "relocation", "GBL"],
    "hotshot": ["hotshot", "expedited", "time-critical", "AOG", "urgent delivery"],
}
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

**Value prop:** DDI is a Contract Management TPA (MC-1647572, DOT-4250594) with a credentialed owner-operator carrier network. EDWOSB prime contractor for federal freight — one contract, one invoice, vetted carrier pool.

**Best fit contracts:**
- **USPS Highway Contract Routes (HCR)** — multi-year, steady, $3.80-$5.20/mile
- **FEMA pre-positioned logistics** — seasonal, high rates during activation
- **DOD/SDDC base resupply** — steady volume, CONUS freight
- **DLA distribution center freight** — high volume, reliable
- LTL programs (multiple smaller shipments over time)
- Equipment returns / reverse logistics
- Regional distribution (Michigan/Midwest)
- Government surplus/disposal shipping
- Medical equipment transport

**Fulfillment:** Credentialed OO network managed through Freight 1st Direct Federal Carrier Qualification Program.
**See:** `FREIGHT_1ST_DIRECT_OO_PROGRAM.md` for full program framework.

---

## NON-SAM.GOV CHANNELS (ADD TO WEEKLY CHECK)

| Channel | URL | Lanes | What to Check |
|---|---|---|---|
| **USPS eSourcing (Coupa)** | usps.coupa.com | Dry van | Highway Contract Routes, surface mail transport |
| **USPS Logistics Gateway** | logistics.usps.com | Dry van | HCR bidding portal (⚠️ needs active SCAC) |
| **FEMA Vendor Program** | fema.gov/grants/procurement/doing-business | All | Pre-positioned logistics, emergency freight |
| **SDDC** | sddc.army.mil | Heavy, auto, HHG, intermodal | Military freight, PCS moves, vehicle shipping |
| **SDDC Personal Property** | move.mil | HHG/Moving | Military household goods moves (PCS program) |
| **GSA eBuy** | ebuy.gsa.gov | All | Task orders for Schedule 48 holders |
| **GSA Fleet** | gsa.gov/buying-selling/products-services/transportation-logistics-services | Auto transport | Government vehicle distribution contracts |
| **DLA Distribution** | dla.mil/distribution | Dry van, reefer, tanker, intermodal | DLA distribution center freight, fuel distribution |
| **USDA TEFAP** | fns.usda.gov/tefap | Reefer | Emergency food assistance commodity transport |
| **State DOT portals** | Various | Flatbed, heavy haul | Bridge materials, guardrails, equipment transport |
| **DAT/Truckstop** | dat.com / truckstop.com | All (commercial) | Commercial load boards — backfill between federal |
| **FHWA** | fhwa.dot.gov | Flatbed, heavy haul | Highway construction material transport |

---

## LANE-SPECIFIC OPPORTUNITY EXAMPLES (What to Look For)

### Reefer Lane Targets
- USDA commodity distribution (TEFAP, CSFP, FDPIR) — delivers food to food banks, tribal nations, schools
- VA pharmaceutical transport — hospitals need temp-controlled Rx delivery
- DOD base food service — military dining facilities need frozen/refrigerated supply chains
- FEMA disaster food supply — MREs, water, perishables during activations
- State WIC programs — Women, Infants, Children food distribution

### Auto Transport Targets
- GSA Fleet vehicle distribution — 225,000+ vehicles managed, constant movement
- Military PCS vehicle shipping — soldiers PCS every 2-3 years, vehicles ship too
- DHS/CBP patrol vehicle distribution — new vehicle deliveries to border stations
- USPS mail truck replacement — ongoing multi-year NGDV (Next Generation Delivery Vehicle) rollout
- State/local government fleet purchases — police cruisers, fire trucks, ambulances

### Heavy Haul Targets
- USACE construction projects — dam repairs, levee construction, bridge replacement
- DOD base infrastructure — barracks, hangars, runways need heavy materials
- FEMA temporary structures — generators, modular buildings for disaster response
- DOE energy infrastructure — wind turbine components, transformer transport
- State DOT bridge beams and steel — every state rebuilds infrastructure annually

### Tanker Targets
- DLA bulk fuel — JP-8 to military bases (one of the largest federal freight programs period)
- FEMA fuel distribution — disaster zone fuel supply
- DOE strategic petroleum reserve — fuel movement and management
- Federal facility water delivery — remote installations need potable water transport
- Chemical transport for federal labs — DOE, EPA, VA research facilities

### Military HHG/Moving Targets
- SDDC Personal Property Program — millions of military moves per year
- State Department diplomatic moves — embassies, consulates worldwide
- GSA government employee relocation — civilian federal employees transfer too
- VA employee relocation — new VA facility openings create move clusters

---

*Run ALL lane searches weekly. More equipment types = more contracts = more OOs busy = more DDI revenue. The multi-lane approach is how you fill 125+ loads/week.*
