# 🔍 Google Custom Search - Setup Instructions

**Date:** January 13, 2026  
**Status:** Script added, needs Search Engine ID  

---

## ✅ **What Was Fixed**

I added the Google Custom Search script back to your `index.html` file.

**File Modified:** `nexus-frontend/public/index.html`

**Added (line 29):**
```html
<!-- Google Custom Search Engine -->
<script async src="https://cse.google.com/cse.js?cx=YOUR_SEARCH_ENGINE_ID"></script>
```

---

## 🔧 **Setup Required (5 minutes)**

### **Step 1: Get Your Search Engine ID**

1. Go to: https://programmablesearchengine.google.com/
2. Sign in with your Google account
3. Click **"Add"** or **"Create a new search engine"**

### **Step 2: Configure Your Search Engine**

**Sites to search:**
- Option A: **Search the entire web** (recommended for general use)
  - Select "Search the entire web"
  
- Option B: **Search specific sites** (if you want to limit results)
  - Add domains like: sam.gov, gsa.gov, etc.

**Name:** NEXUS Search (or whatever you want)

**Language:** English

Click **Create**

### **Step 3: Get Your Search Engine ID**

After creation, you'll see a page with code. Look for:

```html
<script async src="https://cse.google.com/cse.js?cx=012345678901234567890:abcdefghij"></script>
```

The part after `cx=` is your **Search Engine ID**.

Example: `012345678901234567890:abcdefghij`

### **Step 4: Add ID to Your Code**

1. Open: `nexus-frontend/public/index.html`
2. Find line 29 (the script we just added)
3. Replace `YOUR_SEARCH_ENGINE_ID` with your actual ID

**Before:**
```html
<script async src="https://cse.google.com/cse.js?cx=YOUR_SEARCH_ENGINE_ID"></script>
```

**After:**
```html
<script async src="https://cse.google.com/cse.js?cx=012345678901234567890:abcdefghij"></script>
```

### **Step 5: Restart Frontend**

```bash
cd "nexus-frontend"
npm start
```

The search bar should now appear in the header!

---

## 🎨 **Customization Options**

### **In Google Console:**

After creating your search engine, you can customize:

1. **Look and Feel:**
   - Colors (match your NEXUS theme)
   - Layout (compact, full-width, two-page)
   - Font (match your site)

2. **Search Features:**
   - Enable image search
   - Enable autocomplete
   - Safe search settings
   - Result ranking

3. **Sites to Search:**
   - Add specific government sites
   - Add your own documentation
   - Exclude spammy sites

### **Recommended Settings for NEXUS:**

**Theme:**
- Background color: `#1F2937` (matches your header)
- Border color: `#374151`
- Text color: `#FFFFFF`

**Layout:** Compact (fits in header)

**Sites to Include:**
- sam.gov
- gsa.gov
- beta.sam.gov
- fbo.gov
- grants.gov
- your documentation sites

---

## 🔍 **Alternative: Custom Internal Search**

If you want to search **within your NEXUS data** instead of Google:

### **Option 1: Search Nexus Records**

Replace the Google search with a custom search that queries:
- Opportunities (GPSS)
- Contacts
- Projects (ATLAS)
- Clients
- Documents
- Invoices

**Advantage:** Searches your actual data, private and secure

**Implementation:** ~2-3 hours to build

### **Option 2: Both Google + Internal**

Have two search options:
- **Web Search** (Google CSE) - for finding new opportunities
- **NEXUS Search** (internal) - for finding your records

**Implementation:** ~3-4 hours to build

---

## 📊 **Search Analytics**

Once set up, you can track:
- What people search for
- Which results get clicked
- Search trends over time

View analytics at: https://programmablesearchengine.google.com/

---

## 💡 **Pro Tips**

### **For Government Contract Searching:**

Add these sites to your CSE:
```
sam.gov
beta.sam.gov
gsa.gov
grants.gov
fbo.gov (archived but still useful)
acquisition.gov
```

### **Exclude These:**
```
pinterest.com
facebook.com
twitter.com
instagram.com
```
(Social media clutter)

### **Custom Search Shortcuts:**

In Google CSE settings, you can create shortcuts:
- Search only SAM.gov: `site:sam.gov`
- Search only GSA: `site:gsa.gov`
- Search PDFs: `filetype:pdf`

---

## 🚨 **Troubleshooting**

### **Search bar doesn't appear:**
1. Check browser console for errors
2. Verify Search Engine ID is correct
3. Make sure script loads (check Network tab)
4. Clear cache and reload

### **Search bar looks weird:**
1. Customize in Google CSE console
2. Adjust colors to match NEXUS theme
3. Use compact layout for header

### **No results:**
1. Check CSE is set to "Search the entire web"
2. Verify CSE is enabled (not paused)
3. Check query isn't too specific

---

## 📝 **Current Status**

✅ Script added to index.html  
⏳ Needs Search Engine ID  
⏳ Needs customization (optional)  
⏳ Needs testing  

**Next Steps:**
1. Create Google CSE
2. Get Search Engine ID
3. Replace `YOUR_SEARCH_ENGINE_ID` in index.html
4. Restart frontend
5. Test search functionality

---

## 🔗 **Useful Links**

- **Create CSE:** https://programmablesearchengine.google.com/
- **CSE Documentation:** https://developers.google.com/custom-search
- **Styling Guide:** https://developers.google.com/custom-search/docs/element#cse-element
- **Analytics:** https://programmablesearchengine.google.com/ (under each engine)

---

**Status:** Ready to configure  
**Priority:** MEDIUM  
**Time to Complete:** 5 minutes  
**Impact:** Restores search functionality in header
