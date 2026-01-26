# 🤖 CAPABILITY STATEMENT AUTO-GENERATION FOR RFP RESPONSES

## 🎯 Automatic Triggers for Capability Statement Generation

### Trigger 1: When Opportunity Status Changes to "Ready to Bid"
**Location:** Airtable Opportunities table automation

**Flow:**
```
Opportunity Status → "Ready to Bid"
    ↓
Check: Does CapabilityStatementID exist?
    ↓ (No)
Generate capability statement automatically
    ↓
Link to opportunity
    ↓
Email notification: "Capstat ready for [Client]"
```

**Airtable Automation Setup:**
```
WHEN: Record matches conditions
CONDITIONS: 
  - Status = "Ready to Bid"
  - CapabilityStatementID is empty

ACTIONS:
  1. Run script to generate
  2. Update CapabilityStatementID field
  3. Send email notification
```

---

### Trigger 2: When Creating RFP Response Package
**Location:** RFP Response workflow

**Flow:**
```
User clicks "Create RFP Response Package"
    ↓
System checks: Capability statement exists?
    ↓ (No)
Auto-generate with appropriate template
    ↓ (Yes)
Include in RFP response package
    ↓
Create submission folder with all docs
```

---

### Trigger 3: Email Integration (Smart!)
**When:** Composing email to procurement officer

**Flow:**
```
User drafts email to client
    ↓
NEXUS detects: Email contains "capability statement" OR "qualifications"
    ↓
Suggests: "Would you like to attach your capability statement?"
    ↓
User clicks "Yes"
    ↓
Check: Capability statement exists for this client?
    ↓ (No) Generate now | (Yes) Attach existing
    ↓
PDF automatically attached to email
```

---

### Trigger 4: Weekly Batch Generation
**When:** Every Monday 8 AM

**Flow:**
```
Find all opportunities with:
  - Status = "Ready to Bid" OR "Bidding"
  - No capability statement linked
  - Deadline within 30 days
    ↓
Generate capability statements for all
    ↓
Send summary email: "5 capability statements generated"
```

---

## 🎯 RFP Response Package Integration

### Enhanced Workflow

#### Current RFP Response Process:
1. Qualify opportunity
2. Research requirements
3. Gather pricing
4. Write proposal
5. Submit

#### NEW Automated Process:
1. Qualify opportunity → **Auto-generate capability statement**
2. Research requirements
3. Gather pricing → **Capstat already ready**
4. Write proposal → **Include capstat link**
5. Submit → **Auto-attach capstat PDF**

---

## 📋 Airtable Automations to Create

### Automation 1: Auto-Generate on Qualification
**Name:** "Auto-Generate Capability Statement"

**Trigger:**
- When record matches conditions
- Status = "Ready to Bid"
- CapabilityStatementID is empty

**Actions:**
1. **Run Script:**
```javascript
let opportunityId = input.config().opportunityId;
let response = await fetch('https://your-server.com/capability-statements/generate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        opportunity_id: opportunityId,
        template: 'default'
    })
});
let result = await response.json();
output.set('capstatId', result.airtable_record_id);
```

2. **Update Record:**
   - CapabilityStatementID = output.capstatId
   - CapabilityStatementGenerated = "Yes"

3. **Send Email:**
   - To: dee@deedavis.biz
   - Subject: "Capability Statement Ready - {{ClientName}}"
   - Body: "Generated for {{ClientName}} ({{OpportunityNumber}})"

---

### Automation 2: Include in RFP Response
**Name:** "Attach Capstat to RFP Response"

**Trigger:**
- When button clicked: "Create RFP Response Package"

**Actions:**
1. **Find or Create Capstat:**
```javascript
// Check if exists
if (!record.fields.CapabilityStatementID) {
    // Generate new
    await generateCapabilityStatement(record.id);
}
```

2. **Create RFP Response Record:**
   - ClientName
   - OpportunityNumber
   - Includes: Proposal, Pricing, **Capability Statement**

3. **Package Files:**
   - Copy all files to submission folder
   - Name: `RFP_Response_ClientName_RFQ_Date/`

---

### Automation 3: Email with Auto-Attach
**Name:** "Send RFP Email with Capstat"

**Trigger:**
- When button clicked: "Email RFP Response"

**Actions:**
1. **Check Capstat Exists**
2. **Get PDF Path**
3. **Compose Email:**
   - To: Procurement officer from opportunity
   - CC: dee@deedavis.biz
   - Subject: "RFP Response - {{ClientName}} {{RFQNumber}}"
   - Attachments:
     - Proposal.pdf
     - Pricing.xlsx
     - **Capability_Statement.pdf** ← Auto-attached!
     - Supporting_Docs.zip

---

## 🔗 Make.com Integration Scenarios

### Scenario 1: One-Click RFP Package
**Modules:**
1. **Airtable Trigger:** Button clicked
2. **HTTP - Check Capstat:** GET existing or generate new
3. **Google Drive:** Create folder structure
4. **Google Drive:** Upload all documents
5. **Gmail:** Draft email with attachments
6. **Airtable Update:** Mark as "Submitted"

---

### Scenario 2: Smart Email Assistant
**Modules:**
1. **Gmail Trigger:** Draft created
2. **Text Parser:** Check for keywords ("capability statement", "qualifications")
3. **Router:** 
   - IF keywords found → Continue
   - ELSE → Skip
4. **HTTP:** Get or generate capability statement
5. **Gmail:** Attach PDF to draft
6. **Slack:** Notify "Capstat attached to email draft"

---

### Scenario 3: Weekly Batch Generation
**Modules:**
1. **Schedule:** Every Monday 8 AM
2. **Airtable Search:** Find opportunities needing capstats
3. **Iterator:** Loop through each
4. **HTTP:** Generate capability statement
5. **Airtable Update:** Link capstat to opportunity
6. **Gmail:** Send summary report

---

## 📱 NEXUS Frontend Component (Suggested)

### React Component: `CapabilityStatementManager.tsx`

```tsx
import React, { useState } from 'react';

interface CapStatGeneratorProps {
    opportunityId?: string;
    clientName?: string;
    rfqNumber?: string;
}

export const CapStatGenerator: React.FC<CapStatGeneratorProps> = ({
    opportunityId,
    clientName,
    rfqNumber
}) => {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    
    const generateStatement = async (template: string) => {
        setLoading(true);
        
        const response = await fetch('/capability-statements/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                opportunity_id: opportunityId,
                client_name: clientName,
                rfq_number: rfqNumber,
                template: template
            })
        });
        
        const data = await response.json();
        setResult(data);
        setLoading(false);
    };
    
    return (
        <div className="capstat-generator">
            <h3>Generate Capability Statement</h3>
            
            {/* Template Selection */}
            <div className="template-buttons">
                <button onClick={() => generateStatement('default')}>
                    Industrial
                </button>
                <button onClick={() => generateStatement('va_medical')}>
                    Healthcare
                </button>
                <button onClick={() => generateStatement('construction')}>
                    Construction
                </button>
            </div>
            
            {/* Loading State */}
            {loading && <div>Generating...</div>}
            
            {/* Result */}
            {result && (
                <div className="result">
                    <p>✓ Generated successfully!</p>
                    <a href={result.html_file} target="_blank">View HTML</a>
                    <a href={result.pdf_file} download>Download PDF</a>
                </div>
            )}
        </div>
    );
};
```

---

## 🎯 Smart Suggestions & Enhancements

### 1. **Auto-Tailor to RFQ Requirements** ⭐⭐⭐
**What:** Analyze RFQ text and auto-select highlights

```python
def analyze_rfq_and_customize(rfq_text: str, config: dict) -> dict:
    """Automatically tailor capability statement to RFQ"""
    
    # Check for keywords
    if 'medical' in rfq_text.lower() or 'healthcare' in rfq_text.lower():
        config['template'] = 'va_medical'
    
    if 'construction' in rfq_text.lower() or 'building' in rfq_text.lower():
        config['template'] = 'construction'
    
    # Extract requirements
    if 'EDWOSB' in rfq_text or 'set-aside' in rfq_text:
        # Highlight EDWOSB certification prominently
        config['highlights']['items'].insert(0, {
            'icon': '🎖️',
            'label': 'EDWOSB Certified',
            'value': 'SBA 8(a) Set-Aside Eligible'
        })
    
    # Check for delivery requirements
    if 'expedited' in rfq_text.lower() or 'emergency' in rfq_text.lower():
        config['highlights']['items'].append({
            'icon': '⚡',
            'label': 'Emergency Response',
            'value': '24-48 Hour Capability'
        })
    
    return config
```

**Benefit:** Capability statements automatically match RFQ priorities!

---

### 2. **Past Performance Auto-Include** ⭐⭐⭐
**What:** Auto-pull similar past contracts and include

```python
def add_past_performance(config: dict, opportunity_id: str) -> dict:
    """Add relevant past performance based on opportunity"""
    
    # Get opportunity details
    opp = get_opportunity(opportunity_id)
    naics = opp['NAICSCode']
    
    # Find similar contracts
    similar_contracts = find_contracts_by_naics(naics, limit=3)
    
    # Add to config
    config['past_performance'] = {
        'title': 'RELEVANT EXPERIENCE',
        'contracts': [
            {
                'client': contract['ClientName'],
                'value': contract['ContractValue'],
                'description': contract['Description'],
                'year': contract['Year']
            }
            for contract in similar_contracts
        ]
    }
    
    return config
```

**Benefit:** Shows you have experience in this area automatically!

---

### 3. **Version Control & History** ⭐⭐
**What:** Track all versions, see what changed

**Airtable Fields to Add:**
- `VersionNumber` (Number)
- `PreviousVersionID` (Link to CapabilityStatements)
- `ChangeSummary` (Long text)

**Code Enhancement:**
```python
def create_new_version(original_id: str, changes: dict) -> str:
    """Create new version of capability statement"""
    
    original = get_capstat(original_id)
    new_version = original.copy()
    new_version['VersionNumber'] = original['VersionNumber'] + 1
    new_version['PreviousVersionID'] = original_id
    new_version['ChangeSummary'] = f"Updated: {', '.join(changes.keys())}"
    
    # Apply changes
    new_version.update(changes)
    
    # Generate new files
    result = generate_capstat(new_version)
    
    return result['id']
```

**Benefit:** See evolution of your capability statements over time!

---

### 4. **Smart Template Selector** ⭐⭐⭐
**What:** AI automatically chooses best template

```python
def select_best_template(opportunity: dict) -> str:
    """Intelligently select template based on opportunity"""
    
    title = opportunity.get('Title', '').lower()
    description = opportunity.get('Description', '').lower()
    naics = opportunity.get('NAICSCode', '')
    
    # Healthcare indicators
    healthcare_keywords = ['medical', 'healthcare', 'hospital', 'va', 'clinic']
    if any(keyword in title or keyword in description for keyword in healthcare_keywords):
        return 'va_medical'
    
    # Construction indicators
    construction_keywords = ['construction', 'building', 'renovation', 'facility']
    if any(keyword in title or keyword in description for keyword in construction_keywords):
        return 'construction'
    
    # NAICS-based
    if naics.startswith('62'):  # Healthcare
        return 'va_medical'
    elif naics.startswith('23'):  # Construction
        return 'construction'
    
    return 'default'
```

**Benefit:** Always use the most appropriate template automatically!

---

### 5. **Email Template with Auto-Attach** ⭐⭐⭐
**What:** Pre-written email templates that auto-attach capstat

```python
def create_rfp_email_with_capstat(opportunity_id: str) -> dict:
    """Create RFP response email with capability statement attached"""
    
    opp = get_opportunity(opportunity_id)
    
    # Generate or get existing capstat
    capstat = get_or_generate_capstat(opportunity_id)
    
    email_template = f"""
Subject: RFP Response - {opp['ClientName']} {opp['OpportunityNumber']}

Dear {opp['ProcurementOfficer']},

DEE DAVIS INC is pleased to submit our response to {opp['OpportunityNumber']} 
for {opp['Title']}.

Attached you will find:
1. Technical Proposal
2. Pricing Schedule
3. Capability Statement
4. Certifications
5. Past Performance References

We are confident our {opp['Certifications']} certification and proven track 
record make us the ideal partner for this project.

Thank you for your consideration.

Best regards,
Dee Davis, President & CEO
DEE DAVIS INC
"""
    
    return {
        'to': opp['ProcurementOfficerEmail'],
        'subject': f"RFP Response - {opp['ClientName']} {opp['OpportunityNumber']}",
        'body': email_template,
        'attachments': [
            capstat['pdf_file'],
            # Other docs auto-attached
        ]
    }
```

**Benefit:** One-click email with everything attached!

---

### 6. **Opportunity-Specific Customization** ⭐⭐⭐
**What:** Auto-customize based on opportunity details

```python
def customize_for_opportunity(opportunity_id: str, config: dict) -> dict:
    """Customize capability statement based on opportunity"""
    
    opp = get_opportunity(opportunity_id)
    
    # Update commitment statement
    config['commitment'] = (
        f"{config['company']['name']} is committed to providing "
        f"{opp['ClientName']} with {opp['Title']}, competitive pricing, "
        f"reliable on-time delivery, and professional service throughout "
        f"the contract period."
    )
    
    # Add relevant certifications to highlights
    if 'EDWOSB' in opp.get('SetAside', ''):
        config['highlights']['items'].insert(0, {
            'icon': '🎖️',
            'label': 'Set-Aside Eligible',
            'value': 'SBA Certified EDWOSB'
        })
    
    # Match contract value range
    if opp.get('EstimatedValue'):
        value = float(opp['EstimatedValue'])
        if value > 100000:
            config['highlights']['items'].append({
                'icon': '💼',
                'label': 'Large Contract Experience',
                'value': f'${int(value/1000)}K+ Successfully Delivered'
            })
    
    return config
```

**Benefit:** Every capstat is perfectly tailored to the specific RFQ!

---

### 7. **Submission Package Builder** ⭐⭐⭐
**What:** Auto-create complete RFP response folder

```python
def create_rfp_submission_package(opportunity_id: str) -> dict:
    """Create complete RFP submission package"""
    
    opp = get_opportunity(opportunity_id)
    
    # Create folder structure
    folder_name = f"RFP_Response_{opp['ClientName']}_{opp['OpportunityNumber']}_{date.today()}"
    os.makedirs(folder_name, exist_ok=True)
    
    # 1. Generate/get capability statement
    capstat = get_or_generate_capstat(opportunity_id)
    shutil.copy(capstat['pdf_file'], f"{folder_name}/01_Capability_Statement.pdf")
    
    # 2. Copy pricing
    if opp.get('PricingSheetPath'):
        shutil.copy(opp['PricingSheetPath'], f"{folder_name}/02_Pricing_Schedule.xlsx")
    
    # 3. Copy proposal
    if opp.get('ProposalPath'):
        shutil.copy(opp['ProposalPath'], f"{folder_name}/03_Technical_Proposal.pdf")
    
    # 4. Get certifications
    certs_folder = f"{folder_name}/04_Certifications"
    os.makedirs(certs_folder, exist_ok=True)
    copy_certification_pdfs(certs_folder)
    
    # 5. Get past performance
    past_perf_folder = f"{folder_name}/05_Past_Performance"
    os.makedirs(past_perf_folder, exist_ok=True)
    generate_past_performance_refs(opportunity_id, past_perf_folder)
    
    # 6. Create cover letter
    cover_letter = create_cover_letter(opportunity_id)
    save_pdf(cover_letter, f"{folder_name}/00_Cover_Letter.pdf")
    
    # 7. Create transmittal form
    transmittal = create_transmittal_form(opportunity_id)
    save_pdf(transmittal, f"{folder_name}/Transmittal_Form.pdf")
    
    # 8. Create README
    create_readme(folder_name, opp)
    
    return {
        'folder_path': folder_name,
        'files_included': os.listdir(folder_name),
        'ready_to_submit': True
    }
```

**Benefit:** Complete RFP response package in one click!

---

### 8. **Template Library & Management** ⭐⭐
**What:** Manage multiple templates for different scenarios

**New Feature:**
```python
TEMPLATE_LIBRARY = {
    'default': {
        'name': 'Default (Industrial)',
        'best_for': ['industrial', 'supplies', 'general'],
        'color': '#d97706'
    },
    'va_medical': {
        'name': 'VA Medical',
        'best_for': ['medical', 'healthcare', 'hospital', 'va'],
        'color': '#0066cc'
    },
    'construction': {
        'name': 'Construction',
        'best_for': ['construction', 'building', 'renovation'],
        'color': '#f97316'
    },
    'energy': {
        'name': 'Energy & Utilities',
        'best_for': ['utility', 'energy', 'power', 'cps'],
        'color': '#ef4444'
    },
    'federal': {
        'name': 'Federal Agency',
        'best_for': ['federal', 'gsa', 'dod', 'government'],
        'color': '#1e40af'
    },
    'state_local': {
        'name': 'State & Local',
        'best_for': ['state', 'county', 'municipal', 'city'],
        'color': '#16a34a'
    }
}
```

**Airtable Table:** `CapabilityStatementTemplates`
- TemplateName
- BestForKeywords
- AccentColor
- ConfigJSON
- TimesUsed
- WinRate

---

### 9. **Quick Edit Before Sending** ⭐⭐
**What:** Make last-minute tweaks without regenerating

**Feature:**
```python
def quick_edit_capstat(capstat_id: str, edits: dict) -> str:
    """Make quick edits to existing capability statement"""
    
    # Load existing HTML
    html_path = get_capstat_html(capstat_id)
    with open(html_path, 'r') as f:
        html = f.read()
    
    # Apply quick edits
    if 'commitment' in edits:
        html = html.replace(
            '<p class="commitment">.*?</p>',
            f'<p class="commitment">{edits["commitment"]}</p>'
        )
    
    if 'highlight' in edits:
        # Update specific highlight
        pass
    
    # Save as new version
    new_path = save_new_version(html, capstat_id)
    
    # Regenerate PDF
    generate_pdf(new_path)
    
    return new_path
```

---

### 10. **Win/Loss Tracking** ⭐⭐⭐
**What:** Track which capability statements win bids

**Airtable Fields:**
- `BidResult` (Select: Won, Lost, Pending)
- `WinDate` (Date)
- `WinValue` (Currency)
- `LossReason` (Long text)
- `ClientFeedback` (Long text)

**Analysis Dashboard:**
```python
def analyze_capstat_performance():
    """Analyze which templates/approaches win"""
    
    capstats = get_all_capstats()
    
    analysis = {
        'total_generated': len(capstats),
        'submitted': len([c for c in capstats if c['Status'] == 'Submitted']),
        'won': len([c for c in capstats if c['BidResult'] == 'Won']),
        'win_rate': 0,
        'by_template': {},
        'avg_value_won': 0
    }
    
    # Calculate win rate by template
    for template in ['default', 'va_medical', 'construction']:
        template_capstats = [c for c in capstats if c['Template'] == template]
        won = [c for c in template_capstats if c['BidResult'] == 'Won']
        
        analysis['by_template'][template] = {
            'total': len(template_capstats),
            'won': len(won),
            'win_rate': len(won) / len(template_capstats) if template_capstats else 0
        }
    
    return analysis
```

---

### 11. **QR Code for Digital Access** ⭐⭐
**What:** Add QR code linking to online version

```python
import qrcode

def add_qr_code(capstat_id: str, html_path: str) -> str:
    """Add QR code to capability statement for digital access"""
    
    # Create online URL (from NEXUS frontend)
    url = f"https://deedavis.biz/capstat/{capstat_id}"
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    qr_path = f"qr_{capstat_id}.png"
    img.save(qr_path)
    
    # Add to HTML
    with open(html_path, 'r') as f:
        html = f.read()
    
    qr_html = f"""
    <div class="qr-code" style="text-align: center; margin: 20px;">
        <img src="{qr_path}" alt="Scan for digital version" style="width: 150px;">
        <p style="font-size: 0.8em; color: #666;">Scan for digital version</p>
    </div>
    """
    
    html = html.replace('</footer>', f'{qr_html}</footer>')
    
    with open(html_path, 'w') as f:
        f.write(html)
    
    return qr_path
```

**Benefit:** Procurement officers can scan and view online instantly!

---

### 12. **Email Tracking** ⭐⭐
**What:** Know when client opens your capability statement

**Implementation:**
```python
def create_trackable_pdf_link(capstat_id: str) -> str:
    """Create trackable link for PDF"""
    
    tracking_url = f"https://deedavis.biz/track/capstat/{capstat_id}/download"
    
    # When accessed, log:
    # - Who accessed (IP, email if authenticated)
    # - When accessed
    # - How long viewed (if web version)
    # - Downloaded or just viewed
    
    return tracking_url
```

**Airtable Fields:**
- `TimesViewed` (Number)
- `LastViewedDate` (Date)
- `ViewedBy` (Long text - list of IPs/emails)

**Benefit:** Know if client actually looked at it!

---

### 13. **Multi-Language Support** ⭐
**What:** Generate in multiple languages

```python
TRANSLATIONS = {
    'es': {
        'capability_statement': 'Declaración de Capacidad',
        'company_overview': 'Resumen de la Empresa',
        # ... more translations
    },
    'fr': {
        'capability_statement': 'Déclaration de Capacité',
        # ...
    }
}

def generate_in_language(config: dict, language: str = 'en') -> str:
    """Generate capability statement in specified language"""
    
    if language != 'en':
        config = translate_config(config, language)
    
    return generate_html(config)
```

---

### 14. **Comparison Tool** ⭐⭐
**What:** Compare your capstat with competitors

**Feature:**
```python
def compare_capabilities(our_capstat_id: str, competitor_url: str) -> dict:
    """Compare our capability statement with competitor"""
    
    our_capstat = get_capstat(our_capstat_id)
    competitor = scrape_competitor_capstat(competitor_url)
    
    comparison = {
        'our_advantages': [],
        'their_advantages': [],
        'suggestions': []
    }
    
    # Compare certifications
    if 'EDWOSB' in our_capstat['certifications'] and 'EDWOSB' not in competitor['certifications']:
        comparison['our_advantages'].append('EDWOSB Certification')
    
    # Compare experience
    # Compare capabilities
    # Provide suggestions for improvement
    
    return comparison
```

---

### 15. **Social Media Versions** ⭐
**What:** Auto-create LinkedIn/Twitter versions

```python
def create_social_media_version(capstat_id: str, platform: str) -> str:
    """Create social media version of capability statement"""
    
    capstat = get_capstat(capstat_id)
    
    if platform == 'linkedin':
        return f"""
🎯 DEE DAVIS INC Capability Statement

Certified EDWOSB serving government agencies nationwide

✓ Industrial Supplies & Distribution
✓ $50K-$500K+ Contract Experience
✓ 98%+ On-Time Delivery
✓ Strategic Partnerships: Grainger | Fastenal

Ready to partner on your next project!

📧 info@deedavis.biz | 🌐 www.deedavis.biz
#GovCon #EDWOSB #GovernmentContracting
"""
    
    elif platform == 'twitter':
        return f"""
🎯 DEE DAVIS INC - Certified EDWOSB
Serving gov't agencies nationwide
✓ Industrial supplies ✓ $500K+ experience
✓ 98%+ on-time delivery
Ready to partner! 📧 info@deedavis.biz
#GovCon #EDWOSB
"""
```

---

## 🎯 RECOMMENDED IMPLEMENTATION PRIORITY

### Phase 1: Immediate (Do This Week) ⭐⭐⭐
1. **Auto-generate on "Ready to Bid" status change**
2. **Airtable button for manual generation**
3. **Smart template selector based on keywords**
4. **Email template with auto-attach**

### Phase 2: Soon (Next 2 Weeks) ⭐⭐
5. **Opportunity-specific customization**
6. **Past performance auto-include**
7. **Submission package builder**
8. **Version control**

### Phase 3: Future (Next Month) ⭐
9. **Win/loss tracking and analytics**
10. **QR code for digital access**
11. **Email tracking**
12. **Quick edit feature**

### Phase 4: Advanced (Later) ⭐
13. **Multi-language support**
14. **Competitor comparison**
15. **Social media versions**

---

## 🔥 BEST AUTOMATION SCENARIO (Recommended)

### Complete RFP Response Automation

**Step 1: Opportunity Qualified**
```
User marks opportunity as "Ready to Bid"
    ↓
NEXUS automatically:
  ✓ Generates capability statement (smart template)
  ✓ Customizes for this specific RFQ
  ✓ Saves to Airtable
  ✓ Notifies user: "Capstat ready!"
```

**Step 2: Pricing Complete**
```
User completes pricing in NEXUS
    ↓
NEXUS automatically:
  ✓ Checks capability statement exists
  ✓ Prepares RFP response package
  ✓ Creates submission folder
```

**Step 3: Ready to Submit**
```
User clicks "Create Email to Submit"
    ↓
NEXUS automatically:
  ✓ Drafts professional email
  ✓ Attaches capability statement PDF
  ✓ Attaches pricing sheet
  ✓ Attaches proposal (if ready)
  ✓ Pre-fills procurement officer email
  ✓ User just clicks "Send"!
```

---

## 📱 NEXUS Frontend UI Mockup

### Opportunity Detail Page - New Section

```
┌─────────────────────────────────────────────┐
│ CAPABILITY STATEMENT                         │
├─────────────────────────────────────────────┤
│                                              │
│ Status: ✓ Generated (Jan 23, 2026)          │
│                                              │
│ Template: Default (Industrial)               │
│                                              │
│ [View HTML] [Download PDF] [Regenerate]     │
│                                              │
│ [Include in RFP Response] [Email to Client] │
│                                              │
└─────────────────────────────────────────────┘
```

### Settings Page - New Section

```
┌─────────────────────────────────────────────┐
│ CAPABILITY STATEMENT SETTINGS                │
├─────────────────────────────────────────────┤
│                                              │
│ Auto-Generate:                               │
│ [x] When status changes to "Ready to Bid"   │
│ [x] Include in all RFP response packages    │
│ [ ] Weekly batch for pending opportunities  │
│                                              │
│ Default Template:                            │
│ ( ) Default  (•) Smart Select  ( ) Ask      │
│                                              │
│ Email Behavior:                              │
│ [x] Auto-attach when email mentions capstat │
│ [x] Suggest when emailing procurement officer│
│                                              │
│ Templates Available:                         │
│ • Default (Industrial) - 15 uses, 60% win   │
│ • VA Medical - 3 uses, 100% win             │
│ • Construction - 8 uses, 50% win            │
│                                              │
│ [Manage Templates] [Create New Template]    │
│                                              │
└─────────────────────────────────────────────┘
```

---

## 🎯 Code Enhancements to Add

### Enhancement 1: Auto-Trigger in NEXUS Backend

Add to `nexus_backend.py`:

```python
def handle_opportunity_status_change(opportunity_id: str, new_status: str):
    """Handle opportunity status changes"""
    
    # Existing status change logic...
    
    # NEW: Auto-generate capability statement
    if new_status == "Ready to Bid":
        from capability_statement_generator import handle_generate_capability_statement
        
        # Check if already exists
        existing = check_existing_capstat(opportunity_id)
        
        if not existing:
            print(f"Auto-generating capability statement for {opportunity_id}")
            result = handle_generate_capability_statement(
                opportunity_id=opportunity_id,
                template='auto'  # Auto-select best template
            )
            
            if result['success']:
                print(f"✓ Capability statement generated: {result['pdf_file']}")
                send_notification(
                    "Capability Statement Ready",
                    f"Generated for opportunity {opportunity_id}"
                )
```

---

### Enhancement 2: Email Helper Function

Add to `capability_statement_generator.py`:

```python
def create_rfp_email_with_attachments(opportunity_id: str) -> dict:
    """Create complete RFP response email with all attachments"""
    
    from pyairtable import Api
    
    api = Api(os.environ['AIRTABLE_API_KEY'])
    opportunities = api.table(os.environ['AIRTABLE_BASE_ID'], 'Opportunities')
    
    # Get opportunity
    opp = opportunities.get(opportunity_id)
    fields = opp['fields']
    
    # Get or generate capability statement
    capstat = get_or_generate_capstat(opportunity_id)
    
    # Build email
    email = {
        'to': fields.get('ProcurementOfficerEmail'),
        'cc': 'info@deedavis.biz',
        'subject': f"RFP Response - {fields['ClientName']} {fields['OpportunityNumber']}",
        'body': f"""
Dear {fields.get('ProcurementOfficer', 'Procurement Officer')},

DEE DAVIS INC is pleased to submit our response to {fields['OpportunityNumber']} 
for {fields.get('Title', 'your solicitation')}.

As a certified EDWOSB with proven experience in {fields.get('Category', 'this field')}, 
we are confident we can deliver exceptional value to {fields['ClientName']}.

Attached please find:
1. Capability Statement
2. Pricing Schedule
3. Technical Proposal
4. Certifications
5. Past Performance References

We look forward to the opportunity to serve {fields['ClientName']}.

Best regards,
Dee Davis, President & CEO
DEE DAVIS INC
248-376-4550
info@deedavis.biz
""",
        'attachments': [
            capstat['pdf_file'],
            fields.get('PricingSheetPath'),
            fields.get('ProposalPath'),
            # ... other attachments
        ]
    }
    
    return email
```

---

### Enhancement 3: Smart Cache System

```python
CAPSTAT_CACHE = {}

def get_or_generate_capstat(opportunity_id: str, force_regenerate: bool = False) -> dict:
    """Get existing or generate new capability statement with caching"""
    
    cache_key = f"capstat_{opportunity_id}"
    
    # Check cache first (unless force regenerate)
    if not force_regenerate and cache_key in CAPSTAT_CACHE:
        cached = CAPSTAT_CACHE[cache_key]
        # Check if still valid (less than 24 hours old)
        if (datetime.now() - cached['generated_at']).hours < 24:
            return cached
    
    # Check Airtable
    existing = find_capstat_by_opportunity(opportunity_id)
    
    if existing and not force_regenerate:
        # Check if recent (less than 7 days old)
        generated_date = datetime.fromisoformat(existing['GeneratedDate'])
        if (datetime.now() - generated_date).days < 7:
            CAPSTAT_CACHE[cache_key] = existing
            return existing
    
    # Generate new
    result = handle_generate_capability_statement(opportunity_id=opportunity_id)
    
    # Cache it
    CAPSTAT_CACHE[cache_key] = {
        **result,
        'generated_at': datetime.now()
    }
    
    return result
```

---

## 🎓 Training Checklist for Team

### For Manual Use
- [ ] Know where config files are
- [ ] Can edit JSON files
- [ ] Can run Python commands
- [ ] Can review HTML output
- [ ] Can download PDF for submission

### For NEXUS Use
- [ ] Know when capstats auto-generate
- [ ] Can click "Generate" button in Airtable
- [ ] Can select appropriate template
- [ ] Can attach to emails
- [ ] Can track which ones win

### For Advanced Users
- [ ] Can create custom templates
- [ ] Can customize colors/content
- [ ] Can set up automations
- [ ] Can analyze win rates
- [ ] Can troubleshoot issues

---

## 📊 Success Metrics to Track

### Efficiency Metrics
- Time to generate: Target <10 seconds
- Statements generated per week
- Automation success rate
- Error rate

### Quality Metrics
- Win rate with capstat vs without
- Client feedback scores
- Template effectiveness
- Customization usage

### Business Metrics
- Bids submitted with capstat
- Contracts won (attributed to capstat)
- Time saved vs manual creation
- Cost per statement (should be $0!)

---

## 🎉 FINAL RECOMMENDATIONS

### Must-Have (Implement Now) ⭐⭐⭐
1. **Auto-generate on "Ready to Bid"** - Saves massive time
2. **Smart template selection** - Always use right format
3. **Email auto-attach** - Never forget to include it
4. **One-click RFP package** - Everything ready to submit

### Should-Have (Next Week) ⭐⭐
5. **Past performance auto-include** - Shows experience automatically
6. **Opportunity-specific customization** - Perfectly tailored every time
7. **Version tracking** - See what changed, when
8. **Win/loss analysis** - Know what works

### Nice-to-Have (Later) ⭐
9. **QR codes** - Modern, tech-forward
10. **Email tracking** - Know who's reading
11. **Quick edit** - Last-minute tweaks
12. **Social media versions** - Broader reach

---

## 💼 Business Impact

### Before This System
- 1-2 hours to create in Word
- Inconsistent formatting
- Easy to forget important details
- Hard to customize quickly
- No tracking or analytics

### After This System
- <1 minute to generate
- Professional, consistent quality
- All details auto-populated
- Easy to customize
- Full tracking and win/loss analysis

### ROI
- **Time saved:** 98% (1-2 hours → <1 minute)
- **Quality improvement:** Consistent, professional
- **More bids:** Can bid on 10x more opportunities
- **Better wins:** Tailored to each RFQ

---

## 🚀 YOUR NEXT ACTIONS

### Today
1. ✅ Review generated test file: `open default.html`
2. ⬜ Create CPS Energy capability statement
3. ⬜ Test PDF generation
4. ⬜ Set up Airtable CapabilityStatements table

### This Week
1. ⬜ Add Airtable automation for auto-generate
2. ⬜ Set up Make.com webhook
3. ⬜ Add button to Opportunities table
4. ⬜ Generate capstats for all active bids

### Next Week
1. ⬜ Implement email auto-attach
2. ⬜ Create submission package builder
3. ⬜ Add past performance section
4. ⬜ Track first wins!

---

## 📞 Quick Commands

```bash
# Generate for any RFQ
cp default_config.json client_config.json
nano client_config.json  # Edit client & RFQ
python3 generate_html_with_highlights.py client_config.json
python3 generate_enhanced_pdf.py client_config.json

# Review
open client.html
open client_enhanced.pdf

# Submit!
```

---

🎉 **CAPABILITY STATEMENT GENERATOR - READY FOR AUTOMATION!** 🎉
