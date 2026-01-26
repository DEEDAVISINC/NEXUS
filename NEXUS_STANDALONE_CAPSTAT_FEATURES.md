# 🎯 NEXUS STAND-ALONE CAPABILITY STATEMENT FEATURES

## Vision: Professional Capability Statement Manager in NEXUS

---

## 🖥️ NEXUS Frontend Features (Recommended)

### Feature 1: Capability Statement Dashboard 📊

**Location:** New section in NEXUS main menu

```
NEXUS Main Menu:
├── Opportunities
├── AI Recommendations
├── Officer Outreach
├── Fulfillment
└── ✨ Capability Statements (NEW!)
    ├── All Statements
    ├── By Client
    ├── By Template
    ├── Win Analysis
    └── Quick Generate
```

**Dashboard View:**
```
┌────────────────────────────────────────────────────────────┐
│ CAPABILITY STATEMENTS DASHBOARD                             │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Statistics                                              │
│  ┌──────────┬──────────┬──────────┬──────────┐            │
│  │ Total    │ This Week│ Win Rate │ Avg Time │            │
│  │ 47       │ 5        │ 63%      │ 1.2 sec  │            │
│  └──────────┴──────────┴──────────┴──────────┘            │
│                                                             │
│  🎨 Templates Performance                                   │
│  ┌────────────────┬───────┬─────────┬──────────┐          │
│  │ Template       │ Used  │ Won     │ Win Rate │          │
│  ├────────────────┼───────┼─────────┼──────────┤          │
│  │ Default        │ 25    │ 16      │ 64%      │          │
│  │ VA Medical     │ 8     │ 6       │ 75%      │          │
│  │ Construction   │ 14    │ 8       │ 57%      │          │
│  └────────────────┴───────┴─────────┴──────────┘          │
│                                                             │
│  📝 Recent Statements                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ CPS Energy - RFQ 7000205103      [View] [Download]  │  │
│  │ Generated: Jan 23, 2026 | Status: Submitted         │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ City of Detroit - DPW-2026-001   [View] [Download]  │  │
│  │ Generated: Jan 22, 2026 | Status: Generated         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  [+ Generate New] [Batch Generate] [Settings]              │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

### Feature 2: Quick Generate Modal 🚀

**Triggered by:** Click "Generate New" button anywhere in NEXUS

```
┌──────────────────────────────────────────┐
│ ⚡ GENERATE CAPABILITY STATEMENT          │
├──────────────────────────────────────────┤
│                                           │
│ Generate From:                            │
│ ( ) Existing Opportunity                  │
│ (•) Quick Generate (Manual)               │
│                                           │
│ Client Name: [CPS Energy            ]    │
│ RFQ Number:  [7000205103            ]    │
│ RFQ Title:   [Industrial Wipers     ]    │
│                                           │
│ Template:                                 │
│ [Default ▼] [Preview Colors]             │
│                                           │
│ Customize (Optional):                     │
│ [ ] Edit highlights                       │
│ [ ] Change colors                         │
│ [ ] Add custom sections                   │
│                                           │
│ [Cancel] [Generate HTML + PDF]            │
│                                           │
└──────────────────────────────────────────┘
```

**After generation:**
```
┌──────────────────────────────────────────┐
│ ✅ CAPABILITY STATEMENT GENERATED!        │
├──────────────────────────────────────────┤
│                                           │
│ Client: CPS Energy                        │
│ RFQ: 7000205103                          │
│                                           │
│ Files Created:                            │
│ • HTML (for preview)                     │
│ • PDF (for submission)                   │
│                                           │
│ [📄 View HTML] [📥 Download PDF]          │
│                                           │
│ Quick Actions:                            │
│ [📧 Email to Client]                      │
│ [📦 Add to RFP Package]                   │
│ [🔗 Copy Link]                            │
│ [↩️ Regenerate]                           │
│                                           │
└──────────────────────────────────────────┘
```

---

### Feature 3: Capability Statement in Opportunity Detail 📋

**Location:** Opportunity detail page

```
┌────────────────────────────────────────────────┐
│ OPPORTUNITY: CPS Energy - RFQ 7000205103       │
├────────────────────────────────────────────────┤
│                                                 │
│ [Overview] [Pricing] [Documents] [Capstat]     │
│                                                 │
│ ┌─────────────────────────────────────────────┐│
│ │ CAPABILITY STATEMENT                         ││
│ ├─────────────────────────────────────────────┤│
│ │                                              ││
│ │ Status: ✅ Generated                         ││
│ │ Date: Jan 23, 2026 10:30 AM                 ││
│ │ Template: Default (Industrial)               ││
│ │                                              ││
│ │ [👁️ Preview] [📥 Download] [🔄 Regenerate]   ││
│ │                                              ││
│ │ Customizations:                              ││
│ │ • Highlights tailored for CPS Energy        ││
│ │ • Commitment statement customized           ││
│ │ • Colors: Navy/Amber (professional)         ││
│ │                                              ││
│ │ Usage:                                       ││
│ │ • Included in RFP response: ✅               ││
│ │ • Emailed to client: ✅ (Jan 23)            ││
│ │ • Times downloaded: 3                       ││
│ │                                              ││
│ │ [Edit Highlights] [Change Colors]           ││
│ │ [Create New Version] [Email to Client]      ││
│ │                                              ││
│ └─────────────────────────────────────────────┘│
│                                                 │
└────────────────────────────────────────────────┘
```

---

### Feature 4: Template Gallery 🎨

```
┌────────────────────────────────────────────────┐
│ 🎨 CAPABILITY STATEMENT TEMPLATES               │
├────────────────────────────────────────────────┤
│                                                 │
│ ┌──────────────┬──────────────┬─────────────┐ │
│ │ DEFAULT      │ VA MEDICAL   │ CONSTRUCTION│ │
│ │ [Preview]    │ [Preview]    │ [Preview]   │ │
│ │              │              │             │ │
│ │ 🟠 Amber     │ 🔵 Blue      │ 🟠 Orange   │ │
│ │ Industrial   │ Healthcare   │ Building    │ │
│ │              │              │             │ │
│ │ Used: 25x    │ Used: 8x     │ Used: 14x   │ │
│ │ Win Rate:64% │ Win Rate:75% │ Win Rate:57%│ │
│ │              │              │             │ │
│ │ [Use This]   │ [Use This]   │ [Use This]  │ │
│ └──────────────┴──────────────┴─────────────┘ │
│                                                 │
│ ┌──────────────┬──────────────┬─────────────┐ │
│ │ ENERGY       │ FEDERAL      │ STATE/LOCAL │ │
│ │ [Preview]    │ [Preview]    │ [Preview]   │ │
│ │              │              │             │ │
│ │ 🔴 Red       │ 🔵 Blue      │ 🟢 Green    │ │
│ │ Utilities    │ Federal Govt │ Municipal   │ │
│ │              │              │             │ │
│ │ [Use This]   │ [Use This]   │ [Use This]  │ │
│ └──────────────┴──────────────┴─────────────┘ │
│                                                 │
│ [+ Create Custom Template]                     │
│                                                 │
└────────────────────────────────────────────────┘
```

---

### Feature 5: Email Integration 📧

**Smart Email Assistant:**

```
When composing email to procurement officer:

┌────────────────────────────────────────────┐
│ 💡 SUGGESTION                               │
├────────────────────────────────────────────┤
│                                             │
│ It looks like you're emailing about an     │
│ RFP response. Would you like to:           │
│                                             │
│ [✓] Attach capability statement            │
│ [✓] Use RFP response email template        │
│ [ ] Include pricing sheet                  │
│ [ ] Include certifications                 │
│                                             │
│ [Apply] [Dismiss]                          │
│                                             │
└────────────────────────────────────────────┘
```

**Auto-Attach on Keywords:**
- Email contains "capability statement" → Auto-suggest attachment
- Email contains "qualifications" → Auto-suggest attachment
- Email to known procurement officer → Auto-suggest full package

---

### Feature 6: Submission Package Builder 📦

```
┌──────────────────────────────────────────────────┐
│ 📦 CREATE RFP SUBMISSION PACKAGE                 │
├──────────────────────────────────────────────────┤
│                                                   │
│ Opportunity: CPS Energy - RFQ 7000205103         │
│                                                   │
│ Package Contents:                                 │
│ ┌───────────────────────────────────────────┐   │
│ │ ✅ 01_Capability_Statement.pdf            │   │
│ │ ⚠️  02_Pricing_Schedule.xlsx (missing)    │   │
│ │ ⚠️  03_Technical_Proposal.pdf (missing)   │   │
│ │ ✅ 04_Certifications/ (4 files)           │   │
│ │ ✅ 05_Past_Performance/ (3 refs)          │   │
│ │ ✅ 00_Cover_Letter.pdf                    │   │
│ │ ✅ EMAIL_DRAFT.txt                        │   │
│ │ ✅ README.md                              │   │
│ └───────────────────────────────────────────┘   │
│                                                   │
│ Missing Files:                                    │
│ • Pricing Schedule [Upload] [Create in NEXUS]   │
│ • Technical Proposal [Upload] [Generate]        │
│                                                   │
│ Ready to Submit: ⚠️ (2 files missing)            │
│                                                   │
│ [Create Package] [Cancel]                        │
│                                                   │
└──────────────────────────────────────────────────┘
```

---

### Feature 7: Quick Actions Menu 🎯

**Right-click on any opportunity:**

```
┌──────────────────────────────────┐
│ Quick Actions                     │
├──────────────────────────────────┤
│ ⚡ Generate Capability Statement  │
│ 📧 Email RFP Response            │
│ 📦 Create Submission Package     │
│ 📊 View Pricing                  │
│ 📝 Add Notes                     │
│ 🔗 Copy Link                     │
└──────────────────────────────────┘
```

---

### Feature 8: Template Customizer 🎨

```
┌────────────────────────────────────────────────┐
│ 🎨 CUSTOMIZE CAPABILITY STATEMENT               │
├────────────────────────────────────────────────┤
│                                                 │
│ Base Template: [Default ▼]                     │
│                                                 │
│ Colors:                                         │
│ Primary:  [#0f172a] [🎨]                       │
│ Accent:   [#d97706] [🎨]                       │
│                                                 │
│ Highlights (Drag to reorder):                   │
│ ┌─────────────────────────────────────────┐   │
│ │ ☰ 🎯 Primary NAICS                       │   │
│ │   423850 - Industrial Supplies    [Edit]│   │
│ ├─────────────────────────────────────────┤   │
│ │ ☰ 🤝 Key Partners                        │   │
│ │   Grainger | Fastenal           [Edit]│   │
│ ├─────────────────────────────────────────┤   │
│ │ ☰ 📊 Contract Range                      │   │
│ │   $50K-$500K+                    [Edit]│   │
│ └─────────────────────────────────────────┘   │
│                                                 │
│ [+ Add Highlight] [- Remove]                   │
│                                                 │
│ Competencies:                                   │
│ [✓] Industrial Supplies & Distribution         │
│ [✓] Government Contracting                     │
│ [✓] Supply Chain Management                    │
│ [ ] Custom: [________________]                 │
│                                                 │
│ [Preview Changes] [Save Template] [Generate]   │
│                                                 │
└────────────────────────────────────────────────┘
```

---

### Feature 9: Smart Auto-Complete 🤖

**As you type client name, NEXUS suggests:**

```
Client Name: CPS En...

┌──────────────────────────────────┐
│ 💡 Suggestions                    │
├──────────────────────────────────┤
│ CPS Energy                        │
│   • Last generated: 2 days ago   │
│   • Template: Default            │
│   • [Use Previous] [Generate New]│
└──────────────────────────────────┘
```

---

### Feature 10: One-Click RFP Response 📤

**Button in Opportunity:**

```
┌────────────────────────────────────┐
│ [📤 ONE-CLICK RFP RESPONSE]        │
└────────────────────────────────────┘
        ↓ (When clicked)
┌────────────────────────────────────┐
│ ⏳ Creating your RFP response...   │
│                                     │
│ ✅ Capability statement generated   │
│ ✅ Pricing sheet prepared          │
│ ⏳ Technical proposal...            │
│ ✅ Certifications gathered         │
│ ✅ Email draft created             │
│                                     │
│ [View Package] [Send Email]        │
└────────────────────────────────────┘
```

---

## 🔧 Backend Automation Features

### Auto-Trigger System

Add to `nexus_backend.py`:

```python
class CapabilityStatementAutomation:
    """Automatic capability statement generation"""
    
    def __init__(self):
        self.triggers_enabled = {
            'status_change': True,
            'email_assist': True,
            'weekly_batch': False,
            'smart_suggest': True
        }
    
    def on_opportunity_status_change(self, opp_id: str, new_status: str):
        """Auto-generate when status changes"""
        if not self.triggers_enabled['status_change']:
            return
        
        if new_status in ['Ready to Bid', 'Bidding']:
            self.auto_generate_if_needed(opp_id)
    
    def on_email_compose(self, email_data: dict):
        """Suggest capstat when composing RFP email"""
        if not self.triggers_enabled['email_assist']:
            return
        
        keywords = ['capability', 'qualifications', 'rfp response']
        
        if any(kw in email_data['body'].lower() for kw in keywords):
            return {
                'suggestion': 'attach_capstat',
                'message': 'Attach capability statement to this email?'
            }
    
    def weekly_batch_generation(self):
        """Run weekly to catch any missed opportunities"""
        if not self.triggers_enabled['weekly_batch']:
            return
        
        from auto_generate_capstats import get_qualified_opportunities, generate_for_opportunity
        
        opps = get_qualified_opportunities()
        
        for opp in opps:
            try:
                generate_for_opportunity(opp['id'])
            except Exception as e:
                print(f"Error generating for {opp['id']}: {e}")
    
    def smart_suggest_template(self, opportunity: dict) -> str:
        """Suggest best template based on opportunity"""
        if not self.triggers_enabled['smart_suggest']:
            return 'default'
        
        title = opportunity.get('Title', '').lower()
        description = opportunity.get('Description', '').lower()
        
        # Healthcare
        if any(kw in title or kw in description for kw in ['medical', 'healthcare', 'va', 'hospital']):
            return 'va_medical'
        
        # Construction
        if any(kw in title or kw in description for kw in ['construction', 'building', 'renovation']):
            return 'construction'
        
        return 'default'
```

---

## 📱 Mobile-Friendly Features

### Mobile Quick Generate

```
┌─────────────────────────────┐
│ ⚡ Quick Capstat             │
├─────────────────────────────┤
│                              │
│ Client: [____________]      │
│ RFQ:    [____________]      │
│                              │
│ Template: [Default ▼]       │
│                              │
│ [Generate]                   │
│                              │
└─────────────────────────────┘
```

---

## 🎯 RECOMMENDED FEATURES (Priority Order)

### Tier 1: Essential (Do First) ⭐⭐⭐

1. **Auto-Generate Button in Opportunities**
   - Simple button: "Generate Capability Statement"
   - Click → Files created → Success message

2. **Status Change Trigger**
   - When status → "Ready to Bid"
   - Auto-generate in background
   - Notify when ready

3. **Email Draft Creator**
   - Button: "Email RFP Response"
   - Pre-fills everything
   - Auto-attaches capstat PDF

4. **Quick View in NEXUS**
   - View HTML directly in NEXUS
   - No need to download
   - Professional preview

### Tier 2: Very Useful (Do Soon) ⭐⭐

5. **Template Selector**
   - Visual template picker
   - Preview before generating
   - Win rate stats for each

6. **Smart Suggestions**
   - Auto-select best template
   - Customize highlights based on RFQ
   - Pre-fill commitment statement

7. **Submission Package Builder**
   - One button creates everything
   - All files organized
   - Ready-to-send email

8. **Capability Statement Dashboard**
   - See all statements
   - Filter, search, analyze
   - Win/loss tracking

### Tier 3: Nice Enhancements (Do Later) ⭐

9. **Quick Edit Mode**
   - Make small tweaks without regenerating
   - Live preview
   - Save as new version

10. **Template Library**
    - Save custom templates
    - Share templates
    - Import/export

11. **Analytics Dashboard**
    - Win rate by template
    - Best performing highlights
    - Client preferences

12. **Version History**
    - See all versions
    - Compare changes
    - Revert if needed

---

## 💻 Code Snippets for Frontend Integration

### React Component: Generate Button

```tsx
// GenerateCapstatButton.tsx
import React, { useState } from 'react';

export const GenerateCapstatButton = ({ opportunityId }) => {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    
    const generate = async () => {
        setLoading(true);
        
        const response = await fetch('/capability-statements/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                opportunity_id: opportunityId,
                template: 'auto'
            })
        });
        
        const data = await response.json();
        setResult(data);
        setLoading(false);
    };
    
    if (result?.success) {
        return (
            <div className="success">
                <p>✅ Capability Statement Generated!</p>
                <button onClick={() => window.open(result.html_file)}>
                    View HTML
                </button>
                <button onClick={() => window.open(result.pdf_file)}>
                    Download PDF
                </button>
            </div>
        );
    }
    
    return (
        <button 
            onClick={generate} 
            disabled={loading}
            className="btn-primary"
        >
            {loading ? '⏳ Generating...' : '⚡ Generate Capability Statement'}
        </button>
    );
};
```

---

### React Component: Template Picker

```tsx
// TemplatePicker.tsx
const TEMPLATES = [
    { id: 'default', name: 'Industrial', color: '#d97706', icon: '🏭' },
    { id: 'va_medical', name: 'Healthcare', color: '#0066cc', icon: '🏥' },
    { id: 'construction', name: 'Construction', color: '#f97316', icon: '🏗️' }
];

export const TemplatePicker = ({ onSelect }) => {
    return (
        <div className="template-grid">
            {TEMPLATES.map(template => (
                <div 
                    key={template.id}
                    className="template-card"
                    onClick={() => onSelect(template.id)}
                >
                    <div className="icon">{template.icon}</div>
                    <h3>{template.name}</h3>
                    <div 
                        className="color-preview" 
                        style={{backgroundColor: template.color}}
                    />
                    <button>Use This Template</button>
                </div>
            ))}
        </div>
    );
};
```

---

## 🎯 MY TOP SUGGESTIONS FOR YOU

### 1. **Implement Auto-Generate on "Ready to Bid"** ⭐⭐⭐⭐⭐
**Why:** Saves you 1-2 hours per bid  
**How:** Airtable automation → webhook → NEXUS  
**Impact:** HIGH - Never manually create again

### 2. **One-Click Email with Auto-Attach** ⭐⭐⭐⭐⭐
**Why:** Never forget to attach capstat  
**How:** Button in NEXUS → Drafts email with PDF attached  
**Impact:** HIGH - Faster submissions, no mistakes

### 3. **Smart Template Selection** ⭐⭐⭐⭐
**Why:** Always use the right format  
**How:** Analyze RFQ keywords → Auto-select template  
**Impact:** MEDIUM-HIGH - Better first impressions

### 4. **RFP Submission Package Builder** ⭐⭐⭐⭐
**Why:** Complete package in one click  
**How:** Gather all docs → Organize → Ready to submit  
**Impact:** HIGH - Professional, organized submissions

### 5. **Past Performance Auto-Include** ⭐⭐⭐
**Why:** Shows experience automatically  
**How:** Match NAICS/category → Pull similar contracts  
**Impact:** MEDIUM - Stronger qualifications

### 6. **Win/Loss Tracking** ⭐⭐⭐
**Why:** Know what works  
**How:** Track results → Analyze → Improve  
**Impact:** MEDIUM - Data-driven improvements

### 7. **Version Control** ⭐⭐
**Why:** Track changes over time  
**How:** Save each version → Link together  
**Impact:** LOW-MEDIUM - Useful for revisions

### 8. **QR Code for Digital Access** ⭐⭐
**Why:** Modern, professional touch  
**How:** Generate QR → Links to online version  
**Impact:** LOW-MEDIUM - Nice differentiation

---

## 🚀 IMMEDIATE ACTION PLAN

### This Week (Must Do)

**Day 1-2: Airtable Setup**
1. Create CapabilityStatements table
2. Add fields from setup guide
3. Test manual record creation

**Day 3-4: Automation**
1. Create Airtable automation:
   - Trigger: Status → "Ready to Bid"
   - Action: Call webhook to generate
2. Test with one opportunity

**Day 5: Integration**
1. Add button to Opportunities table
2. Test manual generation
3. Verify files are created

**Weekend: Testing**
1. Generate for 2-3 active bids
2. Review quality
3. Make any tweaks needed

### Next Week (High Priority)

**Week 2: Email Integration**
1. Create email template function
2. Add auto-attach logic
3. Test sending RFP response

**Week 2: Package Builder**
1. Build submission package script
2. Test with complete RFP
3. Verify all files included

### This Month (Medium Priority)

**Week 3-4: Analytics**
1. Track which statements are used
2. Record win/loss results
3. Create simple dashboard

**Week 3-4: Templates**
1. Create 2-3 more templates
2. Test with different RFQ types
3. Document best practices

---

## 📊 Expected Results

### Month 1
- 10-20 capability statements generated
- 50% auto-generated, 50% manual
- 1-2 hours saved per week

### Month 2
- 20-30 statements generated
- 80% auto-generated, 20% manual
- 3-5 hours saved per week
- First wins attributed to professional capstats

### Month 3
- 30-50 statements generated
- 95% auto-generated, 5% manual
- 5-10 hours saved per week
- Clear data on what templates win

---

## 🎉 SUMMARY OF SUGGESTIONS

### Must Implement ✅
1. Auto-generate on status change
2. Email with auto-attach
3. Smart template selection
4. One-click RFP package

### Should Implement 📋
5. Past performance integration
6. Win/loss tracking
7. Template library
8. Quick edit feature

### Nice to Have 💡
9. QR codes
10. Multi-language
11. Social media versions
12. Competitor comparison

---

## 💼 Business Value

### Immediate Benefits
- **Save 1-2 hours per bid** - No manual creation
- **Never miss a capstat** - Auto-generated
- **Professional quality** - Consistent branding
- **Faster submissions** - Everything ready instantly

### Long-Term Benefits
- **Bid on more opportunities** - Time freed up
- **Higher win rates** - Professional presentation
- **Data-driven improvements** - Know what works
- **Scalable process** - Handle 10x volume

---

## 🚀 GET STARTED NOW

### Fastest Path to Value:

```bash
# 1. Test the system (already working!)
open default.html

# 2. Generate for your next RFP
python3 quick_capstat.py
# Follow prompts → Files generated!

# 3. Set up Airtable automation (30 minutes)
# See: AIRTABLE_CAPABILITY_STATEMENTS_SETUP.md

# 4. Add button to Opportunities (15 minutes)
# Button → Webhook → Generate

# 5. Done! Fully automated! 🎉
```

---

**You're ready to automate capability statement generation for every RFP response!** 🚀
