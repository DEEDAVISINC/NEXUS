"""
DDI service-lane relevance for government opportunities.
Shared by miners, dashboard, and any scoring that asks "does this fit us?"
"""

from __future__ import annotations

import re
from typing import Any, Dict, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# Same keyword / NAICS universe as presolicitation miner (keep in sync intentionally)
# ─────────────────────────────────────────────────────────────────────────────

DDI_KEYWORDS = {
    # Drug Testing Services
    "drug test": "Drug & Alcohol Testing",
    "drug screen": "Drug & Alcohol Testing",
    "drug testing": "Drug & Alcohol Testing",
    "drug and alcohol testing": "Drug & Alcohol Testing",
    "drug & alcohol testing": "Drug & Alcohol Testing",
    "substance abuse": "Drug & Alcohol Testing",
    "substance abuse testing": "Drug & Alcohol Testing",
    "toxicology": "Drug & Alcohol Testing",
    "toxicology testing": "Drug & Alcohol Testing",
    "urine test": "Drug & Alcohol Testing",
    "urine drug screen": "Drug & Alcohol Testing",
    "uds": "Drug & Alcohol Testing",
    "alcohol test": "Drug & Alcohol Testing",
    "alcohol testing": "Drug & Alcohol Testing",
    "breath alcohol": "Drug & Alcohol Testing",
    "breath alcohol test": "Drug & Alcohol Testing",
    "bat": "Drug & Alcohol Testing",
    "evidential breath testing": "Drug & Alcohol Testing",
    "ebt": "Drug & Alcohol Testing",
    "dot compliance": "Drug & Alcohol Testing",
    "dot drug testing": "Drug & Alcohol Testing",
    "dot testing": "Drug & Alcohol Testing",
    "dot physical": "Drug & Alcohol Testing",
    "fmcsa testing": "Drug & Alcohol Testing",
    "fta testing": "Drug & Alcohol Testing",
    "fra testing": "Drug & Alcohol Testing",
    "phmsa testing": "Drug & Alcohol Testing",
    "uscg testing": "Drug & Alcohol Testing",
    "49 cfr part 40": "Drug & Alcohol Testing",
    "part 40": "Drug & Alcohol Testing",
    "random testing": "Drug & Alcohol Testing",
    "random drug testing": "Drug & Alcohol Testing",
    "random pool": "Drug & Alcohol Testing",
    "pre-employment screening": "Drug & Alcohol Testing",
    "pre employment screening": "Drug & Alcohol Testing",
    "pre-employment drug": "Drug & Alcohol Testing",
    "pre employment drug": "Drug & Alcohol Testing",
    "post-accident testing": "Drug & Alcohol Testing",
    "post accident testing": "Drug & Alcohol Testing",
    "reasonable suspicion": "Drug & Alcohol Testing",
    "reasonable cause": "Drug & Alcohol Testing",
    "return to duty": "Drug & Alcohol Testing",
    "follow-up testing": "Drug & Alcohol Testing",
    "occupational health testing": "Drug & Alcohol Testing",
    "employee drug": "Drug & Alcohol Testing",
    "employee testing": "Drug & Alcohol Testing",
    "workplace drug testing": "Drug & Alcohol Testing",
    "workplace testing": "Drug & Alcohol Testing",
    "mro service": "Drug & Alcohol Testing",
    "medical review officer": "Drug & Alcohol Testing",
    "mro": "Drug & Alcohol Testing",
    "sap service": "Drug & Alcohol Testing",
    "substance abuse professional": "Drug & Alcohol Testing",
    "oral fluid": "Drug & Alcohol Testing",
    "oral fluid testing": "Drug & Alcohol Testing",
    "saliva test": "Drug & Alcohol Testing",
    "hair follicle": "Drug & Alcohol Testing",
    "hair testing": "Drug & Alcohol Testing",
    "instant test": "Drug & Alcohol Testing",
    "rapid test": "Drug & Alcohol Testing",
    "point of collection": "Drug & Alcohol Testing",
    "poct": "Drug & Alcohol Testing",
    "samhsa certified": "Drug & Alcohol Testing",
    "hhs certified lab": "Drug & Alcohol Testing",
    "c/tpa": "Drug & Alcohol Testing",
    "consortium": "Drug & Alcohol Testing",
    "third party administrator drug": "Drug & Alcohol Testing",
    "drug testing program": "Drug & Alcohol Testing",
    "clearinghouse": "Drug & Alcohol Testing",
    "fmcsa clearinghouse": "Drug & Alcohol Testing",
    # Drug Testing Supplies
    "drug testing supplies": "Drug Testing Supplies",
    "drug test supplies": "Drug Testing Supplies",
    "drug test kit": "Drug Testing Supplies",
    "drug testing kit": "Drug Testing Supplies",
    "urine collection": "Drug Testing Supplies",
    "urine cup": "Drug Testing Supplies",
    "specimen cup": "Drug Testing Supplies",
    "collection cup": "Drug Testing Supplies",
    "collection kit": "Drug Testing Supplies",
    "drug screen cup": "Drug Testing Supplies",
    "instant drug test": "Drug Testing Supplies",
    "rapid drug test": "Drug Testing Supplies",
    "drug test panel": "Drug Testing Supplies",
    "5 panel": "Drug Testing Supplies",
    "10 panel": "Drug Testing Supplies",
    "12 panel": "Drug Testing Supplies",
    "multi panel": "Drug Testing Supplies",
    "oral fluid device": "Drug Testing Supplies",
    "saliva drug test": "Drug Testing Supplies",
    "breathalyzer": "Drug Testing Supplies",
    "breath alcohol device": "Drug Testing Supplies",
    "alcohol test strip": "Drug Testing Supplies",
    "etg test": "Drug Testing Supplies",
    "adulteration test": "Drug Testing Supplies",
    "specimen validity": "Drug Testing Supplies",
    "temperature strip": "Drug Testing Supplies",
    "chain of custody form": "Drug Testing Supplies",
    "ccf": "Drug Testing Supplies",
    "federal ccf": "Drug Testing Supplies",
    "non-dot ccf": "Drug Testing Supplies",
    "collection supplies": "Drug Testing Supplies",
    "lab supplies": "Drug Testing Supplies",
    "fingerprint": "Fingerprinting & Background Checks",
    "biometric": "Fingerprinting & Background Checks",
    "background check": "Fingerprinting & Background Checks",
    "background investigation": "Fingerprinting & Background Checks",
    "livescan": "Fingerprinting & Background Checks",
    "live scan": "Fingerprinting & Background Checks",
    "identity verification": "Fingerprinting & Background Checks",
    "credentialing": "Fingerprinting & Background Checks",
    "security clearance": "Fingerprinting & Background Checks",
    "channeler": "Fingerprinting & Background Checks",
    "fbi channeler": "Fingerprinting & Background Checks",
    "cjis": "Fingerprinting & Background Checks",
    "criminal history record": "Fingerprinting & Background Checks",
    "criminal background": "Fingerprinting & Background Checks",
    "noncriminal justice": "Fingerprinting & Background Checks",
    "identity history summary": "Fingerprinting & Background Checks",
    "dna test": "DNA & Genetic Testing",
    "genetic test": "DNA & Genetic Testing",
    "paternity": "DNA & Genetic Testing",
    "dna collection": "DNA & Genetic Testing",
    "dna sample": "DNA & Genetic Testing",
    "buccal swab": "DNA & Genetic Testing",
    "chain of custody dna": "DNA & Genetic Testing",
    "child support dna": "DNA & Genetic Testing",
    "parentage": "DNA & Genetic Testing",
    "aabb": "DNA & Genetic Testing",
    "nemt": "NEMT & Healthcare Transportation",
    "non-emergency medical": "NEMT & Healthcare Transportation",
    "non emergency medical": "NEMT & Healthcare Transportation",
    "medical transportation": "NEMT & Healthcare Transportation",
    "patient transport": "NEMT & Healthcare Transportation",
    "medical shuttle": "NEMT & Healthcare Transportation",
    "ambulatory transport": "NEMT & Healthcare Transportation",
    "medicaid transport": "NEMT & Healthcare Transportation",
    "wheelchair transport": "NEMT & Healthcare Transportation",
    "dialysis transport": "NEMT & Healthcare Transportation",
    "veteran home transport": "NEMT & Healthcare Transportation",
    "veterans home transport": "NEMT & Healthcare Transportation",
    "veteran facility transport": "NEMT & Healthcare Transportation",
    "mvfa": "NEMT & Healthcare Transportation",
    "mvhgr": "NEMT & Healthcare Transportation",
    "mvhct": "NEMT & Healthcare Transportation",
    "corrections transport": "NEMT & Healthcare Transportation",
    "prisoner transport": "NEMT & Healthcare Transportation",
    "inmate transport": "NEMT & Healthcare Transportation",
    "inmate medical transport": "NEMT & Healthcare Transportation",
    "behavioral health transport": "NEMT & Healthcare Transportation",
    "mental health transport": "NEMT & Healthcare Transportation",
    "cmh transport": "NEMT & Healthcare Transportation",
    "community mental health transport": "NEMT & Healthcare Transportation",
    "senior transport": "NEMT & Healthcare Transportation",
    "elderly transport": "NEMT & Healthcare Transportation",
    "area agency on aging": "NEMT & Healthcare Transportation",
    "paratransit": "NEMT & Healthcare Transportation",
    "demand response transport": "NEMT & Healthcare Transportation",
    "underserved area transport": "NEMT & Healthcare Transportation",
    "underserved population transport": "NEMT & Healthcare Transportation",
    "rural health transport": "NEMT & Healthcare Transportation",
    "rural transportation": "NEMT & Healthcare Transportation",
    "rural transit": "NEMT & Healthcare Transportation",
    "tribal health transport": "NEMT & Healthcare Transportation",
    "tribal transport": "NEMT & Healthcare Transportation",
    "indian health service": "NEMT & Healthcare Transportation",
    "ihs transport": "NEMT & Healthcare Transportation",
    "developmental disabilities transport": "NEMT & Healthcare Transportation",
    "dd transport": "NEMT & Healthcare Transportation",
    "waiver transport": "NEMT & Healthcare Transportation",
    "hcbs transport": "NEMT & Healthcare Transportation",
    "home community based transport": "NEMT & Healthcare Transportation",
    "critical access hospital": "NEMT & Healthcare Transportation",
    "state veteran home": "NEMT & Healthcare Transportation",
    "state corrections transport": "NEMT & Healthcare Transportation",
    "department of corrections": "NEMT & Healthcare Transportation",
    "doc transport": "NEMT & Healthcare Transportation",
    "jail medical transport": "NEMT & Healthcare Transportation",
    "detainee transport": "NEMT & Healthcare Transportation",
    "detainee medical": "NEMT & Healthcare Transportation",
    "medically underserved": "NEMT & Healthcare Transportation",
    "health shortage area": "NEMT & Healthcare Transportation",
    "freight broker": "Freight & Logistics",
    "freight brokerage": "Freight & Logistics",
    "freight service": "Freight & Logistics",
    "ltl": "Freight & Logistics",
    "less than truckload": "Freight & Logistics",
    "courier": "Freight & Logistics",
    "courier service": "Freight & Logistics",
    "courier services": "Freight & Logistics",
    # Medical Courier
    "medical courier": "Medical Courier",
    "healthcare courier": "Medical Courier",
    "hospital courier": "Medical Courier",
    "medical delivery": "Medical Courier",
    "medical document delivery": "Medical Courier",
    "medical records delivery": "Medical Courier",
    "medical supply delivery": "Medical Courier",
    "dme delivery": "Medical Courier",
    "medical equipment delivery": "Medical Courier",
    "organ transport": "Medical Courier",
    "blood transport": "Medical Courier",
    "tissue transport": "Medical Courier",
    # Lab Courier / Specimen Transport
    "lab courier": "Lab Courier",
    "laboratory courier": "Lab Courier",
    "specimen transport": "Lab Courier",
    "specimen pickup": "Lab Courier",
    "specimen delivery": "Lab Courier",
    "specimen courier": "Lab Courier",
    "clinical specimen": "Lab Courier",
    "clinical sample": "Lab Courier",
    "lab sample transport": "Lab Courier",
    "diagnostic specimen": "Lab Courier",
    "pathology courier": "Lab Courier",
    "lab logistics": "Lab Courier",
    "reference lab": "Lab Courier",
    "newborn screening": "Lab Courier",
    "blood sample transport": "Lab Courier",
    "urine sample transport": "Lab Courier",
    # Pharmacy Courier
    "pharmacy courier": "Pharmacy Courier",
    "pharmacy delivery": "Pharmacy Courier",
    "prescription delivery": "Pharmacy Courier",
    "medication delivery": "Pharmacy Courier",
    "rx delivery": "Pharmacy Courier",
    "pharmaceutical delivery": "Pharmacy Courier",
    "pharmaceutical courier": "Pharmacy Courier",
    "controlled substance delivery": "Pharmacy Courier",
    "specialty pharmacy delivery": "Pharmacy Courier",
    "mail order pharmacy": "Pharmacy Courier",
    "pharmacy distribution": "Pharmacy Courier",
    "medication distribution": "Pharmacy Courier",
    "drug distribution": "Pharmacy Courier",
    "pharmaceutical distribution": "Pharmacy Courier",
    "cold chain": "Pharmacy Courier",
    "temperature controlled delivery": "Pharmacy Courier",
    "refrigerated delivery": "Pharmacy Courier",
    # Legal Courier
    "legal courier": "Legal Courier",
    "court courier": "Legal Courier",
    "court filing": "Legal Courier",
    "legal document delivery": "Legal Courier",
    "process server": "Legal Courier",
    "process serving": "Legal Courier",
    "legal messenger": "Legal Courier",
    "court filing service": "Legal Courier",
    "legal filing": "Legal Courier",
    "document filing service": "Legal Courier",
    "court document": "Legal Courier",
    "legal records": "Legal Courier",
    "subpoena service": "Legal Courier",
    "summons service": "Legal Courier",
    # General Logistics
    "logistics service": "Freight & Logistics",
    "delivery service": "Freight & Logistics",
    "parcel delivery": "Freight & Logistics",
    "last mile": "Freight & Logistics",
    "supply chain": "Freight & Logistics",
    "aircraft parts courier": "Freight & Logistics / AOG Courier",
    "aog courier": "Freight & Logistics / AOG Courier",
    "aog delivery": "Freight & Logistics / AOG Courier",
    "aviation courier": "Freight & Logistics / AOG Courier",
    "aircraft on ground": "Freight & Logistics / AOG Courier",
    "aog": "Freight & Logistics / AOG Courier",
    "into plane fuel": "JETA / Jet Fuel Supply",
    "flight line fuel": "JETA / Jet Fuel Supply",
    "jet fuel": "JETA / Jet Fuel Supply",
    "aviation fuel": "JETA / Jet Fuel Supply",
    "turbine fuel": "JETA / Jet Fuel Supply",
    "jp-8": "JETA / Jet Fuel Supply",
    "jp 8": "JETA / Jet Fuel Supply",
    "jet a-1": "JETA / Jet Fuel Supply",
    "jet a1": "JETA / Jet Fuel Supply",
    "into-plane": "JETA / Jet Fuel Supply",
    "into plane": "JETA / Jet Fuel Supply",
    "fixed base operator": "JETA / Jet Fuel Supply",
    "fbo fuel": "JETA / Jet Fuel Supply",
    "airport fuel": "JETA / Jet Fuel Supply",
    "fuel farm": "JETA / Jet Fuel Supply",
    "avgas": "JETA / Jet Fuel Supply",
    "notary": "Notary & Document Services",
    "notarization": "Notary & Document Services",
    "apostille": "Notary & Document Services",
    "document authentication": "Notary & Document Services",
    "loan signing": "Notary & Document Services",
    "remote online notarization": "Notary & Document Services",
    "document preparation": "Notary & Document Services",
    "signing agent": "Notary & Document Services",
    "staffing": "Staffing & Admin Support",
    "administrative support": "Staffing & Admin Support",
    "clerical": "Staffing & Admin Support",
    "temporary staff": "Staffing & Admin Support",
    "contract staff": "Staffing & Admin Support",
    "office support": "Staffing & Admin Support",
    "data entry": "Staffing & Admin Support",
    "program support": "Staffing & Admin Support",
    "project management": "Project Management & Consulting",
    "program management": "Project Management & Consulting",
    "management consulting": "Project Management & Consulting",
    "business continuity": "Project Management & Consulting",
    "emergency management": "Project Management & Consulting",
    "crisis management": "Project Management & Consulting",
    "program coordinator": "Project Management & Consulting",
    "contract management": "Project Management & Consulting",
    "occupational health": "Occupational Health Services",
    "occupational medicine": "Occupational Health Services",
    "pre-employment physical": "Occupational Health Services",
    "pre employment physical": "Occupational Health Services",
    "fit for duty": "Occupational Health Services",
    "employee health": "Occupational Health Services",
    "health screening": "Occupational Health Services",
    "medical surveillance": "Occupational Health Services",
    "eap": "Occupational Health Services",
    "employee assistance": "Occupational Health Services",
}

DDI_NAICS = {
    "621511",
    "541990",
    "922120",
    "561611",
    "561612",
    "485999",
    "488510",
    "488190",
    "561410",
    "541611",
    "541618",
    "541512",
    "541519",
    "621999",
    "561320",
    "561421",
    "491110",
    "492110",
    "492210",
    "621610",
    "339113",
}

NAICS_LANE_LABELS: Dict[str, str] = {
    "621511": "Drug & Alcohol Testing / Medical Lab",
    "541990": "Drug & Alcohol Testing / Professional Services",
    "922120": "Fingerprinting & Background Checks",
    "561611": "Fingerprinting & Background Checks",
    "561612": "Security & Credentialing",
    "485999": "NEMT & Healthcare Transportation",
    "488510": "Freight & Logistics",
    "561410": "Notary & Document Services",
    "541611": "Project Management & Consulting",
    "541618": "Project Management & Consulting",
    "541512": "Technology Consulting",
    "541519": "Technology Consulting",
    "621999": "NEMT & Healthcare Transportation",
    "561320": "Staffing & Admin Support",
    "492110": "Freight & Logistics / Courier",
    "492210": "Freight & Logistics / Local Delivery",
    "621610": "Healthcare Transportation",
    "488190": "Air Transport Support (classify: AOG courier vs JETA fuel)",
    "339113": "Medical Supplies & Equipment",
    "561421": "Telephone Answering Services",
    "491110": "Postal Service",
}


def normalize_naics(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, list):
        val = val[0] if val else ""
    s = str(val).strip()
    m = re.match(r"^(\d{6})", s)
    if m:
        return m.group(1)
    if len(s) >= 6 and s[:6].isdigit():
        return s[:6]
    return ""


def airtable_fields_to_opp_dict(fields: Dict[str, Any]) -> Dict[str, str]:
    """Map GPSS OPPORTUNITIES (and similar) Airtable fields to miner-shaped dict."""
    title = fields.get("Name") or fields.get("Title") or ""
    description = (
        fields.get("Description")
        or fields.get("Notes")
        or fields.get("summary")
        or fields.get("Summary")
        or ""
    )
    naics_raw = (
        fields.get("NAICS Code")
        or fields.get("NAICS")
        or fields.get("naicsCode")
        or fields.get("NAICS Code(s)")
        or fields.get("Primary NAICS")
        or ""
    )
    naics = normalize_naics(naics_raw)
    return {
        "title": str(title) if title else "",
        "description": str(description) if description else "",
        "naicsCode": naics,
    }


def gpss_opportunity_is_closed(fields: Dict[str, Any]) -> bool:
    s = (fields.get("Status") or fields.get("Source Status") or "").lower()
    if not s:
        return False
    return any(
        x in s
        for x in (
            "won",
            "lost",
            "not pursuing",
            "passed",
            "no bid",
            "cancelled",
            "canceled",
            "declined",
            "archived",
            "withdrawn",
        )
    )


# ── Stretch tier: not a core lane, but worth a glance for subcontract / teaming ───────────────

TEAMING_PHRASES: Tuple[str, ...] = (
    "subcontract",
    "sub-contract",
    "subcontractor",
    "subcontracting",
    "sub contractor",
    "teaming",
    "team arrangement",
    "teaming arrangement",
    "mentor-protégé",
    "mentor protégé",
    "mentor-protege",
    "protégé",
    "protege",
    "joint venture",
    "jv partner",
    "small business participation",
    "subcontracting plan",
    "workshare",
    "work share",
    "portion of the work",
    "portion of work",
    "partial award",
    "multiple awardee",
    "multiple award",
)

# Broader than DDI_KEYWORDS: places DDI often participates as sub or partner.
SUBCONTRACT_ADJACENT_KEYWORDS: Dict[str, str] = {
    "janitorial": "Janitorial / facilities",
    "custodial": "Custodial",
    "landscaping": "Grounds / landscaping",
    "snow removal": "Snow / grounds",
    "grounds maintenance": "Grounds maintenance",
    "facility maintenance": "Facility maintenance",
    "building maintenance": "Building maintenance",
    "general construction": "Construction",
    "renovation": "Construction / renovation",
    "demolition": "Construction",
    "hvac": "HVAC / facilities",
    "plumbing": "Plumbing",
    "electrical contractor": "Electrical",
    "pest control": "Pest control",
    "food service": "Food service",
    "catering": "Catering",
    "warehousing": "Warehousing",
    "warehouse": "Warehousing",
    "distribution center": "Distribution",
    "fulfillment": "Fulfillment / logistics",
    "it support": "IT support",
    "help desk": "Help desk / IT",
    "call center": "Call center / operations",
    "records management": "Records / admin",
    "document imaging": "Document services",
    "inventory management": "Inventory / supply",
    "supply chain": "Supply chain",
    "fleet maintenance": "Fleet / vehicle",
    "vehicle maintenance": "Vehicle maintenance",
    "parking lot": "Pavement / facilities",
    "elevator maintenance": "Elevator / facilities",
    "fire alarm": "Life safety",
    "security guard": "Security services",
    "armed guard": "Security services",
    "staff augmentation": "Staff augmentation",
}

# NAICS outside DDI_NAICS that still often route to subcontract / partner roles.
ADJACENT_NAICS_SUBCONTRACT: frozenset[str] = frozenset({
    "561720",  # Janitorial
    "561730",  # Landscaping
    "236220",  # Commercial building construction
    "238990",  # All other specialty trade contractors
    "238210",  # Electrical contractors
    "238220",  # Plumbing, heating, AC contractors
    "493110",  # General warehousing and storage
    "562111",  # Solid waste collection
    "562920",  # Materials recovery / recycling
    "611430",  # Professional and management development training
    "541614",  # Process, physical distribution, logistics consulting
    "541613",  # Marketing consulting
    "237310",  # Highway, street, bridge construction
    "237990",  # Other heavy construction
    "484121",  # General freight trucking, long-distance
    "485320",  # Limousine service (charter)
})


def analyze_subcontract_stretch(opp: Dict[str, Any]) -> Dict[str, Any]:
    """
    When a solicitation is NOT a core DDI lane, still flag if it looks sub/teaming-friendly
    or adjacent to services you often support as a partner.

    Scores are capped below core lane matches so prime fits always rank higher.
    """
    title = (opp.get("title") or "").lower()
    description = (opp.get("description") or "").lower()
    text = f"{title} {description}"
    naics = normalize_naics(opp.get("naicsCode"))

    teaming = any(p in text for p in TEAMING_PHRASES)
    hits: list[str] = []
    for kw, label in SUBCONTRACT_ADJACENT_KEYWORDS.items():
        if kw in text:
            if label not in hits:
                hits.append(label)

    adjacent_naics = bool(naics) and naics in ADJACENT_NAICS_SUBCONTRACT and naics not in DDI_NAICS

    score = 0
    reasons: list[str] = []

    if teaming:
        score += 30
        reasons.append("mentions subcontracting or teaming")

    if hits:
        add = min(12 + 7 * len(hits), 36)
        score += add
        reasons.append("adjacent work types: " + ", ".join(hits[:4]))

    if adjacent_naics:
        score += 24
        reasons.append(f"adjacent NAICS {naics} (often sub-heavy)")

    if teaming and any(x in text for x in ("idiq", "task order", "bpa", "gwac", "multiple award")):
        score += 10
        reasons.append("IDIQ / task-order style (frequent sub use)")

    score = min(score, 58)
    suggest = score >= 40

    headline = "Possible subcontract / teaming path"
    if teaming and hits:
        headline = f"Worth a look — sub/teaming ({hits[0]})"
    elif teaming:
        headline = "Worth a look — teaming or subcontracting"
    elif hits:
        headline = f"Adjacent work — consider partnering ({hits[0]})"
    elif adjacent_naics:
        headline = f"Adjacent NAICS — may fit as sub ({naics})"

    return {
        "suggest": suggest,
        "score": score,
        "headline": headline,
        "blurb": "; ".join(reasons) if reasons else "",
        "hits": hits[:5],
        "teaming_language": teaming,
    }


def analyze_ddi_fit(opp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns dict: relevant (bool), lane (str), score (int 0–100), source (naics|title|description|'').
    """
    title = (opp.get("title") or "").lower()
    description = (opp.get("description") or "").lower()
    naics = normalize_naics(opp.get("naicsCode"))

    if naics and naics in DDI_NAICS:
        lane = NAICS_LANE_LABELS.get(naics, f"NAICS {naics}")
        return {"relevant": True, "lane": lane, "score": 100, "source": "naics"}

    for keyword, lane in DDI_KEYWORDS.items():
        if keyword in title:
            return {"relevant": True, "lane": lane, "score": 88, "source": "title"}

    for keyword, lane in DDI_KEYWORDS.items():
        if keyword in description:
            return {
                "relevant": True,
                "lane": f"{lane} (desc)",
                "score": 62,
                "source": "description",
            }

    return {"relevant": False, "lane": "", "score": 0, "source": ""}


def is_ddi_relevant(opp: Dict[str, Any]) -> Tuple[bool, str]:
    r = analyze_ddi_fit(opp)
    return r["relevant"], r["lane"]
