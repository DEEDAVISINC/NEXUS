# NEXUS LEARNING ENGINE — ALL SECTOR INTEGRATION HOOKS

**Purpose:** This document specifies exactly where and how to add learning engine calls to EVERY NEXUS sector. Every action that generates data should log to the learning engine.

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

## ALL NEXUS SECTORS & THEIR LEARNING DOMAINS

| Sector | Domain(s) | What It Tracks |
|--------|-----------|----------------|
| **GPSS** | `opportunities`, `outreach`, `bids`, `suppliers`, `subcontractors`, `pricing`, `intelligence` | Opportunities → Bids → Win/Loss |
| **PRISM** | `service_orders`, `agent_performance` | Orders → QC → Completion |
| **VERTEX** | `billing` | Invoices → Claims → Payments |
| **DDCSS** | `ddcss_prospects`, `ddcss_pipeline` | Leads → Pipeline → Closed |
| **ATLAS PM** | `atlas_projects`, `partner_onboarding` | Projects → Milestones → Completion |
| **JETA** | `jeta_deals`, `jeta_fraud` | Deals → KYC → Fraud Detection |
| **SHIELD** | `shield_referrals`, `shield_verification` | Referrals → Services → Verification |
| **LBPC** | `lbpc_leads` | Surplus Leads → Claims → Recovery |
| **GBIS** | `gbis_grants` | Grants → Applications → Awards |
| **COMPASS** | `relationships` | Contacts → Touchpoints → Contracts |
| **TRANSPORT** | `transport` | Trips → Dispatch → Completion |

---

## SECTOR 1: GPSS — Government Pipeline & Sourcing System

### Files:
- `api_server.py` (main)
- `nexus_opportunity_hunter_api.py`
- `nexus_pipeline_api.py`
- `contract_intelligence.py`
- `pricing_intelligence.py`

### Domains:
- `opportunities` — Mining → Scoring → Pursue/Skip → Win/Lose
- `outreach` — Emails → Responses → Relationships
- `bids` — Go/No-Go → Prepared → Submitted → Won/Lost
- `suppliers` — RFQ → Quote → Competitiveness
- `subcontractors` — Vetted → Hired → Performance
- `pricing` — Markup → Won/Lost → Margin
- `intelligence` — Primes → Contacted → Sub opportunities

### Integration Status: ✅ INTEGRATED
```python
# Already in api_server.py:
nxlearn('opportunities', opportunity_id, action, meta)
```

---

## SECTOR 2: PRISM — Professional Resource Inspection & Service Management

### Files:
- `prism_service_router.py` ✅ INTEGRATED
- `prism_orders_api.py`
- `prism_inspection_engine.py`
- `prism_nemt.py` ✅ INTEGRATED
- `prism_dot_compliance.py`
- `prism_dna_compliance.py`
- `prism_fingerprinting_compliance.py`
- `prism_notary_compliance.py`
- `prism_occupational_health_compliance.py`

### Domains:
- `service_orders` — Order creation → Routing → QC → Completion
- `agent_performance` — Assignments → Pass/Fail → Certifications
- `transport` — NEMT trips → Dispatch → Completion

### Add to `prism_orders_api.py`:
```python
from nexus_learning_engine import nxlearn

# After order completion:
nxlearn('service_orders', order_id, 'completed', {
    'service_type': service_type,
    'division': division,
    'agent_id': agent_id,
    'turnaround_hours': hours,
    'client_id': client_id
})
nxlearn('agent_performance', agent_id, 'order_completed', {
    'service_type': service_type,
    'order_id': order_id
})
```

### Add to `prism_inspection_engine.py`:
```python
# After QC pass:
nxlearn('service_orders', order_id, 'qc_passed', {
    'service_type': service_type,
    'agent_id': agent_id
})
nxlearn('agent_performance', agent_id, 'qc_passed', {
    'service_type': service_type
})

# After QC fail:
nxlearn('service_orders', order_id, 'qc_failed', {
    'service_type': service_type,
    'agent_id': agent_id,
    'fail_reason': reason
})
nxlearn('agent_performance', agent_id, 'qc_failed', {
    'fail_reason': reason
})
```

---

## SECTOR 3: VERTEX — Billing & Revenue

### Files:
- `vertex_automation.py`
- `nemt_billing.py`
- `nemt_factoring_invoice_html.py`

### Domain: `billing`

### Add to `vertex_automation.py`:
```python
from nexus_learning_engine import nxlearn

# After invoice creation:
nxlearn('billing', invoice_id, 'invoice_created', {
    'client_id': client_id,
    'service_type': service_type,
    'invoice_amount': amount,
    'payer_type': payer_type
})

# After payment received:
nxlearn('billing', invoice_id, 'payment_received', {
    'client_id': client_id,
    'days_to_pay': days,
    'invoice_amount': amount
})

# After claim submission:
nxlearn('billing', claim_id, 'claim_submitted', {
    'payer_type': 'medicaid',
    'mco_id': mco_id,
    'claim_amount': amount
})

# After claim approval/denial:
nxlearn('billing', claim_id, 'claim_approved', {...})  # or 'claim_denied'
```

---

## SECTOR 4: DDCSS — Corporate Sales System

### Files:
- `nexus_backend.py` (DDCSS components)
- Frontend: `DDCSSSystem.tsx`

### Domains:
- `ddcss_prospects` — Leads → Qualification → Outreach → Close
- `ddcss_pipeline` — Pipeline stages → Win/Loss

### Add hooks for:
```python
from nexus_learning_engine import nxlearn

# After lead qualified:
nxlearn('ddcss_prospects', prospect_id, 'lead_qualified', {
    'sector': sector,
    'company_size': size,
    'source': source,
    'deal_value': estimated_value
})

# After avatar built:
nxlearn('ddcss_prospects', prospect_id, 'avatar_built', {
    'sector': sector,
    'ai_qualification_score': score
})

# After pitch generated:
nxlearn('ddcss_prospects', prospect_id, 'pitch_generated', {
    'sector': sector,
    'pitch_type': pitch_type
})

# After response received:
nxlearn('ddcss_prospects', prospect_id, 'responded', {
    'sector': sector,
    'response_type': response_type,
    'days_to_respond': days
})

# Pipeline stage changes:
nxlearn('ddcss_pipeline', deal_id, 'stage_proposal', {
    'sector': sector,
    'deal_value': value,
    'probability': probability
})

# Deal won/lost:
nxlearn('ddcss_pipeline', deal_id, 'stage_closed_won', {
    'sector': sector,
    'deal_value': value,
    'sales_cycle_days': days
})
```

---

## SECTOR 5: ATLAS PM — Project Management

### Files:
- `atlas_migration.py`
- `nexus_backend.py` (ATLAS components)
- Frontend: `ATLASSystem.tsx`

### Domains:
- `atlas_projects` — Projects → Milestones → Completion
- `partner_onboarding` — Partner leads → Activation

### Add hooks for:
```python
from nexus_learning_engine import nxlearn

# Project created:
nxlearn('atlas_projects', project_id, 'project_created', {
    'project_type': project_type,
    'client_id': client_id,
    'budget': budget,
    'duration_days': duration
})

# RFP analyzed:
nxlearn('atlas_projects', project_id, 'rfp_analyzed', {
    'win_probability': probability,
    'risk_score': risk_score
})

# Milestone reached:
nxlearn('atlas_projects', project_id, 'milestone_reached', {
    'milestone_name': name,
    'on_time': was_on_time
})

# Change order:
nxlearn('atlas_projects', project_id, 'change_order_approved', {
    'change_value': value,
    'impact_days': impact
})

# Project completed:
nxlearn('atlas_projects', project_id, 'project_completed', {
    'on_time': on_time,
    'under_budget': under_budget,
    'client_satisfaction': rating
})
```

---

## SECTOR 6: JETA — Jet Fuel Trading & Fraud Detection

### Files:
- `jeta_fraud_detection.py`
- `jeta_compliance_layers.py`
- `jeta_deal_schema.py`
- `jeta_buyer_schema.py`
- `jeta_seller_schema.py`

### Domains:
- `jeta_deals` — Deal creation → KYC → Completion
- `jeta_fraud` — Fraud flags → Review → Resolution

### Add to `jeta_fraud_detection.py`:
```python
from nexus_learning_engine import nxlearn

# After counterparty scored:
nxlearn('jeta_deals', deal_id, 'counterparty_scored', {
    'counterparty_type': ctype,
    'fraud_score': score,
    'flags_count': flags
})

# After KYC pass/fail:
nxlearn('jeta_deals', deal_id, 'kyc_passed', {
    'counterparty_type': ctype,
    'deal_value': value
})

# Fraud flagged:
nxlearn('jeta_fraud', flag_id, 'term_flagged', {
    'flag_type': flag_type,
    'severity': severity,
    'counterparty': counterparty
})

# After manual review:
nxlearn('jeta_fraud', flag_id, 'cleared', {
    'review_time_hours': hours,
    'false_positive': was_false_positive
})
```

---

## SECTOR 7: SHIELD — Service Verification (Cause We Care)

### Files:
- `shield_verification.py`
- `shield_lead_screening.py`
- `shield_notifications.py`

### Domains:
- `shield_referrals` — Referrals → Screening → Services → Billing
- `shield_verification` — SMS verification → Completion

### Add to `shield_lead_screening.py`:
```python
from nexus_learning_engine import nxlearn

# Referral received:
nxlearn('shield_referrals', referral_id, 'referral_received', {
    'referral_source': source,
    'county': county,
    'service_type': service_type
})

# After screening:
nxlearn('shield_referrals', referral_id, 'qualified', {
    'family_size': size,
    'services_assigned': services
})

# Family enrolled:
nxlearn('shield_referrals', referral_id, 'family_enrolled', {
    'enrollment_date': date,
    'navigator_id': navigator_id
})
```

### Add to `shield_verification.py`:
```python
# Verification started:
nxlearn('shield_verification', activation_id, 'verification_started', {
    'service_type': service_type,
    'contractor_id': contractor_id,
    'steps_required': steps_count
})

# SMS response received:
nxlearn('shield_verification', activation_id, 'sms_response_received', {
    'step_name': step,
    'response_time_hours': hours
})

# Verification passed:
nxlearn('shield_verification', activation_id, 'verification_passed', {
    'service_type': service_type,
    'total_time_hours': hours,
    'steps_completed': steps
})
```

---

## SECTOR 8: LBPC — Surplus Recovery

### Files:
- `nexus_backend.py` (LBPC components)
- Frontend: `LBPCSystem.tsx`

### Domain: `lbpc_leads`

### Add hooks for:
```python
from nexus_learning_engine import nxlearn

# Lead mined:
nxlearn('lbpc_leads', lead_id, 'lead_mined', {
    'county': county,
    'property_type': property_type,
    'estimated_value': value,
    'source': source
})

# Initial notice sent:
nxlearn('lbpc_leads', lead_id, 'initial_notice_sent', {
    'county': county,
    'method': 'mail'  # or 'email'
})

# Response received:
nxlearn('lbpc_leads', lead_id, 'response_received', {
    'days_to_respond': days,
    'response_type': response_type
})

# Claim filed:
nxlearn('lbpc_leads', lead_id, 'claim_filed', {
    'claim_type': claim_type,
    'claim_amount': amount
})

# Claim approved/denied:
nxlearn('lbpc_leads', lead_id, 'claim_approved', {
    'approved_amount': amount,
    'processing_days': days
})

# Payment received:
nxlearn('lbpc_leads', lead_id, 'payment_received', {
    'payment_amount': amount,
    'ddi_commission': commission
})
```

---

## SECTOR 9: GBIS — Grants Intelligence System

### Files:
- `gbis_community_health_miner.py`
- `nexus_backend.py` (GBIS components)

### Domain: `gbis_grants`

### Add to `gbis_community_health_miner.py`:
```python
from nexus_learning_engine import nxlearn

# Grant discovered:
nxlearn('gbis_grants', grant_id, 'grant_discovered', {
    'funding_agency': agency,
    'grant_type': grant_type,
    'award_amount': amount,
    'research_subtype': subtype
})

# Eligibility checked:
nxlearn('gbis_grants', grant_id, 'eligible', {
    'applicant_entity': 'DDI',  # or 'Cause We Care'
    'funding_agency': agency
})

# Application submitted:
nxlearn('gbis_grants', grant_id, 'application_submitted', {
    'applicant_entity': entity,
    'requested_amount': amount
})

# Awarded:
nxlearn('gbis_grants', grant_id, 'awarded', {
    'award_amount': amount,
    'funding_agency': agency,
    'applicant_entity': entity
})
```

---

## SECTOR 10: COMPASS — CRM & Relationships

### Files:
- `compass_api.py`
- `auto_contact_manager.py`

### Domain: `relationships`

### Add to `compass_api.py`:
```python
from nexus_learning_engine import nxlearn

# Contact added:
nxlearn('relationships', contact_id, 'contact_added', {
    'contact_type': contact_type,
    'organization': org_name,
    'industry': industry
})

# Touchpoint logged:
nxlearn('relationships', contact_id, 'touchpoint_logged', {
    'touchpoint_type': ttype,  # 'email', 'call', 'meeting'
    'organization': org_name
})

# Meeting held:
nxlearn('relationships', contact_id, 'meeting_held', {
    'organization': org_name,
    'meeting_type': meeting_type,
    'outcome': outcome
})

# Contract signed:
nxlearn('relationships', contact_id, 'contract_signed', {
    'organization': org_name,
    'contract_value': value,
    'service_type': service_type
})
```

---

## IMPLEMENTATION PRIORITY

### Phase 1 — CRITICAL (Do First)
1. ✅ `prism_service_router.py` — Order routing
2. ✅ `prism_nemt.py` — NEMT trips
3. ✅ `quote_generator_api.py` — Supplier RFQs
4. `prism_inspection_engine.py` — QC pass/fail
5. `vertex_automation.py` — Billing/invoicing

### Phase 2 — HIGH VALUE
6. `shield_verification.py` — Service verification
7. `shield_lead_screening.py` — SHIELD referrals
8. `jeta_fraud_detection.py` — Fraud detection
9. `compass_api.py` — CRM relationships
10. `gbis_community_health_miner.py` — Grants

### Phase 3 — COMPLETE COVERAGE
11. All remaining PRISM compliance modules
12. DDCSS prospect/pipeline tracking
13. ATLAS project management
14. LBPC surplus recovery

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

Once all sectors are integrated, the learning engine will:

1. **GPSS:** Learn which agencies, NAICS codes, and set-asides have highest win rates
2. **PRISM:** Learn which agents, service types, and regions have best QC pass rates
3. **VERTEX:** Learn which clients pay fastest, which claims get approved
4. **DDCSS:** Learn which sectors, pitches, and avatars convert best
5. **JETA:** Learn which counterparty patterns indicate fraud
6. **SHIELD:** Learn which referral sources and contractors perform best
7. **LBPC:** Learn which counties and property types have best claim approval
8. **GBIS:** Learn which agencies and grant types DDI/CWC win
9. **ATLAS:** Learn which project types finish on time and under budget
10. **COMPASS:** Learn which touchpoint patterns lead to contracts

---

*Every sector integrated = every action becomes training data. NEXUS gets smarter across the entire business.*
