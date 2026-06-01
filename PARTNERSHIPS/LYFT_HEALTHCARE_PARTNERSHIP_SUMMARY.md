# Lyft Healthcare — Partnership Summary

**Last Updated:** May 30, 2026  
**Status:** ⏳ **PENDING** — Developer account approval + AE sales call not completed

---

## Company

| Field | Value |
|-------|--------|
| **Product** | Lyft Healthcare / Lyft Concierge (healthcare NEMT) |
| **Website** | lyft.com/business/healthcare |
| **DDI use** | Wheelchair-accessible (WAV) + ambulatory NEMT fulfillment under DDI prime |

---

## DDI Account Status

| Item | Status |
|------|--------|
| Developer / API application | ⏳ Submitted — awaiting Lyft approval |
| API credentials in `.env` | Empty — `LYFT_HEALTHCARE_CLIENT_ID`, `LYFT_HEALTHCARE_CLIENT_SECRET`, `LYFT_HEALTHCARE_ACCOUNT_ID` |
| AE sales call | ⬜ **TODO** — schedule per `PENDING_ACTIONS.md` |
| PRISM integration | `prism_lyft_healthcare.py` · `prism_nemt.py` (dispatch lane when creds live) |

---

## Questions for AE Call

1. When is **Lyft Assisted** coming to Michigan?
2. **Medicaid** approval timeline for MI?
3. Is the **healthcare broker** program available for TPA/NEMT coordinators?

---

## Outreach / References

- HAVEN strategy — transport fulfillment partner (`HAVEN/STRATEGY/HAVEN_DISASTER_RECOVERY_TPA_STRATEGY.md`)
- ModivCare / Veyo broker applications reference Uber Health + Lyft Healthcare (buyer-facing — fulfillment stack)
- Initial outreach: contact form noted **May 8, 2026** in HAVEN strategy checklist

---

## Actions

- [ ] Schedule Lyft Healthcare AE sales call
- [ ] Complete developer account approval
- [ ] Load API credentials into `.env`
- [ ] Test WAV + ambulatory dispatch in PRISM

---

*Add to `PARTNERSHIPS_INDEX.md` when status moves to ✅ ACTIVE.*
