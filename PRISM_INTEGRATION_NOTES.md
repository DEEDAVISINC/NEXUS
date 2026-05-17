# PRISM Integration — Fulfillment Platform Notes

**Last Updated:** May 16, 2026

---

## API ACCESS STATUS

| Platform | API Available? | Requirement | Current Access |
|----------|---------------|-------------|----------------|
| **Uber Health** | Yes | $200K annual revenue | ❌ Manual dashboard only |
| **Roadie** | TBD | Unknown — need to research | ❌ Manual dashboard only |
| **DoorDash Drive** | Yes | Unknown — pending sales call | ⏳ Pending |

---

## UBER HEALTH API

- Requires **$200K annual revenue** to qualify for API integration
- Once DDI hits that threshold (University Health contract alone is $4M+/year), request API access
- API enables: automated dispatch, real-time tracking feed, webhook notifications, bulk uploads

**Contact:** Jeff Metz (jeffm@uber.com) — mentioned API in May 15 call

---

## ROADIE API

- Need to research if Roadie offers API access
- Their website mentions "API" and "bulk upload" options
- May require enterprise tier or volume commitment

**Research needed:**
- Does Roadie have a developer portal?
- What's the volume/revenue threshold for API?
- Can DDI get sandbox access for testing?

---

## PRISM INTEGRATION GOAL

Eventually integrate fulfillment platforms into PRISM so:
1. Dispatch requests flow from PRISM → Platform automatically
2. Real-time tracking data flows back into PRISM
3. Proof of delivery / POD images sync to PRISM
4. Billing reconciliation automated
5. SLA reporting pulls from platform data

**For now:** Manual dashboard operation. API integration is Phase 2 after contracts are won and revenue flows.

---

## NEXT STEPS

1. Win University Health contracts (Lab + Pharmacy)
2. Build revenue to $200K threshold for Uber Health API
3. Research Roadie API access requirements
4. Wait for DoorDash Drive callback — ask about API
5. Design PRISM integration architecture once API access is confirmed
