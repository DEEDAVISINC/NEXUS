# HAVEN Action Plan

**Created:** May 9, 2026
**Updated:** May 25, 2026
**Status:** ACTIVE EMERGENCY RESPONSE — Louisiana Flooding
**Goal:** HAVEN ready to pitch MCOs by June 2026 (before hurricane season)

---

## ⚠️ EMERGENCY STATUS (May 25, 2026)

**Louisiana Flood Watch in effect.** SE Louisiana experiencing flash flooding. MCO outreach initiated — emergency follow-ups being sent today.

**New Rule:** Active emergencies override registration gates. Reach out NOW, sort paperwork after.

**Tracker:** `HAVEN/OUTREACH/HAVEN_MCO_OUTREACH_TRACKER.md`

---

## NEXUS INTEGRATION — COMPLETE ✅

The HAVEN system is now built into NEXUS:

| Component | Status | File |
|-----------|--------|------|
| Airtable Schema | ✅ Complete | `HAVEN_NETWORK_REGISTRY_SCHEMA.md` |
| Airtable Base | ✅ Created | Base ID: `appdCPCU8mYLCryd4` |
| MCO Records | ✅ 31 MCOs | FL (8), TX (17), LA (5), MI (1) |
| Transport Partners | ✅ 34 partners | Rideshare, Fleet, Charter |
| Housing Partners | ✅ 19 partners | Hotels, Extended Stay, Corporate |
| Medical Partners | ✅ 39 partners | HHA, DME, Pharmacy |
| NEXUS Module | ✅ Complete | `haven_module.py` |
| Backend Integration | ✅ Complete | `nexus_backend.py` → `HAVENSystem` |

**CLI Commands:**
```bash
python3 haven_module.py status     # System status
python3 haven_module.py readiness  # Hurricane readiness
python3 haven_module.py network    # Partner network stats
python3 haven_module.py mcos       # MCO pipeline
```

**Python API:**
```python
from nexus_backend import HAVENSystem
haven = HAVENSystem()
haven.get_system_status()    # Full status
haven.get_readiness_report() # Readiness check
haven.get_mco_pipeline()     # MCO stats
```

---

## PRIORITY 0: STATE REGISTRATIONS (Do First)

DDI must be legally authorized to do business in FL, TX, LA before signing contracts.

### Florida
| Item | Status | Action | Cost |
|---|---|---|---|
| Foreign Corp Registration | ⬜ Not Started | File with Sunbiz.org | ~$70 |
| Registered Agent | ⬜ Not Started | Confirm family member | FREE |
| Certificate of Good Standing | ⬜ Not Started | Order from Michigan LARA | ~$10 |
| Virtual Business Address | ⬜ Not Started | Anytime Mailbox or similar | ~$10-15/mo |

**Dee Action:** Confirm FL family member will serve as registered agent → File online

### Texas
| Item | Status | Action | Cost |
|---|---|---|---|
| Foreign Corp Registration | ⬜ Not Started | File Form 301 with TX SOS | ~$750 |
| Registered Agent | ⬜ Not Started | Confirm family member | FREE |
| Certificate of Good Standing | ⬜ Not Started | Order from Michigan LARA | ~$10 |
| Virtual Business Address | ⬜ Not Started | Anytime Mailbox or similar | ~$10-15/mo |

**Dee Action:** Confirm TX family member will serve as registered agent → File online

### Louisiana
| Item | Status | Action | Cost |
|---|---|---|---|
| Foreign Corp Registration | ⬜ Not Started | File Form SS326 with LA SOS | ~$100 |
| Registered Agent | ⬜ Not Started | Use paid service (no family) | ~$100/yr |
| Certificate of Good Standing | ⬜ Not Started | Order from Michigan LARA | ~$10 |
| Virtual Business Address | ⬜ Not Started | Anytime Mailbox or similar | ~$10-15/mo |

**Total Entry Cost:** ~$920 filing + ~$1,380/year ongoing

---

## PRIORITY 1: TRANSPORT PARTNERS (Week 1-2)

### Rideshare Platforms
| Partner | Status | Next Action | Contact |
|---|---|---|---|
| Lyft Healthcare | ✅ Contact form submitted 5/8 | Wait for response | lyft.com/healthcare |
| Uber Health | ⬜ Prospect | Submit partnership inquiry | uberhealth.com |

### Fleet Operators (Priority — fill stretcher/bariatric gap)
| Partner | State | Specialty | Next Action |
|---|---|---|---|
| Stellar Transportation | FL | Stretcher statewide | Research contact, send T2 |
| PrimeCare Transports | TX | Bariatric 650 lbs | Research contact, send T2 |
| Healthlift Medical | TX | Bariatric Houston | Research contact, send T2 |
| SPD LLC | LA | Stretcher/wheelchair | Call (877) 577-1440 |
| A-MED Ambulance | LA | Wheelchair New Orleans | Research contact |
| HOUR Transportation | MI | Bariatric 400 lbs | Call (248) 569-7500 |

### Charter (Mass Evacuation)
| Partner | Coverage | Next Action |
|---|---|---|
| Greyhound Charter | National | Research healthcare/emergency contact |

---

## PRIORITY 2: HOUSING PARTNERS (Week 2-3)

### National Chains (Volume)
| Partner | Contact Target | Next Action |
|---|---|---|
| Extended Stay America | Client Connect / Tim Horan (Group VP) | **SEND Tuesday May 27** — Email ready in `HAVEN/OUTREACH/EXTENDED_STAY_AMERICA_OUTREACH.md` |
| Marriott Extended Stay | Sameh Sekina (sameh.sekina@marriott.com) — Gov Group Sales | **SEND Tuesday May 27** — Email ready in `HAVEN/OUTREACH/MARRIOTT_EXTENDED_STAY_OUTREACH.md` |
| Hilton Extended Stay | GovernmentSales@hilton.com / Katherine Lugar (EVP Corp Affairs) | **SEND Tuesday May 27** — Email ready in `HAVEN/OUTREACH/HILTON_EXTENDED_STAY_OUTREACH.md` |
| Wyndham Extended Stay | Max Izmaylov (max.izmaylov@wyndham.com) — Gov & Agencies | **SEND Tuesday May 27** — Email ready in `HAVEN/OUTREACH/WYNDHAM_EXTENDED_STAY_OUTREACH.md` |
| Sonesta Extended Stay | Sonesta GSO / development@sonesta.com | **SEND Tuesday May 27** — Email ready in `HAVEN/OUTREACH/SONESTA_EXTENDED_STAY_OUTREACH.md` |

### Disaster Specialists (Priority — they get it)
| Partner | State | Next Action |
|---|---|---|
| Lodgeur Houston | TX | Research contact, send H2 |
| Houston Corporate Housing | TX | Research contact, send H2 |

---

## PRIORITY 3: MEDICAL PARTNERS (Week 3-4)

### Home Health Agencies
| Partner | State | Why Priority | Next Action |
|---|---|---|---|
| CenterWell Home Health | FL + TX | Humana subsidiary, scale | Research contact, send M1 |
| Ochsner Home Health | LA | NOLA + BR, major system | Research contact, send M1 |
| BayCare HomeCare | FL | Tampa Bay, 4.5-star | Research contact, send M1 |
| Pulse Home Health | LA | #1 LA satisfaction | Research contact, send M1 |

### DME Suppliers
| Partner | State | Why Priority | Next Action |
|---|---|---|---|
| JC Home Medical | FL | Jacksonville, respiratory | Research contact, send M2 |
| Care Medical Supplies | FL | Statewide delivery | Research contact, send M2 |

### Pharmacy (Later — complex)
| Partner | Notes |
|---|---|
| CVS/Caremark | Need to find healthcare partnerships contact |
| Walgreens | Need to find healthcare partnerships contact |

---

## PRIORITY 4: MCO OUTREACH

**~~Do NOT start MCO outreach until:~~** ← OVERRIDDEN May 25, 2026

**NEW RULE:** Active emergencies bypass all gates. When members are being displaced, we reach out immediately.

**Registration status (still needed for contracts):**
- [ ] FL foreign corp registration — in progress
- [ ] TX foreign corp registration — in progress  
- [ ] LA foreign corp registration — in progress

**But outreach happens NOW during emergencies.**

**Tracker:** `HAVEN/OUTREACH/HAVEN_MCO_OUTREACH_TRACKER.md`

### MCO Priority Targets

**Centene Family (HAP CareSource connection):**
| MCO | State | Members | Template |
|---|---|---|---|
| Sunshine Health | FL | 2M | T3 (Centene) |
| Superior HealthPlan | TX | 2M | T3 (Centene) |
| Louisiana Healthcare Connections | LA | 500K | T3 (Centene) |

**Anthem/Elevance Family:**
| MCO | State | Members | Template |
|---|---|---|---|
| Simply Healthcare | FL | 1M | T4 (Anthem) |
| Amerigroup Texas | TX | 1M | T4 (Anthem) |
| Healthy Blue Louisiana | LA | 450K | T4 (Anthem) |

---

## CONTACT RESEARCH METHOD

For each priority partner:

1. **Website:** Look for "Contact Us," "Partnerships," "Healthcare," or "Provider" pages
2. **LinkedIn:** Search for:
   - "[Company] healthcare partnerships"
   - "[Company] business development"
   - "[Company] provider relations"
3. **Phone:** Call main number, ask for healthcare/provider partnerships
4. **Google:** "[Company] healthcare partnership contact" or "[Company] disaster housing"

**Update Airtable** with:
- Contact name
- Title
- Email
- Phone
- LinkedIn URL
- Date researched

---

## MILESTONES

| Milestone | Target Date | Status |
|---|---|---|
| Airtable base created | May 9, 2026 | ✅ Complete |
| MCOs seeded (31) | May 9, 2026 | ✅ Complete |
| Partners seeded (123) | May 9, 2026 | ✅ Complete |
| FL registration filed | May 16, 2026 | ⬜ |
| TX registration filed | May 16, 2026 | ⬜ |
| LA registration filed | May 16, 2026 | ⬜ |
| First transport partner signed | May 31, 2026 | ⬜ |
| First housing partner signed | May 31, 2026 | ⬜ |
| First medical partner signed | June 7, 2026 | ⬜ |
| MCO outreach begins | June 14, 2026 | ⬜ |
| First MCO pitch meeting | June 30, 2026 | ⬜ |
| **Hurricane season starts** | **June 1, 2026** | 📅 |

---

## FILES REFERENCE

| File | Purpose |
|---|---|
| `HAVEN_DISASTER_RECOVERY_TPA_STRATEGY.md` | Master strategy doc |
| `HAVEN_Master_Proposal.html` | MCO pitch document |
| `HAVEN_MCO_OUTREACH_TEMPLATES.md` | MCO email templates |
| `HAVEN_PARTNER_OUTREACH_TEMPLATES.md` | Partner email templates |
| `HAVEN_NETWORK_REGISTRY_SCHEMA.md` | Airtable schema |
| `HAVEN_ACTION_PLAN.md` | This file |

---

## DAILY CHECK-IN

Each working day on HAVEN:
1. Check Lyft response (submitted 5/8)
2. Update Airtable with any contact research
3. Send 3-5 outreach emails
4. Follow up on pending responses
5. Update this action plan

---

*Hurricane season starts June 1. Work backward from there.*

---

## EMERGENCY OUTREACH LOG

| Date | Event | MCOs Contacted | Response |
|------|-------|----------------|----------|
| May 25, 2026 | LA Flood Watch | LA MCOs (5) — emergency follow-up | PENDING |

**Full tracker:** `HAVEN/OUTREACH/HAVEN_MCO_OUTREACH_TRACKER.md`
