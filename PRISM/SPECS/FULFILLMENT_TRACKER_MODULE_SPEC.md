# PRISM Fulfillment Tracker Module — Spec

**Created:** May 16, 2026  
**Status:** BUILD NOW  
**Priority:** CRITICAL — Core DDI infrastructure

---

## SCOPE — ALL DDI OPERATIONS

This is **not** just for University Health. This is the fulfillment visibility layer for:

| System | Use Case |
|--------|----------|
| **MCOs** | NEMT rides, pharmacy delivery for health plans |
| **VITAL** | Specimen transport, mobile collection logistics |
| **HAVEN** | Care coordination transport, social services delivery |
| **University Health** | Lab courier, pharmacy courier |
| **Future contracts** | Any logistics-dependent service DDI manages |

**This is foundational DDI infrastructure — build before contracts go live.**

---

## PURPOSE

Unified view of all fulfillment activity across platforms (Uber Health, Roadie, DoorDash) within PRISM — even before API integration is available.

---

## CORE FEATURES

### 1. Delivery Log

| Field | Type | Source |
|-------|------|--------|
| `delivery_id` | String | Auto-generated or platform ID |
| `platform` | Enum | Uber Health / Roadie / DoorDash / Other |
| `client` | Lookup | Contract/client reference |
| `service_type` | Enum | Scheduled / STAT / After-Hours / Weekend / Holiday |
| `pickup_location` | String | Pharmacy/lab name or address |
| `delivery_address` | String | Patient/recipient address |
| `status` | Enum | Pending / Dispatched / In Transit / Delivered / Failed / Returned |
| `dispatched_at` | Timestamp | When sent to platform |
| `delivered_at` | Timestamp | When completed |
| `pod_link` | URL | Link to proof of delivery (photo/signature) |
| `driver_name` | String | If available from platform |
| `notes` | Text | Any issues, special instructions |

### 2. Dashboard View

**Panels:**
- **Today's Deliveries** — Count by status (Pending / In Transit / Delivered / Failed)
- **By Platform** — Breakdown of volume per fulfillment partner
- **SLA Tracker** — On-time % vs. target (85% for UH)
- **Alerts** — Failed deliveries, late deliveries, returns

### 3. Manual Entry Form

Quick-add form for logging deliveries:
- Select platform
- Select client/contract
- Enter pickup and delivery info
- Set status
- Add POD link when complete

### 4. Bulk Import

- CSV upload for batch entry
- Fields map to delivery log schema
- Validates required fields before import

### 5. Platform Links

Quick links to open each platform dashboard:
- Uber Health: health.uber.com
- Roadie: send.roadie.com
- DoorDash: doordash.com/drive/portal

---

## DATA MODEL

```python
class Delivery(BaseModel):
    id: str  # UUID
    platform: Literal["uber_health", "roadie", "doordash", "other"]
    client_id: str  # Reference to contract/client
    service_type: Literal["scheduled", "stat", "after_hours", "weekend", "holiday"]
    pickup_location: str
    delivery_address: str
    status: Literal["pending", "dispatched", "in_transit", "delivered", "failed", "returned"]
    dispatched_at: Optional[datetime]
    delivered_at: Optional[datetime]
    pod_link: Optional[str]
    driver_name: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
```

---

## API ENDPOINTS (PRISM Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/prism/deliveries` | List all deliveries (filterable) |
| GET | `/prism/deliveries/{id}` | Get single delivery |
| POST | `/prism/deliveries` | Create new delivery |
| PATCH | `/prism/deliveries/{id}` | Update delivery status |
| DELETE | `/prism/deliveries/{id}` | Delete delivery |
| POST | `/prism/deliveries/bulk` | Bulk import from CSV |
| GET | `/prism/deliveries/stats` | Dashboard stats |

---

## UI MOCKUP (Conceptual)

```
┌─────────────────────────────────────────────────────────────┐
│ PRISM — Fulfillment Tracker                    [+ New Delivery] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TODAY'S DELIVERIES                                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ Pending │ │In Transit│ │Delivered│ │ Failed  │           │
│  │   12    │ │    8    │ │   45    │ │    2    │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│                                                             │
│  BY PLATFORM                    SLA: 94.2% On-Time          │
│  ┌──────────────────────┐      Target: 85% ✅               │
│  │ Uber Health    35%   │                                   │
│  │ Roadie         65%   │                                   │
│  └──────────────────────┘                                   │
│                                                             │
│  RECENT DELIVERIES                                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ID      │ Platform │ Status    │ Pickup      │ Time   │ │
│  │ D-0047  │ Roadie   │ Delivered │ UH Main     │ 2:34p  │ │
│  │ D-0046  │ Uber     │ In Transit│ UH West     │ 2:15p  │ │
│  │ D-0045  │ Roadie   │ Delivered │ UH Main     │ 1:58p  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  QUICK LINKS: [Uber Health] [Roadie] [DoorDash]            │
└─────────────────────────────────────────────────────────────┘
```

---

## PHASE 2: API INTEGRATION

Once API access is unlocked:
- Auto-create deliveries when dispatched via API
- Webhook receivers for status updates
- Auto-pull POD images
- Real-time tracking feed

---

## BUILD TIMELINE

| Phase | Scope | When |
|-------|-------|------|
| **Phase 1** | Manual entry + dashboard + CSV import | **NOW — before contracts go live** |
| **Phase 2** | Uber Health API integration | After $200K revenue threshold |
| **Phase 3** | Roadie + DoorDash API integration | TBD based on access |

**Phase 1 is critical path.** DDI needs fulfillment visibility across MCOs, VITAL, HAVEN, and all courier contracts from day one.

---

## DEPENDENCIES

- PRISM backend running
- Database schema updated
- Frontend dashboard built (React or similar)
- Platform accounts active (✅ Uber Health, ✅ Roadie)
