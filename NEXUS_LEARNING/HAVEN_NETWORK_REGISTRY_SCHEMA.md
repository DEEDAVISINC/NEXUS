# HAVEN Network Registry — Airtable Schema

**Created:** May 9, 2026
**NEXUS Module:** `haven_module.py`
**Backend Integration:** `nexus_backend.py` → `HAVENSystem` class
**Purpose:** Database structure for HAVEN disaster response vendor network
**Platform:** Airtable (manual Phase 1) → NEXUS integration (Phase 3)

---

## BASE: `HAVEN_Network`

---

## TABLE 1: `Transport_Partners`

Rideshare, NEMT fleets, charter buses, medical transport, courier/delivery.

| Field | Type | Description |
|---|---|---|
| `partner_id` | Auto Number | Unique identifier |
| `company_name` | Single Line Text | Legal business name |
| `dba_name` | Single Line Text | Doing business as (if different) |
| `partner_type` | Single Select | Rideshare / NEMT Fleet / Charter Bus / Medical Transport / Courier |
| `contact_name` | Single Line Text | Primary contact |
| `contact_email` | Email | Primary email |
| `contact_phone` | Phone | Primary phone |
| `address` | Long Text | Business address |
| `states_served` | Multiple Select | FL / TX / LA / National |
| `counties_served` | Long Text | Specific counties (comma-separated) |
| `vehicle_types` | Multiple Select | Sedan / SUV / Wheelchair Van / Stretcher / Bus / Cargo Van |
| `fleet_size` | Number | Total vehicles available |
| `disaster_capacity` | Number | Vehicles committed for disaster response |
| `insurance_current` | Checkbox | Insurance verified and current |
| `insurance_expiry` | Date | Insurance expiration date |
| `rate_type` | Single Select | Per Trip / Per Mile / Per Hour / Flat Fee |
| `standard_rate` | Currency | Normal rate |
| `disaster_rate` | Currency | Pre-negotiated disaster rate |
| `agreement_status` | Single Select | Prospect / Outreach / Negotiating / Signed / Active |
| `agreement_date` | Date | Date agreement signed |
| `agreement_file` | Attachment | Signed agreement PDF |
| `activation_status` | Single Select | 🟢 Ready / 🟡 Limited / 🔴 Unavailable |
| `last_contact` | Date | Last communication date |
| `notes` | Long Text | Internal notes |
| `created` | Created Time | Record created |
| `modified` | Last Modified Time | Record last updated |

---

## TABLE 2: `Housing_Partners`

Hotels, extended stay, corporate housing, property managers.

| Field | Type | Description |
|---|---|---|
| `partner_id` | Auto Number | Unique identifier |
| `property_name` | Single Line Text | Hotel/property name |
| `chain_brand` | Single Select | Marriott / Hilton / IHG / Wyndham / Choice / Independent / Extended Stay |
| `partner_type` | Single Select | Hotel / Extended Stay / Corporate Housing / Property Manager / FEMA Trailer |
| `contact_name` | Single Line Text | Sales/emergency contact |
| `contact_email` | Email | Primary email |
| `contact_phone` | Phone | Primary phone |
| `address` | Long Text | Property address |
| `city` | Single Line Text | City |
| `state` | Single Select | FL / TX / LA |
| `county` | Single Line Text | County |
| `zip` | Single Line Text | ZIP code |
| `total_rooms` | Number | Total room inventory |
| `disaster_block` | Number | Rooms committed for disaster response |
| `room_types` | Multiple Select | Standard / Suite / ADA / Pet-Friendly / Kitchen |
| `amenities` | Multiple Select | WiFi / Breakfast / Laundry / Pool / Fitness / Pet-Friendly |
| `standard_rate` | Currency | Rack rate |
| `disaster_rate` | Currency | Pre-negotiated disaster rate |
| `fema_approved` | Checkbox | On FEMA TSA approved list |
| `insurance_direct_bill` | Checkbox | Can direct bill insurance carriers |
| `agreement_status` | Single Select | Prospect / Outreach / Negotiating / Signed / Active |
| `agreement_date` | Date | Date agreement signed |
| `agreement_file` | Attachment | Signed agreement PDF |
| `activation_status` | Single Select | 🟢 Ready / 🟡 Limited / 🔴 Unavailable |
| `current_availability` | Number | Rooms available NOW |
| `last_contact` | Date | Last communication date |
| `notes` | Long Text | Internal notes |
| `created` | Created Time | Record created |
| `modified` | Last Modified Time | Record last updated |

---

## TABLE 3: `Medical_Partners`

Home health agencies, DME suppliers, pharmacies, medical couriers.

| Field | Type | Description |
|---|---|---|
| `partner_id` | Auto Number | Unique identifier |
| `company_name` | Single Line Text | Legal business name |
| `partner_type` | Single Select | Home Health Agency / DME Supplier / Pharmacy / Medical Courier / Hospice |
| `license_number` | Single Line Text | State license number |
| `license_state` | Single Select | FL / TX / LA |
| `license_expiry` | Date | License expiration date |
| `medicare_certified` | Checkbox | Medicare certified |
| `medicaid_enrolled` | Checkbox | Enrolled in state Medicaid |
| `contact_name` | Single Line Text | Primary contact |
| `contact_email` | Email | Primary email |
| `contact_phone` | Phone | Primary phone |
| `address` | Long Text | Business address |
| `states_served` | Multiple Select | FL / TX / LA |
| `counties_served` | Long Text | Specific counties (comma-separated) |
| `services_offered` | Multiple Select | Skilled Nursing / PT / OT / Speech / Aide / Rx Delivery / DME / Oxygen / CPAP |
| `staff_count` | Number | Total field staff |
| `disaster_capacity` | Number | Staff available for disaster deployment |
| `languages` | Multiple Select | English / Spanish / Vietnamese / Creole / Other |
| `insurance_current` | Checkbox | Insurance verified and current |
| `insurance_expiry` | Date | Insurance expiration date |
| `rate_type` | Single Select | Per Visit / Per Hour / Per Diem / Per Item |
| `standard_rate` | Currency | Normal rate |
| `disaster_rate` | Currency | Pre-negotiated disaster rate |
| `agreement_status` | Single Select | Prospect / Outreach / Negotiating / Signed / Active |
| `agreement_date` | Date | Date agreement signed |
| `agreement_file` | Attachment | Signed agreement PDF |
| `activation_status` | Single Select | 🟢 Ready / 🟡 Limited / 🔴 Unavailable |
| `24_7_available` | Checkbox | Can respond 24/7 |
| `last_contact` | Date | Last communication date |
| `notes` | Long Text | Internal notes |
| `created` | Created Time | Record created |
| `modified` | Last Modified Time | Record last updated |

---

## TABLE 4: `MCO_Contracts`

Managed care organization relationships for HAVEN services.

| Field | Type | Description |
|---|---|---|
| `contract_id` | Auto Number | Unique identifier |
| `mco_name` | Single Line Text | MCO name |
| `parent_company` | Single Line Text | Parent company (Centene, Molina, etc.) |
| `state` | Single Select | FL / TX / LA / MI |
| `program_type` | Multiple Select | Medicaid / Medicare Advantage / Dual Eligible / CHIP |
| `member_count` | Number | Approximate member population |
| `contact_name` | Single Line Text | Provider relations contact |
| `contact_email` | Email | Primary email |
| `contact_phone` | Phone | Primary phone |
| `services_contracted` | Multiple Select | NEMT / Housing / Medical Continuity / Evacuation / All HAVEN |
| `contract_status` | Single Select | Target / Outreach / Negotiating / Credentialing / Active |
| `contract_start` | Date | Contract effective date |
| `contract_end` | Date | Contract expiration date |
| `contract_value` | Currency | Estimated annual value |
| `rates_transport` | Currency | Per-trip transport rate |
| `rates_housing` | Currency | Housing placement fee |
| `rates_medical` | Currency | Medical coordination fee |
| `credentialing_status` | Single Select | Not Started / In Progress / Complete |
| `portal_access` | Checkbox | Have portal access |
| `portal_url` | URL | Provider portal URL |
| `portal_login` | Single Line Text | Login username |
| `agreement_file` | Attachment | Signed contract PDF |
| `last_contact` | Date | Last communication date |
| `next_action` | Single Line Text | Next step needed |
| `notes` | Long Text | Internal notes |
| `created` | Created Time | Record created |
| `modified` | Last Modified Time | Record last updated |

---

## TABLE 5: `Disaster_Events`

Active and historical disaster events being served.

| Field | Type | Description |
|---|---|---|
| `event_id` | Auto Number | Unique identifier |
| `event_name` | Single Line Text | Event name (e.g., "Hurricane Maria 2026") |
| `event_type` | Single Select | Hurricane / Tornado / Flood / Wildfire / Winter Storm / Other |
| `fema_declaration` | Single Line Text | FEMA declaration number (if applicable) |
| `declaration_date` | Date | Date of disaster declaration |
| `states_affected` | Multiple Select | FL / TX / LA |
| `counties_affected` | Long Text | Affected counties |
| `event_status` | Single Select | Pre-Event / Active / Recovery / Closed |
| `activation_date` | Date | When DDI activated response |
| `deactivation_date` | Date | When DDI closed response |
| `cases_served` | Number | Total cases/families served |
| `transport_trips` | Number | Total transport trips |
| `housing_placements` | Number | Total housing placements |
| `medical_services` | Number | Total medical services coordinated |
| `total_revenue` | Currency | Total revenue from event |
| `total_cost` | Currency | Total vendor costs |
| `margin` | Currency | DDI margin |
| `lessons_learned` | Long Text | Post-event notes |
| `created` | Created Time | Record created |
| `modified` | Last Modified Time | Record last updated |

---

## TABLE 6: `Cases`

Individual cases/families being served during disasters.

| Field | Type | Description |
|---|---|---|
| `case_id` | Auto Number | Unique identifier |
| `event_id` | Link to Disaster_Events | Which disaster event |
| `mco_id` | Link to MCO_Contracts | Referring MCO |
| `member_id` | Single Line Text | MCO member ID |
| `member_name` | Single Line Text | Primary member name |
| `member_phone` | Phone | Contact phone |
| `member_email` | Email | Contact email |
| `family_size` | Number | Number of people in household |
| `special_needs` | Multiple Select | Wheelchair / Oxygen / Dialysis / Pediatric / Elderly / Pregnant / Mental Health |
| `languages` | Multiple Select | English / Spanish / Vietnamese / Creole / Other |
| `home_address` | Long Text | Original home address |
| `current_location` | Long Text | Current location |
| `needs_housing` | Checkbox | Needs temporary housing |
| `needs_transport` | Checkbox | Needs transport services |
| `needs_medical` | Checkbox | Needs medical continuity |
| `needs_rx` | Checkbox | Needs prescription assistance |
| `needs_dme` | Checkbox | Needs DME replacement |
| `case_status` | Single Select | Intake / Active / Resolved / Closed |
| `assigned_to` | Single Line Text | DDI staff assigned |
| `intake_date` | Date | When case was received |
| `resolution_date` | Date | When case was resolved |
| `notes` | Long Text | Case notes |
| `created` | Created Time | Record created |
| `modified` | Last Modified Time | Record last updated |

---

## TABLE 7: `Service_Activations`

Individual service requests within a case.

| Field | Type | Description |
|---|---|---|
| `activation_id` | Auto Number | Unique identifier |
| `case_id` | Link to Cases | Parent case |
| `service_type` | Single Select | Transport / Housing / Home Health / DME / Rx / Other |
| `partner_id` | Link (conditional) | Assigned vendor (Transport, Housing, or Medical partner) |
| `service_description` | Long Text | Details of service needed |
| `scheduled_date` | Date | When service is scheduled |
| `scheduled_time` | Single Line Text | Time of service |
| `pickup_address` | Long Text | Pickup location (transport) |
| `destination_address` | Long Text | Destination (transport/housing) |
| `service_status` | Single Select | Requested / Scheduled / In Progress / Completed / Cancelled |
| `completion_date` | Date | When service was completed |
| `vendor_cost` | Currency | What DDI pays vendor |
| `billable_amount` | Currency | What DDI bills MCO/insurance |
| `billed` | Checkbox | Invoice submitted |
| `paid` | Checkbox | Payment received |
| `notes` | Long Text | Service notes |
| `created` | Created Time | Record created |
| `modified` | Last Modified Time | Record last updated |

---

## VIEWS TO CREATE

### Transport_Partners
- All Partners (grid)
- By State (grouped)
- Ready to Activate (🟢 only)
- Needs Follow-up (last_contact > 30 days)
- Pending Agreements

### Housing_Partners
- All Properties (grid)
- By State (grouped)
- By Chain/Brand (grouped)
- Available Now (current_availability > 0)
- FEMA Approved Only

### Medical_Partners
- All Partners (grid)
- By State (grouped)
- By Service Type (grouped)
- 24/7 Available
- License Expiring Soon

### MCO_Contracts
- All MCOs (grid)
- By State (grouped)
- Active Contracts
- Pipeline (Outreach/Negotiating)
- Michigan (HAP CareSource reference)

### Cases
- Active Cases (gallery)
- By Event (grouped)
- By MCO (grouped)
- Needs Attention (special_needs not empty)
- Resolved This Week

---

## AUTOMATIONS TO ADD (PHASE 3)

1. **New Case Alert** — Slack/email when new case is created
2. **Service Completion** — Update case status when all services complete
3. **Insurance Expiry Warning** — Alert 30 days before partner insurance expires
4. **License Expiry Warning** — Alert 60 days before medical partner license expires
5. **Follow-up Reminder** — Alert when partner not contacted in 30+ days
6. **FEMA Declaration Monitor** — (future) auto-create event when FEMA declares disaster

---

## NEXT STEPS

1. [ ] Create Airtable base `HAVEN_Network`
2. [ ] Build all 7 tables with fields above
3. [ ] Create standard views
4. [ ] Seed with initial partner prospects
5. [ ] Begin outreach and populate as partners sign

---

*This schema supports manual operations (Phase 1-2) and will integrate with NEXUS automation in Phase 3.*
