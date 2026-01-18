# 🚀 FINAL MINING SETUP - COMPLETE GUIDE

**Total Time: 15 minutes**

---

## ✅ STEP 1: ADD FIELDS TO VENDOR PORTAL

Open your **VENDOR PORTAL** table in Airtable and add these 9 fields:

```
1. Portal Name          → Single line text
2. Portal URL           → URL
3. Portal Type          → Single select (Federal, State, Local, Cooperative)
4. Auto-Mining Enabled  → Checkbox
5. Search Enabled       → Checkbox
6. Description          → Long text
7. Keywords             → Long text
8. Category             → Single select (Government, Commercial, Cooperative)
9. Icon                 → Single line text
```

---

## ✅ STEP 2: ADD FIELDS TO MINING TARGETS

Open your **Mining Targets** table in Airtable and add these 10 fields:

```
1. Target Name          → Single line text (PRIMARY FIELD)
2. Target URL           → URL
3. Source Type          → Single select (Intelligence, Marketplace, Archive, News, Portal)
4. Active               → Checkbox
5. Description          → Long text
6. Keywords             → Long text
7. Scraping Method      → Single select (API, Web Scraping, RSS Feed, Email Parsing, Manual)
8. Last Scraped         → Date & time
9. Scraping Frequency   → Single select (Hourly, Daily, Twice Daily, Weekly, Manual Only)
10. Opportunities Found → Number (Integer format)
```

---

## ✅ STEP 3: RUN THE POPULATE SCRIPT

Once fields are added, run this command:

```bash
cd "/Users/deedavis/NEXUS BACKEND"
python3 initialize_portals.py
```

---

## 📊 WHAT GETS POPULATED:

### VENDOR PORTAL (6 portals):
- ✅ SAM.gov - Federal Opportunities
- ✅ GSA eBuy
- ✅ DIBBS - Defense Logistics
- ✅ Unison Marketplace
- ✅ SBA SubNet
- ✅ NECO Cooperative

### Mining Targets (5 intelligence sources):
- ✅ FPDS - Federal Procurement Data
- ✅ USASpending.gov
- ✅ Acquisition.gov - Procurement Forecasts
- ✅ FedBizOpps Archive
- ✅ GSA Advantage

---

## 🎯 CHECKLIST:

- [ ] Add 9 fields to VENDOR PORTAL (5 min)
- [ ] Add 10 fields to Mining Targets (5 min)
- [ ] Run `python3 initialize_portals.py` (2 min)
- [ ] Verify 6 portals in VENDOR PORTAL
- [ ] Verify 5 targets in Mining Targets
- [ ] Reply "done" and I'll help you add the UI buttons next

---

## ⏱️ TIME BREAKDOWN:

| Task | Time |
|------|------|
| VENDOR PORTAL fields | 5 min |
| Mining Targets fields | 5 min |
| Run script | 2 min |
| Verify data | 3 min |
| **TOTAL** | **15 min** |

---

## 💡 NEXT STEPS AFTER THIS:

Once tables are populated, we'll add:
1. "Start Mining" button to GPSS dashboard
2. Mining Control Panel UI
3. Portal management interface

But first - complete steps 1-3 above! 🚀

---

**Let me know when you're done or if you hit any issues!**
