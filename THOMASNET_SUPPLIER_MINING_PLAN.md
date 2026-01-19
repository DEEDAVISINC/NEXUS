# THOMASNET SUPPLIER MINING - IMPLEMENTATION PLAN
## Free Account Access with Login Automation

**Corrected Understanding:** ThomasNet.com allows free access to manufacturer/wholesaler searches with a basic (free) account login.

---

## 🎯 WHAT WE'LL BUILD

**Automated supplier discovery from ThomasNet.com:**
1. User searches: "office chairs"
2. System logs into ThomasNet
3. Performs search
4. Extracts manufacturer/supplier info
5. Creates records in Airtable
6. Returns qualified suppliers

---

## 🔧 TECHNICAL APPROACH

### **Option 1: Playwright (Recommended)** ⭐

**Why Playwright:**
- Handles login/cookies automatically
- Works with JavaScript-heavy sites
- Can run headless (no browser window)
- Robust and maintained by Microsoft
- Better than Selenium for modern sites

**How it works:**
```python
from playwright.sync_api import sync_playwright

def search_thomasnet(product: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 1. Login (one-time per session)
        page.goto('https://www.thomasnet.com/account/login')
        page.fill('#email', os.environ.get('THOMASNET_EMAIL'))
        page.fill('#password', os.environ.get('THOMASNET_PASSWORD'))
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')
        
        # 2. Search for product
        page.goto(f'https://www.thomasnet.com/search?term={product}')
        page.wait_for_selector('.search-results')
        
        # 3. Extract results
        suppliers = page.query_selector_all('.supplier-card')
        
        results = []
        for supplier in suppliers[:10]:  # Top 10
            results.append({
                'company_name': supplier.query_selector('.company-name').inner_text(),
                'location': supplier.query_selector('.location').inner_text(),
                'description': supplier.query_selector('.description').inner_text(),
                'website': supplier.query_selector('a').get_attribute('href'),
                'phone': supplier.query_selector('.phone').inner_text(),
                'products': supplier.query_selector('.products').inner_text()
            })
        
        browser.close()
        return results
```

**Dependencies:**
```bash
pip install playwright
python -m playwright install chromium
```

**Pros:**
- ✅ Handles login automatically
- ✅ Works with modern JavaScript sites
- ✅ Reliable and fast
- ✅ Can screenshot results for debugging
- ✅ Handles CAPTCHA detection (can pause for manual solve)

**Cons:**
- ❌ Requires browser installation (~100MB)
- ❌ Slightly slower than pure HTTP requests
- ❌ More memory usage

---

### **Option 2: Selenium (Alternative)**

**Why Selenium:**
- Older, more widely used
- More tutorials/examples available
- Similar to Playwright

**How it works:**
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def search_thomasnet(product: str):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    # Login
    driver.get('https://www.thomasnet.com/account/login')
    driver.find_element(By.ID, 'email').send_keys(os.environ.get('THOMASNET_EMAIL'))
    driver.find_element(By.ID, 'password').send_keys(os.environ.get('THOMASNET_PASSWORD'))
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    
    # Search
    driver.get(f'https://www.thomasnet.com/search?term={product}')
    
    # Extract results
    suppliers = driver.find_elements(By.CSS_SELECTOR, '.supplier-card')
    
    results = []
    for supplier in suppliers[:10]:
        results.append({
            'company_name': supplier.find_element(By.CSS_SELECTOR, '.company-name').text,
            'location': supplier.find_element(By.CSS_SELECTOR, '.location').text,
            # ... etc
        })
    
    driver.quit()
    return results
```

**Dependencies:**
```bash
pip install selenium webdriver-manager
```

---

### **Option 3: BeautifulSoup + Requests (Fastest, but harder)**

**Why BS4:**
- Faster (no browser)
- Less memory
- Direct HTTP requests

**Challenge:**
- Need to handle session cookies manually
- May trigger anti-bot detection
- Login flow can be complex

**How it works:**
```python
import requests
from bs4 import BeautifulSoup

session = requests.Session()

# Login
login_url = 'https://www.thomasnet.com/account/login'
session.post(login_url, data={
    'email': os.environ.get('THOMASNET_EMAIL'),
    'password': os.environ.get('THOMASNET_PASSWORD')
})

# Search
search_url = f'https://www.thomasnet.com/search?term={product}'
response = session.get(search_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract
suppliers = soup.find_all('div', class_='supplier-card')
```

**Pros:**
- ✅ Very fast
- ✅ Low resource usage
- ✅ Simple code

**Cons:**
- ❌ May not work if site uses JavaScript
- ❌ Session management is manual
- ❌ More brittle (breaks if site changes)

---

## 🏗️ RECOMMENDED IMPLEMENTATION

### **Use Playwright** - Best balance of reliability and ease

**File:** `nexus_backend.py` - Add to `GPSSSupplierMiner` class

```python
class GPSSSupplierMiner:
    """Mine and qualify wholesale suppliers"""
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.ai = AnthropicClient()
        self._thomasnet_session = None  # Reuse login session
    
    # ============================================
    # THOMASNET MINING (NEW)
    # ============================================
    
    def search_thomasnet(self, product: str, category: str = None) -> List[Dict]:
        """
        Search ThomasNet for manufacturers/wholesalers
        
        Args:
            product: Product to search for
            category: Product category (optional filter)
            
        Returns:
            List of suppliers found on ThomasNet
        """
        try:
            from playwright.sync_api import sync_playwright
            
            print(f"🔍 Searching ThomasNet for: {product}")
            
            results = []
            
            with sync_playwright() as p:
                # Launch browser (headless)
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                # Check if we need to login
                page.goto('https://www.thomasnet.com/')
                
                # Check if already logged in (has user menu)
                if not page.query_selector('.user-menu'):
                    print("🔐 Logging into ThomasNet...")
                    
                    # Go to login page
                    page.goto('https://www.thomasnet.com/account/login')
                    
                    # Fill login form
                    email = os.environ.get('THOMASNET_EMAIL')
                    password = os.environ.get('THOMASNET_PASSWORD')
                    
                    if not email or not password:
                        print("❌ ThomasNet credentials not found in environment variables")
                        print("   Set THOMASNET_EMAIL and THOMASNET_PASSWORD in .env")
                        browser.close()
                        return []
                    
                    page.fill('input[type="email"], input[name="email"]', email)
                    page.fill('input[type="password"], input[name="password"]', password)
                    page.click('button[type="submit"]')
                    
                    # Wait for login to complete
                    page.wait_for_load_state('networkidle')
                    
                    # Check if login successful
                    if 'login' in page.url.lower() or page.query_selector('.error-message'):
                        print("❌ ThomasNet login failed - check credentials")
                        browser.close()
                        return []
                    
                    print("✅ Logged in successfully")
                
                # Perform search
                print(f"🔎 Searching for '{product}'...")
                search_url = f'https://www.thomasnet.com/search?term={product.replace(" ", "+")}'
                
                if category:
                    search_url += f'&category={category.replace(" ", "+")}'
                
                page.goto(search_url)
                page.wait_for_load_state('networkidle')
                
                # Wait for results to load
                try:
                    page.wait_for_selector('.search-result, .supplier-listing, .company-card', timeout=10000)
                except:
                    print("⚠️  No results found or page structure changed")
                    browser.close()
                    return []
                
                # Extract supplier information
                # NOTE: These selectors are EXAMPLES - need to verify actual ThomasNet HTML structure
                supplier_cards = page.query_selector_all('.search-result, .supplier-listing, .company-card')
                
                print(f"📦 Found {len(supplier_cards)} potential suppliers")
                
                for i, card in enumerate(supplier_cards[:15]):  # Top 15 results
                    try:
                        # Extract data (adjust selectors based on actual site structure)
                        company_name_elem = card.query_selector('.company-name, h3, .listing-title')
                        location_elem = card.query_selector('.location, .address, .city-state')
                        description_elem = card.query_selector('.description, .summary, p')
                        website_elem = card.query_selector('a.website, a.url')
                        phone_elem = card.query_selector('.phone, .contact-phone')
                        products_elem = card.query_selector('.products, .categories, .services')
                        
                        # Build supplier object
                        supplier = {
                            'Company Name': company_name_elem.inner_text().strip() if company_name_elem else f'Supplier {i+1}',
                            'Location': location_elem.inner_text().strip() if location_elem else '',
                            'Description': description_elem.inner_text().strip() if description_elem else '',
                            'Website': website_elem.get_attribute('href') if website_elem else '',
                            'Primary Contact Phone': phone_elem.inner_text().strip() if phone_elem else '',
                            'Product Keywords': products_elem.inner_text().strip() if products_elem else product,
                            'Product Categories': [category] if category else ['Uncategorized'],
                            'Discovery Method': 'ThomasNet',
                            'Discovery Date': datetime.now().isoformat(),
                            'Discovered By': 'NEXUS Auto-Mining',
                            'Business Status': 'Prospective',
                            'Relationship Stage': 'Discovered',
                            'Source Notes': f'Found via ThomasNet search for "{product}"'
                        }
                        
                        # Only add if we got company name
                        if supplier['Company Name'] and supplier['Company Name'] != f'Supplier {i+1}':
                            results.append(supplier)
                            print(f"  ✓ {supplier['Company Name']} ({supplier['Location']})")
                    
                    except Exception as e:
                        print(f"  ⚠️  Error extracting supplier {i+1}: {e}")
                        continue
                
                # Cleanup
                browser.close()
            
            print(f"✅ Found {len(results)} qualified suppliers from ThomasNet")
            return results
        
        except ImportError:
            print("❌ Playwright not installed. Run: pip install playwright && python -m playwright install chromium")
            return []
        
        except Exception as e:
            print(f"❌ Error searching ThomasNet: {e}")
            return []
    
    def mine_and_import_thomasnet(self, product: str, category: str = None, 
                                   auto_import: bool = False) -> Dict:
        """
        Search ThomasNet and optionally import to Airtable
        
        Args:
            product: Product to search for
            category: Product category
            auto_import: If True, automatically add to Airtable
            
        Returns:
            Dictionary with results and import status
        """
        # Search ThomasNet
        suppliers = self.search_thomasnet(product, category)
        
        if not suppliers:
            return {
                'success': False,
                'found': 0,
                'imported': 0,
                'message': 'No suppliers found on ThomasNet'
            }
        
        imported = 0
        skipped = 0
        
        if auto_import:
            print(f"\n📥 Importing {len(suppliers)} suppliers to Airtable...")
            
            for supplier in suppliers:
                try:
                    # Check if supplier already exists
                    existing = self.airtable.search_records(
                        'GPSS Suppliers',
                        formula=f"{{Company Name}} = '{supplier['Company Name']}'"
                    )
                    
                    if existing:
                        print(f"  ⏭️  Skipped: {supplier['Company Name']} (already exists)")
                        skipped += 1
                    else:
                        self.airtable.create_record('GPSS Suppliers', supplier)
                        print(f"  ✅ Imported: {supplier['Company Name']}")
                        imported += 1
                
                except Exception as e:
                    print(f"  ❌ Error importing {supplier.get('Company Name', 'Unknown')}: {e}")
                    skipped += 1
        
        return {
            'success': True,
            'found': len(suppliers),
            'imported': imported,
            'skipped': skipped,
            'suppliers': suppliers,
            'message': f"Found {len(suppliers)} suppliers. Imported {imported}, skipped {skipped}."
        }
    
    # ============================================
    # UPDATE find_suppliers_for_product() TO USE THOMASNET
    # ============================================
    
    def find_suppliers_for_product(self, product: str, category: str = None, 
                                    max_results: int = 10, use_thomasnet: bool = True) -> List[Dict]:
        """
        MAIN METHOD: Find suppliers for specific product
        
        Args:
            product: Product name or description
            category: Product category
            max_results: Maximum suppliers to return
            use_thomasnet: If True, search ThomasNet if not enough in database
            
        Returns:
            List of qualified suppliers ranked by fit
        """
        # Step 1: Check existing database
        keywords = product.split()
        existing = self.search_existing_suppliers(
            category=category,
            keywords=keywords,
            min_rating=3.0
        )
        
        print(f"Found {len(existing)} existing suppliers for '{product}'")
        
        # Step 2: If we have enough good suppliers, return them
        if len(existing) >= max_results:
            return existing[:max_results]
        
        # Step 3: Mine from ThomasNet if enabled
        if use_thomasnet and len(existing) < max_results:
            print(f"\n🌐 Not enough suppliers in database. Mining ThomasNet...")
            
            thomasnet_results = self.search_thomasnet(product, category)
            
            if thomasnet_results:
                # Import to database
                for supplier in thomasnet_results:
                    try:
                        # Check if exists
                        exists = self.airtable.search_records(
                            'GPSS Suppliers',
                            formula=f"{{Company Name}} = '{supplier['Company Name']}'"
                        )
                        
                        if not exists:
                            self.airtable.create_record('GPSS Suppliers', supplier)
                            print(f"  ✅ Added: {supplier['Company Name']}")
                            
                            # Add to existing list
                            existing.append({
                                'company_name': supplier['Company Name'],
                                'product_categories': supplier.get('Product Categories', []),
                                'overall_rating': 3.0,  # Default for new suppliers
                                'discovery_method': 'ThomasNet'
                            })
                    except:
                        pass
        
        return existing[:max_results]
```

---

## 🔐 ENVIRONMENT SETUP

**Add to `.env` file:**
```bash
# ThomasNet Credentials (Free Account)
THOMASNET_EMAIL=your-email@example.com
THOMASNET_PASSWORD=your-password-here
```

**Add to `.env.example`:**
```bash
THOMASNET_EMAIL=your_thomasnet_email
THOMASNET_PASSWORD=your_thomasnet_password
```

---

## 📡 API ENDPOINT

**File:** `api_server.py`

```python
@app.route('/gpss/suppliers/mine-thomasnet', methods=['POST'])
def mine_thomasnet_suppliers():
    """
    Mine suppliers from ThomasNet.com
    
    POST body:
    {
        "product": "office chairs",
        "category": "Office Furniture",
        "auto_import": true
    }
    """
    try:
        from nexus_backend import GPSSSupplierMiner
        
        data = request.get_json()
        product = data.get('product')
        category = data.get('category')
        auto_import = data.get('auto_import', False)
        
        if not product:
            return jsonify({'error': 'Product is required'}), 400
        
        miner = GPSSSupplierMiner()
        results = miner.mine_and_import_thomasnet(product, category, auto_import)
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## ⚠️ IMPORTANT CONSIDERATIONS

### **1. ThomasNet Terms of Service**
- Check ThomasNet TOS for scraping policies
- Free accounts may have usage limits
- Consider rate limiting (1 search per 5-10 seconds)
- Don't scrape excessively

### **2. Account Required**
- You need to create free ThomasNet account
- Keep login credentials secure in `.env`
- Don't commit credentials to git

### **3. Site Structure Changes**
- ThomasNet may update their HTML
- Selectors (`.company-name`, etc.) may break
- Need to inspect actual site to verify
- May need periodic maintenance

### **4. Error Handling**
- Login failures (wrong credentials)
- CAPTCHA challenges (rare, but possible)
- Rate limiting (too many searches)
- No results found

### **5. Performance**
- Browser automation is slower than API calls
- Takes 10-30 seconds per search
- Use sparingly (only when needed)

---

## 🎯 USAGE EXAMPLES

### **Example 1: Search and Review**
```python
miner = GPSSSupplierMiner()

# Search ThomasNet (don't import yet)
results = miner.mine_and_import_thomasnet(
    product='industrial pumps',
    category='Industrial Equipment',
    auto_import=False  # Just return results
)

print(f"Found {results['found']} suppliers")
for supplier in results['suppliers']:
    print(f"- {supplier['Company Name']} in {supplier['Location']}")
```

### **Example 2: Search and Auto-Import**
```python
# Search and automatically add to Airtable
results = miner.mine_and_import_thomasnet(
    product='office furniture',
    category='Office Furniture',
    auto_import=True  # Add to database automatically
)

print(f"Imported {results['imported']} new suppliers")
```

### **Example 3: Via API**
```bash
curl -X POST http://localhost:8000/gpss/suppliers/mine-thomasnet \
  -H "Content-Type: application/json" \
  -d '{
    "product": "safety equipment",
    "category": "Safety & PPE",
    "auto_import": true
  }'
```

---

## 📋 IMPLEMENTATION STEPS

### **Step 1: Install Dependencies (5 minutes)**
```bash
pip install playwright
python -m playwright install chromium
```

### **Step 2: Create ThomasNet Account (5 minutes)**
1. Go to https://www.thomasnet.com
2. Click "Sign Up" (free account)
3. Verify email
4. Add credentials to `.env`

### **Step 3: Inspect ThomasNet HTML (15 minutes)**
- Search for a product manually
- Right-click → Inspect
- Find CSS selectors for:
  - Company name
  - Location
  - Description
  - Website link
  - Phone number
  - Product categories
- Update selectors in code

### **Step 4: Add Code to `nexus_backend.py` (30 minutes)**
- Add methods to `GPSSSupplierMiner` class
- Test locally

### **Step 5: Add API Endpoint (10 minutes)**
- Add route to `api_server.py`
- Test via curl or Postman

### **Step 6: Test Full Workflow (15 minutes)**
- Search for a product
- Verify results
- Import to Airtable
- Check data quality

**Total Time: ~1.5 hours**

---

## 🚀 WANT ME TO BUILD IT?

I can implement this right now. It'll take about 1-2 hours:

**What I'll do:**
1. ✅ Install Playwright
2. ✅ Add ThomasNet scraping to `GPSSSupplierMiner`
3. ✅ Update `find_suppliers_for_product()` to use ThomasNet
4. ✅ Add API endpoint `/gpss/suppliers/mine-thomasnet`
5. ✅ Test with a real search
6. ✅ Document the selectors

**What you need to do:**
1. Create free ThomasNet account
2. Add credentials to `.env`
3. Run `pip install playwright && python -m playwright install chromium`

**Ready to build this?**

---

## 📝 NEXT STEPS

**Option 1: Build ThomasNet Now**
- I implement full ThomasNet integration
- You get automated supplier discovery
- ~1.5 hours of work

**Option 2: Start with Manual Supplier Entry**
- Skip automation for now
- Add 10-20 suppliers manually to Airtable
- Come back to ThomasNet later

**Option 3: Build Google CSE First**
- Easier to implement (no login)
- Free API, simpler code
- Then add ThomasNet later

**Which approach makes most sense for you right now?**
