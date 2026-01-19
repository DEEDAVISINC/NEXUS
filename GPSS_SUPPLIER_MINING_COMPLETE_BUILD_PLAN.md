# GPSS SUPPLIER MINING - COMPLETE BUILD PLAN
## Full System Implementation - All Sources, All Features

**Goal:** Build 100% functional supplier mining system with automated discovery from multiple sources, full UI integration, and complete workflow.

---

## 📋 WHAT WE'RE BUILDING

### **Complete Supplier Mining System:**

**Supplier Discovery Sources:**
1. ✅ Manual Entry (already works)
2. ✅ Airtable Database Search (already works)
3. 🔨 ThomasNet.com (manufacturer/wholesaler scraping with login)
4. 🔨 Google Custom Search API (AI-powered extraction)
5. 🔨 GSA Advantage API (official government suppliers)
6. 🔨 CSV Import (bulk upload from purchased databases)

**Features:**
- Multi-source supplier discovery
- AI-powered qualification and scoring
- Duplicate detection and merging
- Automated data enrichment
- Quote request automation
- Order tracking
- Performance analytics
- Full UI integration in GPSS

**Airtable Tables:**
- GPSS Suppliers (90+ fields)
- GPSS Supplier Quotes (40+ fields)
- GPSS Supplier Orders (50+ fields)

---

## 🏗️ ARCHITECTURE

### **Backend Flow:**
```
User searches for "office chairs"
         ↓
1. Check Airtable database (existing suppliers)
         ↓
2. If < 5 found, trigger web mining:
   - ThomasNet search
   - Google Custom Search
   - GSA Advantage API
         ↓
3. AI qualifies each result (0-100 score)
         ↓
4. Import qualified suppliers (score > 70)
         ↓
5. Return ranked list to user
         ↓
6. User reviews and approves
```

### **Tech Stack:**
- **Backend:** Python, Flask
- **Web Scraping:** Playwright (ThomasNet)
- **APIs:** Google CSE, GSA Advantage
- **AI:** Claude (qualification, data extraction)
- **Database:** Airtable
- **Frontend:** React, TypeScript

---

## 🎯 BUILD PHASES

### **PHASE 1: BACKEND - SUPPLIER MINING SOURCES** (3-4 hours)

**1.1: ThomasNet Integration** ⭐ HIGH PRIORITY
- Playwright automation
- Login handling
- Search + pagination
- Data extraction (company, location, phone, products)
- Error handling (CAPTCHA, rate limits)
- **Time:** 1.5 hours

**1.2: Google Custom Search API** ⭐ HIGH PRIORITY
- Google CSE setup
- Query optimization ("wholesale", "Net 30", "government supplier")
- AI-powered data extraction from snippets
- Website scraping for contact info
- **Time:** 1 hour

**1.3: GSA Advantage API** ⭐ MEDIUM PRIORITY
- API key registration
- Search by product category
- Filter by GSA schedule
- Extract verified government suppliers
- **Time:** 1 hour

**1.4: CSV Import Handler**
- Parse uploaded CSV files
- Map columns to Airtable fields
- Duplicate detection
- Validation and error handling
- **Time:** 30 minutes

**1.5: AI Qualification Engine**
- Score suppliers (0-100)
- Factors: company size, terms, pricing, certifications
- Auto-approve threshold (score > 80)
- Review queue for 70-79
- **Time:** 30 minutes

---

### **PHASE 2: API ENDPOINTS** (1 hour)

**New Endpoints:**
```
POST /gpss/suppliers/mine-thomasnet      # ThomasNet search
POST /gpss/suppliers/mine-google         # Google CSE search
POST /gpss/suppliers/mine-gsa            # GSA Advantage search
POST /gpss/suppliers/mine-all            # Search all sources
POST /gpss/suppliers/import-csv          # CSV upload
POST /gpss/suppliers/qualify             # AI qualification
GET  /gpss/suppliers/pending-review      # Review queue
PUT  /gpss/suppliers/approve/<id>        # Approve supplier
```

**Enhanced Existing:**
```
POST /gpss/suppliers/find-for-product    # Update to use all sources
POST /gpss/auto-quote/process-opportunity # Full automation
```

---

### **PHASE 3: FRONTEND INTEGRATION** (1.5 hours)

**3.1: Add Suppliers Tab to GPSS**
- Import SuppliersTab component
- Add to GPSSSystem tabs
- Test navigation

**3.2: Supplier Mining UI**
- "🔍 Find Suppliers" button
- Mining source selector (ThomasNet, Google, GSA, All)
- Progress indicator
- Results preview
- Bulk approve/reject
- Import controls

**3.3: Supplier Detail View**
- Full supplier profile
- Edit capabilities
- Quote history
- Order history
- Performance metrics

**3.4: Auto-Quote Integration**
- "Find Suppliers" button on opportunities
- Supplier matching panel
- Quote comparison table
- Select and generate quote

---

### **PHASE 4: AIRTABLE SETUP** (User Action - 45 min)

**Option A: Automated Script**
- Python script creates tables
- Adds all fields programmatically
- Sets up relationships
- **User runs:** `python setup_supplier_tables.py`

**Option B: Manual Guide**
- Step-by-step instructions
- Copy/paste field configurations
- Spreadsheet with all field definitions

---

### **PHASE 5: TESTING & REFINEMENT** (1 hour)

**End-to-End Tests:**
1. Search for "office chairs" → Mine from all sources
2. Review results → AI scores accurate
3. Import to Airtable → No duplicates
4. Find suppliers for opportunity → Match correctly
5. Generate quote request → AI email quality
6. Track quote responses → Update status
7. Create order → Link to supplier + opportunity

---

## 📊 DETAILED IMPLEMENTATION

### **1. ThomasNet Mining (COMPLETE CODE)**

**File:** `nexus_backend.py` - Add to `GPSSSupplierMiner`

```python
def search_thomasnet(self, product: str, max_results: int = 15) -> List[Dict]:
    """
    Search ThomasNet for manufacturers/wholesalers
    Requires: pip install playwright
    """
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
        
        print(f"🔍 Searching ThomasNet for: {product}")
        results = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            # Login to ThomasNet
            email = os.environ.get('THOMASNET_EMAIL')
            password = os.environ.get('THOMASNET_PASSWORD')
            
            if not email or not password:
                print("⚠️  ThomasNet credentials not set. Attempting guest search...")
                # Try searching without login (limited results)
            else:
                try:
                    page.goto('https://www.thomasnet.com/account/login', timeout=30000)
                    page.fill('input[type="email"]', email, timeout=10000)
                    page.fill('input[type="password"]', password, timeout=10000)
                    page.click('button[type="submit"]', timeout=10000)
                    page.wait_for_load_state('networkidle', timeout=15000)
                    print("✅ Logged into ThomasNet")
                except Exception as e:
                    print(f"⚠️  Login failed: {e}. Continuing with guest access...")
            
            # Perform search
            search_url = f'https://www.thomasnet.com/search?term={product.replace(" ", "+")}'
            page.goto(search_url, timeout=30000)
            
            try:
                # Wait for results (adjust selector based on actual site)
                page.wait_for_selector('.search-result, .company-listing, .supplier-card', timeout=15000)
            except PlaywrightTimeout:
                print("⚠️  No results found or page timeout")
                browser.close()
                return []
            
            # Scroll to load more results
            for _ in range(3):
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(1000)
            
            # Extract supplier data
            # NOTE: These selectors need to be verified against actual ThomasNet HTML
            suppliers = page.query_selector_all('.search-result, .company-listing')
            
            for i, supplier_elem in enumerate(suppliers[:max_results]):
                try:
                    # Extract company info (adjust selectors to match actual site)
                    company_name = self._extract_text(supplier_elem, '.company-name, h3, .title')
                    location = self._extract_text(supplier_elem, '.location, .address, .city')
                    phone = self._extract_text(supplier_elem, '.phone, .contact-phone')
                    website = self._extract_attribute(supplier_elem, 'a[href*="http"]', 'href')
                    description = self._extract_text(supplier_elem, '.description, .summary, p')
                    products = self._extract_text(supplier_elem, '.products, .categories')
                    
                    if company_name:
                        results.append({
                            'Company Name': company_name,
                            'Location': location,
                            'Primary Contact Phone': phone,
                            'Website': website,
                            'Description': description,
                            'Product Keywords': products or product,
                            'Discovery Method': 'ThomasNet',
                            'Discovery Date': datetime.now().strftime('%Y-%m-%d'),
                            'Discovered By': 'NEXUS Auto-Mining',
                            'Business Status': 'Prospective',
                            'Relationship Stage': 'Discovered'
                        })
                        print(f"  ✓ {company_name}")
                
                except Exception as e:
                    print(f"  ⚠️  Error extracting result {i+1}: {e}")
            
            browser.close()
        
        print(f"✅ Found {len(results)} suppliers on ThomasNet")
        return results
    
    except ImportError:
        print("❌ Playwright not installed. Run: pip install playwright && python -m playwright install chromium")
        return []
    except Exception as e:
        print(f"❌ ThomasNet search error: {e}")
        return []

def _extract_text(self, element, selector: str) -> str:
    """Helper: Extract text from element"""
    try:
        elem = element.query_selector(selector)
        return elem.inner_text().strip() if elem else ''
    except:
        return ''

def _extract_attribute(self, element, selector: str, attribute: str) -> str:
    """Helper: Extract attribute from element"""
    try:
        elem = element.query_selector(selector)
        return elem.get_attribute(attribute) if elem else ''
    except:
        return ''
```

---

### **2. Google Custom Search Integration**

```python
def search_google_suppliers(self, product: str, max_results: int = 10) -> List[Dict]:
    """
    Search Google for suppliers using Custom Search API
    Requires: GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID in .env
    """
    try:
        api_key = os.environ.get('GOOGLE_CSE_API_KEY')
        cse_id = os.environ.get('GOOGLE_CSE_ID')
        
        if not api_key or not cse_id:
            print("⚠️  Google CSE credentials not set")
            return []
        
        print(f"🔍 Searching Google for: {product}")
        results = []
        
        # Build search query
        queries = [
            f'{product} wholesale distributor',
            f'{product} manufacturer supplier',
            f'{product} government supplier Net 30'
        ]
        
        for query in queries:
            url = 'https://www.googleapis.com/customsearch/v1'
            params = {
                'key': api_key,
                'cx': cse_id,
                'q': query,
                'num': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('items', []):
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    link = item.get('link', '')
                    
                    # Use AI to extract company info from snippet
                    company_info = self._ai_extract_company_info(title, snippet, link)
                    
                    if company_info and company_info.get('company_name'):
                        results.append({
                            'Company Name': company_info['company_name'],
                            'Website': link,
                            'Description': snippet,
                            'Product Keywords': product,
                            'Discovery Method': 'Google Search',
                            'Discovery Date': datetime.now().strftime('%Y-%m-%d'),
                            'Discovered By': 'NEXUS Auto-Mining',
                            'Business Status': 'Prospective',
                            'Relationship Stage': 'Discovered'
                        })
                        print(f"  ✓ {company_info['company_name']}")
            
            # Respect rate limits
            time.sleep(1)
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for r in results:
            name = r['Company Name'].lower()
            if name not in seen:
                seen.add(name)
                unique_results.append(r)
        
        print(f"✅ Found {len(unique_results)} unique suppliers via Google")
        return unique_results[:max_results]
    
    except Exception as e:
        print(f"❌ Google search error: {e}")
        return []

def _ai_extract_company_info(self, title: str, snippet: str, url: str) -> Dict:
    """Use AI to extract company info from search result"""
    prompt = f"""
Extract company information from this Google search result:

Title: {title}
Snippet: {snippet}
URL: {url}

Extract ONLY if this is a business/supplier (not a marketplace, article, or review site):
- Company name
- Is this a supplier/manufacturer? (yes/no)

Return JSON: {{"company_name": "...", "is_supplier": true/false}}
"""
    
    try:
        response = self.ai.complete(prompt, max_tokens=100)
        clean_json = response.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean_json)
        
        if data.get('is_supplier'):
            return data
        return {}
    except:
        return {}
```

---

### **3. GSA Advantage API Integration**

```python
def search_gsa_suppliers(self, product: str, max_results: int = 10) -> List[Dict]:
    """
    Search GSA Advantage for government suppliers
    Requires: SAM_GOV_API_KEY in .env
    """
    try:
        api_key = os.environ.get('SAM_GOV_API_KEY')
        
        if not api_key:
            print("⚠️  SAM.gov API key not set")
            return []
        
        print(f"🔍 Searching GSA Advantage for: {product}")
        results = []
        
        # GSA Advantage search endpoint
        url = 'https://api.gsa.gov/acquisitions/advantage/v1/product'
        headers = {'X-Api-Key': api_key}
        params = {
            'keyword': product,
            'limit': max_results
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract vendor info from products
            vendors_seen = set()
            
            for item in data.get('data', []):
                vendor = item.get('vendor', {})
                vendor_name = vendor.get('name', '')
                
                if vendor_name and vendor_name not in vendors_seen:
                    vendors_seen.add(vendor_name)
                    
                    results.append({
                        'Company Name': vendor_name,
                        'GSA Contract Holder': True,
                        'GSA Schedule Number': item.get('schedule', ''),
                        'Product Keywords': item.get('description', product),
                        'Government Supplier': True,
                        'Discovery Method': 'GSA Advantage',
                        'Discovery Date': datetime.now().strftime('%Y-%m-%d'),
                        'Discovered By': 'NEXUS Auto-Mining',
                        'Business Status': 'Active',
                        'Relationship Stage': 'Discovered'
                    })
                    print(f"  ✓ {vendor_name} (GSA)")
        
        print(f"✅ Found {len(results)} GSA suppliers")
        return results
    
    except Exception as e:
        print(f"❌ GSA search error: {e}")
        return []
```

---

### **4. Master Mining Function**

```python
def mine_all_sources(self, product: str, category: str = None, 
                     sources: List[str] = None) -> Dict:
    """
    Search all supplier sources and combine results
    
    Args:
        product: Product to search for
        category: Product category
        sources: List of sources to search ['thomasnet', 'google', 'gsa', 'database']
                If None, searches all
    
    Returns:
        Combined results with stats
    """
    if sources is None:
        sources = ['database', 'thomasnet', 'google', 'gsa']
    
    all_results = []
    stats = {
        'database': 0,
        'thomasnet': 0,
        'google': 0,
        'gsa': 0,
        'total': 0,
        'qualified': 0,
        'imported': 0
    }
    
    print(f"\n🚀 Mining suppliers for '{product}' from {len(sources)} sources...\n")
    
    # Source 1: Existing database
    if 'database' in sources:
        db_results = self.search_existing_suppliers(
            category=category,
            keywords=product.split(),
            min_rating=0
        )
        all_results.extend(db_results)
        stats['database'] = len(db_results)
        print(f"✅ Database: {len(db_results)} suppliers\n")
    
    # Source 2: ThomasNet
    if 'thomasnet' in sources:
        thomasnet_results = self.search_thomasnet(product, max_results=15)
        all_results.extend(thomasnet_results)
        stats['thomasnet'] = len(thomasnet_results)
        print(f"✅ ThomasNet: {len(thomasnet_results)} suppliers\n")
    
    # Source 3: Google Custom Search
    if 'google' in sources:
        google_results = self.search_google_suppliers(product, max_results=10)
        all_results.extend(google_results)
        stats['google'] = len(google_results)
        print(f"✅ Google: {len(google_results)} suppliers\n")
    
    # Source 4: GSA Advantage
    if 'gsa' in sources:
        gsa_results = self.search_gsa_suppliers(product, max_results=10)
        all_results.extend(gsa_results)
        stats['gsa'] = len(gsa_results)
        print(f"✅ GSA Advantage: {len(gsa_results)} suppliers\n")
    
    stats['total'] = len(all_results)
    
    # AI qualify and import
    print(f"🤖 AI qualifying {len(all_results)} suppliers...\n")
    
    qualified = []
    for supplier in all_results:
        # Skip if already in database (has 'id' field)
        if supplier.get('id'):
            qualified.append(supplier)
            continue
        
        # AI qualification
        score = self._ai_qualify_supplier(supplier)
        supplier['ai_score'] = score
        
        if score >= 70:
            qualified.append(supplier)
            
            # Auto-import if score > 80
            if score >= 80:
                try:
                    # Check for duplicates
                    existing = self.airtable.search_records(
                        'GPSS Suppliers',
                        formula=f"{{Company Name}} = '{supplier['Company Name']}'"
                    )
                    
                    if not existing:
                        self.airtable.create_record('GPSS Suppliers', supplier)
                        stats['imported'] += 1
                        print(f"  ✅ Imported: {supplier['Company Name']} (score: {score})")
                except Exception as e:
                    print(f"  ⚠️  Import failed: {supplier['Company Name']}: {e}")
    
    stats['qualified'] = len(qualified)
    
    print(f"\n🎉 Mining complete!")
    print(f"   Total found: {stats['total']}")
    print(f"   Qualified: {stats['qualified']}")
    print(f"   Auto-imported: {stats['imported']}")
    
    return {
        'success': True,
        'suppliers': qualified,
        'stats': stats
    }

def _ai_qualify_supplier(self, supplier: Dict) -> int:
    """AI scores supplier 0-100 based on available info"""
    prompt = f"""
Score this supplier for government contract fulfillment (0-100):

Company: {supplier.get('Company Name', 'Unknown')}
Location: {supplier.get('Location', 'Unknown')}
Website: {supplier.get('Website', 'Unknown')}
Products: {supplier.get('Product Keywords', 'Unknown')}
GSA Contract: {supplier.get('GSA Contract Holder', False)}
Government Supplier: {supplier.get('Government Supplier', False)}

Score based on:
- Has contact info (phone/email/website)
- Looks legitimate (not spam/marketplace)
- Relevant to government contracting
- Has GSA contract (big bonus)
- Professional presence

Return ONLY a number 0-100.
"""
    
    try:
        response = self.ai.complete(prompt, max_tokens=10)
        score = int(response.strip())
        return min(100, max(0, score))
    except:
        return 50  # Default moderate score
```

---

## 🔐 ENVIRONMENT VARIABLES NEEDED

**Add to `.env`:**
```bash
# ThomasNet (Free Account)
THOMASNET_EMAIL=your-email@example.com
THOMASNET_PASSWORD=your-password

# Google Custom Search (Free: 100/day)
GOOGLE_CSE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-custom-search-engine-id

# SAM.gov API (Already have this)
SAM_GOV_API_KEY=your-existing-sam-gov-key
```

---

## 📦 DEPENDENCIES TO INSTALL

```bash
# Playwright for web scraping
pip install playwright
python -m playwright install chromium

# Already installed
pip install requests anthropic pyairtable python-dotenv flask
```

---

## ⏱️ ESTIMATED TIME

**Total Implementation: 5-6 hours**

| Phase | Time |
|-------|------|
| ThomasNet mining | 1.5 hours |
| Google CSE mining | 1 hour |
| GSA Advantage mining | 1 hour |
| Master mining function | 30 min |
| API endpoints | 1 hour |
| Frontend integration | 1.5 hours |
| Testing | 30 min |

---

## 🚀 READY TO BUILD?

I'll implement this systematically:

**Phase 1: Backend (3.5 hours)**
- All mining sources
- AI qualification
- Duplicate handling

**Phase 2: API (1 hour)**
- All endpoints
- Error handling

**Phase 3: Frontend (1.5 hours)**
- Suppliers tab integration
- Mining UI
- Results display

**Want me to start building now?**

I'll work through it step-by-step, showing you progress along the way.
