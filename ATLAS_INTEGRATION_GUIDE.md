# ATLAS PM ↔ NEXUS Integration Guide

## Overview

This guide explains how to integrate the existing ATLAS PM HTML system with the NEXUS backend, providing a seamless transition from localStorage-based data to Airtable-powered persistence with AI capabilities.

## Architecture

### Current ATLAS PM HTML System
- **Standalone HTML file** with embedded React
- **localStorage persistence** for data storage
- **No backend dependencies**
- **Complete project management features**

### NEXUS Integration
- **Python Flask backend** with AI agents
- **Airtable database** for data persistence
- **REST API endpoints** for CRUD operations
- **React dashboard** integration
- **DDCSS integration** via data sharing

## Migration Steps

### Step 1: Set Up Airtable Tables

Create the following tables in your Airtable base using the schema in `ATLAS_AIRTABLE_SCHEMA.md`:

1. **ATLAS Projects** - Main project records
2. **ATLAS RFPs** - RFP tracking and analysis
3. **ATLAS Change Orders** - Change management
4. **ATLAS WBS** - Work breakdown structures
5. **ATLAS RFP Analysis** - AI analysis results
6. **ATLAS Project Logs** - Activity tracking

### Step 2: Extract Data from HTML System

Use the migration utility to extract existing data:

```bash
# Extract data from ATLAS PM HTML file
python atlas_migration.py --export-html-data "/path/to/ATLAS_PM_v2.1_COMPLETE.html"

# This creates: atlas_extracted_data.json
```

### Step 3: Migrate Data to Airtable

```bash
# Migrate extracted data to Airtable
python atlas_migration.py \
  --migrate-to-airtable atlas_extracted_data.json \
  --airtable-key YOUR_AIRTABLE_API_KEY \
  --airtable-base YOUR_AIRTABLE_BASE_ID
```

### Step 4: Validate Migration

```bash
# Validate that data was migrated correctly
python atlas_migration.py --validate-migration \
  --airtable-key YOUR_AIRTABLE_API_KEY \
  --airtable-base YOUR_AIRTABLE_BASE_ID
```

## API Endpoints

### Project Management
```javascript
// Get all projects
GET /atlas/projects

// Create new project
POST /atlas/projects
{
  "name": "Project Name",
  "client": "Client Name",
  "budget": 100000,
  "timeline": "6 months"
}

// Get specific project
GET /atlas/projects/{project_id}

// Update project
PUT /atlas/projects/{project_id}
{
  "status": "Active",
  "completion_percentage": 25
}
```

### RFP Management
```javascript
// Get RFPs (optionally filtered by project)
GET /atlas/rfps?project_id={project_id}

// Create RFP
POST /atlas/rfps
{
  "name": "RFP Title",
  "client": "Client Name",
  "value": 50000,
  "due_date": "2025-02-01"
}

// AI RFP Analysis
POST /atlas/analyze-rfp
{
  "rfp_content": "Full RFP text content...",
  "project_id": "rec123" // optional
}
```

### Change Orders
```javascript
// Get change orders
GET /atlas/change-orders?project_id={project_id}

// Create change order
POST /atlas/change-orders
{
  "project_id": "rec123",
  "title": "Scope Change Request",
  "description": "Detailed change description",
  "type": "Scope"
}

// AI Change Impact Analysis
POST /atlas/analyze-change-request
{
  "change_description": "Change details...",
  "project_id": "rec123"
}
```

### AI-Powered Features
```javascript
// Generate WBS (Work Breakdown Structure)
POST /atlas/generate-wbs
{
  "project_id": "rec123"
}
```

## React Dashboard Integration

The ATLAS PM system is now accessible through the NEXUS React dashboard:

```javascript
// In the React dashboard, users can:
// 1. View all projects and RFPs
// 2. Create new projects and RFPs
// 3. Use AI RFP analysis
// 4. Generate WBS automatically
// 5. Manage change orders with AI impact assessment
```

## DDCSS ↔ ATLAS PM Integration

### Data Flow
1. **DDCSS creates RFP** → Exports to localStorage (`ddcss_rfp_data`)
2. **ATLAS PM imports** → Processes via `/atlas/analyze-rfp` endpoint
3. **AI Analysis** → Extracts requirements, risks, win strategy
4. **Project Creation** → Links RFP to project management

### Integration Points
- **RFP Data Sharing**: `ddcss_rfp_data` → ATLAS RFP records
- **Status Sync**: RFP status updates flow between systems
- **Project Linking**: DDCSS RFPs become ATLAS projects

## Testing the Integration

### 1. Backend Testing
```bash
# Test health endpoint
curl http://127.0.0.1:8000/health

# Test project creation
curl -X POST http://127.0.0.1:8000/atlas/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Project","client":"Test Client"}'
```

### 2. Frontend Testing
```bash
# Start React dashboard
cd nexus-dashboard && npm start

# Navigate to ATLAS PM section
# Test project creation, RFP analysis, etc.
```

### 3. End-to-End Testing
1. Create RFP in DDCSS system
2. Export to localStorage
3. Import in ATLAS PM (via API)
4. Run AI analysis
5. Create project and WBS
6. Test change order workflow

## Migration Checklist

### Pre-Migration
- [ ] Airtable tables created with correct schema
- [ ] API keys configured in environment
- [ ] ATLAS PM HTML file accessible
- [ ] Data backup created (if any existing data)

### Migration Execution
- [ ] Extract data from HTML: `python atlas_migration.py --export-html-data ...`
- [ ] Migrate to Airtable: `python atlas_migration.py --migrate-to-airtable ...`
- [ ] Validate migration: `python atlas_migration.py --validate-migration`
- [ ] Test API endpoints with migrated data

### Post-Migration
- [ ] React dashboard shows migrated data
- [ ] AI features work with existing projects
- [ ] DDCSS integration functions
- [ ] Change order workflow operational

## Troubleshooting

### Common Issues

**Migration Fails**
- Check Airtable API key and base ID
- Verify table names match schema exactly
- Ensure network connectivity

**API Errors**
- Check Flask server is running: `curl http://127.0.0.1:8000/health`
- Verify environment variables are set
- Check Airtable permissions

**Data Import Issues**
- Validate JSON structure in extracted data
- Check for special characters in project names
- Ensure date formats are ISO 8601

### Data Recovery
If migration fails, original data remains in:
- HTML localStorage (browser-based)
- `atlas_extracted_data.json` backup file
- Manual re-migration possible

## Performance Considerations

### API Rate Limits
- Airtable: 5 requests/second, 1000 records/request
- Claude AI: Token limits and rate limits apply
- Implement caching for frequently accessed data

### Data Volume
- Large RFP documents truncated to fit Airtable limits
- WBS data stored as JSON for complex structures
- Implement pagination for large result sets

## Future Enhancements

### Phase 2 Features
- Real-time collaboration
- Advanced reporting and analytics
- Mobile app integration
- CRM system sync
- Automated follow-up workflows

### Advanced AI Features
- Predictive project success scoring
- Resource optimization recommendations
- Risk trend analysis
- Automated status updates

---

## Quick Start Commands

```bash
# 1. Set up environment
export AIRTABLE_API_KEY="your_key"
export AIRTABLE_BASE_ID="your_base"

# 2. Extract data from HTML
python atlas_migration.py --export-html-data ATLAS_PM_v2.1_COMPLETE.html

# 3. Migrate to Airtable
python atlas_migration.py --migrate-to-airtable atlas_extracted_data.json

# 4. Start services
python api_server.py &  # Backend
cd nexus-dashboard && npm start  # Frontend
```

## Support

For issues with:
- **Migration**: Check `atlas_migration.py` error messages
- **API Issues**: Review Flask server logs
- **Data Problems**: Validate Airtable table schemas
- **Integration**: Test with sample data first

The integration maintains backward compatibility - existing HTML systems continue to work while new features are added through the NEXUS backend.
