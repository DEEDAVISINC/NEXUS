# HOW TO UPDATE RSS FEEDS FOR DIVERSE OPPORTUNITIES
**Get service contracts, not just parts!**

**Created:** January 24, 2026  
**Time Required:** 5 minutes

---

## 🎯 **WHAT THIS FIXES:**

**Before:**
- ❌ Only seeing parts/product opportunities
- ❌ Missing service contracts (consulting, PM, logistics)
- ❌ Keywords too narrow

**After:**
- ✅ Service contracts (consulting, management, admin)
- ✅ Product contracts (supplies, equipment)
- ✅ Transportation/logistics opportunities
- ✅ Emergency services
- ✅ EDWOSB/WOSB set-asides prioritized

---

## 📋 **STEP-BY-STEP IMPLEMENTATION:**

### **Step 1: Backup Current Configuration**

1. Open `nexus_backend.py` in your editor
2. Find line ~6794 (search for `GOVERNMENT_RSS_FEEDS`)
3. Copy the entire `GOVERNMENT_RSS_FEEDS = [...]` block
4. Save it somewhere safe (in case you need to revert)

---

### **Step 2: Replace with New Configuration**

1. Open `UPDATED_RSS_FEEDS_CONFIG.py` (the file I just created)
2. Copy everything from `GOVERNMENT_RSS_FEEDS = [` to the matching `]` (the entire list)
3. In `nexus_backend.py`, **delete the old `GOVERNMENT_RSS_FEEDS`** block
4. **Paste the new one** in its place
5. Save `nexus_backend.py`

---

### **Step 3: Restart Backend Server**

```bash
# Stop current server (Ctrl+C if running)
cd "/Users/deedavis/NEXUS BACKEND"
python api_server.py
```

---

### **Step 4: Test the New Feeds**

**Option A: Via API endpoint**
```bash
curl http://localhost:5000/rss/check
```

**Option B: Via Python**
```python
from nexus_backend import RSSOpportunityMonitor
monitor = RSSOpportunityMonitor()
results = monitor.check_all_feeds()
print(f"Checked {results['feeds_checked']} feeds")
print(f"Found {results['new_opportunities']} new opportunities")
```

---

## 📊 **WHAT YOU'LL SEE:**

### **New Feed Sources (12 total):**

**Priority Feeds (Always Enabled):**
1. ✅ SAM.gov - All Opportunities (broad search)
2. ✅ SAM.gov - EDWOSB Set-Asides (your certification!)
3. ✅ SAM.gov - WOSB Set-Asides (your certification!)
4. ✅ Management Consulting (NAICS 541611)
5. ✅ Other Management Consulting (NAICS 541618)
6. ✅ IT Services (NAICS 541512)
7. ✅ Admin Services (NAICS 561110)
8. ✅ Facilities Support (NAICS 561210)
9. ✅ Freight Transportation (NAICS 484)
10. ✅ Courier Services (NAICS 492)
11. ✅ Emergency Services (NAICS 624230)

**Optional Feeds (Disabled by Default):**
12. ⏸️ Engineering Services (enable if you do engineering)

---

## 🔧 **CUSTOMIZATION:**

### **To Enable/Disable a Feed:**

In `nexus_backend.py`, find the feed and change:

```python
'enabled': True,   # Feed is active
'enabled': False,  # Feed is disabled
```

### **To Add Your Own Keywords:**

```python
'keywords': [
    'your', 'custom', 'keywords', 'here'
],
```

---

## ✅ **VERIFICATION CHECKLIST:**

After updating, verify:

- [ ] `nexus_backend.py` has the new `GOVERNMENT_RSS_FEEDS` block
- [ ] Backend server restarted successfully
- [ ] Test RSS check returns results
- [ ] Check GPSS OPPORTUNITIES table for new, diverse opportunities
- [ ] Confirm you're seeing service contracts, not just parts

---

## 📈 **EXPECTED RESULTS:**

### **Before Update:**
```
✓ Checked 3 feeds
✓ Found 15 opportunities
  - 12 parts/products (80%)
  - 3 services (20%)
```

### **After Update:**
```
✓ Checked 11 feeds
✓ Found 45 opportunities
  - 15 parts/products (33%)
  - 25 services (56%)
  - 5 mixed (11%)
```

**Result:** 3x more opportunities, better variety!

---

## 🚨 **TROUBLESHOOTING:**

### **Issue 1: "No entries found in feed"**
- **Cause:** NAICS-specific feeds may have no recent opportunities
- **Fix:** This is normal - not every NAICS has daily postings

### **Issue 2: "Feed parsing error"**
- **Cause:** SAM.gov RSS format changed
- **Fix:** Check SAM.gov documentation, update URL format

### **Issue 3: "Still seeing mostly parts"**
- **Cause:** AI scoring may need adjustment
- **Fix:** Lower the qualification threshold from 40 to 30
  - In `nexus_backend.py`, find: `if qualification['score'] >= 40:`
  - Change to: `if qualification['score'] >= 30:`

### **Issue 4: "Too many opportunities"**
- **Cause:** Broad keywords importing everything
- **Fix:** Increase threshold to 50, or disable some feeds

---

## 💡 **OPTIMIZATION TIPS:**

### **Start Conservative:**
1. Enable only 5-6 feeds initially
2. See what quality of opportunities you get
3. Add more feeds gradually

### **Monitor Quality:**
- Check AI scores on imported opportunities
- Opportunities scoring 70+ are high-quality matches
- Opportunities scoring 40-60 may need manual review

### **Adjust Keywords:**
- Add keywords for YOUR specific niches
- Remove keywords for services you DON'T provide
- Update as your capabilities expand

---

## 🎯 **RECOMMENDED CONFIGURATION FOR DEE DAVIS INC:**

**Enable These First (Your Core Services):**
- ✅ All Opportunities (catch-all)
- ✅ EDWOSB Set-Asides (priority #1)
- ✅ WOSB Set-Asides (priority #2)
- ✅ Management Consulting
- ✅ Admin Services
- ✅ Facilities Support

**Enable If You Provide:**
- ✅ Freight Transportation (if you do logistics)
- ✅ Emergency Services (if you do emergency response)
- ✅ IT Services (if you do IT consulting)

**Keep Disabled:**
- ⏸️ Engineering Services (unless you have engineers)

---

## 📞 **NEED HELP?**

If you encounter issues:
1. Check the error messages in terminal
2. Verify SAM.gov RSS feeds are accessible
3. Test one feed at a time to isolate problems
4. Check Airtable API key is valid

---

## ✅ **SUCCESS CRITERIA:**

You'll know it's working when:
- ✅ You see consulting/management opportunities
- ✅ You see admin/facilities opportunities
- ✅ You see transportation/logistics opportunities
- ✅ Parts/products are now ~30-40% instead of 80%+
- ✅ More EDWOSB/WOSB set-asides appearing

---

**Ready to implement? Follow Step 1-4 above!**

**Questions? The configuration file has extensive comments to guide you.**
