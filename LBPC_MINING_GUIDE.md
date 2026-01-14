# LBPC LEAD MINING GUIDE - SURPLUS RECOVERY DATA SOURCES

## 🎯 **OVERVIEW**

This guide documents how to automatically mine surplus recovery leads from county and state websites. Surplus funds (also called "excess proceeds" or "overage funds") are created when a property is foreclosed and sold for more than the debt owed.

**Business Opportunity:**
- Property owners often don't know these funds exist
- Funds are held by county treasurers or court systems
- You help them recover funds, charge 30% contingency fee
- No cost to property owner unless successful

---

## 📊 **PRIORITY STATES & COUNTIES**

### **Tier 1: Home States (Start Here)**

**Michigan:**
- Wayne County (Detroit) - High volume
- Oakland County - High value
- Macomb County - Good mix

**Georgia:**
- Fulton County (Atlanta) - High volume
- DeKalb County - Good mix
- Gwinnett County - Growing market

**Maryland:**
- Baltimore City - High volume
- Montgomery County - High value
- Prince George's County - Good volume

**Texas:**
- Harris County (Houston) - Massive volume
- Dallas County - High volume
- Travis County (Austin) - Growing

**California:**
- Los Angeles County - Huge volume
- San Diego County - High value
- Orange County - High value

**Illinois:**
- Cook County (Chicago) - High volume
- DuPage County - Good mix

### **Tier 2: Expansion States**
- Florida (Miami-Dade, Broward, Orange)
- New York (NYC boroughs, Nassau, Suffolk)
- Pennsylvania (Philadelphia, Allegheny)
- Ohio (Cuyahoga, Franklin)
- North Carolina (Mecklenburg, Wake)

---

## 🌐 **DATA SOURCES BY STATE**

### **Michigan**

#### Wayne County
**URL:** https://www.waynecounty.com/elected/treasurer/foreclosure.aspx  
**Data Format:** PDF lists, searchable database  
**Fields Available:**
- Property owner name
- Property address
- Case number
- Surplus amount
- Sale date

**Scraping Strategy:**
- Check quarterly foreclosure lists
- Parse PDF tables with PyPDF2 or pdfplumber
- Extract property owner names and addresses
- Look for "Surplus" or "Excess Proceeds" section

**Sample Code:**
```python
import requests
from bs4 import BeautifulSoup
import pdfplumber

def scrape_wayne_county():
    url = "https://www.waynecounty.com/elected/treasurer/foreclosure.aspx"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find PDF links
    pdf_links = soup.find_all('a', href=lambda x: x and 'surplus' in x.lower())
    
    leads = []
    for link in pdf_links:
        pdf_url = link['href']
        # Download and parse PDF
        pdf_data = parse_surplus_pdf(pdf_url)
        leads.extend(pdf_data)
    
    return leads

def parse_surplus_pdf(url):
    # Use pdfplumber to extract tables
    with pdfplumber.open(url) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            # Process table data
            pass
```

#### Oakland County
**URL:** https://www.oakgov.com/treasurer/surplus-funds  
**Data Format:** Online database, downloadable spreadsheet  
**Easier to scrape:** Yes - structured data

#### Macomb County
**URL:** https://treasurer.macombgov.org/Treasurer-ForeclosureSurplus  
**Data Format:** PDF quarterly reports  
**Fields Available:** Similar to Wayne County

---

### **Georgia**

#### Fulton County
**URL:** https://www.fultoncountyga.gov/services/taxes/tax-commissioner/tax-sales  
**Data Format:** Excel spreadsheets posted online  
**Update Frequency:** Monthly  

**Scraping Strategy:**
- Download Excel files automatically
- Parse with pandas
- Clean and normalize data

**Sample Code:**
```python
import pandas as pd

def scrape_fulton_county():
    url = "https://www.fultoncountyga.gov/.../surplus_list.xlsx"
    df = pd.read_excel(url)
    
    leads = []
    for _, row in df.iterrows():
        lead = {
            'client_name': row['Owner Name'],
            'property': row['Property Address'],
            'surplus_amount': row['Excess Proceeds'],
            'case_number': row['Case Number'],
            'county': 'Fulton',
            'state': 'GA'
        }
        leads.append(lead)
    
    return leads
```

#### DeKalb County
**URL:** https://www.dekalbcountyga.gov/tax-commissioner/excess-funds  
**Data Format:** PDF and online portal  
**Access:** Public, no login required

#### Gwinnett County
**URL:** https://www.gwinnettcounty.com/web/gwinnett/departments/taxcommissioner  
**Data Format:** Searchable online database  
**Best for:** Real-time checking

---

### **Maryland**

#### Baltimore City
**URL:** https://comptroller.baltimorecity.gov/tax-sales  
**Data Format:** CSV files available  
**Update Frequency:** After each tax sale (quarterly)

**Scraping Strategy:**
- Download CSV files
- Filter for records with surplus
- Cross-reference with case outcomes

#### Montgomery County
**URL:** https://www.montgomerycountymd.gov/Finance/Resources/Files/TaxSale/  
**Data Format:** PDF and Excel  
**High value area:** Yes - affluent county

#### Prince George's County
**URL:** https://www.princegeorgescountymd.gov/departments-offices/finance/divisions/treasury  
**Data Format:** PDF reports  
**Volume:** High

---

### **Texas**

#### Harris County
**URL:** https://www.hctax.net/Property/PropertyTax  
**Data Format:** Online database, CSV export available  
**Volume:** Very high - Houston metro area

**Scraping Strategy:**
- Use county property search API (if available)
- Filter for tax sale properties
- Check for surplus/overage status

#### Dallas County
**URL:** https://www.dallascounty.org/departments/tax/foreclosure.php  
**Data Format:** Online portal with search  
**Access:** Public database

#### Travis County
**URL:** https://tax-office.traviscountytx.gov/  
**Data Format:** Online database  
**Growing market:** Austin area

---

### **California**

#### Los Angeles County
**URL:** https://ttc.lacounty.gov/  
**Data Format:** Complex - multiple departments  
**Challenge:** Large volume, fragmented data

**Note:** California has strict surplus recovery regulations - consult attorney before operating here.

#### San Diego County
**URL:** https://arcc.sdcounty.ca.gov/Pages/tax-sales.aspx  
**Data Format:** Online portal  
**High value:** Yes

#### Orange County
**URL:** https://www.ocgov.com/gov/auditor/tt/tax-sale  
**Data Format:** PDF and online  
**High value:** Yes

---

### **Illinois**

#### Cook County
**URL:** https://www.cookcountytreasurer.com/  
**Data Format:** Online database, CSV exports  
**Volume:** Very high - Chicago metro

**Scraping Strategy:**
- Use county scavenger sale data
- Filter for properties with surplus
- Parse annual sale results

---

## 🔧 **TECHNICAL IMPLEMENTATION**

### **Tools & Libraries**

```python
# Web scraping
import requests
from bs4 import BeautifulSoup
from selenium import webdriver  # For JavaScript-heavy sites
from selenium.webdriver.common.by import By

# PDF processing
import pdfplumber
import PyPDF2

# Data processing
import pandas as pd
import numpy as np

# Date/time
from datetime import datetime, timedelta

# Database
from pyairtable import Api  # For Airtable
```

### **Base Mining Class**

```python
class SurplusMiner:
    def __init__(self, county, state, airtable_api_key):
        self.county = county
        self.state = state
        self.airtable = Api(airtable_api_key)
        self.base = self.airtable.base('YOUR_BASE_ID')
        self.leads_table = self.base.table('LBPC Leads')
    
    def scrape(self):
        """Override in subclass for each county"""
        raise NotImplementedError
    
    def clean_data(self, raw_leads):
        """Standardize and clean data"""
        cleaned = []
        for lead in raw_leads:
            cleaned_lead = {
                'Client Name': self.clean_name(lead.get('name', '')),
                'Property Address': self.clean_address(lead.get('address', '')),
                'City': lead.get('city', ''),
                'County': self.county,
                'State': self.state,
                'Surplus Amount': self.parse_currency(lead.get('amount', 0)),
                'Case Number': lead.get('case_number', ''),
                'Lead Source': f'{self.county} County Website Mining',
                'Date Discovered': datetime.now().isoformat(),
                'Status': 'New'
            }
            cleaned.append(cleaned_lead)
        return cleaned
    
    def deduplicate(self, leads):
        """Check against existing leads in Airtable"""
        existing = self.leads_table.all()
        existing_cases = {r['fields'].get('Case Number') for r in existing}
        
        new_leads = []
        for lead in leads:
            if lead['Case Number'] not in existing_cases:
                new_leads.append(lead)
        
        return new_leads
    
    def ai_qualify(self, leads):
        """Score leads using AI"""
        # Call Claude API to score each lead
        for lead in leads:
            score = self.calculate_priority_score(lead)
            lead['Priority Score'] = score
        return leads
    
    def calculate_priority_score(self, lead):
        """Calculate 0-100 priority score"""
        score = 0
        
        # Surplus amount (0-40 points)
        amount = lead.get('Surplus Amount', 0)
        if amount >= 50000:
            score += 40
        elif amount >= 25000:
            score += 30
        elif amount >= 10000:
            score += 20
        else:
            score += 10
        
        # Has contact info (0-30 points)
        if lead.get('Contact Email'):
            score += 15
        if lead.get('Contact Phone'):
            score += 15
        
        # Case age (0-20 points)
        # Newer cases = higher score (owner easier to find)
        
        # Home state (0-10 points)
        if lead['State'] in ['MI', 'GA', 'MD', 'TX', 'CA', 'IL']:
            score += 10
        
        return min(score, 100)
    
    def save_to_airtable(self, leads):
        """Save leads to Airtable"""
        for lead in leads:
            try:
                self.leads_table.create(lead)
            except Exception as e:
                print(f"Error saving lead: {e}")
    
    def run(self):
        """Full mining pipeline"""
        print(f"Mining {self.county} County, {self.state}...")
        
        # 1. Scrape
        raw_leads = self.scrape()
        print(f"Found {len(raw_leads)} raw records")
        
        # 2. Clean
        cleaned_leads = self.clean_data(raw_leads)
        print(f"Cleaned {len(cleaned_leads)} leads")
        
        # 3. Deduplicate
        new_leads = self.deduplicate(cleaned_leads)
        print(f"{len(new_leads)} new leads (after deduplication)")
        
        # 4. AI Qualify
        qualified_leads = self.ai_qualify(new_leads)
        print(f"Qualified {len(qualified_leads)} leads")
        
        # 5. Save
        self.save_to_airtable(qualified_leads)
        print(f"Saved {len(qualified_leads)} leads to Airtable")
        
        return len(qualified_leads)
```

### **County-Specific Miners**

```python
class WayneCountyMiner(SurplusMiner):
    def __init__(self, airtable_api_key):
        super().__init__('Wayne', 'MI', airtable_api_key)
    
    def scrape(self):
        url = "https://www.waynecounty.com/elected/treasurer/foreclosure.aspx"
        # Implement Wayne County specific scraping
        leads = []
        # ... scraping logic ...
        return leads

class FultonCountyMiner(SurplusMiner):
    def __init__(self, airtable_api_key):
        super().__init__('Fulton', 'GA', airtable_api_key)
    
    def scrape(self):
        # Download Excel file
        url = "https://www.fultoncountyga.gov/.../surplus_list.xlsx"
        df = pd.read_excel(url)
        leads = df.to_dict('records')
        return leads
```

---

## 📅 **MINING SCHEDULE**

### **Recommended Frequency**

**Daily:**
- High-priority counties (Wayne, Fulton, Harris, Cook)
- Check for new postings

**Weekly:**
- Medium-priority counties
- All Tier 1 states

**Monthly:**
- Full sweep of all states
- Update existing lead statuses

### **Automation with Cron**

```bash
# Daily mining - High priority counties
0 6 * * * python /path/to/mine_leads.py --priority-only

# Weekly mining - All Tier 1 states
0 6 * * 1 python /path/to/mine_leads.py --tier1

# Monthly full sweep
0 6 1 * * python /path/to/mine_leads.py --all-states
```

---

## ⚖️ **LEGAL & COMPLIANCE**

### **State Regulations**

**Check before operating in each state:**

1. **California**: Requires surplus recovery license in some counties
2. **Florida**: May require collection agency license
3. **Texas**: Generally business-friendly, few restrictions
4. **New York**: Check county-specific rules

**Best Practices:**
- Include required disclosures in all communications
- "THIS LETTER IS IN NO WAY OF A FORM OF SOLICITATION, NOR AN ATTEMPT TO COLLECT A DEBT"
- Clearly state you are NOT a debt collector
- Honor do-not-contact requests
- Maintain compliance documentation

### **Data Privacy**

- Public records = legal to access and use
- Don't scrape behind login walls
- Respect robots.txt files
- Rate limit requests (be polite to servers)
- Store data securely

---

## 🎯 **SUCCESS METRICS**

### **Mining Performance**

Track these metrics:
- Leads discovered per day/week/month
- Average surplus amount per lead
- Priority score distribution
- Duplicate rate
- Coverage (% of counties actively mined)

### **Lead Quality**

- Conversion rate (leads → contracts signed)
- Average days from discovery to contact
- Response rate by contact method
- Success rate by surplus amount range
- Success rate by state/county

### **Expected Results**

**Good mining operation:**
- 50-200 new leads per month
- Average surplus: $5,000-$20,000
- Average priority score: 60-70
- 10-20% conversion rate
- Average fee: $3,000-$8,000 per closed deal

---

## 🚀 **QUICK START**

### **Phase 1: Pilot (Week 1)**
1. Start with Wayne County, MI (easiest to scrape)
2. Mine 1 month of data manually
3. Test data quality
4. Contact 10-20 property owners
5. Measure response rate

### **Phase 2: Expand (Weeks 2-4)**
1. Add Fulton County, GA
2. Add Harris County, TX
3. Automate daily mining
4. Build AI qualification
5. Track conversion rates

### **Phase 3: Scale (Month 2+)**
1. Add all Tier 1 states (6 states)
2. Add 2-3 counties per state
3. Full automation
4. Weekly batch processing
5. Continuous improvement

---

## 📞 **TROUBLESHOOTING**

### **Common Issues**

**Website changed structure:**
- Update scraper selectors
- Check for new PDF formats
- Monitor for errors

**IP blocked:**
- Use rotating proxies
- Add delays between requests
- Respect rate limits

**Data quality issues:**
- Improve cleaning functions
- Add validation rules
- Manual review of high-value leads

**Low conversion rates:**
- Improve AI qualification
- Focus on higher surplus amounts
- Test different contact methods
- Refine messaging

---

## 🛠️ **TOOLS & RESOURCES**

**Web Scraping:**
- Beautiful Soup - HTML parsing
- Selenium - JavaScript sites
- Scrapy - Large-scale scraping

**PDF Processing:**
- pdfplumber - Best for tables
- PyPDF2 - General PDF reading
- Tabula - PDF table extraction

**Data Processing:**
- pandas - Data manipulation
- numpy - Numerical operations

**Databases:**
- pyairtable - Airtable API
- SQLite - Local caching

**AI/ML:**
- Anthropic Claude API - Lead qualification
- scikit-learn - Scoring models

---

## 📈 **OPTIMIZATION TIPS**

1. **Focus on high-value leads first** (>$25K surplus)
2. **Prioritize home states** (easier to visit if needed)
3. **Contact quickly** (speed matters - competition exists)
4. **Use multi-channel outreach** (email + phone + mail)
5. **Track everything** (data drives improvement)
6. **Automate workflows** (follow-up sequences)
7. **Build relationships** (referrals from satisfied clients)

---

**Next:** Once mining is working, integrate with LBPC frontend and workflow automation! 🎯
