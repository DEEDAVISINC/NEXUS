# ATLAS PM Airtable Schema

## Overview
ATLAS PM (Project Management System) requires 6 Airtable tables to support the complete project lifecycle management, RFP analysis, and change order tracking.

## Table 1: ATLAS Projects
**Purpose**: Main project records with complete project information

**Fields**:
- `Project ID` (Auto-number, Primary Key)
- `Project Name` (Single line text) - Required
- `Client Name` (Single line text) - Required
- `Project Type` (Single select) - Options: Consulting, Development, Implementation, Support
- `Industry` (Single line text)
- `Project Scope` (Long text)
- `Budget` (Currency)
- `Timeline` (Single line text) - e.g., "8 weeks", "3 months"
- `Start Date` (Date)
- `End Date` (Date)
- `Status` (Single select) - Options: Planning, Active, On-Hold, Completed, Cancelled
- `Priority` (Single select) - Options: Low, Medium, High, Critical
- `Project Manager` (Single line text)
- `Team Members` (Multiple select) - For future expansion
- `Completion Percentage` (Number, 0-100)
- `Risk Level` (Single select) - Options: Low, Medium, High
- `Created Date` (Date, auto-populated)
- `Last Updated` (Date, auto-populated)

## Table 2: ATLAS RFPs
**Purpose**: RFP tracking and management with analysis integration

**Fields**:
- `RFP ID` (Auto-number, Primary Key)
- `RFP Name` (Single line text) - Required
- `Client Name` (Single line text) - Required
- `RFP Number` (Single line text)
- `Value` (Currency)
- `Due Date` (Date)
- `Industry` (Single line text)
- `Description` (Long text)
- `Contact Name` (Single line text)
- `Contact Email` (Email)
- `Contact Phone` (Phone number)
- `Status` (Single select) - Options: Draft, Submitted, Won, Lost, Withdrawn
- `Probability` (Number, 0-100)
- `Submission Date` (Date)
- `Win/Loss Reason` (Long text)
- `Competition` (Multiple select) - Competitor names
- `Requirements Count` (Number)
- `Compliance Score` (Number, 0-100)
- `Risk Assessment` (Long text)
- `Assigned To` (Single line text)
- `Created Date` (Date, auto-populated)
- `Last Updated` (Date, auto-populated)

## Table 3: ATLAS Change Orders
**Purpose**: Change order tracking and impact analysis

**Fields**:
- `CO ID` (Auto-number, Primary Key)
- `Project ID` (Link to ATLAS Projects)
- `Title` (Single line text) - Required
- `Description` (Long text) - Required
- `Type` (Single select) - Options: Scope, Schedule, Budget, Quality, Resources
- `Priority` (Single select) - Options: Low, Medium, High, Critical
- `Impact Scope` (Single select) - Options: Low, Medium, High
- `Impact Schedule` (Single line text) - e.g., "+2 weeks", "-1 week"
- `Impact Budget` (Currency)
- `Status` (Single select) - Options: Draft, Submitted, Approved, Rejected, Implemented
- `Requested By` (Single line text)
- `Approved By` (Single line text)
- `Approval Date` (Date)
- `Implementation Date` (Date)
- `Contractual Implications` (Long text)
- `Client Notification Required` (Checkbox)
- `Created Date` (Date, auto-populated)
- `Last Updated` (Date, auto-populated)

## Table 4: ATLAS WBS (Work Breakdown Structure)
**Purpose**: Project planning and task breakdown storage

**Fields**:
- `WBS ID` (Auto-number, Primary Key)
- `Project ID` (Link to ATLAS Projects) - Required
- `WBS Data` (Long text) - JSON string containing full WBS structure
- `Critical Path` (Long text) - JSON array of critical path task IDs
- `Total Tasks` (Number)
- `Estimated Hours` (Number)
- `Resource Allocation` (Long text) - JSON object with resource assignments
- `Milestones` (Long text) - JSON array of milestone objects
- `Risk Mitigation` (Long text) - JSON array of risk mitigation strategies
- `Generated Date` (Date, auto-populated)
- `Version` (Number) - For tracking WBS versions

## Table 5: ATLAS RFP Analysis
**Purpose**: AI-generated RFP analysis results storage

**Fields**:
- `Analysis ID` (Auto-number, Primary Key)
- `Project ID` (Link to ATLAS Projects)
- `RFP Content` (Long text) - Truncated RFP content for reference
- `Analysis Result` (Long text) - JSON string with full AI analysis
- `Executive Summary` (Long text)
- `Key Requirements Count` (Number)
- `Compliance Requirements` (Long text) - JSON array
- `Timeline Analysis` (Long text) - JSON object
- `Budget Estimate` (Long text) - JSON object
- `Win Strategy` (Long text) - JSON object
- `Risk Assessment` (Long text) - JSON object
- `Recommended Team` (Long text) - JSON array
- `Confidence Score` (Number, 0-100)
- `Analyzed Date` (Date, auto-populated)

## Table 6: ATLAS Project Logs
**Purpose**: Activity logging and project history

**Fields**:
- `Log ID` (Auto-number, Primary Key)
- `Project ID` (Link to ATLAS Projects) - Required
- `Entry Date` (Date) - Required
- `Entry Time` (Time)
- `Log Type` (Single select) - Options: Status Update, Milestone, Issue, Decision, Meeting, Deliverable
- `Title` (Single line text) - Required
- `Description` (Long text)
- `Category` (Single select) - Options: Planning, Execution, Risk, Quality, Communication, Financial
- `Priority` (Single select) - Options: Low, Medium, High, Critical
- `Status` (Single select) - Options: Open, In Progress, Resolved, Closed
- `Assigned To` (Single line text)
- `Due Date` (Date)
- `Resolution Date` (Date)
- `Created By` (Single line text)
- `Created Date` (Date, auto-populated)

## Integration Notes

### DDCSS ↔ ATLAS PM Data Flow
- **Source**: DDCSS exports `ddcss_rfp_data` to localStorage
- **Destination**: ATLAS PM imports via `/atlas/analyze-rfp` endpoint
- **Mapping**: DDCSS RFP fields → ATLAS RFP fields
- **Trigger**: Manual import or automatic detection

### Data Relationships
```
ATLAS Projects (1) → (Many) ATLAS RFPs
ATLAS Projects (1) → (Many) ATLAS Change Orders
ATLAS Projects (1) → (Many) ATLAS WBS
ATLAS Projects (1) → (Many) ATLAS RFP Analysis
ATLAS Projects (1) → (Many) ATLAS Project Logs
```

### API Endpoints Required
- `GET /atlas/projects` - List all projects
- `POST /atlas/projects` - Create new project
- `GET /atlas/projects/{id}` - Get project details
- `PUT /atlas/projects/{id}` - Update project
- `GET /atlas/rfps` - List RFPs (with project filter)
- `POST /atlas/rfps` - Create RFP
- `POST /atlas/analyze-rfp` - AI RFP analysis (existing)
- `POST /atlas/generate-wbs` - Generate WBS (existing)
- `GET /atlas/change-orders` - List change orders
- `POST /atlas/change-orders` - Create change order
- `POST /atlas/analyze-change-request` - Change impact analysis (existing)

### Migration Strategy
1. Create Airtable tables with above schemas
2. Export data from HTML localStorage
3. Transform data to match Airtable schema
4. Import via API endpoints
5. Update HTML to use API calls (optional)

### Performance Considerations
- WBS data stored as JSON in single field for complex structures
- RFP analysis truncated to fit Airtable text limits (100,000 chars)
- Use pagination for large result sets
- Implement caching for frequently accessed data
