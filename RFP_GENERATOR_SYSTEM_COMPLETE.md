# NEXUS RFP GENERATOR SYSTEM
**Automated Supplier RFP Creation with Buyer Protection**

**Created:** January 30, 2026  
**Purpose:** Auto-generate professional, branded supplier RFPs from buyer RFQs  
**Model:** Similar to Quote Generator & Capability Statement Generator

---

## 🎯 SYSTEM OVERVIEW

**What It Does:**
1. You upload/paste buyer's RFP/RFQ
2. System extracts key information
3. You select what to sanitize (buyer identity protection)
4. System generates professional DDI-branded RFP with watermark
5. System creates PDF ready to send to suppliers
6. Tracks RFPs sent and quotes received

**Just like:**
- ✅ Quote Generator (automated quote creation)
- ✅ Capability Statement Generator (automated document assembly)
- ✅ But for creating SUPPLIER-FACING RFPs

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                   NEXUS FRONTEND                            │
│              (React/TypeScript Interface)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📄 RFP Generator Page                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ CREATE NEW SUPPLIER RFP                             │   │
│  │                                                     │   │
│  │ [Upload Buyer RFP PDF] or [Paste Text]            │   │
│  │                                                     │   │
│  │ ↓ AI extracts information ↓                        │   │
│  │                                                     │   │
│  │ Form appears with extracted data:                  │   │
│  │ • Project Name                                     │   │
│  │ • Services/Products Needed                         │   │
│  │ • Specifications                                   │   │
│  │ • Location (SANITIZED)                            │   │
│  │ • Timeline                                         │   │
│  │ • Insurance Requirements                           │   │
│  │                                                     │   │
│  │ Review & Edit: ✏️                                  │   │
│  │ [Generate DDI RFP] → Creates PDF with watermark   │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  📊 RFP Tracking Dashboard                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ DDI-2026-PW-001 | Pressure Washing | Sent to 5    │   │
│  │ DDI-2026-PL-002 | Padlocks | Sent to 8            │   │
│  │ DDI-2026-LS-003 | Landscaping | Draft              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                        ↓ API Calls ↓
┌─────────────────────────────────────────────────────────────┐
│                  NEXUS BACKEND API                          │
│               (Python/FastAPI or Flask)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  POST /api/rfp/parse                                        │
│  • Parse uploaded buyer RFP (PDF or text)                   │
│  • Extract key information using AI/NLP                     │
│  • Return structured data                                   │
│                                                             │
│  POST /api/rfp/generate                                     │
│  • Take sanitized data                                      │
│  • Apply DDI RFP template                                   │
│  • Generate PDF with watermark                              │
│  • Save to database                                         │
│  • Return download link                                     │
│                                                             │
│  GET /api/rfp/list                                          │
│  • List all RFPs created                                    │
│  • Track status (draft, sent, closed)                       │
│                                                             │
│  POST /api/rfp/publish                                      │
│  • Publish RFP to vendor portal (if enabled)                │
│  • Send email notifications to matching vendors             │
│                                                             │
│  POST /api/rfp/quote-received                               │
│  • Log quote received from vendor                           │
│  • Track and compare quotes                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                        ↓ Stores In ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE (Airtable or PostgreSQL)        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  BUYER_RFPS Table (Original buyer RFPs)                     │
│  SUPPLIER_RFPS Table (Generated DDI RFPs)                   │
│  VENDOR_QUOTES Table (Quotes received)                      │
│  RFP_TEMPLATES Table (Reusable templates)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                        ↓ Generates ↓
┌─────────────────────────────────────────────────────────────┐
│                     PDF OUTPUT                              │
│          (DDI-branded RFP with watermark)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  • Professional formatting                                  │
│  • DEE DAVIS INC watermark on every page                    │
│  • Header/footer with CAGE, DUNS, contact info             │
│  • Buyer identity sanitized                                 │
│  • Ready to email to suppliers                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 DATABASE SCHEMA

### **Table 1: buyer_rfps** (Original Buyer RFPs)
```sql
CREATE TABLE buyer_rfps (
    id INT PRIMARY KEY AUTO_INCREMENT,
    buyer_rfp_number VARCHAR(100),           -- Original buyer RFP # (e.g., "RFQ-01-30-2026-001")
    buyer_name VARCHAR(255),                 -- CONFIDENTIAL (e.g., "City of Auburn Hills")
    project_name VARCHAR(255),               -- Original project name
    uploaded_file_path VARCHAR(500),         -- Path to original PDF
    raw_text TEXT,                           -- Extracted text from PDF
    project_type VARCHAR(100),               -- "Services", "Products", "Construction", etc.
    due_date DATETIME,                       -- Buyer's due date
    estimated_value DECIMAL(10,2),           -- Contract value
    specifications TEXT,                     -- Full specifications
    location VARCHAR(255),                   -- Specific location (CONFIDENTIAL)
    insurance_requirements TEXT,             -- Insurance required by buyer
    special_requirements TEXT,               -- Any special terms
    status ENUM('active', 'quoted', 'awarded', 'lost') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);
```

### **Table 2: supplier_rfps** (Generated DDI RFPs)
```sql
CREATE TABLE supplier_rfps (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ddi_rfp_number VARCHAR(50) UNIQUE,       -- Generated DDI RFP # (e.g., "DDI-2026-PW-001")
    buyer_rfp_id INT,                        -- Links to buyer_rfps table
    project_name VARCHAR(255),               -- Sanitized project name
    category VARCHAR(100),                   -- "Pressure Washing", "Landscaping", etc.
    sanitized_location VARCHAR(255),         -- Generic location (e.g., "Oakland County, MI")
    scope_of_work TEXT,                      -- Sanitized specifications
    service_locations_count INT,             -- Number of locations (if applicable)
    contract_value_min DECIMAL(10,2),        -- Estimated value range
    contract_value_max DECIMAL(10,2),
    contract_period VARCHAR(100),            -- "March 2026 - December 2026"
    quote_due_date DATETIME,                 -- When quotes due to DDI
    insurance_requirements TEXT,             -- Insurance DDI requires from sub
    pdf_generated_path VARCHAR(500),         -- Path to generated PDF
    status ENUM('draft', 'ready', 'sent', 'quotes_received', 'closed') DEFAULT 'draft',
    sent_date DATETIME,                      -- When sent to suppliers
    num_vendors_contacted INT DEFAULT 0,     -- How many vendors sent to
    num_quotes_received INT DEFAULT 0,       -- How many quotes received
    published_to_portal BOOLEAN DEFAULT FALSE, -- Published to vendor portal?
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_rfp_id) REFERENCES buyer_rfps(id)
);
```

### **Table 3: vendor_quotes_received** (Quotes from Vendors)
```sql
CREATE TABLE vendor_quotes_received (
    id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_rfp_id INT,                     -- Links to supplier_rfps table
    vendor_name VARCHAR(255),                -- Vendor/subcontractor name
    vendor_email VARCHAR(255),
    vendor_phone VARCHAR(50),
    quote_amount DECIMAL(10,2),              -- Total quoted amount
    quote_breakdown TEXT,                    -- Detailed pricing
    quote_notes TEXT,                        -- Vendor's notes/proposal
    attachments JSON,                        -- Paths to uploaded docs
    received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('received', 'under_review', 'selected', 'declined') DEFAULT 'received',
    rating INT,                              -- 1-5 star rating
    selected BOOLEAN DEFAULT FALSE,          -- Winner?
    FOREIGN KEY (supplier_rfp_id) REFERENCES supplier_rfps(id)
);
```

### **Table 4: rfp_templates** (Reusable Templates)
```sql
CREATE TABLE rfp_templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    template_name VARCHAR(255),              -- "Standard Services RFP", "Products RFP", etc.
    category VARCHAR(100),                   -- "Services", "Products", "Construction"
    template_content TEXT,                   -- HTML/Markdown template
    sections JSON,                           -- Array of section names
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### **Table 5: rfp_sections_library** (Reusable Content Blocks)
```sql
CREATE TABLE rfp_sections_library (
    id INT PRIMARY KEY AUTO_INCREMENT,
    section_name VARCHAR(255),               -- "Insurance Requirements", "Confidentiality Clause", etc.
    section_type VARCHAR(100),               -- "terms", "insurance", "evaluation", etc.
    content TEXT,                            -- Actual content
    category VARCHAR(100),                   -- Which types of RFPs this applies to
    is_required BOOLEAN DEFAULT FALSE,       -- Always include?
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🖥️ FRONTEND INTERFACE

### **PAGE 1: RFP Generator Form**

```typescript
// Location: nexus-frontend/src/components/RFPGenerator.tsx

import React, { useState } from 'react';
import { Upload, FileText, Download, Send, Eye } from 'lucide-react';

export default function RFPGenerator() {
  const [step, setStep] = useState<'upload' | 'edit' | 'preview' | 'complete'>('upload');
  const [buyerRfpFile, setBuyerRfpFile] = useState<File | null>(null);
  const [extractedData, setExtractedData] = useState<any>(null);
  const [rfpData, setRfpData] = useState({
    projectName: '',
    category: '',
    location: '',
    sanitizedLocation: '',
    scopeOfWork: '',
    estimatedValue: { min: 0, max: 0 },
    quoteDueDate: '',
    insuranceRequirements: '',
    serviceLocations: 0,
  });

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* HEADER */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">RFP Generator</h1>
        <p className="text-gray-600 mt-2">
          Create professional, branded supplier RFPs with buyer identity protection
        </p>
      </div>

      {/* PROGRESS STEPS */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <Step number={1} label="Upload Buyer RFP" active={step === 'upload'} />
          <div className="flex-1 h-0.5 bg-gray-300 mx-4" />
          <Step number={2} label="Edit & Sanitize" active={step === 'edit'} />
          <div className="flex-1 h-0.5 bg-gray-300 mx-4" />
          <Step number={3} label="Preview RFP" active={step === 'preview'} />
          <div className="flex-1 h-0.5 bg-gray-300 mx-4" />
          <Step number={4} label="Generate PDF" active={step === 'complete'} />
        </div>
      </div>

      {/* STEP 1: UPLOAD BUYER RFP */}
      {step === 'upload' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Upload Buyer's RFP/RFQ</h2>
          
          {/* FILE UPLOAD */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-600 mb-4">
              Drop PDF file here or click to upload
            </p>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  setBuyerRfpFile(file);
                  // Parse file
                  handleParseRFP(file);
                }
              }}
              className="hidden"
              id="rfp-upload"
            />
            <label
              htmlFor="rfp-upload"
              className="btn-primary cursor-pointer inline-block"
            >
              Choose File
            </label>
          </div>

          <div className="my-6 text-center text-gray-500">OR</div>

          {/* PASTE TEXT */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Paste RFP Text
            </label>
            <textarea
              rows={10}
              className="w-full border border-gray-300 rounded-lg p-3"
              placeholder="Paste the RFP/RFQ text here..."
              onChange={(e) => {
                if (e.target.value) {
                  handleParseText(e.target.value);
                }
              }}
            />
          </div>

          {/* MANUAL ENTRY */}
          <div className="mt-6">
            <button
              onClick={() => setStep('edit')}
              className="text-blue-600 hover:underline"
            >
              Or enter information manually →
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: EDIT & SANITIZE */}
      {step === 'edit' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Edit & Sanitize RFP Information</h2>
          
          <div className="space-y-6">
            {/* BUYER INFORMATION (Confidential) */}
            <div className="border-l-4 border-red-500 pl-4 bg-red-50 p-4">
              <h3 className="font-semibold text-red-900 mb-2">
                🔒 CONFIDENTIAL - Buyer Information (NOT shared with suppliers)
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Buyer Name
                  </label>
                  <input
                    type="text"
                    className="w-full border border-gray-300 rounded-lg p-2"
                    placeholder="City of Auburn Hills"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Buyer's RFP Number
                  </label>
                  <input
                    type="text"
                    className="w-full border border-gray-300 rounded-lg p-2"
                    placeholder="RFQ-01-30-2026-001"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Specific Location
                  </label>
                  <input
                    type="text"
                    className="w-full border border-gray-300 rounded-lg p-2"
                    placeholder="Auburn Hills, Michigan"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Buyer Due Date
                  </label>
                  <input
                    type="date"
                    className="w-full border border-gray-300 rounded-lg p-2"
                  />
                </div>
              </div>
            </div>

            {/* SUPPLIER-FACING INFORMATION (Sanitized) */}
            <div className="border-l-4 border-green-500 pl-4 bg-green-50 p-4">
              <h3 className="font-semibold text-green-900 mb-2">
                ✅ PUBLIC - Information Shared with Suppliers
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    DDI RFP Number (Auto-generated)
                  </label>
                  <input
                    type="text"
                    className="w-full border border-gray-300 rounded-lg p-2 bg-gray-100"
                    value="DDI-2026-PW-001"
                    readOnly
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Project Name (Generic)
                  </label>
                  <input
                    type="text"
                    className="w-full border border-gray-300 rounded-lg p-2"
                    placeholder="Municipal Parks Pressure Washing Services"
                    value={rfpData.projectName}
                    onChange={(e) => setRfpData({...rfpData, projectName: e.target.value})}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <select className="w-full border border-gray-300 rounded-lg p-2">
                    <option>Pressure Washing</option>
                    <option>Landscaping</option>
                    <option>Janitorial</option>
                    <option>Construction</option>
                    <option>Supplies</option>
                    <option>HVAC</option>
                    <option>Plumbing</option>
                    <option>Electrical</option>
                    <option>Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Location (Sanitized)
                  </label>
                  <input
                    type="text"
                    className="w-full border border-gray-300 rounded-lg p-2"
                    placeholder="Oakland County, Michigan"
                    value={rfpData.sanitizedLocation}
                    onChange={(e) => setRfpData({...rfpData, sanitizedLocation: e.target.value})}
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    Use general area only (county/region, not specific city)
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Scope of Work
                  </label>
                  <textarea
                    rows={6}
                    className="w-full border border-gray-300 rounded-lg p-2"
                    placeholder="Hot water pressure washing services for park structures, playground equipment, picnic shelters..."
                    value={rfpData.scopeOfWork}
                    onChange={(e) => setRfpData({...rfpData, scopeOfWork: e.target.value})}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Estimated Value (Min)
                    </label>
                    <input
                      type="number"
                      className="w-full border border-gray-300 rounded-lg p-2"
                      placeholder="8000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Estimated Value (Max)
                    </label>
                    <input
                      type="number"
                      className="w-full border border-gray-300 rounded-lg p-2"
                      placeholder="15000"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Quote Due Date (to DEE DAVIS INC)
                  </label>
                  <input
                    type="date"
                    className="w-full border border-gray-300 rounded-lg p-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Insurance Requirements
                  </label>
                  <textarea
                    rows={4}
                    className="w-full border border-gray-300 rounded-lg p-2"
                    placeholder="General Liability: $1,000,000..."
                  />
                </div>
              </div>
            </div>

            {/* TEMPLATE SELECTION */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                RFP Template
              </label>
              <select className="w-full border border-gray-300 rounded-lg p-2">
                <option>Standard Services RFP (Comprehensive)</option>
                <option>Quick Services RFP (Simplified)</option>
                <option>Products/Supplies RFP</option>
                <option>Construction RFP</option>
              </select>
            </div>

            {/* ACTION BUTTONS */}
            <div className="flex justify-between pt-4">
              <button
                onClick={() => setStep('upload')}
                className="btn-secondary"
              >
                ← Back
              </button>
              <button
                onClick={() => setStep('preview')}
                className="btn-primary"
              >
                Preview RFP →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* STEP 3: PREVIEW */}
      {step === 'preview' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Preview Supplier RFP</h2>
          
          <div className="border border-gray-300 rounded-lg p-6 bg-gray-50">
            {/* PDF Preview */}
            <div className="bg-white p-8 shadow-inner">
              <div className="text-center mb-6">
                <h1 className="text-2xl font-bold">DEE DAVIS INC</h1>
                <p className="text-gray-600">Certified EDWOSB Prime Contractor</p>
              </div>
              
              <div className="border-t-4 border-blue-600 pt-6 mt-6">
                <h2 className="text-xl font-bold text-center mb-2">
                  REQUEST FOR PROPOSAL
                </h2>
                <h3 className="text-lg text-center mb-4">
                  {rfpData.projectName}
                </h3>
                <div className="text-center text-sm space-y-1">
                  <p>RFP Number: DDI-2026-PW-001</p>
                  <p>Issue Date: January 31, 2026</p>
                  <p>Proposals Due: February 10, 2026 at 5:00 PM EST</p>
                </div>
              </div>

              <div className="mt-8 space-y-4 text-sm">
                <div>
                  <h4 className="font-semibold">Project Overview</h4>
                  <p className="text-gray-700">{rfpData.scopeOfWork}</p>
                </div>
                <div>
                  <h4 className="font-semibold">Location</h4>
                  <p className="text-gray-700">{rfpData.sanitizedLocation}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 flex justify-between">
            <button
              onClick={() => setStep('edit')}
              className="btn-secondary"
            >
              ← Edit
            </button>
            <div className="space-x-3">
              <button className="btn-secondary">
                <Eye className="w-4 h-4 inline mr-2" />
                View Full Preview
              </button>
              <button
                onClick={handleGeneratePDF}
                className="btn-primary"
              >
                <Download className="w-4 h-4 inline mr-2" />
                Generate PDF
              </button>
            </div>
          </div>
        </div>
      )}

      {/* STEP 4: COMPLETE */}
      {step === 'complete' && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              RFP Generated Successfully!
            </h2>
            <p className="text-gray-600 mb-6">
              DDI-2026-PW-001 - Municipal Parks Pressure Washing Services
            </p>

            <div className="space-x-4">
              <button className="btn-primary">
                <Download className="w-4 h-4 inline mr-2" />
                Download PDF
              </button>
              <button className="btn-secondary">
                <Send className="w-4 h-4 inline mr-2" />
                Email to Vendors
              </button>
              <button className="btn-secondary">
                Publish to Vendor Portal
              </button>
            </div>

            <div className="mt-8 border-t pt-6">
              <button
                onClick={() => setStep('upload')}
                className="text-blue-600 hover:underline"
              >
                Create Another RFP
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper component for progress steps
function Step({ number, label, active }: { number: number; label: string; active: boolean }) {
  return (
    <div className="flex items-center">
      <div className={`
        w-10 h-10 rounded-full flex items-center justify-center font-semibold
        ${active ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'}
      `}>
        {number}
      </div>
      <span className="ml-2 text-sm font-medium text-gray-700">{label}</span>
    </div>
  );
}
```

### **PAGE 2: RFP Tracking Dashboard**

```typescript
// Location: nexus-frontend/src/components/RFPDashboard.tsx

import React from 'react';
import { FileText, Send, CheckCircle, Clock } from 'lucide-react';

export default function RFPDashboard() {
  const rfps = [
    {
      id: 1,
      ddiNumber: 'DDI-2026-PW-001',
      projectName: 'Municipal Parks Pressure Washing',
      category: 'Pressure Washing',
      status: 'sent',
      vendorsSent: 5,
      quotesReceived: 2,
      quoteDueDate: '2026-02-10',
      createdDate: '2026-01-30',
    },
    {
      id: 2,
      ddiNumber: 'DDI-2026-PL-002',
      projectName: 'Industrial Padlocks - Texas Utility',
      category: 'Supplies',
      status: 'quotes_received',
      vendorsSent: 8,
      quotesReceived: 5,
      quoteDueDate: '2026-02-06',
      createdDate: '2026-01-28',
    },
    {
      id: 3,
      ddiNumber: 'DDI-2026-LS-003',
      projectName: 'Landscaping Materials - Metro Detroit',
      category: 'Landscaping',
      status: 'draft',
      vendorsSent: 0,
      quotesReceived: 0,
      quoteDueDate: '2026-02-10',
      createdDate: '2026-01-30',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">RFP Dashboard</h1>
        <button className="btn-primary">
          <FileText className="w-4 h-4 inline mr-2" />
          Create New RFP
        </button>
      </div>

      {/* STATS */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Total RFPs"
          value="12"
          icon={<FileText className="w-6 h-6" />}
          color="blue"
        />
        <StatCard
          label="Sent to Vendors"
          value="8"
          icon={<Send className="w-6 h-6" />}
          color="purple"
        />
        <StatCard
          label="Quotes Received"
          value="23"
          icon={<CheckCircle className="w-6 h-6" />}
          color="green"
        />
        <StatCard
          label="Awaiting Quotes"
          value="5"
          icon={<Clock className="w-6 h-6" />}
          color="yellow"
        />
      </div>

      {/* RFP TABLE */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                RFP Number
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Project
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Category
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Vendors/Quotes
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Due Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {rfps.map((rfp) => (
              <tr key={rfp.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{rfp.ddiNumber}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900">{rfp.projectName}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                    {rfp.category}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusBadge status={rfp.status} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {rfp.vendorsSent} sent / {rfp.quotesReceived} received
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {rfp.quoteDueDate}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <button className="text-blue-600 hover:underline mr-3">View</button>
                  <button className="text-blue-600 hover:underline mr-3">Download</button>
                  <button className="text-blue-600 hover:underline">Quotes</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, color }: any) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    purple: 'bg-purple-100 text-purple-600',
    green: 'bg-green-100 text-green-600',
    yellow: 'bg-yellow-100 text-yellow-600',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
        <div className="ml-4">
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-600">{label}</p>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const statusConfig = {
    draft: { label: 'Draft', color: 'bg-gray-100 text-gray-800' },
    ready: { label: 'Ready', color: 'bg-blue-100 text-blue-800' },
    sent: { label: 'Sent', color: 'bg-purple-100 text-purple-800' },
    quotes_received: { label: 'Quotes Received', color: 'bg-green-100 text-green-800' },
    closed: { label: 'Closed', color: 'bg-gray-100 text-gray-800' },
  };

  const config = statusConfig[status] || statusConfig.draft;

  return (
    <span className={`px-2 py-1 text-xs rounded-full ${config.color}`}>
      {config.label}
    </span>
  );
}
```

---

## 🐍 BACKEND API

### **File: `rfp_generator_api.py`**

```python
#!/usr/bin/env python3
"""
RFP Generator API
Handles RFP creation, parsing, PDF generation, and tracking
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime
from pyairtable import Api
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
import PyPDF2
import openai

app = Flask(__name__)
CORS(app)

# Configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = os.getenv('AIRTABLE_BASE_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize APIs
airtable_api = Api(AIRTABLE_API_KEY)
openai.api_key = OPENAI_API_KEY

# ============================================================================
# ENDPOINT 1: Parse Buyer RFP (Extract Information)
# ============================================================================

@app.route('/api/rfp/parse', methods=['POST'])
def parse_buyer_rfp():
    """
    Parse uploaded buyer RFP and extract key information using AI
    """
    try:
        # Get file or text
        if 'file' in request.files:
            file = request.files['file']
            text = extract_text_from_pdf(file)
        else:
            text = request.json.get('text', '')

        # Use OpenAI to extract structured information
        extracted_data = extract_rfp_data_with_ai(text)

        return jsonify({
            'success': True,
            'data': extracted_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text


def extract_rfp_data_with_ai(text):
    """Use OpenAI to extract structured data from RFP text"""
    
    prompt = f"""
    Extract the following information from this RFP/RFQ document:
    
    - Buyer/Client Name (agency, city, organization)
    - RFP/RFQ Number
    - Project Name/Title
    - Services or Products Required
    - Location (specific city/address)
    - Due Date
    - Estimated Contract Value
    - Key Specifications (bullet points)
    - Insurance Requirements
    - Special Requirements
    
    RFP Text:
    {text[:4000]}  # Limit to avoid token limits
    
    Return as JSON format.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert at extracting structured information from RFP documents."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    # Parse AI response
    extracted_json = json.loads(response.choices[0].message.content)
    
    # Sanitize location (suggest generic version)
    if 'location' in extracted_json:
        extracted_json['sanitized_location'] = sanitize_location(extracted_json['location'])
    
    return extracted_json


def sanitize_location(specific_location):
    """Convert specific location to generic area"""
    # Simple logic - can be enhanced
    if 'Auburn Hills' in specific_location:
        return 'Oakland County, Michigan'
    elif 'Detroit' in specific_location:
        return 'Metro Detroit area, Michigan'
    # Add more patterns as needed
    return specific_location


# ============================================================================
# ENDPOINT 2: Generate Supplier RFP (Create PDF)
# ============================================================================

@app.route('/api/rfp/generate', methods=['POST'])
def generate_supplier_rfp():
    """
    Generate professional DDI-branded supplier RFP as PDF
    """
    try:
        data = request.json
        
        # Generate DDI RFP number
        ddi_rfp_number = generate_rfp_number(data.get('category', 'GEN'))
        
        # Save to database
        rfp_record = save_rfp_to_database(ddi_rfp_number, data)
        
        # Generate PDF
        pdf_path = create_rfp_pdf(ddi_rfp_number, data)
        
        return jsonify({
            'success': True,
            'rfp_number': ddi_rfp_number,
            'pdf_path': pdf_path,
            'record_id': rfp_record['id']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def generate_rfp_number(category):
    """Generate unique DDI RFP number"""
    # Get count of RFPs this year
    table = airtable_api.table(BASE_ID, 'SUPPLIER_RFPS')
    records = table.all()
    
    year = datetime.now().year
    count = len([r for r in records if str(year) in r['fields'].get('ddi_rfp_number', '')])
    
    # Category codes
    category_codes = {
        'Pressure Washing': 'PW',
        'Landscaping': 'LS',
        'Janitorial': 'JAN',
        'Construction': 'CON',
        'Supplies': 'SUP',
        'HVAC': 'HVAC',
        'Plumbing': 'PLU',
        'Electrical': 'ELE',
    }
    
    code = category_codes.get(category, 'GEN')
    number = f"DDI-{year}-{code}-{count + 1:03d}"
    
    return number


def save_rfp_to_database(ddi_rfp_number, data):
    """Save RFP to Airtable"""
    table = airtable_api.table(BASE_ID, 'SUPPLIER_RFPS')
    
    record = table.create({
        'ddi_rfp_number': ddi_rfp_number,
        'project_name': data.get('projectName'),
        'category': data.get('category'),
        'sanitized_location': data.get('sanitizedLocation'),
        'scope_of_work': data.get('scopeOfWork'),
        'contract_value_min': data.get('estimatedValue', {}).get('min'),
        'contract_value_max': data.get('estimatedValue', {}).get('max'),
        'quote_due_date': data.get('quoteDueDate'),
        'insurance_requirements': data.get('insuranceRequirements'),
        'status': 'draft',
    })
    
    return record


def create_rfp_pdf(ddi_rfp_number, data):
    """Generate PDF with DDI branding and watermark"""
    
    filename = f"RFP_{ddi_rfp_number}.pdf"
    filepath = os.path.join('generated_rfps', filename)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # COVER PAGE
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("DEE DAVIS INC", styles['Title']))
    story.append(Paragraph("Certified EDWOSB Prime Contractor", styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"REQUEST FOR PROPOSAL", styles['Heading1']))
    story.append(Paragraph(data.get('projectName', ''), styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"RFP Number: {ddi_rfp_number}", styles['Normal']))
    # ... Add more content ...
    
    # Build PDF
    doc.build(story)
    
    # Add watermark (requires additional library like PyPDF2 or reportlab canvas)
    add_watermark_to_pdf(filepath)
    
    return filepath


def add_watermark_to_pdf(pdf_path):
    """Add DEE DAVIS INC watermark to every page"""
    # Implementation using reportlab canvas or PyPDF2
    # This is a placeholder - full implementation would overlay watermark
    pass


# ============================================================================
# ENDPOINT 3: List RFPs
# ============================================================================

@app.route('/api/rfp/list', methods=['GET'])
def list_rfps():
    """Get all RFPs"""
    try:
        table = airtable_api.table(BASE_ID, 'SUPPLIER_RFPS')
        records = table.all()
        
        rfps = [
            {
                'id': r['id'],
                **r['fields']
            }
            for r in records
        ]
        
        return jsonify({
            'success': True,
            'rfps': rfps
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ENDPOINT 4: Publish to Vendor Portal
# ============================================================================

@app.route('/api/rfp/publish', methods=['POST'])
def publish_to_vendor_portal():
    """Publish RFP to public vendor portal"""
    try:
        rfp_id = request.json.get('rfp_id')
        
        # Update status
        table = airtable_api.table(BASE_ID, 'SUPPLIER_RFPS')
        table.update(rfp_id, {
            'status': 'sent',
            'published_to_portal': True,
            'sent_date': datetime.now().isoformat()
        })
        
        # Send email notifications to matching vendors
        # ... Implementation ...
        
        return jsonify({
            'success': True,
            'message': 'RFP published to vendor portal'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ENDPOINT 5: Log Quote Received
# ============================================================================

@app.route('/api/rfp/quote-received', methods=['POST'])
def log_quote_received():
    """Log quote received from vendor"""
    try:
        data = request.json
        
        table = airtable_api.table(BASE_ID, 'VENDOR_QUOTES_RECEIVED')
        record = table.create({
            'supplier_rfp_id': data.get('rfp_id'),
            'vendor_name': data.get('vendor_name'),
            'vendor_email': data.get('vendor_email'),
            'quote_amount': data.get('quote_amount'),
            'quote_notes': data.get('quote_notes'),
            'status': 'received'
        })
        
        # Update RFP quotes count
        rfp_table = airtable_api.table(BASE_ID, 'SUPPLIER_RFPS')
        rfp = rfp_table.get(data.get('rfp_id'))
        current_count = rfp['fields'].get('num_quotes_received', 0)
        rfp_table.update(data.get('rfp_id'), {
            'num_quotes_received': current_count + 1,
            'status': 'quotes_received'
        })
        
        return jsonify({
            'success': True,
            'quote_id': record['id']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5002)
```

---

## 📋 IMPLEMENTATION CHECKLIST

### **PHASE 1: Basic RFP Generator (Week 1-2)**

**Frontend:**
- [ ] Create RFPGenerator.tsx component
- [ ] Upload file functionality
- [ ] Form for manual data entry
- [ ] Preview page
- [ ] Success page with download

**Backend:**
- [ ] Create `/api/rfp/generate` endpoint
- [ ] PDF generation with reportlab or similar
- [ ] Save to Airtable SUPPLIER_RFPS table
- [ ] File storage for PDFs

**Database:**
- [ ] Create SUPPLIER_RFPS table in Airtable
- [ ] Test data entry

**Test:**
- [ ] Create Auburn Hills RFP manually
- [ ] Download PDF
- [ ] Verify watermark and branding

---

### **PHASE 2: AI Parsing (Week 3-4)**

**Backend:**
- [ ] Integrate OpenAI API
- [ ] Create `/api/rfp/parse` endpoint
- [ ] PDF text extraction (PyPDF2)
- [ ] AI extraction of key fields
- [ ] Location sanitization logic

**Frontend:**
- [ ] File upload triggers parsing
- [ ] Display extracted fields for review
- [ ] Allow editing of extracted data

**Test:**
- [ ] Upload Auburn Hills original RFP
- [ ] Verify AI extracts correct information
- [ ] Verify buyer info is flagged as confidential

---

### **PHASE 3: RFP Tracking Dashboard (Week 5-6)**

**Frontend:**
- [ ] Create RFPDashboard.tsx component
- [ ] Stats cards
- [ ] RFP list table
- [ ] Status filtering
- [ ] View/download/email actions

**Backend:**
- [ ] Create `/api/rfp/list` endpoint
- [ ] Create `/api/rfp/quote-received` endpoint
- [ ] Quote tracking in VENDOR_QUOTES_RECEIVED table

**Test:**
- [ ] View all created RFPs
- [ ] Track quotes received
- [ ] Compare vendor quotes

---

### **PHASE 4: Vendor Portal Integration (Week 7-8)**

**Public Website:**
- [ ] Create `/vendors/rfqs` page
- [ ] Display published RFPs
- [ ] Download RFP PDFs
- [ ] Submit quote form

**Backend:**
- [ ] Create `/api/rfp/publish` endpoint
- [ ] Email notifications to vendors
- [ ] Public API for vendor portal

**Test:**
- [ ] Publish RFP to vendor portal
- [ ] Vendors can view and download
- [ ] Quote submission works

---

### **PHASE 5: Templates & Automation (Week 9-10)**

**Backend:**
- [ ] Create RFP_TEMPLATES table
- [ ] Create RFP_SECTIONS_LIBRARY table
- [ ] Template selection logic
- [ ] Section reuse

**Frontend:**
- [ ] Template selection dropdown
- [ ] Section library browser
- [ ] Save custom templates

**Test:**
- [ ] Create RFP from template
- [ ] Reuse sections across RFPs

---

## 🚀 QUICK START (THIS WEEK)

**IMMEDIATE: Manual Process** (No coding yet)
1. Use the RFP I created today (Auburn Hills)
2. Convert to PDF with watermark in Word/Canva
3. Track RFPs in spreadsheet
4. Track quotes in spreadsheet

**NEXT WEEK: Start Building**
1. Create simple form in NEXUS
2. Form generates RFP text
3. Copy/paste into PDF tool
4. Saves to Airtable

**2 WEEKS: Automated PDF**
1. Form generates PDF automatically
2. Watermark added automatically
3. Download ready-to-send PDF

**1 MONTH: Full System**
1. Upload buyer RFP → AI extracts data
2. Review and sanitize
3. Generate professional PDF
4. Track all RFPs and quotes
5. Vendor portal integration

---

**SUMMARY:**

You now have a complete RFP Generator system design that:
- ✅ Protects buyer identity automatically
- ✅ Generates professional DDI-branded RFPs
- ✅ Tracks all RFPs and quotes
- ✅ Integrates with vendor portal
- ✅ Uses AI to parse buyer RFPs
- ✅ Similar workflow to Quote Generator & Capability Statement Generator

**Want me to start building the basic frontend form first, or the backend API?**
