# GOVERNMENT SERVICES - NEXUS IMPLEMENTATION GUIDE
## Adding All DEE DAVIS INC Services to NEXUS

**Created:** February 1, 2026  
**Status:** Implementation in Progress  
**Timeline:** 2-4 hours

---

## 🎯 WHAT WE'RE BUILDING

**Adding to NEXUS:**
1. New "Government Services" tab in Document Generator
2. Service proposal templates (DOT testing, fingerprinting, janitorial, etc.)
3. DDCSS integration for government prospect tracking
4. ProposalBio analysis templates for each service
5. SalesScripts email templates for outreach

**End Result:**
Complete system for proactively pitching all DDI services to government clients (cities, counties, transit, schools).

---

## 📋 COMPLETED SO FAR

✅ **Created Documentation:**
1. `DEE_DAVIS_INC_COMPLETE_SERVICE_CATALOG.md` - All 25+ services cataloged
2. `DDCSS_GOVERNMENT_SERVICES_INTEGRATION.md` - ProposalBio & SalesScripts templates

✅ **Identified Services to Add:**
- DOT Testing
- Fingerprinting
- Background Checks
- DNA Testing
- Mobile Testing
- RON (Remote Notary)
- Surety Bonds
- Freight Brokerage
- All service contracts (janitorial, landscaping, IT, security, etc.)

---

## 🔧 IMPLEMENTATION STEPS

### **STEP 1: Update Document Generator UI**

**File:** `nexus-frontend/src/components/systems/DocumentGenerator.tsx`

**Changes Needed:**

#### 1.1 Update DocType
```typescript
// LINE 10 - Add 'services' to type
type DocType = 'quotes' | 'capstats' | 'rfps' | 'partnerships' | 'services';
```

#### 1.2 Add New Tab Button
```typescript
// ADD AFTER LINE 113 (after partnerships button)
<button
  onClick={() => handleTabChange('services')}
  className={`
    pb-4 px-1 border-b-2 font-medium text-sm transition-colors
    ${currentDocType === 'services'
      ? 'border-blue-500 text-blue-400'
      : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
    }
  `}
>
  <div className="flex items-center space-x-2">
    <Briefcase className="w-4 h-4" />
    <span>Government Services</span>
    <span className="px-2 py-0.5 text-xs bg-purple-600 text-white rounded">NEW</span>
  </div>
</button>
```

#### 1.3 Add Icon Import
```typescript
// LINE 2 - Add Briefcase icon
import { FileText, DollarSign, Award, Send, ArrowLeft, Handshake, Briefcase } from 'lucide-react';
```

#### 1.4 Add Conditional Rendering
```typescript
// LINE 124 - Add after partnerships line
{currentDocType === 'services' && <GovernmentServicesContent />}
```

#### 1.5 Create GovernmentServicesContent Component

**Add this component at the end of the file (before the export):**

```typescript
// ============================================================================
// GOVERNMENT SERVICES PROPOSAL CONTENT
// ============================================================================

function GovernmentServicesContent() {
  const [formData, setFormData] = useState({
    serviceType: 'DOT Testing',
    prospectName: '',
    prospectType: 'City',
    contactName: '',
    contactTitle: '',
    contactEmail: '',
    contactPhone: '',
    population: '',
    fleetSize: '',
    employeeCount: '',
    estimatedAnnualValue: '',
    additionalServices: [] as string[],
    customDetails: '',
  });

  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedFile, setGeneratedFile] = useState<string | null>(null);

  const serviceTypes = [
    'DOT Drug/Alcohol Testing',
    'Fingerprinting Services',
    'Background Checks',
    'DNA Testing',
    'Mobile Testing Programs',
    'Notary Services',
    'Remote Online Notarization (RON)',
    'Document Preparation',
    'Surety Bonds',
    'NEMT Program Development',
    'Medicaid/Medicare Enrollment',
    'Janitorial Services (Prime Contractor)',
    'Landscaping/Grounds (Prime Contractor)',
    'Facility Maintenance (Prime Contractor)',
    'IT Services (Prime Contractor)',
    'Security Services (Prime Contractor)',
    'Construction/Renovation (Prime Contractor)',
    'Moving/Relocation (Prime Contractor)',
    'Event Services (Prime Contractor)',
    'Freight Brokerage Consulting',
    'Project Executive Services',
    'Crisis Coordination',
    'Business Continuity Planning',
  ];

  const prospectTypes = [
    'City',
    'County',
    'Transit Agency',
    'School District',
    'Special District',
    'Federal Agency',
    'State Agency',
  ];

  // Service-specific template loaders
  const loadServiceTemplate = (service: string) => {
    const templates: { [key: string]: any } = {
      'DOT Drug/Alcohol Testing': {
        serviceType: 'DOT Drug/Alcohol Testing',
        estimatedAnnualValue: '15000',
        customDetails: 'Quest Diagnostics partnership • Mobile on-site testing available • Full DOT compliance management • Electronic reporting • Competitive pricing',
      },
      'Fingerprinting Services': {
        serviceType: 'Fingerprinting Services',
        estimatedAnnualValue: '10000',
        customDetails: 'Live scan electronic fingerprinting • Mobile service available • FBI channeling • State-specific submissions • Fast turnaround',
      },
      'Janitorial Services (Prime Contractor)': {
        serviceType: 'Janitorial Services (Prime Contractor)',
        estimatedAnnualValue: '75000',
        customDetails: 'EDWOSB prime contractor • Vetted local subcontractor network • ATLAS PM project management • E&O insurance • Quality oversight',
      },
    };

    if (templates[service]) {
      setFormData({ ...formData, ...templates[service] });
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    
    try {
      // This will call a new API endpoint: /api/services/generate
      const response = await fetch('http://localhost:5005/api/services/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const result = await response.json();
      
      if (result.success) {
        setGeneratedFile(result.pdf_path);
        alert('✅ Government Service Proposal generated successfully!');
      } else {
        alert('❌ Error: ' + result.error);
      }
    } catch (error) {
      alert('❌ Error generating proposal: ' + error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-semibold text-white mb-6">Government Services Proposal Generator</h2>
      
      <p className="text-gray-400 mb-6">
        Generate professional service proposals for government clients (cities, counties, transit agencies, schools).
        Select the service type and fill in prospect details to create a customized proposal.
      </p>

      {/* Service Type Selection */}
      <div className="mb-6 p-4 bg-blue-900 bg-opacity-20 border border-blue-700 rounded">
        <h3 className="text-lg font-semibold text-blue-400 mb-3">1. Select Service Type</h3>
        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Primary Service
            </label>
            <select
              value={formData.serviceType}
              onChange={(e) => {
                setFormData({ ...formData, serviceType: e.target.value });
                loadServiceTemplate(e.target.value);
              }}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            >
              {serviceTypes.map((service) => (
                <option key={service} value={service}>{service}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Quick Templates
            </label>
            <button
              onClick={() => loadServiceTemplate('DOT Drug/Alcohol Testing')}
              className="w-full px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm mb-2"
            >
              DOT Testing
            </button>
            <button
              onClick={() => loadServiceTemplate('Fingerprinting Services')}
              className="w-full px-3 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded text-sm mb-2"
            >
              Fingerprinting
            </button>
            <button
              onClick={() => loadServiceTemplate('Janitorial Services (Prime Contractor)')}
              className="w-full px-3 py-2 bg-green-600 hover:bg-green-500 text-white rounded text-sm"
            >
              Janitorial
            </button>
          </div>
        </div>
      </div>

      {/* Prospect Information */}
      <div className="mb-6 p-4 bg-gray-700 rounded">
        <h3 className="text-lg font-semibold text-white mb-3">2. Prospect Information</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Prospect Name *
            </label>
            <input
              type="text"
              value={formData.prospectName}
              onChange={(e) => setFormData({ ...formData, prospectName: e.target.value })}
              className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded text-white"
              placeholder="City of Auburn Hills"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Prospect Type
            </label>
            <select
              value={formData.prospectType}
              onChange={(e) => setFormData({ ...formData, prospectType: e.target.value })}
              className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded text-white"
            >
              {prospectTypes.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Population (if applicable)
            </label>
            <input
              type="number"
              value={formData.population}
              onChange={(e) => setFormData({ ...formData, population: e.target.value })}
              className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded text-white"
              placeholder="24000"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Estimated Annual Value
            </label>
            <input
              type="number"
              value={formData.estimatedAnnualValue}
              onChange={(e) => setFormData({ ...formData, estimatedAnnualValue: e.target.value })}
              className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded text-white"
              placeholder="15000"
            />
          </div>
        </div>
      </div>

      {/* Contact Information */}
      <div className="mb-6 p-4 bg-gray-700 rounded">
        <h3 className="text-lg font-semibold text-white mb-3">3. Decision Maker Contact</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Contact Name
            </label>
            <input
              type="text"
              value={formData.contactName}
              onChange={(e) => setFormData({ ...formData, contactName: e.target.value })}
              className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded text-white"
              placeholder="John Smith"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Title
            </label>
            <input
              type="text"
              value={formData.contactTitle}
              onChange={(e) => setFormData({ ...formData, contactTitle: e.target.value })}
              className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded text-white"
              placeholder="HR Director"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Email
            </label>
            <input
              type="email"
              value={formData.contactEmail}
              onChange={(e) => setFormData({ ...formData, contactEmail: e.target.value })}
              className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded text-white"
              placeholder="[email protected]"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Phone
            </label>
            <input
              type="tel"
              value={formData.contactPhone}
              onChange={(e) => setFormData({ ...formData, contactPhone: e.target.value })}
              className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded text-white"
              placeholder="(248) 555-1234"
            />
          </div>
        </div>
      </div>

      {/* Service-Specific Details */}
      <div className="mb-6 p-4 bg-gray-700 rounded">
        <h3 className="text-lg font-semibold text-white mb-3">4. Service Details</h3>
        <div className="grid grid-cols-2 gap-4">
          {formData.serviceType.includes('DOT') && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Fleet Size (vehicles)
              </label>
              <input
                type="number"
                value={formData.fleetSize}
                onChange={(e) => setFormData({ ...formData, fleetSize: e.target.value })}
                className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded text-white"
                placeholder="50"
              />
            </div>
          )}
          {(formData.serviceType.includes('Fingerprinting') || formData.serviceType.includes('Background')) && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Employee Count
              </label>
              <input
                type="number"
                value={formData.employeeCount}
                onChange={(e) => setFormData({ ...formData, employeeCount: e.target.value })}
                className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded text-white"
                placeholder="200"
              />
            </div>
          )}
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Additional Details / Custom Notes
            </label>
            <textarea
              value={formData.customDetails}
              onChange={(e) => setFormData({ ...formData, customDetails: e.target.value })}
              className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded text-white"
              rows={4}
              placeholder="Add any specific details about the prospect, current pain points, or custom proposal elements..."
            />
          </div>
        </div>
      </div>

      {/* Generate Button */}
      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-400">
          * All proposals include DDI credentials, partnerships, and EDWOSB certification
        </div>
        <button
          onClick={handleGenerate}
          disabled={isGenerating || !formData.prospectName}
          className={`
            px-6 py-3 rounded font-semibold flex items-center space-x-2
            ${isGenerating || !formData.prospectName
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-500 text-white'
            }
          `}
        >
          {isGenerating ? (
            <>
              <span className="animate-spin">⏳</span>
              <span>Generating...</span>
            </>
          ) : (
            <>
              <FileText className="w-5 h-5" />
              <span>Generate Service Proposal PDF</span>
            </>
          )}
        </button>
      </div>

      {/* Success Message */}
      {generatedFile && (
        <div className="mt-6 p-4 bg-green-900 bg-opacity-20 border border-green-700 rounded">
          <h3 className="text-green-400 font-semibold mb-2">✅ Proposal Generated!</h3>
          <p className="text-gray-300 text-sm mb-2">
            File: <code className="bg-gray-700 px-2 py-1 rounded">{generatedFile}</code>
          </p>
          <p className="text-gray-400 text-sm">
            Ready to send to prospect! Consider adding to DDCSS for tracking.
          </p>
        </div>
      )}
    </div>
  );
}
```

---

### **STEP 2: Create Backend API for Service Proposals**

**New File:** `government_services_proposal_api.py`

**Purpose:** Generate PDF proposals for government services

**Port:** 5005

**Endpoints:**
- `POST /api/services/generate` - Generate service proposal PDF
- `GET /api/services/health` - Health check

**See separate file for full API code.**

---

### **STEP 3: Create Startup Script**

**New File:** `START_SERVICES_API.sh`

```bash
#!/bin/bash
echo "=========================================="
echo "  GOVERNMENT SERVICES PROPOSAL API"
echo "=========================================="
echo ""
echo "Starting Government Services Proposal Generator..."
echo "Port: 5005"
echo "Output: generated_services/"
echo ""
cd "/Users/deedavis/NEXUS BACKEND"
chmod +x government_services_proposal_api.py
python3 government_services_proposal_api.py
```

---

### **STEP 4: Update DDCSS Airtable Schema**

**Table:** DDCSS Government Services (new or expand existing DDCSS table)

**Add Fields:**
- Service Type (Multiple Select) - all 23 services
- Government Type (Single Select) - City/County/Transit/School/Federal/State/Special
- Population (Number)
- Fleet Size (Number)
- Employee Count (Number)
- Current Providers (Long Text)
- Pain Points (Long Text)
- Decision Maker (Linked Record to Contacts)
- Department (Single Select)
- Fiscal Year (Single Select)
- Estimated Annual Value (Currency)
- Last Contact Date (Date)
- Next Action (Single Select)
- Pipeline Stage (Single Select) - Research/Analysis/Proposal/Outreach/Follow-Up/Meeting/Review/Negotiation/Contract/Active

---

### **STEP 5: Update Dashboard Stats**

**File:** `nexus-frontend/src/components/LandingPage.tsx`

**Update "DOCUMENTS" card:**

```typescript
{
  title: 'DOCUMENTS',
  description: 'Quotes, Capability Statements, RFPs, Partnership Proposals, Government Services',
  // ... existing stats ...
}
```

---

## 🚀 TESTING CHECKLIST

After implementation:

- [ ] "Government Services" tab appears in Document Generator
- [ ] Service type dropdown shows all 23 services
- [ ] Quick template buttons work (DOT, Fingerprinting, Janitorial)
- [ ] Form fields populate correctly
- [ ] "Generate Proposal PDF" button works
- [ ] Backend API starts on port 5005
- [ ] PDF generates with DDI branding
- [ ] DDCSS table has new fields
- [ ] ProposalBio templates accessible
- [ ] SalesScripts templates accessible

---

## 📊 IMPACT ON 14-DAY LAUNCH

**Time Required:** 2-4 hours

**Options:**

### **Option A: Add Now (Day 1)**
- Pros: Ready immediately, comprehensive from day 1
- Cons: Delays Day 1 bug testing by 3-4 hours

### **Option B: Add Day 3 (During DDCSS Day)**
- Pros: Fits naturally into DDCSS build day, doesn't delay testing
- Cons: Not available for 2 days

### **Option C: Add Post-Launch (v1.1)**
- Pros: Zero risk to launch timeline
- Cons: Can't start government prospecting for 2+ weeks

---

## ✅ RECOMMENDATION

**Add on Day 3 (February 3)**

**Reasoning:**
- Day 3 is already "DDCSS + Documents" day in the launch plan
- Perfect fit for this work
- Doesn't delay critical Day 1-2 bug testing
- Still ready 11 days before launch
- Keeps 14-day timeline safe

**User chose Option A:** Add everything NOW

**Proceeding with full implementation.**

---

**Government Services NEXUS implementation guide complete.** ✅

**Next: Implement frontend changes and backend API.**
