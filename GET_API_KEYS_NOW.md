# 🔑 GET API KEYS FOR SUB-SOURCING (30 Minutes)

**What you need:** Google Maps Places API + Yelp Fusion API  
**What you have:** ✅ Google CSE API (for general search) - different from Maps API  
**Cost:** Both have generous FREE tiers

---

## 🗺️ STEP 1: Google Maps Places API (15 minutes)

### **Why You Need This:**
Find subcontractors by service + location (e.g., "lawn care Oakland County MI")

### **Get the Key:**

1. **Go to:** https://console.cloud.google.com/
2. **Create project** (if you don't have one):
   - Click "Select Project" dropdown → "New Project"
   - Name: "Dee Davis Nexus"
   - Click "Create"
3. **Enable Places API:**
   - Click "☰" menu → "APIs & Services" → "Library"
   - Search: "Places API"
   - Click "Places API" → "Enable"
4. **Create API Key:**
   - Click "☰" menu → "APIs & Services" → "Credentials"
   - Click "+ CREATE CREDENTIALS" → "API Key"
   - Copy the key (starts with `AIza...`)
5. **Restrict the key** (security):
   - Click "Edit" on your new key
   - Under "API restrictions" → "Restrict key"
   - Select "Places API"
   - Click "Save"

### **Add to .env:**
```bash
GOOGLE_MAPS_API_KEY=AIzaSyC_your_actual_key_here
```

### **Free Tier:**
- $200/month credit (enough for 5,000-10,000 searches)
- You won't hit the limit for months

---

## 🍽️ STEP 2: Yelp Fusion API (15 minutes)

### **Why You Need This:**
Cross-reference subcontractors, get ratings/reviews, find more businesses

### **Get the Key:**

1. **Go to:** https://www.yelp.com/developers/v3/manage_app
2. **Log in** (or create free Yelp account if you don't have one)
3. **Create New App:**
   - App Name: "Dee Davis Nexus Sub Sourcing"
   - Industry: "Business Services"
   - Contact Email: Your email
   - Description: "Finding qualified subcontractors for government contracts"
   - Accept terms → Click "Create New App"
4. **Copy API Key:**
   - You'll see "Client ID" and "API Key"
   - Copy the **API Key** (long string)

### **Add to .env:**
```bash
YELP_API_KEY=your_yelp_api_key_here
```

### **Free Tier:**
- 500 API calls/day
- Perfect for your needs (10-20 searches per bid)

---

## ✅ STEP 3: Add to Your .env File

Open `/Users/deedavis/NEXUS BACKEND/.env` and add these two lines:

```bash
# Sub-Sourcing APIs (Added Feb 8, 2026)
GOOGLE_MAPS_API_KEY=AIzaSyC_your_key_here
YELP_API_KEY=your_yelp_key_here
```

---

## 🧪 STEP 4: Test It Works

Run this command to test:

```bash
python3 automated_sub_sourcing.py find \
  --service "pressure washing" \
  --location "Oakland County, MI" \
  --limit 10
```

**Expected output:**
```
============================================================
🔍 SEARCHING FOR SUBCONTRACTORS
============================================================
Service: pressure washing
Location: Oakland County, MI
Radius: 25 miles

✓ Google Maps: Found 15 businesses
✓ Yelp: Found 12 businesses

============================================================
✅ FOUND 20 QUALIFIED SUBCONTRACTORS
============================================================

Top Results:
1. ⭐⭐⭐⭐⭐ ABC Pressure Washing (4.8★, 245 reviews)
   📍 Pontiac, MI | 📞 (248) 555-0123
   💻 https://abcpressurewashing.com

2. ⭐⭐⭐⭐ Pro Clean Services (4.5★, 180 reviews)
   📍 Auburn Hills, MI | 📞 (248) 555-0456
   💻 https://proclean.com
...
```

---

## ⚠️ IF YOU DON'T GET THE KEYS

**Temporary workaround:**

You can still use the system! Just manually add subs to Airtable:

1. Google search: "lawn care Oakland County MI"
2. Open Airtable → GPSS SUBCONTRACTORS table
3. Add each business manually:
   - Company Name
   - Phone
   - Service Type
   - Location
   - Rating (from Google/Yelp)

**But automation is WAY better** - get the keys!

---

## 💰 Cost Breakdown (Per Month)

**Your usage estimate:**
- 5 service opportunities/week = 20/month
- 20 searches per opportunity = 400 searches/month

**Google Maps Places:**
- 400 searches = ~$2-4/month
- BUT you get $200/month free credit
- **Actual cost: $0/month** ✅

**Yelp Fusion:**
- 400 calls = FREE (under 500/day limit)
- **Actual cost: $0/month** ✅

**Total cost: $0/month** (for months to come)

---

## 🎯 NEXT STEPS

**After getting keys:**
1. ✅ Add to .env file
2. ✅ Test with command above
3. ✅ Use SubcontractorsTab.tsx (I'm building it now)
4. ✅ Click "Find Subs" in NEXUS UI

**Timeline: 30 minutes total, then it's automated forever!**

---

*Get the keys now - this is the foundation for your EDWOSB service opportunities!*
