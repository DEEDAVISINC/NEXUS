# VITAL SYSTEM SPECIFICATION

**Program:** VITAL — Verified Integrated Transport And Logistics  
**Based On:** University Health RFPs (RFP-226-03-068-SVC + RFP-226-04-073-SVC)  
**Created:** May 13, 2026  
**Purpose:** Define PRISM module requirements for Lab & Pharmaceutical Courier TPA operations

---

## OVERVIEW

VITAL is DDI's healthcare logistics TPA platform for:
- **Lab Courier** — Specimen transport, slides, instruments, equipment
- **Pharmaceutical Courier** — Medication delivery, cold chain, controlled substances

Built to the spec of University Health (San Antonio) contracts:
- Combined volume: **8,750 deliveries/month**
- Combined value: **$913K–$1.65M/year**
- Contract term: **5 years (3+2 renewals)**

---

## 1. SERVICE TYPES & SLAs

### 1.1 Service Level Definitions

| Service Type | Definition | Max Delivery Time | Typical Volume |
|--------------|------------|-------------------|----------------|
| **SCHEDULED** | Scheduled pickup window, deliveries compiled daily 12–2 PM | 2 hours from request | Pharma: 95% |
| **ROUTINE** | Non-scheduled, as-needed, non-urgent | 2 hours from request | Lab: 50% |
| **STAT** | Emergency, time-critical | 1 hour from request | Lab: 30%, Pharma: <5% |
| **AFTER HOURS** | Requests between 8:00 PM – 7:00 AM | 2 hours (unless STAT) | Lab: 20%, Pharma: <10% |
| **AD-HOC** | On-demand, non-scheduled, non-recurring | 4 hours from request | Pharma: <5% |

### 1.2 Success Rate SLA

- **Target:** 85% Delivery Completion Success Rate
- **Definition:** Driver arrives at destination within required delivery window
- **Note:** If driver arrives on time but recipient unavailable = still counts as SUCCESS

### 1.3 Weekend/Holiday Operations

| Metric | Pharmacy | Lab |
|--------|----------|-----|
| Weekend volume | 25% | 10-15% |
| Holiday volume | 10% | 5% |

---

## 2. ITEM CLASSIFICATION

### 2.1 Pharmacy Items

| Item Type | Temperature | Handling | Notes |
|-----------|-------------|----------|-------|
| Standard Medications | Ambient | Standard | Majority of volume |
| Cold Chain Medications | Refrigerated | Ice packs | Pharmacy provides ice packs |
| Controlled Substances | Ambient/Cold | Chain of custody | Schedule II-V, DEA tracking |

**No dry ice required for pharmacy courier**

### 2.2 Lab Items

| Item Type | Temperature | Handling | Notes |
|-----------|-------------|----------|-------|
| Lab Specimens | Ambient/Refrigerated | Biohazard | Blood, urine, tissue |
| Pathology Slides | Ambient | Fragile | Medical/pathology slides |
| Frozen Specimens | Frozen | Dry ice (rare) | Vendor provides dry ice |
| Surgical Instruments | Ambient | Hand-carry | Size/weight varies |
| Medical Equipment | Ambient | Hand-carry | Components, parts |

**Temperature Control:**
- Ice packs provided by Pathology, returned by courier
- Dry ice: Extremely rare (<5 times/year), vendor provides

---

## 3. GEOGRAPHIC SCOPE

### 3.1 Service Area

- **Primary:** Bexar County, Texas (San Antonio metro)
- **Extended:** Austin, TX (CDC Austin delivery point)
- **Model:** National — scale for any metro area

### 3.2 Mileage Zones

| Zone | Distance (one-way loaded) |
|------|---------------------------|
| Zone 1 | 0–10 miles |
| Zone 2 | 11–25 miles |
| Zone 3 | 26–50 miles |
| Zone 4 | 51–75 miles |
| Zone 5 | 76+ miles |

**Note:** Zone = one-way "loaded" mileage from pickup to delivery. Return/empty mileage NOT included.

---

## 4. PRICING MODELS

### 4.1 Zone-Based Pricing

| Zone | Scheduled | Routine | STAT | After Hours | Ad-Hoc |
|------|-----------|---------|------|-------------|--------|
| 0-10 mi | $X | $X | $X | $X | $X |
| 11-25 mi | $X | $X | $X | $X | $X |
| 26-50 mi | $X | $X | $X | $X | $X |
| 51-75 mi | $X | $X | $X | $X | $X |
| 76+ mi | $X | $X | $X | $X | $X |

### 4.2 Per-Mile Pricing

| Service Type | Rate per Loaded Mile |
|--------------|---------------------|
| Scheduled/Routine | $X/mile |
| STAT | $X/mile |
| After Hours | $X/mile |

### 4.3 Flat Rate Pricing

| Service Type | Flat Rate | Mileage Radius |
|--------------|-----------|----------------|
| 1-hour STAT | $X | Up to X miles |
| 2-hour Routine | $X | Up to X miles |
| After Hours | $X | Up to X miles |

### 4.4 Special Rates

| Event | Rate |
|-------|------|
| Dry Run (unable to deliver) | Flat rate per attempt |
| Undelivered Return | Included or separate rate |
| Dry Ice (vendor provides) | Cost + handling fee |
| Miscellaneous/Special | Per request |

---

## 5. PRISM VITAL MODULE REQUIREMENTS

### 5.1 Order Intake (`prism_vital_orders.py`)

```python
VITAL_ORDER_SCHEMA = {
    "order_id": str,  # VITAL-YYYYMMDD-####
    "service_lane": ["pharmacy", "lab"],
    "service_type": ["scheduled", "routine", "stat", "after_hours", "ad_hoc"],
    "urgency_minutes": int,  # 60 for STAT, 120 for routine, 240 for ad-hoc
    "item_type": ["medication", "specimen", "slide", "instrument", "equipment"],
    "temperature": ["ambient", "refrigerated", "frozen"],
    "controlled_substance": bool,
    "dea_schedule": ["II", "III", "IV", "V", None],
    "pickup": {
        "facility_id": str,
        "address": str,
        "contact": str,
        "window_start": datetime,
        "window_end": datetime
    },
    "delivery": {
        "address": str,
        "recipient": str,
        "phone": str,
        "instructions": str
    },
    "ice_pack_provided": bool,
    "ice_pack_return_required": bool,
    "dry_ice_required": bool,
    "proof_of_delivery_required": bool
}
```

### 5.2 QC Checklists (`prism_vital_compliance.py`)

#### Pharmacy Courier QC
```python
PHARMACY_QC_CHECKLIST = [
    {"id": "rx_label_verified", "description": "Medication label matches order", "required": True},
    {"id": "recipient_verified", "description": "Recipient name verified", "required": True},
    {"id": "cold_chain_verified", "description": "Ice packs present if cold chain", "required": True},
    {"id": "controlled_substance_logged", "description": "DEA chain of custody completed", "conditional": "controlled_substance"},
    {"id": "signature_captured", "description": "Recipient signature captured", "required": True},
    {"id": "photo_proof", "description": "Delivery photo captured", "required": True},
    {"id": "timestamp_logged", "description": "Delivery timestamp recorded", "required": True}
]
```

#### Lab Courier QC
```python
LAB_QC_CHECKLIST = [
    {"id": "specimen_integrity", "description": "Specimen container sealed and labeled", "required": True},
    {"id": "biohazard_compliance", "description": "Biohazard packaging verified", "required": True},
    {"id": "temperature_verified", "description": "Temperature control verified", "conditional": "refrigerated|frozen"},
    {"id": "ice_pack_present", "description": "Ice packs present and intact", "conditional": "refrigerated"},
    {"id": "dry_ice_handled", "description": "Dry ice properly handled (IATA P650)", "conditional": "frozen"},
    {"id": "chain_of_custody", "description": "Chain of custody documented", "required": True},
    {"id": "delivery_confirmed", "description": "Lab receipt confirmed", "required": True},
    {"id": "ice_pack_returned", "description": "Ice packs returned to Pathology", "conditional": "ice_pack_return_required"}
]
```

### 5.3 SLA Tracking (`prism_vital_sla.py`)

```python
SLA_THRESHOLDS = {
    "stat": {"max_minutes": 60, "alert_at": 45},
    "routine": {"max_minutes": 120, "alert_at": 90},
    "scheduled": {"max_minutes": 120, "alert_at": 90},
    "after_hours": {"max_minutes": 120, "alert_at": 90},
    "ad_hoc": {"max_minutes": 240, "alert_at": 180}
}

SUCCESS_RATE_TARGET = 0.85  # 85% on-time delivery

def calculate_sla_status(order):
    """
    SUCCESS = driver arrives at destination within delivery window
    If driver on time but recipient unavailable = still SUCCESS
    """
    elapsed = (order.arrival_time - order.request_time).total_seconds() / 60
    max_allowed = SLA_THRESHOLDS[order.service_type]["max_minutes"]
    return elapsed <= max_allowed
```

### 5.4 Proof of Delivery (`prism_vital_pod.py`)

Required POD elements per University Health RFP:

```python
POD_REQUIREMENTS = {
    "pickup": {
        "timestamp": True,
        "facility_name": True,
        "driver_id": True,
        "item_count": True,
        "temperature_check": True,  # if applicable
        "signature_or_scan": True
    },
    "delivery": {
        "timestamp": True,
        "recipient_name": True,
        "recipient_signature": True,
        "delivery_address": True,
        "photo_proof": True,
        "driver_id": True,
        "notes": False  # optional
    }
}
```

### 5.5 Credential Requirements (`prism_vital_credentials.py`)

```python
VITAL_CREDENTIALS = {
    "driver": {
        "required": [
            "valid_drivers_license",
            "background_check",
            "hipaa_training",
            "bloodborne_pathogens_training",
            "facility_badge"  # University Health contractor badge
        ],
        "conditional": {
            "controlled_substance": ["dea_awareness_training"],
            "dry_ice": ["iata_p650_training"]
        }
    },
    "vehicle": {
        "required": [
            "valid_registration",
            "valid_insurance",
            "temperature_monitoring_capable"
        ]
    }
}

# Symplr credentialing integration
SYMPLR_CONFIG = {
    "enabled": True,
    "vendor_portal": "https://www.symplr.com",
    "gc_contact": "GC@symplr.com",
    "badge_required_for": ["clinical_area_access"],
    "badge_not_required_for": ["pickup_dropoff_only"]
}
```

### 5.6 Route Optimization (`prism_vital_routing.py`)

```python
ROUTING_CONFIG = {
    "dynamic_routing": True,  # Routes are NOT fixed point-to-point
    "daily_schedule_window": "12:00-14:00",  # Pharmacy compiles list daily
    "multi_stop_allowed": True,  # Single driver can do multiple pickups/deliveries
    "batching_allowed": True,  # Aggregate orders per driver
    "stat_override": True,  # STAT bypasses normal batching
    "zones": [
        {"id": 1, "min_miles": 0, "max_miles": 10},
        {"id": 2, "min_miles": 11, "max_miles": 25},
        {"id": 3, "min_miles": 26, "max_miles": 50},
        {"id": 4, "min_miles": 51, "max_miles": 75},
        {"id": 5, "min_miles": 76, "max_miles": None}  # 76+
    ]
}
```

---

## 6. REPORTING REQUIREMENTS

### 6.1 University Health Reporting

Per RFP, vendor must submit performance improvement results **4x per year** to Quality Services Department:

```python
QUARTERLY_REPORT = {
    "period": "Q1/Q2/Q3/Q4",
    "metrics": {
        "total_deliveries": int,
        "on_time_rate": float,  # Target: 85%+
        "stat_response_rate": float,
        "after_hours_volume": int,
        "dry_run_count": int,
        "incident_count": int,
        "corrective_actions": list
    },
    "format": "University Health standard reporting format",
    "submit_to": "Quality Services Department"
}
```

### 6.2 DDI Internal Metrics

```python
DDI_METRICS = {
    "daily": [
        "deliveries_completed",
        "sla_compliance_rate",
        "average_delivery_time",
        "active_orders"
    ],
    "weekly": [
        "volume_by_service_type",
        "volume_by_zone",
        "driver_utilization",
        "fulfillment_partner_performance"
    ],
    "monthly": [
        "revenue",
        "margin",
        "sla_trend",
        "client_satisfaction"
    ]
}
```

---

## 7. FULFILLMENT PARTNER INTEGRATION

### 7.1 Pharmacy Courier Partners

| Partner | Capability | Coverage | Volume Min | Status |
|---------|------------|----------|------------|--------|
| **Uber Health** | General Rx delivery, cold chain | National (San Antonio ✅) | None stated | ✅ CONFIRMED May 13, 2026 |
| **ScriptDrop** | Controlled substances (Schedule II-V) | National | TBD | ⚠️ Verify San Antonio |
| **Local courier** | Backup | Regional | None | 🔍 Research |

**Uber Health Pharmacy Notes (May 13, 2026 call):**
- San Antonio / Bexar County = CONFIRMED coverage
- Rx courier / pharmacy delivery = CONFIRMED capability
- Cold chain (ice packs) = CONFIRMED
- 7,900/month volume = NO ISSUE
- AE follow-up call scheduled (May 13 evening or May 14 AM)

### 7.2 Lab Courier Partners

| Partner | Capability | Coverage | Volume Min | Status |
|---------|------------|----------|------------|--------|
| **Uber Health** | Lab specimens, biohazard | National (San Antonio ✅) | **2,000/month** | ⚠️ VOLUME THRESHOLD |
| **carGO Health** | Lab specimens | National | TBD | ⚠️ Awaiting response |
| **MEDS (meds-inc.com)** | Lab specimens, 24/7 | San Antonio | TBD | 🔍 Backup option |
| **Medical Services Plus** | STAT, lab courier | San Antonio | TBD | 🔍 Backup option |

**Uber Health Lab Notes (May 13, 2026 call):**
- Lab courier = CONFIRMED capability
- **MINIMUM VOLUME: 2,000 deliveries/month**
- University Health lab RFP = 850/month = BELOW THRESHOLD
- San Antonio coverage = CONFIRMED

### 7.3 VOLUME AGGREGATION STRATEGY

**Problem:** University Health lab courier (850/mo) is below Uber Health's 2,000/mo minimum.

**Solution:** Aggregate lab courier volume across multiple MCO/health system contracts to hit threshold.

| Client | Est. Lab Volume | Status |
|--------|-----------------|--------|
| University Health (San Antonio) | 850/mo | RFP due May 18 |
| **Additional MCO contracts needed** | **1,150+/mo** | 🎯 TARGET |
| **TOTAL NEEDED** | **2,000/mo** | Uber Health minimum |

**Action Items:**
1. Bid University Health lab courier — even if below threshold, win establishes relationship
2. Pursue additional Texas MCO lab courier contracts (Superior, UHC, Aetna, Amerigroup, BCBS)
3. Once aggregated volume hits 2,000/mo — activate Uber Health for all lab courier
4. Until then — use backup partners (carGO Health, MEDS, Medical Services Plus) for University Health

**Alternative:** Use non-Uber partner for University Health lab (850/mo) while building MCO volume toward Uber threshold.

### 7.4 Partner API Integration

```python
PARTNER_API_SCHEMA = {
    "create_order": {
        "endpoint": "/api/v1/orders",
        "method": "POST",
        "payload": VITAL_ORDER_SCHEMA,
        "response": {"order_id": str, "estimated_pickup": datetime}
    },
    "track_order": {
        "endpoint": "/api/v1/orders/{order_id}/status",
        "method": "GET",
        "response": {"status": str, "location": dict, "eta": datetime}
    },
    "proof_of_delivery": {
        "endpoint": "/api/v1/orders/{order_id}/pod",
        "method": "GET",
        "response": POD_REQUIREMENTS
    }
}
```

---

## 8. COMPLIANCE REQUIREMENTS

### 8.1 Healthcare Compliance

| Requirement | Standard | Status |
|-------------|----------|--------|
| HIPAA Privacy | 45 CFR 164 | ✅ DDI compliant |
| HIPAA Security | 45 CFR 164 | ✅ DDI compliant |
| BAA (Business Associate Agreement) | HIPAA | 📋 Sign per contract |
| Bloodborne Pathogens | 29 CFR 1910.1030 | ✅ Training required |

### 8.2 Controlled Substance Compliance

| Requirement | Standard | Applies To |
|-------------|----------|------------|
| DEA Chain of Custody | 21 CFR 1301 | Pharmacy (controlled) |
| Schedule II-V Tracking | DEA regulations | Pharmacy (controlled) |
| Signature Required | DEA regulations | Pharmacy (controlled) |

### 8.3 Specimen Transport Compliance

| Requirement | Standard | Applies To |
|-------------|----------|------------|
| Biohazard Packaging | DOT 49 CFR 173.196 | Lab specimens |
| Temperature Logging | CAP, CLIA | Lab specimens |
| IATA P650 (Dry Ice) | IATA DGR | Frozen specimens |
| Chain of Custody | Lab standards | All lab items |

### 8.4 Joint Commission

Per RFP: Vendor must comply with Joint Commission Accreditation Standards and submit performance improvement results 4x/year.

---

## 9. BUILD SCHEDULE

### Phase 1: Core Module (May 16, 2026)

- [ ] `prism_vital_orders.py` — Order intake schema
- [ ] `prism_vital_compliance.py` — QC checklists
- [ ] `prism_vital_sla.py` — SLA tracking
- [ ] `prism_vital_pod.py` — Proof of delivery
- [ ] `prism_vital_credentials.py` — Driver/vehicle credentials

### Phase 2: Integration (May 17-18, 2026)

- [ ] Partner API integration (Uber Health, ScriptDrop, carGO)
- [ ] Pricing engine (zone, per-mile, flat rate)
- [ ] Routing optimization
- [ ] Real-time tracking

### Phase 3: Reporting (Post-contract)

- [ ] Quarterly reporting (University Health format)
- [ ] DDI internal dashboards
- [ ] Client portal (if required)

---

## 10. UNIVERSITY HEALTH BID DELIVERABLES

### Required by May 18, 2026:

**Pharmacy Courier (RFP-226-03-068-SVC):**
- [ ] Signed Master Solicitation Document
- [ ] Signed Addendum 1
- [ ] Signed Exhibit A (Terms & Conditions)
- [ ] Signed Exhibit B (State/County Law)
- [ ] Signed Exhibit C (BAA)
- [ ] Completed Exhibit D (Privacy/Security Questionnaire)
- [ ] Completed Exhibit F (References)
- [ ] Completed Bid Table (pricing)
- [ ] Form CIQ (Conflict of Interest)
- [ ] Good Faith Effort Plan
- [ ] Response document (Experience, Qualifications, Operations, Performance)

**Lab Courier (RFP-226-04-073-SVC):**
- [ ] Same document set as above
- [ ] Separate Bid Table for lab pricing

**Both require Bonfire portal registration:** https://universityhealth.bonfirehub.com

---

*This specification was built from actual RFP requirements. When VITAL is deployed, it will be contract-ready from day one.*
