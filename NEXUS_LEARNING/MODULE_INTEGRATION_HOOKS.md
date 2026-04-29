# NEXUS LEARNING ENGINE — MODULE INTEGRATION HOOKS

**Purpose:** This document specifies exactly where and how to add learning engine calls to each NEXUS module. Every action that generates data should log to the learning engine.

---

## LEARNING ENGINE QUICK REFERENCE

```python
from nexus_learning_engine import nxlearn

# Log any event:
nxlearn(domain, entity_id, action, metadata)

# Example:
nxlearn('service_orders', order_id, 'completed', {
    'service_type': 'drug_testing',
    'division': 'occupational_health',
    'agent_id': 'agent-123',
    'region': 'MI',
    'turnaround_hours': 4
})
```

---

## INTEGRATION STATUS BY MODULE

### ✅ ALREADY INTEGRATED

| Module | Domain | Status |
|--------|--------|--------|
| `api_server.py` | opportunities | ✅ Lines 8876-8892 |
| `evaluator_scoring_engine.py` | bids | ✅ Lines 449-451, 917-918 |
| `pricing_intelligence.py` | pricing | ✅ Lines 688-689 |
| `contract_intelligence.py` | intelligence | ✅ Line 437 |
| `agenda_manager.py` | (various) | ✅ Lines 165-171 |
| `nexus_autonomous.py` | (various) | ✅ Line 169 |

### ❌ NEEDS INTEGRATION

---

## PRISM MODULES — `service_orders` + `agent_performance` DOMAINS

### `prism_service_router.py`

**Add at top:**
```python
from nexus_learning_engine import nxlearn
```

**Add after order creation (find `def create_order` or similar):**
```python
nxlearn('service_orders', order_id, 'order_created', {
    'service_type': service_type,
    'division': division,
    'client_id': client_id,
    'region': region
})
```

**Add after agent assignment:**
```python
nxlearn('service_orders', order_id, 'agent_assigned', {
    'service_type': service_type,
    'agent_id': agent_id,
    'region': region
})
```

### `prism_inspection_engine.py`

**Add after QC pass:**
```python
nxlearn('service_orders', order_id, 'qc_passed', {
    'service_type': service_type,
    'agent_id': agent_id,
    'turnaround_hours': turnaround
})
nxlearn('agent_performance', agent_id, 'qc_passed', {
    'service_type': service_type,
    'order_id': order_id
})
```

**Add after QC fail:**
```python
nxlearn('service_orders', order_id, 'qc_failed', {
    'service_type': service_type,
    'agent_id': agent_id,
    'fail_reason': reason
})
nxlearn('agent_performance', agent_id, 'qc_failed', {
    'service_type': service_type,
    'fail_reason': reason
})
```

### `prism_orders_api.py`

**Add after order completion:**
```python
nxlearn('service_orders', order_id, 'completed', {
    'service_type': service_type,
    'division': division,
    'agent_id': agent_id,
    'turnaround_hours': hours
})
nxlearn('agent_performance', agent_id, 'order_completed', {
    'service_type': service_type,
    'order_id': order_id
})
```

**Add after order failure/cancellation:**
```python
nxlearn('service_orders', order_id, 'failed', {
    'service_type': service_type,
    'agent_id': agent_id,
    'fail_reason': reason
})
```

---

## PRISM NEMT/TRANSPORT — `transport` DOMAIN

### `prism_nemt.py`

**Add after trip booking:**
```python
nxlearn('transport', trip_id, 'trip_scheduled', {
    'transport_type': 'nemt',
    'region': region,
    'mco_id': mco_id,
    'fulfillment_partner': 'uber_health'  # or 'lyft', 'ddi_direct'
})
```

**Add after trip completion:**
```python
nxlearn('transport', trip_id, 'trip_completed', {
    'transport_type': 'nemt',
    'driver_id': driver_id,
    'trip_distance': distance,
    'on_time': was_on_time
})
```

**Add after trip cancellation/no-show:**
```python
nxlearn('transport', trip_id, 'trip_cancelled', {
    'transport_type': 'nemt',
    'cancel_reason': reason,
    'mco_id': mco_id
})
```

### `prism_uber_health.py`

**Add after Uber Health trip dispatch:**
```python
nxlearn('transport', trip_id, 'driver_assigned', {
    'transport_type': 'nemt',
    'fulfillment_partner': 'uber_health',
    'region': region
})
```

---

## VERTEX BILLING — `billing` DOMAIN

### `vertex_automation.py` / `nemt_billing.py`

**Add after invoice creation:**
```python
nxlearn('billing', invoice_id, 'invoice_created', {
    'client_id': client_id,
    'service_type': service_type,
    'invoice_amount': amount,
    'payer_type': payer_type  # 'medicaid', 'commercial', 'direct'
})
```

**Add after payment received:**
```python
nxlearn('billing', invoice_id, 'payment_received', {
    'client_id': client_id,
    'days_to_pay': days,
    'invoice_amount': amount
})
```

**Add after claim submission:**
```python
nxlearn('billing', claim_id, 'claim_submitted', {
    'payer_type': 'medicaid',
    'mco_id': mco_id,
    'claim_amount': amount
})
```

**Add after claim approval/denial:**
```python
nxlearn('billing', claim_id, 'claim_approved', {...})  # or 'claim_denied'
```

---

## COMPASS CRM — `relationships` DOMAIN

### `compass_api.py`

**Add after contact added:**
```python
nxlearn('relationships', contact_id, 'contact_added', {
    'contact_type': contact_type,  # 'CO', 'procurement', 'partner', 'client'
    'organization': org_name,
    'industry': industry
})
```

**Add after meeting/touchpoint:**
```python
nxlearn('relationships', contact_id, 'meeting_held', {
    'organization': org_name,
    'meeting_type': meeting_type,
    'outcome': outcome
})
```

**Add after contract signed:**
```python
nxlearn('relationships', contact_id, 'contract_signed', {
    'organization': org_name,
    'contract_value': value,
    'service_type': service_type
})
```

---

## ATLAS PARTNER ONBOARDING — `partner_onboarding` DOMAIN

### `atlas_migration.py` or partner onboarding code

**Add after partner lead identified:**
```python
nxlearn('partner_onboarding', partner_id, 'lead_identified', {
    'partner_type': partner_type,  # 'collector', 'driver', 'notary', etc.
    'service_types': service_types,
    'region': region,
    'source': source  # 'referral', 'job_board', 'existing_sub'
})
```

**Add after NDA signed:**
```python
nxlearn('partner_onboarding', partner_id, 'nda_signed', {
    'partner_type': partner_type,
    'onboarding_days': days_since_first_contact
})
```

**Add after partner activated:**
```python
nxlearn('partner_onboarding', partner_id, 'activated', {
    'partner_type': partner_type,
    'service_types': service_types,
    'region': region,
    'onboarding_days': total_days
})
```

**Add after first order completed:**
```python
nxlearn('partner_onboarding', partner_id, 'first_order_completed', {
    'partner_type': partner_type,
    'order_id': order_id,
    'qc_result': 'passed'  # or 'failed'
})
```

---

## BIDS API — `bids` DOMAIN

### `bids_api.py`

**Add after bid created:**
```python
nxlearn('bids', bid_id, 'identified', {
    'contract_type': contract_type,
    'set_aside': set_aside,
    'agency': agency,
    'value_range': value_range,
    'naics': naics
})
```

**Add after go/no-go decision:**
```python
nxlearn('bids', bid_id, 'go_decision', {...})  # or 'nogo_decision'
```

**Add after bid submitted:**
```python
nxlearn('bids', bid_id, 'bid_submitted', {
    'agency': agency,
    'submission_method': method,
    'on_time': was_on_time
})
```

---

## QUOTE GENERATOR — `suppliers` DOMAIN

### `quote_generator_api.py`

**Add after RFQ sent to supplier:**
```python
nxlearn('suppliers', rfq_id, 'rfq_sent', {
    'supplier_name': supplier,
    'product_type': product_type
})
```

**Add after quote received:**
```python
nxlearn('suppliers', rfq_id, 'quote_received', {
    'supplier_name': supplier,
    'response_days': days,
    'price_vs_market': 'competitive'  # or 'expensive', 'unknown'
})
```

---

## RFP GENERATOR — `bids` DOMAIN

### `rfp_generator_api.py`

**Add after proposal generated:**
```python
nxlearn('bids', proposal_id, 'bid_prepared', {
    'agency': agency,
    'contract_type': contract_type,
    'biohack_score': score
})
```

---

## IMPLEMENTATION PRIORITY

### Phase 1 — HIGH IMPACT (Do First)
1. `prism_service_router.py` — Order creation/routing
2. `prism_inspection_engine.py` — QC pass/fail
3. `prism_nemt.py` — NEMT trip tracking
4. `bids_api.py` — Bid workflow
5. `quote_generator_api.py` — Supplier RFQs

### Phase 2 — MEDIUM IMPACT
6. `prism_orders_api.py` — Order completion
7. `vertex_automation.py` — Billing/invoicing
8. `compass_api.py` — CRM touchpoints
9. `atlas_migration.py` — Partner onboarding

### Phase 3 — COMPLETE COVERAGE
10. All remaining PRISM compliance modules
11. `prism_uber_health.py`, `prism_lyft_healthcare.py`
12. All other API modules

---

## VALIDATION

After adding hooks, verify with:

```python
from nexus_learning_engine import get_engine
engine = get_engine()
status = engine.get_status()
print(status['domains'])  # Should show events in new domains
```

Or call the API:
```
GET /api/learning/status
```

---

## LEARNING ANALYSIS

Once modules are integrated, the learning engine will:

1. **Track patterns** — Which agents have highest QC pass rates? Which MCOs have most trip completions?
2. **Adjust weights** — If certain regions have higher success, weight them higher in routing
3. **Generate insights** — "Agent John has 95% QC pass rate on drug testing" → prioritize assignments
4. **Improve over time** — Every order, every trip, every invoice becomes training data

---

*The more hooks we add, the smarter NEXUS gets. Every action is learning data.*
